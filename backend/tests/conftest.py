"""
Pytest Configuration and Shared Fixtures
=========================================
Provides reusable test fixtures and configuration for all test modules.
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from typing import Generator

# Test data samples
SAMPLE_EASY_TEXT = "The cat sat on the mat. Dogs like to play. Birds fly in the sky."

SAMPLE_HARD_TEXT = (
    "The epistemological ramifications of phenomenological hermeneutics necessitate "
    "a comprehensive reevaluation of ontological paradigms within contemporary discourse."
)

SAMPLE_TEXTS = [
    "Water covers most of Earth.",
    "The sun provides warmth and light.",
    "Plants make oxygen through photosynthesis.",
    "The philosophical implications of radical empiricism demand careful consideration.",
    "Quantum mechanical interpretations remain fundamentally contested within physics.",
]


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Get path to test data directory"""
    return Path(__file__).parent / "test_data"


@pytest.fixture(scope="function")
def temp_artifacts_dir() -> Generator[Path, None, None]:
    """
    Create temporary artifacts directory for testing.
    Automatically cleaned up after test.
    """
    temp_dir = Path(tempfile.mkdtemp(prefix="focusflow_test_"))
    yield temp_dir
    
    # Cleanup
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


@pytest.fixture(scope="function")
def sample_texts() -> list[str]:
    """Provide sample texts for testing"""
    return SAMPLE_TEXTS.copy()


@pytest.fixture(scope="function")
def sample_easy_text() -> str:
    """Provide easy-to-read text sample"""
    return SAMPLE_EASY_TEXT


@pytest.fixture(scope="function")
def sample_hard_text() -> str:
    """Provide difficult-to-read text sample"""
    return SAMPLE_HARD_TEXT


@pytest.fixture(scope="function")
def mock_model_metadata() -> dict:
    """Provide mock model metadata for testing"""
    return {
        "version": "1.0.0",
        "algorithm": "RandomForestClassifier",
        "trained_at": "2024-01-01T00:00:00Z",
        "metrics": {
            "accuracy": 0.90,
            "macro_f1": 0.87,
            "macro_precision": 0.88,
            "macro_recall": 0.86
        },
        "hyperparameters": {
            "n_estimators": 120,
            "max_depth": 7,
            "min_samples_split": 3
        },
        "feature_schema_version": "1.0.0",
        "dataset_version": "1.0.0"
    }


@pytest.fixture(scope="session")
def api_client():
    """
    Provide FastAPI test client for integration tests.
    Reuses client across session for performance.
    """
    from fastapi.testclient import TestClient
    from backend.main import app
    
    client = TestClient(app)
    return client


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "mlops: marks tests related to MLOps functionality"
    )


# Skip certain tests in CI if needed
def pytest_collection_modifyitems(config, items):
    """Modify test collection based on environment"""
    import os
    
    # Skip slow tests in CI unless explicitly requested
    if os.environ.get("CI") and not os.environ.get("RUN_SLOW_TESTS"):
        skip_slow = pytest.mark.skip(reason="Slow test skipped in CI")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)
