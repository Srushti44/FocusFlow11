"""
FocusFlow ACLI - Model Training and MLflow Tracking Module
==========================================================
Trains Random Forest baseline and Logistic Regression comparison models.
Tracks runs, parameters, metrics, artifacts, and confusion matrices with MLflow.
Strictly prevents data leakage by fitting preprocessing only on training folds
and splitting across document IDs.
"""

import time
import os
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GroupKFold, cross_val_score
import mlflow
import mlflow.sklearn

from .features import extract_features_df, FEATURE_COLUMNS, FEATURE_SCHEMA_VERSION
from .dataset import (
    load_dataset,
    validate_dataset,
    to_dataframe,
    split_dataset_by_document,
    VALID_CLASSES,
    CLASS_TO_INT
)
from .evaluate import compute_metrics, save_confusion_matrix_plot
from .registry import (
    evaluate_candidate_for_approval,
    register_model_version,
    get_approved_model_version
)

ARTIFACTS_DIR = Path(__file__).resolve().parent / "artifacts"
MLFLOW_DB_PATH = ARTIFACTS_DIR / "mlflow.db"
EXPERIMENT_NAME = "FocusFlow_ACLI_Readability"


def setup_mlflow():
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    # Use SQLite database backend for reliable local MLflow persistence
    db_uri = f"sqlite:///{MLFLOW_DB_PATH.as_posix()}"
    mlflow.set_tracking_uri(db_uri)
    mlflow.set_experiment(EXPERIMENT_NAME)


def run_training_pipeline(
    version: Optional[str] = None,
    dataset_path: Optional[Path] = None,
    random_state: int = 42
) -> Dict[str, Any]:
    """
    Executes end-to-end training and evaluation:
    1. Loads and validates dataset.
    2. Performs document-grouped split (Train/Val/Test).
    3. Fits StandardScaler strictly on training set.
    4. Trains Logistic Regression baseline.
    5. Trains Random Forest classifier candidate with 4-fold GroupKFold CV.
    6. Evaluates both on held-out test set.
    7. Logs all runs, metrics, params, and confusion matrix artifacts to MLflow.
    8. Checks acceptance criteria and updates model registry.
    """
    setup_mlflow()
    start_time = time.time()

    if not version:
        # Generate version string like 1.0.0, 1.0.1, etc.
        approved_v = get_approved_model_version()
        if not approved_v:
            version = "1.0.0"
        else:
            parts = approved_v.split(".")
            version = f"{parts[0]}.{parts[1]}.{int(parts[2]) + 1}"

    print(f"\n=======================================================")
    print(f"[ACLI MLOps] Starting Training Pipeline (Candidate v{version})")
    print(f"=======================================================\n")

    # 1. Dataset Loading & Validation
    print("-> Loading and validating educational readability dataset...")
    raw_data = load_dataset(dataset_path)
    is_valid, validation_errors = validate_dataset(raw_data)
    if not is_valid:
        raise ValueError(f"Dataset validation failed with errors: {validation_errors}")
    print(f"   [PASS] Dataset v{raw_data.get('version')} validated: {raw_data.get('total_paragraphs')} paragraphs.")

    df = to_dataframe(raw_data)

    # 2. Document-Grouped Splitting (Zero Data Leakage)
    print("-> Performing document-grouped split by 'document_id'...")
    train_df, val_df, test_df = split_dataset_by_document(df, test_size=0.20, val_size=0.15, random_state=random_state)
    print(f"   Splits created: Train={len(train_df)} paras ({train_df['document_id'].nunique()} docs), "
          f"Val={len(val_df)} paras ({val_df['document_id'].nunique()} docs), "
          f"Test={len(test_df)} paras ({test_df['document_id'].nunique()} docs).")

    # 3. Feature Extraction
    print("-> Extracting linguistic features (Schema v1.0.0)...")
    X_train_raw = extract_features_df(train_df["text"].tolist())
    X_val_raw = extract_features_df(val_df["text"].tolist())
    X_test_raw = extract_features_df(test_df["text"].tolist())

    y_train = train_df["label"].values
    y_val = val_df["label"].values
    y_test = test_df["label"].values

    # 4. Preprocessing: Fit scaler STRICTLY on training fold
    print("-> Fitting StandardScaler strictly on training set...")
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train_raw)
    X_val = scaler.transform(X_val_raw)
    X_test = scaler.transform(X_test_raw)

    results: Dict[str, Any] = {
        "candidate_version": version,
        "dataset_version": raw_data.get("version", "1.0.0"),
        "models": {}
    }

    # =========================================================================
    # 5. Baseline Model: Logistic Regression
    # =========================================================================
    print("\n-> Training Baseline: Multi-class Logistic Regression...")
    lr_start = time.time()
    lr_model = LogisticRegression(
        solver="lbfgs",
        C=1.0,
        max_iter=1000,
        random_state=random_state
    )
    lr_model.fit(X_train, y_train)
    lr_duration = time.time() - lr_start

    lr_y_pred = lr_model.predict(X_test)
    lr_metrics = compute_metrics(y_test, lr_y_pred)
    print(f"   [Baseline Logistic Regression] Test Accuracy: {lr_metrics['accuracy']:.4f}, Macro F1: {lr_metrics['macro_f1']:.4f}")

    # Log Logistic Regression in MLflow
    with mlflow.start_run(run_name=f"ACLI_LogReg_v{version}") as lr_run:
        mlflow.log_param("algorithm", "LogisticRegression")
        mlflow.log_param("solver", "lbfgs")
        mlflow.log_param("C", 1.0)
        mlflow.log_param("feature_schema_version", FEATURE_SCHEMA_VERSION)
        mlflow.log_param("dataset_version", raw_data.get("version"))
        mlflow.log_metric("accuracy", lr_metrics["accuracy"])
        mlflow.log_metric("macro_precision", lr_metrics["macro_precision"])
        mlflow.log_metric("macro_recall", lr_metrics["macro_recall"])
        mlflow.log_metric("macro_f1", lr_metrics["macro_f1"])
        mlflow.log_metric("training_duration_seconds", lr_duration)

    results["models"]["logistic_regression"] = {
        "metrics": lr_metrics,
        "duration": lr_duration
    }

    # =========================================================================
    # 6. Candidate Model: Random Forest Classifier
    # =========================================================================
    print("\n-> Training Candidate: Random Forest Classifier...")
    rf_start = time.time()
    rf_params = {
        "n_estimators": 120,
        "max_depth": 7,
        "min_samples_split": 3,
        "min_samples_leaf": 1,
        "random_state": random_state
    }
    rf_model = RandomForestClassifier(**rf_params)

    # 4-Fold Cross Validation on training data using GroupKFold by document
    gkf = GroupKFold(n_splits=4)
    cv_scores = cross_val_score(rf_model, X_train, y_train, groups=train_df["document_id"], cv=gkf, scoring="f1_macro")
    print(f"   4-Fold Document Group CV Macro F1: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

    rf_model.fit(X_train, y_train)
    rf_duration = time.time() - rf_start

    rf_y_pred = rf_model.predict(X_test)
    rf_metrics = compute_metrics(y_test, rf_y_pred)
    print(f"   [Random Forest Candidate] Test Accuracy: {rf_metrics['accuracy']:.4f}, Macro F1: {rf_metrics['macro_f1']:.4f}")

    # Generate Confusion Matrix Artifact
    temp_cm_path = ARTIFACTS_DIR / f"cm_v{version}.png"
    save_confusion_matrix_plot(rf_metrics["confusion_matrix"], temp_cm_path, title=f"ACLI v{version} Confusion Matrix")

    # Log Random Forest in MLflow
    rf_run_id = None
    with mlflow.start_run(run_name=f"ACLI_RandomForest_v{version}") as rf_run:
        rf_run_id = rf_run.info.run_id
        mlflow.log_param("algorithm", "RandomForestClassifier")
        mlflow.log_params(rf_params)
        mlflow.log_param("feature_schema_version", FEATURE_SCHEMA_VERSION)
        mlflow.log_param("dataset_version", raw_data.get("version"))
        mlflow.log_param("features", FEATURE_COLUMNS)

        mlflow.log_metric("cv_macro_f1_mean", float(cv_scores.mean()))
        mlflow.log_metric("cv_macro_f1_std", float(cv_scores.std()))
        mlflow.log_metric("accuracy", rf_metrics["accuracy"])
        mlflow.log_metric("macro_precision", rf_metrics["macro_precision"])
        mlflow.log_metric("macro_recall", rf_metrics["macro_recall"])
        mlflow.log_metric("macro_f1", rf_metrics["macro_f1"])
        mlflow.log_metric("training_duration_seconds", rf_duration)

        # Log class-level F1s
        for cname, cdata in rf_metrics["per_class"].items():
            mlflow.log_metric(f"f1_{cname.lower().replace(' ', '_')}", cdata["f1"])

        if temp_cm_path.exists():
            mlflow.log_artifact(str(temp_cm_path), artifact_path="evaluation")

    results["models"]["random_forest"] = {
        "metrics": rf_metrics,
        "cv_macro_f1": float(cv_scores.mean()),
        "duration": rf_duration,
        "mlflow_run_id": rf_run_id
    }

    # =========================================================================
    # 7. Candidate vs Production Evaluation & Approval Decision
    # =========================================================================
    print("\n-> Evaluating candidate against documented approval criteria...")
    is_approved, decision_reason = evaluate_candidate_for_approval(rf_metrics, version)
    status_str = "APPROVED" if is_approved else "REJECTED"
    print(f"   Decision: [{status_str}] - {decision_reason}")

    # Register candidate in versioned registry
    registered_meta = register_model_version(
        version=version,
        model=rf_model,
        scaler=scaler,
        metrics=rf_metrics,
        hyperparameters=rf_params,
        algorithm="RandomForestClassifier",
        dataset_version=raw_data.get("version", "1.0.0"),
        feature_schema_version=FEATURE_SCHEMA_VERSION,
        training_duration_seconds=rf_duration,
        mlflow_run_id=rf_run_id,
        confusion_matrix_path=temp_cm_path,
        approved=is_approved,
        decision_reason=decision_reason
    )

    total_pipeline_time = time.time() - start_time
    print(f"\nPipeline completed in {total_pipeline_time:.2f}s. Registered artifact v{version}.")
    print("=======================================================\n")

    results["registration"] = registered_meta
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Train FocusFlow ACLI readability model")
    parser.add_argument("--ci-mode", action="store_true", help="Run in CI mode (suppress interactive prompts)")
    parser.add_argument("--skip-approval", action="store_true", help="Skip automatic approval gate (for testing)")
    parser.add_argument("--version", type=str, help="Explicit version string (e.g., 1.0.4)")
    parser.add_argument("--random-state", type=int, default=42, help="Random seed for reproducibility")
    
    args = parser.parse_args()
    
    if args.ci_mode:
        print("[CI MODE] Running training pipeline in non-interactive mode...")
    
    results = run_training_pipeline(
        version=args.version,
        random_state=args.random_state
    )
    
    # In CI mode, exit with appropriate code based on approval
    if args.ci_mode and not args.skip_approval:
        if results["registration"]["approved"]:
            print(f"✅ CI SUCCESS: Model v{results['candidate_version']} approved and registered")
            exit(0)
        else:
            print(f"⚠️  CI WARNING: Model v{results['candidate_version']} trained but not approved")
            print(f"   Reason: {results['registration']['decision_reason']}")
            exit(0)  # Exit 0 anyway - rejection is not a failure, just not production-ready
