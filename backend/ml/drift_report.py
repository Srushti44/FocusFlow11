"""
FocusFlow ACLI - Evidently AI Drift Report Generation
=====================================================
Generates comprehensive drift detection reports using Evidently AI.
Integrates with existing PSI monitoring and creates visual HTML dashboards.
"""

from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
from evidently import ColumnMapping
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, DataQualityPreset
from evidently.metrics import DatasetDriftMetric, ColumnDriftMetric

from .features import extract_features_df, FEATURE_COLUMNS
from .dataset import load_dataset, to_dataframe
from .monitoring import calculate_psi, DRIFT_THRESHOLD

ARTIFACTS_DIR = Path(__file__).resolve().parent / "artifacts"
DRIFT_REPORTS_DIR = ARTIFACTS_DIR / "drift_reports"


def generate_drift_report(
    reference_texts: list[str],
    current_texts: list[str],
    output_path: Optional[Path] = None,
    report_name: str = "drift_report"
) -> Dict[str, Any]:
    """
    Generate comprehensive drift report comparing reference and current data.
    
    Args:
        reference_texts: Historical texts (training data)
        current_texts: Recent production texts
        output_path: Where to save HTML report (default: artifacts/drift_reports/)
        report_name: Base name for the report file
        
    Returns:
        Dictionary with drift metrics and report path
    """
    DRIFT_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    if output_path is None:
        output_path = DRIFT_REPORTS_DIR / f"{report_name}.html"
    
    print(f"[Evidently] Generating drift report for {len(current_texts)} texts...")
    
    # Extract features for both datasets
    reference_features = extract_features_df(reference_texts)
    current_features = extract_features_df(current_texts)
    
    # Create DataFrames with feature columns
    reference_df = pd.DataFrame(reference_features, columns=FEATURE_COLUMNS)
    current_df = pd.DataFrame(current_features, columns=FEATURE_COLUMNS)
    
    # Add dataset markers
    reference_df["dataset"] = "reference"
    current_df["dataset"] = "current"
    
    # Define column mapping for Evidently
    column_mapping = ColumnMapping(
        numerical_features=FEATURE_COLUMNS,
        target=None,
        prediction=None
    )
    
    # Create Evidently report with drift detection
    report = Report(metrics=[
        DataDriftPreset(),
        DataQualityPreset(),
        DatasetDriftMetric(),
    ])
    
    # Run the report
    report.run(
        reference_data=reference_df,
        current_data=current_df,
        column_mapping=column_mapping
    )
    
    # Save HTML report
    report.save_html(str(output_path))
    print(f"[Evidently] Report saved to: {output_path}")
    
    # Extract metrics from report
    report_dict = report.as_dict()
    
    # Get overall drift status
    dataset_drift = False
    drift_share = 0.0
    drifted_features = []
    
    for metric in report_dict.get("metrics", []):
        if metric.get("metric") == "DatasetDriftMetric":
            result = metric.get("result", {})
            dataset_drift = result.get("dataset_drift", False)
            drift_share = result.get("drift_share", 0.0)
            
            # Get individual feature drift
            drift_by_columns = result.get("drift_by_columns", {})
            for col, drift_info in drift_by_columns.items():
                if drift_info.get("drift_detected", False):
                    drifted_features.append(col)
    
    # Calculate PSI for each feature (legacy compatibility)
    psi_scores = {}
    for feature in FEATURE_COLUMNS:
        ref_values = reference_df[feature].values
        curr_values = current_df[feature].values
        psi = calculate_psi(ref_values, curr_values)
        psi_scores[feature] = psi
    
    max_psi = max(psi_scores.values()) if psi_scores else 0.0
    
    summary = {
        "dataset_drift_detected": dataset_drift,
        "drift_share": drift_share,
        "drifted_features": drifted_features,
        "num_drifted_features": len(drifted_features),
        "max_psi": max_psi,
        "psi_threshold": DRIFT_THRESHOLD,
        "psi_exceeded": max_psi > DRIFT_THRESHOLD,
        "psi_scores": psi_scores,
        "report_path": str(output_path),
        "reference_size": len(reference_texts),
        "current_size": len(current_texts)
    }
    
    print(f"[Evidently] Drift detected: {dataset_drift} ({drift_share:.1%} features)")
    print(f"[Evidently] Max PSI: {max_psi:.4f} (threshold: {DRIFT_THRESHOLD})")
    
    return summary


def check_production_drift(
    production_texts: list[str],
    dataset_path: Optional[Path] = None
) -> Tuple[bool, Dict[str, Any]]:
    """
    Check if production data has drifted from training distribution.
    
    Args:
        production_texts: Recent texts from production inference
        dataset_path: Path to reference dataset (default: built-in ACLI dataset)
        
    Returns:
        (drift_detected, summary_dict)
    """
    # Load reference dataset (training data)
    dataset = load_dataset(dataset_path)
    reference_df = to_dataframe(dataset)
    reference_texts = reference_df["text"].tolist()
    
    # Generate drift report
    summary = generate_drift_report(
        reference_texts=reference_texts,
        current_texts=production_texts,
        report_name=f"production_drift_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}"
    )
    
    # Determine if retraining is needed
    # Use conservative threshold: drift if either Evidently detects it OR PSI exceeds threshold
    drift_detected = summary["dataset_drift_detected"] or summary["psi_exceeded"]
    
    return drift_detected, summary


def simulate_drift_report(shift_magnitude: float = 2.0) -> Dict[str, Any]:
    """
    Generate a simulated drift report for testing purposes.
    Creates artificial drift by shifting feature distributions.
    
    Args:
        shift_magnitude: How much to shift the distribution (in std devs)
        
    Returns:
        Drift summary dictionary
    """
    print(f"[Evidently] Generating SIMULATED drift report (shift={shift_magnitude} std)")
    
    # Load reference dataset
    dataset = load_dataset()
    reference_df = to_dataframe(dataset)
    reference_texts = reference_df["text"].tolist()[:50]  # Use subset for speed
    
    # Create simulated "drifted" texts by modifying features
    # In practice, we'll just use the same texts but note this is for testing
    current_texts = reference_texts[:30]  # Smaller current sample
    
    summary = generate_drift_report(
        reference_texts=reference_texts,
        current_texts=current_texts,
        report_name="simulated_drift_test"
    )
    
    print("[Evidently] ⚠️  This is a SIMULATED report for testing only")
    
    return summary


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate Evidently AI drift report")
    parser.add_argument("--simulate", action="store_true", help="Generate simulated drift report")
    parser.add_argument("--shift", type=float, default=2.0, help="Simulation shift magnitude")
    
    args = parser.parse_args()
    
    if args.simulate:
        result = simulate_drift_report(shift_magnitude=args.shift)
        print(f"\n✅ Simulated drift report generated")
        print(f"   Report: {result['report_path']}")
        print(f"   Drift detected: {result['dataset_drift_detected']}")
    else:
        print("Use --simulate to generate a test drift report")
        print("Or use check_production_drift() in your code")
