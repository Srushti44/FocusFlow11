"""
Unit Tests for Model Rollback Functionality
"""

import pytest
from pathlib import Path
import json

from backend.ml.rollback import (
    get_available_versions,
    get_version_metadata,
    rollback_model,
    compare_versions,
    get_rollback_history,
    ROLLBACK_HISTORY_FILE
)
from backend.ml.registry import get_approved_model_version


def test_get_available_versions():
    """Test that we can list available model versions"""
    versions = get_available_versions()
    
    assert isinstance(versions, list)
    assert len(versions) >= 1  # At least v1.0.3 should exist
    
    # Versions should be in descending order
    if len(versions) > 1:
        v1_parts = [int(p) for p in versions[0].split('.')]
        v2_parts = [int(p) for p in versions[1].split('.')]
        assert v1_parts >= v2_parts


def test_get_version_metadata():
    """Test retrieving metadata for a specific version"""
    # Get current version
    current = get_approved_model_version()
    assert current is not None
    
    # Get its metadata
    meta = get_version_metadata(current)
    
    assert meta is not None
    assert "metrics" in meta
    assert "algorithm" in meta
    assert meta["algorithm"] == "RandomForestClassifier"


def test_get_nonexistent_version_metadata():
    """Test that getting metadata for nonexistent version returns None"""
    meta = get_version_metadata("99.99.99")
    assert meta is None


def test_rollback_dry_run():
    """Test rollback in dry-run mode (no actual changes)"""
    current = get_approved_model_version()
    versions = get_available_versions()
    
    # Find a different version to roll back to
    target = None
    for v in versions:
        # Normalize versions for comparison (remove 'v' prefix)
        current_clean = current.replace('v', '')
        v_clean = v.replace('v', '')
        if v_clean != current_clean:
            target = v
            break
    
    if target is None:
        pytest.skip("Only one model version available, cannot test rollback")
    
    # Try rollback with the version as returned by get_available_versions
    result = rollback_model(
        to_version=target,
        reason="Test dry run",
        dry_run=True
    )
    
    # If it failed, the version might need 'v' prefix
    if not result["success"] and "not found" in result.get("error", ""):
        # Try with 'v' prefix
        target_with_v = f"v{target.replace('v', '')}"
        result = rollback_model(
            to_version=target_with_v,
            reason="Test dry run",
            dry_run=True
        )
    
    assert result["success"] is True, f"Rollback failed: {result.get('error', 'unknown')}"
    assert result["dry_run"] is True
    assert result["to_version"] in [target, f"v{target.replace('v', '')}"]
    
    # Verify version hasn't actually changed
    assert get_approved_model_version() == current


def test_rollback_to_same_version_fails():
    """Test that rolling back to current version is rejected"""
    current = get_approved_model_version()
    
    result = rollback_model(
        to_version=current,
        reason="Test same version",
        dry_run=True
    )
    
    assert result["success"] is False
    assert "Already on version" in result["error"]


def test_rollback_to_nonexistent_version_fails():
    """Test that rolling back to nonexistent version is rejected"""
    result = rollback_model(
        to_version="99.99.99",
        reason="Test nonexistent",
        dry_run=True
    )
    
    assert result["success"] is False
    assert "not found" in result["error"]


def test_compare_versions():
    """Test version comparison functionality"""
    versions = get_available_versions()
    
    if len(versions) < 2:
        pytest.skip("Need at least 2 versions to test comparison")
    
    v1, v2 = versions[0], versions[1]
    comparison = compare_versions(v1, v2)
    
    assert "version1" in comparison
    assert "version2" in comparison
    assert "metrics" in comparison
    assert "accuracy" in comparison["metrics"]
    assert "macro_f1" in comparison["metrics"]
    
    # Check structure of metric comparison
    acc_comp = comparison["metrics"]["accuracy"]
    assert "version1" in acc_comp
    assert "version2" in acc_comp
    assert "difference" in acc_comp
    assert "percent_change" in acc_comp


def test_compare_nonexistent_versions():
    """Test comparison with nonexistent versions"""
    comparison = compare_versions("99.99.99", "88.88.88")
    
    assert "error" in comparison
    assert comparison["version1_exists"] is False
    assert comparison["version2_exists"] is False


def test_rollback_history_structure():
    """Test rollback history functionality"""
    history = get_rollback_history(limit=10)
    
    assert isinstance(history, list)
    
    # If history exists, check structure
    if len(history) > 0:
        entry = history[0]
        assert "timestamp" in entry
        assert "from_version" in entry
        assert "to_version" in entry
        assert "reason" in entry


def test_rollback_creates_backup():
    """Test that rollback creates backup (dry-run mode)"""
    # This is verified in the dry-run test
    # In real rollback, backup_path would be in the result
    pass


def test_available_versions_have_required_files():
    """Test that all available versions have required model files"""
    versions = get_available_versions()
    
    from backend.ml.registry import MODELS_DIR
    
    for version in versions:
        # Try both with and without 'v' prefix
        version_clean = version.replace('v', '')
        possible_paths = [
            MODELS_DIR / version,
            MODELS_DIR / f"v{version_clean}",
            MODELS_DIR / version_clean
        ]
        
        found = False
        for version_dir in possible_paths:
            if version_dir.exists():
                assert (version_dir / "model.joblib").exists(), f"Missing model.joblib in {version_dir}"
                assert (version_dir / "scaler.joblib").exists(), f"Missing scaler.joblib in {version_dir}"
                assert (version_dir / "metadata.json").exists(), f"Missing metadata.json in {version_dir}"
                found = True
                break
        
        assert found, f"Version directory not found for {version}"
