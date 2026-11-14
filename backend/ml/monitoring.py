"""
FocusFlow ACLI - Operational Monitoring & Feature Drift Engine
==============================================================
Logs inference requests to SQLite and computes production serving metrics
including request volumes, latency percentiles, difficulty class distributions,
and feature drift (Population Stability Index - PSI) against baseline training data.

Methodological Note:
Input feature drift measures shifts in text characteristics (e.g., user reading
more academic vs elementary articles). It is strictly distinguished from model
accuracy degradation, which can only be evaluated against true ground-truth labels.
"""

import sqlite3
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

from .features import FEATURE_COLUMNS, FEATURE_DESCRIPTIONS
from .dataset import VALID_CLASSES

DB_PATH = Path(__file__).resolve().parent / "artifacts" / "ml_monitoring.db"
DRIFT_THRESHOLD = 0.1  # PSI threshold for alerting


def init_monitoring_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ml_predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        model_version TEXT NOT NULL,
        latency_ms REAL NOT NULL,
        predicted_difficulty TEXT NOT NULL,
        confidence REAL NOT NULL,
        features_json TEXT NOT NULL,
        success INTEGER NOT NULL DEFAULT 1,
        error_message TEXT
    )
    """)
    conn.commit()
    conn.close()


def log_prediction(
    model_version: str,
    latency_ms: float,
    predicted_difficulty: str,
    confidence: float,
    features: Dict[str, float],
    success: bool = True,
    error_message: Optional[str] = None
):
    """
    Persists inference telemetry to SQLite.
    """
    init_monitoring_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO ml_predictions (
        timestamp, model_version, latency_ms, predicted_difficulty,
        confidence, features_json, success, error_message
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        model_version,
        round(latency_ms, 2),
        predicted_difficulty,
        round(confidence, 4),
        json.dumps(features),
        1 if success else 0,
        error_message
    ))
    conn.commit()
    conn.close()


def calculate_psi(baseline: np.ndarray, current: np.ndarray, num_buckets: int = 5) -> float:
    """
    Calculates Population Stability Index (PSI) between baseline and current feature distributions.
    Interpretation:
    - PSI < 0.1: No significant drift / Stable
    - 0.1 <= PSI < 0.2: Moderate shift / Warning
    - PSI >= 0.2: Significant drift / Action required
    """
    if len(baseline) == 0 or len(current) == 0:
        return 0.0

    # Ensure variance
    if np.all(baseline == baseline[0]):
        return 0.0

    # Define quantile buckets based on baseline with open -inf and +inf ends
    percentiles = np.linspace(0, 100, num_buckets + 1)
    bucket_bounds = np.percentile(baseline, percentiles)

    # Ensure strictly monotonic interior bounds
    for i in range(1, len(bucket_bounds) - 1):
        if bucket_bounds[i] <= bucket_bounds[i - 1]:
            bucket_bounds[i] = bucket_bounds[i - 1] + 1e-4

    bucket_bounds[0] = -np.inf
    bucket_bounds[-1] = np.inf

    # Count proportions in buckets
    b_counts, _ = np.histogram(baseline, bins=bucket_bounds)
    c_counts, _ = np.histogram(current, bins=bucket_bounds)

    b_probs = np.maximum(b_counts, 1) / float(np.sum(np.maximum(b_counts, 1)))
    c_probs = np.maximum(c_counts, 1) / float(np.sum(np.maximum(c_counts, 1)))

    psi_val = np.sum((c_probs - b_probs) * np.log(c_probs / b_probs))
    return float(max(0.0, psi_val))


def get_monitoring_dashboard_data(
    reference_features: Optional[Dict[str, List[float]]] = None,
    limit: int = 500
) -> Dict[str, Any]:
    """
    Aggregates live serving statistics, latency percentiles, difficulty distributions,
    and feature drift status from actual production logs.
    """
    init_monitoring_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM ml_predictions ORDER BY id DESC LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()

    total_requests = len(rows)
    if total_requests == 0:
        return {
            "has_data": False,
            "total_requests": 0,
            "error_rate": 0.0,
            "latency": {"p50_ms": 0.0, "p95_ms": 0.0, "mean_ms": 0.0},
            "class_distribution": {cls_name: 0.0 for cls_name in VALID_CLASSES},
            "feature_drift": {
                "overall_drift_status": "NO_DATA",
                "features": {}
            },
            "recent_predictions": []
        }

    successful = [r for r in rows if r["success"] == 1]
    failed = [r for r in rows if r["success"] == 0]
    error_rate = len(failed) / total_requests

    latencies = [r["latency_ms"] for r in successful] if successful else [0.0]
    p50_lat = float(np.percentile(latencies, 50))
    p95_lat = float(np.percentile(latencies, 95))
    mean_lat = float(np.mean(latencies))

    # Difficulty distribution
    class_counts = {cls_name: 0 for cls_name in VALID_CLASSES}
    for r in successful:
        diff = r["predicted_difficulty"]
        if diff in class_counts:
            class_counts[diff] += 1

    class_dist = {
        cls_name: round((class_counts[cls_name] / len(successful)), 4) if successful else 0.0
        for cls_name in VALID_CLASSES
    }

    # Feature Drift Analysis
    feature_drift_results: Dict[str, Any] = {}
    any_high_drift = False
    any_mod_drift = False

    # Extract parsed features from rows
    current_features: Dict[str, List[float]] = {col: [] for col in FEATURE_COLUMNS}
    for r in successful:
        try:
            feats = json.loads(r["features_json"])
            for col in FEATURE_COLUMNS:
                if col in feats:
                    current_features[col].append(float(feats[col]))
        except Exception:
            continue

    for col in FEATURE_COLUMNS:
        cur_vals = np.array(current_features.get(col, []))
        if reference_features and col in reference_features:
            ref_vals = np.array(reference_features[col])
        else:
            # Baseline reference default if not provided
            ref_vals = cur_vals

        if len(cur_vals) >= 5 and len(ref_vals) >= 5:
            psi = calculate_psi(ref_vals, cur_vals)
            cur_mean = float(np.mean(cur_vals))
            ref_mean = float(np.mean(ref_vals))

            if psi >= 0.2:
                status = "SIGNIFICANT_DRIFT"
                any_high_drift = True
            elif psi >= 0.1:
                status = "MODERATE_DRIFT"
                any_mod_drift = True
            else:
                status = "STABLE"

            feature_drift_results[col] = {
                "psi": round(psi, 4),
                "status": status,
                "current_mean": round(cur_mean, 2),
                "reference_mean": round(ref_mean, 2),
                "description": FEATURE_DESCRIPTIONS.get(col, col)
            }
        else:
            feature_drift_results[col] = {
                "psi": 0.0,
                "status": "INSUFFICIENT_SAMPLES",
                "current_mean": round(float(np.mean(cur_vals)), 2) if len(cur_vals) > 0 else 0.0,
                "reference_mean": 0.0,
                "description": FEATURE_DESCRIPTIONS.get(col, col)
            }

    overall_status = "STABLE"
    if any_high_drift:
        overall_status = "DRIFT_DETECTED"
    elif any_mod_drift:
        overall_status = "WARNING"

    # Recent prediction log entries for display
    recent_sample = []
    for r in rows[:15]:
        recent_sample.append({
            "id": r["id"],
            "timestamp": r["timestamp"],
            "model_version": r["model_version"],
            "predicted_difficulty": r["predicted_difficulty"],
            "confidence": r["confidence"],
            "latency_ms": r["latency_ms"],
            "success": bool(r["success"])
        })

    return {
        "has_data": True,
        "total_requests": total_requests,
        "successful_requests": len(successful),
        "error_rate": round(error_rate, 4),
        "latency": {
            "p50_ms": round(p50_lat, 2),
            "p95_ms": round(p95_lat, 2),
            "mean_ms": round(mean_lat, 2)
        },
        "class_counts": class_counts,
        "class_distribution": class_dist,
        "feature_drift": {
            "overall_drift_status": overall_status,
            "features": feature_drift_results
        },
        "recent_predictions": recent_sample
    }


def get_monitoring_summary(days: int = 7) -> Dict[str, Any]:
    """
    Get summary of monitoring metrics for the last N days.
    
    Args:
        days: Number of days to look back
        
    Returns:
        Dictionary with monitoring summary
    """
    db_path = DB_PATH
    if not db_path.exists():
        return {
            "feature_psi_max": 0.0,
            "days": days,
            "records": 0
        }
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Get max PSI from last N days
        cutoff_date = datetime.now() - timedelta(days=days)
        
        cursor.execute("""
            SELECT MAX(psi_score), COUNT(*)
            FROM drift_monitoring
            WHERE timestamp >= ?
        """, (cutoff_date.isoformat(),))
        
        result = cursor.fetchone()
        conn.close()
        
        max_psi = result[0] if result[0] is not None else 0.0
        count = result[1] if result[1] is not None else 0
        
        return {
            "feature_psi_max": max_psi,
            "days": days,
            "records": count,
            "cutoff_date": cutoff_date.isoformat()
        }
    except Exception as e:
        print(f"[Monitoring] Error getting summary: {e}")
        return {
            "feature_psi_max": 0.0,
            "days": days,
            "records": 0,
            "error": str(e)
        }
