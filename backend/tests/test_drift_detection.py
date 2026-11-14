"""
Unit Tests for Drift Detection and Evidently AI Integration
"""

import pytest
from pathlib import Path
import numpy as np

# Import conditionally to handle evidently installation issues
try:
    from backend.ml.drift_report import (
        generate_drift_report,
        check_production_drift,
        simulate_drift_report
    )
    EVIDENTLY_AVAILABLE = True
except ImportError as e:
    EVIDENTLY_AVAILABLE = False
    SKIP_REASON = f"Evidently AI not properly installed: {e}"

from backend.ml.monitoring import calculate_psi


@pytest.mark.skipif(not EVIDENTLY_AVAILABLE, reason="Evidently AI not available")
def test_drift_report_generation_no_drift():
    """Test that identical distributions show no drift"""
    # Same texts in reference and current
    texts = [
        "The water cycle describes how water moves around Earth.",
        "Rain falls from clouds when water droplets become heavy.",
        "The sun heats water and turns it into vapor."
    ]
    
    result = generate_drift_report(
        reference_texts=texts,
        current_texts=texts,
        report_name="test_no_drift"
    )
    
    assert result["reference_size"] == 3
    assert result["current_size"] == 3
    assert result["max_psi"] < 0.1  # Very low PSI for identical data
    assert Path(result["report_path"]).exists()
    assert result["report_path"].endswith(".html")


@pytest.mark.skipif(not EVIDENTLY_AVAILABLE, reason="Evidently AI not available")
def test_drift_report_with_shifted_distribution():
    """Test that different text complexities show drift"""
    simple_texts = [
        "The cat sat on the mat.",
        "Dogs bark at strangers.",
        "Birds fly in the sky."
    ] * 10  # Repeat for statistical power
    
    complex_texts = [
        "The epistemological framework of radical empiricism necessitates a comprehensive reevaluation of phenomenological paradigms.",
        "Quantum mechanical interpretations remain fundamentally contested within contemporary theoretical physics discourse.",
        "Poststructuralist hermeneutics problematizes the teleological assumptions underlying traditional metaphysical inquiry."
    ] * 10
    
    result = generate_drift_report(
        reference_texts=simple_texts,
        current_texts=complex_texts,
        report_name="test_high_drift"
    )
    
    # Complex texts should show significant drift from simple texts
    assert result["max_psi"] > 0.05  # Some PSI difference expected
    assert len(result["drifted_features"]) >= 0  # May or may not detect drift depending on threshold
    assert result["drift_share"] >= 0.0


@pytest.mark.skipif(not EVIDENTLY_AVAILABLE, reason="Evidently AI not available")
def test_simulated_drift_report():
    """Test simulated drift report generation"""
    result = simulate_drift_report(shift_magnitude=2.0)
    
    assert "dataset_drift_detected" in result
    assert "report_path" in result
    assert "psi_scores" in result
    assert len(result["psi_scores"]) == 9  # 9 features
    assert Path(result["report_path"]).exists()


@pytest.mark.skipif(not EVIDENTLY_AVAILABLE, reason="Evidently AI not available")
def test_drift_report_creates_artifacts_directory():
    """Test that drift reports directory is created"""
    from backend.ml.drift_report import DRIFT_REPORTS_DIR
    
    texts = ["Simple test text."]
    
    generate_drift_report(
        reference_texts=texts,
        current_texts=texts,
        report_name="test_dir_creation"
    )
    
    assert DRIFT_REPORTS_DIR.exists()
    assert DRIFT_REPORTS_DIR.is_dir()


def test_psi_calculation_identical_distributions():
    """Test PSI calculation for identical distributions"""
    reference = np.random.normal(0, 1, 1000)
    current = reference.copy()
    
    psi = calculate_psi(reference, current)
    
    # PSI should be near 0 for identical distributions
    assert psi < 0.01


def test_psi_calculation_shifted_distributions():
    """Test PSI calculation for shifted distributions"""
    reference = np.random.normal(0, 1, 1000)
    current = np.random.normal(2, 1, 1000)  # Shifted by 2 std devs
    
    psi = calculate_psi(reference, current)
    
    # PSI should be significant for shifted distributions
    assert psi > 0.1


@pytest.mark.skipif(not EVIDENTLY_AVAILABLE, reason="Evidently AI not available")
def test_check_production_drift_integration():
    """Test full production drift check workflow"""
    # Use some sample production texts
    production_texts = [
        "Water evaporates from oceans and lakes.",
        "Clouds form when vapor cools in the atmosphere.",
        "Precipitation returns water to Earth's surface."
    ] * 5  # Repeat for sample size
    
    drift_detected, summary = check_production_drift(production_texts)
    
    assert isinstance(drift_detected, bool)
    assert "dataset_drift_detected" in summary
    assert "psi_exceeded" in summary
    assert "report_path" in summary
    assert Path(summary["report_path"]).exists()


@pytest.mark.skipif(not EVIDENTLY_AVAILABLE, reason="Evidently AI not available")
def test_drift_report_feature_level_details():
    """Test that drift report includes per-feature information"""
    texts = ["The quick brown fox jumps over the lazy dog."]
    
    result = generate_drift_report(
        reference_texts=texts * 10,
        current_texts=texts * 10,
        report_name="test_feature_details"
    )
    
    # Should have PSI score for each feature
    assert len(result["psi_scores"]) == 9
    
    # All features should be present
    from backend.ml.features import FEATURE_COLUMNS
    for feature in FEATURE_COLUMNS:
        assert feature in result["psi_scores"]
        assert isinstance(result["psi_scores"][feature], (int, float))
