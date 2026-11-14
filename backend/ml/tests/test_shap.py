"""
Unit Tests for SHAP Explainability Engine
"""

import pytest

from backend.ml.service import get_inference_service


def test_shap_explanation_structure():
    service = get_inference_service()
    assert service.is_ready()

    sample_text = (
        "Husserlian phenomenology posits that consciousness is fundamentally characterized by intentionality, "
        "wherein every cognitive act constitutively targets an intentional object through noetic-noematic correlation."
    )
    explanation = service.explain(sample_text)

    assert explanation["available"] is True
    assert explanation["predicted_class"] in ["Hard", "Very Hard"]
    assert 0.0 <= explanation["confidence"] <= 1.0
    assert "feature_contributions" in explanation
    assert len(explanation["feature_contributions"]) == 9

    # Check contribution items
    first_contrib = explanation["feature_contributions"][0]
    assert "feature" in first_contrib
    assert "raw_value" in first_contrib
    assert "shap_value" in first_contrib
    assert "impact" in first_contrib
    assert isinstance(first_contrib["abs_impact"], float)

    # Check natural language narrative
    narrative = explanation["human_explanation"]
    assert isinstance(narrative, str)
    assert len(narrative) > 20
    assert "ACLI model" in narrative


def test_shap_empty_input_handling():
    service = get_inference_service()
    explanation = service.explain("")
    assert explanation["available"] is False
    assert "error" in explanation
