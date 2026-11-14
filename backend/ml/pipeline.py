"""
FocusFlow ACLI - Automated Pipeline Orchestrator CLI
====================================================
Reproducible command-line entry point for running individual stages
or end-to-end MLOps execution:
Dataset Validation -> Feature Extraction -> Training -> Evaluation ->
MLflow Tracking -> Production Comparison -> Approval -> Registration
"""

import argparse
import sys
import json
from pathlib import Path

from .dataset import load_dataset, validate_dataset, to_dataframe, split_dataset_by_document
from .features import extract_features_df, FEATURE_SCHEMA_VERSION
from .evaluate import compute_metrics
from .train import run_training_pipeline
from .registry import (
    get_approved_model_version,
    get_approved_model_metadata,
    load_approved_artifacts,
    get_registry_data
)


def validate_dataset_stage():
    print("\n--- STAGE: Dataset Validation ---")
    data = load_dataset()
    is_valid, errors = validate_dataset(data)
    if is_valid:
        print(f"[SUCCESS] Dataset v{data.get('version')} is valid.")
        print(f"Total Paragraphs: {data.get('total_paragraphs')}")
        print(f"Class Distribution: {data.get('class_counts')}")
    else:
        print("[FAILED] Dataset validation encountered errors:")
        for err in errors:
            print(f" - {err}")
        sys.exit(1)


def evaluate_approved_model_stage():
    print("\n--- STAGE: Approved Model Evaluation ---")
    model, scaler, meta = load_approved_artifacts()
    if not model or not scaler or not meta:
        print("[ERROR] No approved model artifact found. Run training pipeline first: python -m backend.ml.pipeline --train")
        sys.exit(1)

    print(f"Loaded Approved Model: v{meta['version']} ({meta['algorithm']})")
    data = load_dataset()
    df = to_dataframe(data)
    _, _, test_df = split_dataset_by_document(df, test_size=0.20, val_size=0.15, random_state=42)

    X_test_raw = extract_features_df(test_df["text"].tolist())
    X_test = scaler.transform(X_test_raw)
    y_test = test_df["label"].values

    y_pred = model.predict(X_test)
    metrics = compute_metrics(y_test, y_pred)

    print(f"Test Accuracy:     {metrics['accuracy']:.4f}")
    print(f"Macro Precision:   {metrics['macro_precision']:.4f}")
    print(f"Macro Recall:      {metrics['macro_recall']:.4f}")
    print(f"Macro F1-Score:    {metrics['macro_f1']:.4f}")
    print("\nPer-Class Breakdown:")
    for cls_name, cls_data in metrics["per_class"].items():
        print(f" - {cls_name:10s} | Precision: {cls_data['precision']:.4f} | Recall: {cls_data['recall']:.4f} | F1: {cls_data['f1']:.4f} | Support: {cls_data['support']}")
    print(f"\nConfusion Matrix: {metrics['confusion_matrix']}")


def show_status():
    print("\n--- FocusFlow ACLI Model Registry Status ---")
    reg = get_registry_data()
    approved_v = reg.get("approved_model_version")
    if not approved_v:
        print("No approved model registered yet.")
        return

    meta = get_approved_model_metadata()
    print(f"Approved Version:     v{approved_v}")
    print(f"Approved Timestamp:   {reg.get('approved_at')}")
    if meta:
        print(f"Algorithm:            {meta.get('algorithm')}")
        print(f"Dataset Version:      {meta.get('dataset_version')}")
        print(f"Feature Schema:       {meta.get('feature_schema_version')}")
        print(f"Training Duration:    {meta.get('training_duration_seconds')}s")
        print(f"Test Accuracy:        {meta.get('metrics', {}).get('accuracy')}")
        print(f"Test Macro F1:        {meta.get('metrics', {}).get('macro_f1')}")
    print(f"\nTotal Registered Versions in History: {len(reg.get('history', []))}")


def main():
    parser = argparse.ArgumentParser(description="FocusFlow ACLI MLOps Pipeline CLI")
    parser.add_argument("--train", action="store_true", help="Execute complete automated training and approval pipeline")
    parser.add_argument("--evaluate", action="store_true", help="Evaluate current approved model on test dataset")
    parser.add_argument("--validate-dataset", action="store_true", help="Run dataset schema and quality validation")
    parser.add_argument("--status", action="store_true", help="Show registry and approved model status")
    parser.add_argument("--version", type=str, default=None, help="Explicit version string for candidate (optional)")

    args = parser.parse_args()

    if args.train:
        run_training_pipeline(version=args.version)
    elif args.evaluate:
        evaluate_approved_model_stage()
    elif args.validate_dataset:
        validate_dataset_stage()
    elif args.status:
        show_status()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
