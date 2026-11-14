"""
Unit Tests for Model Artifacts, Loading, and Approval Criteria
"""

import pytest

from backend.ml.registry import (
    load_approved_artifacts,
    get_approved_model_metadata,
    get_approved_model_version,
    evaluate_candidate_for_approval
)
from backend.ml.service import get_inference_service


def test_approved_artifacts_exist():
    version = get_approved_model_version()
    assert version is not None

    meta = get_approved_model_metadata()
    assert meta is not None
    assert meta["algorithm"] == "RandomForestClassifier"
    assert "accuracy" in meta["metrics"]
    assert "macro_f1" in meta["metrics"]


def test_model_loading_and_service_readiness():
    service = get_inference_service()
    assert service.is_ready() is True
    assert service.loaded_version is not None

    info = service.get_info()
    assert info["status"] == "ready"
    assert info["model_version"] == service.loaded_version
    assert len(info["features"]) == 9


def test_candidate_approval_criteria():
    # 1. Candidate meeting criteria
    good_metrics = {"accuracy": 0.95, "macro_f1": 0.90}
    is_appr, reason = evaluate_candidate_for_approval(good_metrics, "2.0.0")
    assert is_appr is True

    # 2. Candidate failing accuracy threshold
    low_acc = {"accuracy": 0.40, "macro_f1": 0.70}
    is_appr, reason = evaluate_candidate_for_approval(low_acc, "2.0.1")
    assert is_appr is False
    assert "Accuracy" in reason

    # 3. Candidate failing macro F1 threshold
    low_f1 = {"accuracy": 0.80, "macro_f1": 0.45}
    is_appr, reason = evaluate_candidate_for_approval(low_f1, "2.0.2")
    assert is_appr is False
    assert "Macro F1" in reason
