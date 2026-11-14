"""
Unit Tests for ACLI Dataset Loading, Validation, and Leakage-Free Splitting
"""

import pytest
import pandas as pd

from backend.ml.dataset import (
    load_dataset,
    validate_dataset,
    to_dataframe,
    split_dataset_by_document,
    VALID_CLASSES
)


def test_dataset_loading_and_schema():
    data = load_dataset()
    assert isinstance(data, dict)
    assert "version" in data
    assert "classes" in data
    assert data["classes"] == VALID_CLASSES
    assert "data" in data
    assert len(data["data"]) >= 40


def test_dataset_validation_passes():
    data = load_dataset()
    is_valid, errors = validate_dataset(data)
    assert is_valid is True
    assert len(errors) == 0


def test_dataset_validation_catches_invalid_classes():
    bad_data = {
        "version": "1.0.0",
        "classes": VALID_CLASSES,
        "data": [
            {
                "id": "bad-1",
                "document_id": "doc-1",
                "text": "Valid text with enough words for analysis to pass the minimum word requirement check.",
                "difficulty": "SuperEasy"  # Invalid
            }
        ]
    }
    is_valid, errors = validate_dataset(bad_data)
    assert is_valid is False
    assert any("invalid difficulty" in e for e in errors)


def test_document_grouped_split_prevents_leakage():
    data = load_dataset()
    df = to_dataframe(data)
    train_df, val_df, test_df = split_dataset_by_document(df, test_size=0.20, val_size=0.15, random_state=42)

    # Document sets
    train_docs = set(train_df["document_id"])
    val_docs = set(val_df["document_id"])
    test_docs = set(test_df["document_id"])

    # Strict zero-leakage check: no overlap in document IDs across any splits
    assert len(train_docs.intersection(test_docs)) == 0
    assert len(train_docs.intersection(val_docs)) == 0
    assert len(val_docs.intersection(test_docs)) == 0
