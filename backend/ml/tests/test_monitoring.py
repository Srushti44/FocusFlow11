"""
Unit Tests for MLOps Monitoring and PSI Feature Drift Engine
"""

import pytest
import numpy as np

from backend.ml.monitoring import (
    calculate_psi,
    log_prediction,
    get_monitoring_dashboard_data,
    init_monitoring_db
)


def test_psi_identical_distributions():
    # Identical/near-identical distributions should have PSI close to 0
    np.random.seed(42)
    baseline = np.random.normal(loc=15.0, scale=3.0, size=500)
    current = baseline.copy()
    psi = calculate_psi(baseline, current)
    assert psi < 0.05


def test_psi_shifted_distributions_detects_drift():
    # Significant shift in mean should result in high PSI
    np.random.seed(42)
    baseline = np.random.normal(loc=10.0, scale=2.0, size=100)
    shifted = np.random.normal(loc=35.0, scale=5.0, size=100)
    psi = calculate_psi(baseline, shifted)
    assert psi >= 0.20  # Significant drift threshold


def test_monitoring_logging_and_aggregation():
    init_monitoring_db()

    # Log test predictions
    log_prediction(
        model_version="test-v1",
        latency_ms=18.5,
        predicted_difficulty="Easy",
        confidence=0.92,
        features={"avg_sentence_length": 12.0, "word_count": 65.0},
        success=True
    )
    log_prediction(
        model_version="test-v1",
        latency_ms=32.1,
        predicted_difficulty="Hard",
        confidence=0.88,
        features={"avg_sentence_length": 29.0, "word_count": 110.0},
        success=True
    )

    data = get_monitoring_dashboard_data(limit=50)
    assert data["has_data"] is True
    assert data["total_requests"] >= 2
    assert data["latency"]["mean_ms"] > 0
    assert "class_counts" in data
    assert "feature_drift" in data
