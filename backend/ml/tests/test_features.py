"""
Unit Tests for ACLI Feature Extraction Pipeline
"""

import pytest
import numpy as np
import pandas as pd

from backend.ml.features import (
    extract_features_from_text,
    extract_features_df,
    count_syllables,
    FEATURE_COLUMNS,
    FEATURE_SCHEMA_VERSION
)


def test_feature_schema_columns():
    assert len(FEATURE_COLUMNS) == 9
    assert "avg_sentence_length" in FEATURE_COLUMNS
    assert "avg_word_length" in FEATURE_COLUMNS
    assert "complex_word_pct" in FEATURE_COLUMNS
    assert "flesch_reading_ease" in FEATURE_COLUMNS
    assert "flesch_kincaid_grade" in FEATURE_COLUMNS
    assert "lexical_diversity" in FEATURE_COLUMNS
    assert "syntactic_density" in FEATURE_COLUMNS
    assert FEATURE_SCHEMA_VERSION == "1.0.0"


def test_syllable_counter():
    assert count_syllables("cat") == 1
    assert count_syllables("water") == 2
    assert count_syllables("phenomenology") >= 5
    assert count_syllables("") == 0
    assert count_syllables("a") == 1


def test_empty_and_null_input_handling():
    # Empty string
    f_empty = extract_features_from_text("")
    assert isinstance(f_empty, dict)
    assert f_empty["word_count"] == 0.0
    assert f_empty["sentence_count"] == 0.0 or f_empty["sentence_count"] == 1.0

    # None
    f_none = extract_features_from_text(None)
    assert isinstance(f_none, dict)
    assert f_none["word_count"] == 0.0

    # Non-alphanumeric noise
    f_noise = extract_features_from_text("... ??? !!! ---")
    assert isinstance(f_noise, dict)
    assert f_noise["word_count"] == 0.0


def test_valid_text_feature_calculation():
    text = (
        "FocusFlow mitigates extraneous cognitive load through structured paragraph chunking. "
        "Consequently, working memory maintains optimal attentional bandwidth for comprehension."
    )
    feats = extract_features_from_text(text)
    assert len(feats) == len(FEATURE_COLUMNS)

    assert feats["word_count"] > 15
    assert feats["sentence_count"] == 2
    assert feats["avg_sentence_length"] > 5
    assert feats["avg_word_length"] > 4
    assert feats["complex_word_pct"] > 0
    assert 0 <= feats["flesch_reading_ease"] <= 100
    assert feats["lexical_diversity"] > 0
    assert feats["syntactic_density"] >= 0


def test_dataframe_feature_extraction():
    texts = [
        "Water falls as gentle rain.",
        "Epistemological phenomenology interrogates intentional structures of pure consciousness."
    ]
    df = extract_features_df(texts)
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == FEATURE_COLUMNS
    assert len(df) == 2
    assert not df.isnull().any().any()
