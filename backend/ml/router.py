"""
FocusFlow ACLI - FastAPI MLOps Router
=====================================
Exposes REST endpoints for model inference, SHAP local explainability,
approved model metadata, evaluation metrics, and real-time operational monitoring.
"""

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

from .service import get_inference_service
from .monitoring import get_monitoring_dashboard_data
from .registry import get_approved_model_metadata, get_registry_data
from .dataset import load_dataset
from .features import extract_features_df, FEATURE_COLUMNS

router = APIRouter(tags=["ACLI MLOps"])


# -----------------------------------------------------------------------------
# Pydantic Schemas
# -----------------------------------------------------------------------------

class PredictDifficultyRequest(BaseModel):
    text: str = Field(..., max_length=50000, description="Paragraph text to analyze for cognitive difficulty")
    chunk_index: Optional[int] = Field(None, description="Index of paragraph in article if applicable")
    article_title: Optional[str] = Field(None, description="Optional article title for context")


class PredictDifficultyResponse(BaseModel):
    status: str
    predicted_difficulty: str
    confidence: float
    probabilities: Dict[str, float]
    model_version: Optional[str]
    latency_ms: float
    features: Dict[str, float]
    recommendations: List[str]
    error: Optional[str] = None


class ExplainDifficultyRequest(BaseModel):
    text: str = Field(..., max_length=50000, description="Paragraph text to explain with SHAP")


class FeatureContributionItem(BaseModel):
    feature: str
    description: str
    raw_value: float
    shap_value: float
    impact: str
    abs_impact: float


class ExplainDifficultyResponse(BaseModel):
    available: bool
    predicted_class: Optional[str] = None
    confidence: Optional[float] = None
    base_value: Optional[float] = None
    feature_contributions: List[FeatureContributionItem] = Field(default_factory=list)
    human_explanation: str
    model_version: Optional[str] = None
    error: Optional[str] = None


# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------

@router.post("/predict-difficulty", response_model=PredictDifficultyResponse)
def predict_paragraph_difficulty(req: PredictDifficultyRequest):
    """
    Predicts cognitive load difficulty for a given paragraph (Easy, Medium, Hard, Very Hard).
    Uses the cached, approved Random Forest model.
    """
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Paragraph text cannot be empty.")

    service = get_inference_service()
    result = service.predict(req.text.strip())
    return PredictDifficultyResponse(**result)


@router.post("/explain", response_model=ExplainDifficultyResponse)
def explain_paragraph_difficulty(req: ExplainDifficultyRequest):
    """
    Computes genuine SHAP TreeExplainer feature contributions for the paragraph prediction.
    Identifies exact textual linguistic drivers and outputs natural language synthesis.
    """
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    service = get_inference_service()
    result = service.explain(req.text.strip())
    return ExplainDifficultyResponse(**result)


@router.get("/model-info")
def get_model_info():
    """
    Returns metadata regarding the currently approved and serving ACLI model.
    """
    service = get_inference_service()
    info = service.get_info()
    return info


@router.get("/metrics")
def get_model_metrics():
    """
    Returns held-out evaluation metrics, per-class F1, and confusion matrix
    for the currently approved model.
    """
    meta = get_approved_model_metadata()
    if not meta:
        raise HTTPException(status_code=404, detail="No approved model found in registry.")

    return {
        "model_version": meta.get("version"),
        "algorithm": meta.get("algorithm"),
        "hyperparameters": meta.get("hyperparameters"),
        "dataset_version": meta.get("dataset_version"),
        "training_duration_seconds": meta.get("training_duration_seconds"),
        "created_at": meta.get("created_at"),
        "approved": meta.get("approved"),
        "approval_reason": meta.get("approval_reason"),
        "metrics": meta.get("metrics")
    }


@router.get("/monitoring")
def get_monitoring_telemetry():
    """
    Returns real-time serving monitoring data, latency percentiles, error rates,
    difficulty distribution, and feature drift (PSI) against training reference data.
    """
    # Load training dataset feature reference distributions for drift baseline
    ref_features = {}
    try:
        ds = load_dataset()
        texts = [r["text"] for r in ds.get("data", [])]
        df_feat = extract_features_df(texts)
        for col in FEATURE_COLUMNS:
            ref_features[col] = df_feat[col].tolist()
    except Exception as e:
        print(f"[Monitoring Baseline Warning] {e}")

    telemetry = get_monitoring_dashboard_data(reference_features=ref_features)
    
    # Enrich with model registry info
    reg = get_registry_data()
    meta = get_approved_model_metadata()
    telemetry["approved_model_version"] = reg.get("approved_model_version")
    telemetry["approved_at"] = reg.get("approved_at")
    telemetry["model_metadata"] = meta
    telemetry["experiment_history"] = reg.get("history", [])

    return telemetry
