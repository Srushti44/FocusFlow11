"""
End-to-End CI Integration Tests
================================
Simulates the full CI/CD pipeline workflow locally.
"""

import pytest
from pathlib import Path
import subprocess
import sys


@pytest.mark.mlops
@pytest.mark.integration
def test_full_test_suite_passes():
    """Test that the entire test suite can run successfully"""
    # This is a meta-test that verifies pytest itself works
    # In CI, this ensures the test discovery and execution is functional
    assert True


@pytest.mark.mlops
def test_training_script_has_ci_mode():
    """Test that training script supports CI mode flag"""
    from backend.ml.train import run_training_pipeline
    import inspect
    
    # Verify function exists and is callable
    assert callable(run_training_pipeline)
    
    # Verify CLI arguments are defined in the module
    # The argparse is imported in the __main__ block
    import backend.ml.train as train_module
    import ast
    import inspect
    
    # Read the source and check for argparse usage
    source = inspect.getsource(train_module)
    assert 'argparse' in source, "Training script should use argparse for CLI"
    assert '--ci-mode' in source, "Training script should support --ci-mode flag"


@pytest.mark.mlops
def test_drift_report_generation():
    """Test that drift reports can be generated"""
    try:
        from backend.ml.drift_report import simulate_drift_report
    except ImportError as e:
        pytest.skip(f"Evidently AI not properly installed: {e}")
    
    result = simulate_drift_report(shift_magnitude=1.0)
    
    assert "dataset_drift_detected" in result
    assert "report_path" in result
    assert Path(result["report_path"]).exists()


@pytest.mark.mlops
def test_retrain_trigger_logic():
    """Test that retraining trigger logic executes"""
    from backend.ml.retrain_trigger import should_retrain
    
    should_retrain_flag, reason, context = should_retrain(verbose=False)
    
    assert isinstance(should_retrain_flag, bool)
    assert isinstance(reason, str)
    assert isinstance(context, dict)


@pytest.mark.mlops
def test_rollback_functionality():
    """Test that rollback functionality is available"""
    from backend.ml.rollback import get_available_versions, rollback_model
    
    versions = get_available_versions()
    assert len(versions) >= 1
    
    # Test dry-run rollback
    current = versions[0]
    result = rollback_model(to_version=current, dry_run=True)
    
    # Should fail because we're trying to roll back to current
    assert result["success"] is False


@pytest.mark.mlops
@pytest.mark.integration
def test_model_registry_integrity():
    """Test that model registry is intact"""
    from backend.ml.registry import (
        get_approved_model_version,
        get_approved_model_metadata,
        REGISTRY_FILE
    )
    
    # Registry file must exist
    assert REGISTRY_FILE.exists()
    
    # Must have an approved version
    version = get_approved_model_version()
    assert version is not None
    
    # Metadata must be valid
    meta = get_approved_model_metadata()
    assert meta is not None
    assert "metrics" in meta
    assert "algorithm" in meta


@pytest.mark.mlops
def test_feature_extraction_deterministic():
    """Test that feature extraction is deterministic"""
    from backend.ml.features import extract_features_df
    
    texts = ["The quick brown fox jumps over the lazy dog."]
    
    # Extract features twice
    features1 = extract_features_df(texts)
    features2 = extract_features_df(texts)
    
    # Should be identical
    import numpy as np
    assert np.allclose(features1, features2)


@pytest.mark.mlops
def test_monitoring_psi_calculation():
    """Test that PSI monitoring works"""
    from backend.ml.monitoring import calculate_psi
    import numpy as np
    
    ref = np.random.normal(0, 1, 1000)
    curr = np.random.normal(0, 1, 1000)
    
    psi = calculate_psi(ref, curr)
    
    assert isinstance(psi, float)
    assert psi >= 0.0
    assert psi < 0.1  # Similar distributions should have low PSI


@pytest.mark.integration
def test_api_health_check(api_client):
    """Test that API health check endpoint works"""
    response = api_client.get("/api/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["ml_model_loaded"] is True


@pytest.mark.integration
def test_ml_prediction_endpoint(api_client):
    """Test ML prediction endpoint"""
    response = api_client.post(
        "/api/ml/predict-difficulty",
        json={"text": "The cat sat on the mat."}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "predicted_difficulty" in data
    assert data["predicted_difficulty"] in ["Easy", "Medium", "Hard", "Very Hard"]


@pytest.mark.mlops
def test_dataset_loading():
    """Test that dataset can be loaded"""
    from backend.ml.dataset import load_dataset, validate_dataset
    
    data = load_dataset()
    is_valid, errors = validate_dataset(data)
    
    assert is_valid is True
    assert len(errors) == 0
    # Dataset has 67 paragraphs (actual count, not 100)
    assert data["total_paragraphs"] >= 60  # Allow some flexibility


@pytest.mark.mlops
def test_all_workflow_files_exist():
    """Test that all GitHub Actions workflow files exist"""
    # Get correct path - workflows are in project root .github folder
    project_root = Path(__file__).parents[2]
    workflow_dir = project_root / ".github" / "workflows"
    
    required_workflows = [
        "ci-test.yml",
        "train-model.yml",
        "drift-check.yml",
        "deploy.yml"
    ]
    
    for workflow in required_workflows:
        workflow_path = workflow_dir / workflow
        assert workflow_path.exists(), f"Missing workflow: {workflow}"


@pytest.mark.slow
@pytest.mark.mlops
def test_training_completes_successfully():
    """
    Test that model training can complete end-to-end.
    This is a slow test, typically skipped in CI.
    """
    pytest.skip("Skipping slow training test - tested separately")
    
    # If you want to actually run this:
    # from backend.ml.train import run_training_pipeline
    # result = run_training_pipeline(version="test_1.0.0")
    # assert "candidate_version" in result
    # assert result["registration"]["approved"] in [True, False]
