"""
FocusFlow ACLI - Model Registry & Approval Management
=====================================================
Manages model versioning, persistent artifact storage, candidate-versus-production
evaluation, and explicit documented criteria for model approval and deployment.
"""

import json
import os
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import joblib

ARTIFACTS_DIR = Path(__file__).resolve().parent / "artifacts"
REGISTRY_FILE = ARTIFACTS_DIR / "registry.json"
MODELS_DIR = ARTIFACTS_DIR / "models"

# Documented acceptance thresholds
MIN_ACCEPTABLE_MACRO_F1 = 0.60
MIN_ACCEPTABLE_ACCURACY = 0.60
MAX_ALLOWED_DEGRADATION = 0.02


def ensure_directories():
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    if not REGISTRY_FILE.exists():
        initial_data = {
            "approved_model_version": None,
            "approved_at": None,
            "history": []
        }
        with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
            json.dump(initial_data, f, indent=2)


def get_registry_data() -> Dict[str, Any]:
    ensure_directories()
    with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_registry_data(data: Dict[str, Any]):
    ensure_directories()
    with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_approved_model_version() -> Optional[str]:
    reg = get_registry_data()
    return reg.get("approved_model_version")


def get_approved_model_metadata() -> Optional[Dict[str, Any]]:
    version = get_approved_model_version()
    if not version:
        return None
    meta_path = MODELS_DIR / f"v{version}" / "metadata.json"
    if not meta_path.exists():
        return None
    with open(meta_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_approved_artifacts() -> Tuple[Optional[Any], Optional[Any], Optional[Dict[str, Any]]]:
    """
    Loads the currently approved model, its preprocessing scaler, and its metadata.
    Returns (model, scaler, metadata) or (None, None, None) if not available.
    """
    version = get_approved_model_version()
    if not version:
        return None, None, None

    version_dir = MODELS_DIR / f"v{version}"
    model_path = version_dir / "model.joblib"
    scaler_path = version_dir / "scaler.joblib"
    meta_path = version_dir / "metadata.json"

    if not model_path.exists() or not scaler_path.exists():
        return None, None, None

    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    with open(meta_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    return model, scaler, metadata


def evaluate_candidate_for_approval(
    candidate_metrics: Dict[str, Any],
    candidate_version: str
) -> Tuple[bool, str]:
    """
    Evaluates candidate metrics against documented acceptance criteria:
    1. Minimum absolute Macro F1 (>= 0.60)
    2. Minimum absolute Accuracy (>= 0.60)
    3. Comparison against currently approved model:
       Candidate cannot perform worse than the approved model on the held-out test set
       by more than MAX_ALLOWED_DEGRADATION (2%).
    """
    acc = candidate_metrics.get("accuracy", 0.0)
    f1 = candidate_metrics.get("macro_f1", 0.0)

    if acc < MIN_ACCEPTABLE_ACCURACY:
        return False, f"Candidate failed acceptance: Accuracy ({acc:.4f}) is below minimum threshold ({MIN_ACCEPTABLE_ACCURACY})."

    if f1 < MIN_ACCEPTABLE_MACRO_F1:
        return False, f"Candidate failed acceptance: Macro F1 ({f1:.4f}) is below minimum threshold ({MIN_ACCEPTABLE_MACRO_F1})."

    current_meta = get_approved_model_metadata()
    if current_meta and "metrics" in current_meta:
        curr_f1 = current_meta["metrics"].get("macro_f1", 0.0)
        curr_acc = current_meta["metrics"].get("accuracy", 0.0)
        curr_version = current_meta.get("version", "unknown")

        if f1 < (curr_f1 - MAX_ALLOWED_DEGRADATION):
            return False, (
                f"Candidate rejected: Macro F1 ({f1:.4f}) degraded compared to approved v{curr_version} "
                f"({curr_f1:.4f}) by more than allowed margin ({MAX_ALLOWED_DEGRADATION})."
            )

    return True, f"Candidate v{candidate_version} met all acceptance criteria (Accuracy: {acc:.4f}, Macro F1: {f1:.4f})."


def register_model_version(
    version: str,
    model: Any,
    scaler: Any,
    metrics: Dict[str, Any],
    hyperparameters: Dict[str, Any],
    algorithm: str,
    dataset_version: str,
    feature_schema_version: str,
    training_duration_seconds: float,
    mlflow_run_id: Optional[str] = None,
    confusion_matrix_path: Optional[Path] = None,
    approved: bool = False,
    decision_reason: str = ""
) -> Dict[str, Any]:
    """
    Saves candidate model artifacts and registers version in registry.json.
    """
    ensure_directories()
    version_dir = MODELS_DIR / f"v{version}"
    version_dir.mkdir(parents=True, exist_ok=True)

    # Save joblib model & scaler
    joblib.dump(model, version_dir / "model.joblib")
    joblib.dump(scaler, version_dir / "scaler.joblib")

    # Copy confusion matrix image if provided
    if confusion_matrix_path and Path(confusion_matrix_path).exists():
        shutil.copyfile(confusion_matrix_path, version_dir / "confusion_matrix.png")

    record = {
        "version": version,
        "algorithm": algorithm,
        "hyperparameters": hyperparameters,
        "metrics": metrics,
        "dataset_version": dataset_version,
        "feature_schema_version": feature_schema_version,
        "training_duration_seconds": round(training_duration_seconds, 2),
        "mlflow_run_id": mlflow_run_id,
        "created_at": datetime.now().isoformat(),
        "approved": approved,
        "approval_reason": decision_reason
    }

    # Save metadata.json
    with open(version_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)

    # Update global registry
    reg = get_registry_data()
    reg["history"].append(record)

    if approved:
        reg["approved_model_version"] = version
        reg["approved_at"] = record["created_at"]

    save_registry_data(reg)
    return record
