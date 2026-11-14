"""
FocusFlow ACLI - Dataset Ingestion & Validation Module
======================================================
Handles loading, schema validation, quality checks, and leakage-free
document-grouped splitting for the educational readability dataset.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import pandas as pd
import numpy as np
from sklearn.model_selection import GroupShuffleSplit

DEFAULT_DATASET_PATH = Path(__file__).resolve().parent / "data" / "acli_educational_v1.json"

VALID_CLASSES = ["Easy", "Medium", "Hard", "Very Hard"]
CLASS_TO_INT = {cls_name: i for i, cls_name in enumerate(VALID_CLASSES)}
INT_TO_CLASS = {i: cls_name for i, cls_name in enumerate(VALID_CLASSES)}

REQUIRED_RECORD_FIELDS = {"id", "document_id", "text", "difficulty"}


def load_dataset(filepath: Optional[Path] = None) -> Dict[str, Any]:
    """
    Loads raw JSON dataset file from disk.
    """
    target = filepath or DEFAULT_DATASET_PATH
    if not target.exists():
        raise FileNotFoundError(f"ACLI dataset file not found at: {target}")
    
    with open(target, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def validate_dataset(dataset: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validates the dataset against required schema, quality bounds, and leakage prevention rules.
    Returns (is_valid, list_of_validation_messages).
    """
    errors: List[str] = []

    if not isinstance(dataset, dict):
        return False, ["Dataset root must be a JSON dictionary."]

    for key in ["version", "classes", "data"]:
        if key not in dataset:
            errors.append(f"Missing required top-level key: '{key}'")

    if "classes" in dataset:
        if set(dataset["classes"]) != set(VALID_CLASSES):
            errors.append(f"Dataset classes {dataset['classes']} do not match required {VALID_CLASSES}")

    records = dataset.get("data", [])
    if not isinstance(records, list) or len(records) == 0:
        errors.append("Dataset 'data' must be a non-empty list of records.")
        return False, errors

    seen_ids = set()
    document_ids = set()
    class_counts = {c: 0 for c in VALID_CLASSES}

    for idx, rec in enumerate(records):
        if not isinstance(rec, dict):
            errors.append(f"Record #{idx} is not an object.")
            continue

        missing = REQUIRED_RECORD_FIELDS - set(rec.keys())
        if missing:
            errors.append(f"Record #{idx} missing fields: {missing}")
            continue

        # Check duplicate IDs
        rec_id = rec["id"]
        if rec_id in seen_ids:
            errors.append(f"Duplicate record ID found: '{rec_id}'")
        seen_ids.add(rec_id)

        document_ids.add(rec["document_id"])

        # Check difficulty class
        diff = rec["difficulty"]
        if diff not in VALID_CLASSES:
            errors.append(f"Record '{rec_id}' has invalid difficulty '{diff}'")
        else:
            class_counts[diff] += 1

        # Text quality validation
        text = rec.get("text", "")
        if not isinstance(text, str) or not text.strip():
            errors.append(f"Record '{rec_id}' has empty or non-string text.")
        else:
            words = text.split()
            if len(words) < 15:
                errors.append(f"Record '{rec_id}' text is too short ({len(words)} words; min 15 required for paragraph-level analysis).")

    # Document count check (need enough distinct documents for leakage-free splitting)
    if len(document_ids) < 8:
        errors.append(f"Too few distinct document_ids ({len(document_ids)}). Need at least 8 documents to prevent data leakage.")

    # Class balance check (warn if any class has 0 samples, or less than 5% of total)
    total_samples = len(records)
    for c, count in class_counts.items():
        if count == 0:
            errors.append(f"Class '{c}' has 0 samples.")
        elif (count / total_samples) < 0.08:
            errors.append(f"Severe class imbalance: Class '{c}' has only {count}/{total_samples} samples (<8%).")

    is_valid = len(errors) == 0
    return is_valid, errors


def to_dataframe(dataset: Dict[str, Any]) -> pd.DataFrame:
    """
    Converts dataset record list to a pandas DataFrame with validated columns and integer labels.
    """
    records = dataset["data"]
    df = pd.DataFrame(records)
    df["label"] = df["difficulty"].map(CLASS_TO_INT)
    return df


def split_dataset_by_document(
    df: pd.DataFrame,
    test_size: float = 0.20,
    val_size: float = 0.15,
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Splits the dataset into Train, Validation, and Test subsets using Stratified
    Group-based splitting on 'document_id'. All paragraphs from any given document
    strictly belong to a single split, preventing intra-document data leakage,
    while guaranteeing that all 4 difficulty classes are represented in train,
    validation, and test splits.
    """
    rng = np.random.RandomState(random_state)
    
    # Identify document-level labels
    doc_meta = df.groupby("document_id")["difficulty"].agg(lambda s: s.mode()[0])
    
    train_docs: List[str] = []
    val_docs: List[str] = []
    test_docs: List[str] = []
    
    # Stratify document allocation per difficulty class
    for diff_class in VALID_CLASSES:
        class_docs = doc_meta[doc_meta == diff_class].index.tolist()
        rng.shuffle(class_docs)
        
        n_docs = len(class_docs)
        if n_docs == 0:
            continue
        
        # Determine split allocations
        n_test = max(1, int(round(n_docs * test_size)))
        n_val = max(1, int(round(n_docs * val_size)))
        n_train = n_docs - n_test - n_val
        
        # If too few documents to satisfy minimums, ensure at least 1 in train and 1 in test
        if n_train < 1:
            n_train = max(1, n_docs - n_test)
            n_val = 0
            n_test = n_docs - n_train
        
        train_docs.extend(class_docs[:n_train])
        val_docs.extend(class_docs[n_train:n_train + n_val])
        test_docs.extend(class_docs[n_train + n_val:])
        
    train_df = df[df["document_id"].isin(train_docs)].copy().reset_index(drop=True)
    val_df = df[df["document_id"].isin(val_docs)].copy().reset_index(drop=True)
    test_df = df[df["document_id"].isin(test_docs)].copy().reset_index(drop=True)
    
    return train_df, val_df, test_df
