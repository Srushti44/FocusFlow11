"""
Integration Tests for FastAPI ACLI Endpoints
"""

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_health_check_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["ml_model_loaded"] is True
    assert data["ml_model_version"] is not None


def test_model_info_endpoint():
    res = client.get("/api/ml/model-info")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ready"
    assert "model_version" in data
    assert "features" in data
    assert len(data["features"]) == 9


def test_predict_difficulty_valid_input():
    text = "The quick brown fox jumps over the lazy dog. Dogs love to play in the green grass outside."
    res = client.post("/api/ml/predict-difficulty", json={"text": text})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["predicted_difficulty"] in ["Easy", "Medium", "Hard", "Very Hard"]
    assert 0.0 <= data["confidence"] <= 1.0
    assert len(data["recommendations"]) > 0
    assert "features" in data
    assert "avg_sentence_length" in data["features"]


def test_predict_difficulty_empty_input():
    res = client.post("/api/ml/predict-difficulty", json={"text": "   "})
    assert res.status_code == 400


def test_predict_difficulty_invalid_schema():
    res = client.post("/api/ml/predict-difficulty", json={"wrong_key": 123})
    assert res.status_code == 422


def test_explain_endpoint_valid():
    text = (
        "In relativistic quantum field theory, local gauge invariance dictates vector interactions "
        "generating asymptotic freedom at elevated momentum transfers."
    )
    res = client.post("/api/ml/explain", json={"text": text})
    assert res.status_code == 200
    data = res.json()
    assert data["available"] is True
    assert len(data["feature_contributions"]) == 9
    assert len(data["human_explanation"]) > 20


def test_explain_endpoint_empty():
    res = client.post("/api/ml/explain", json={"text": ""})
    assert res.status_code == 400


def test_metrics_endpoint():
    res = client.get("/api/ml/metrics")
    assert res.status_code == 200
    data = res.json()
    assert "metrics" in data
    assert "accuracy" in data["metrics"]
    assert "confusion_matrix" in data["metrics"]


def test_monitoring_endpoint():
    res = client.get("/api/ml/monitoring")
    assert res.status_code == 200
    data = res.json()
    assert "total_requests" in data
    assert "latency" in data
    assert "feature_drift" in data
    assert "class_distribution" in data
