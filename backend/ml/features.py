"""
FocusFlow ACLI - Feature Engineering Pipeline
==============================================
Feature Schema Version: 1.0.0

Calculates defensible, reproducible numerical linguistic features from individual
paragraphs to predict textual cognitive difficulty (Easy, Medium, Hard, Very Hard).

Important Limitation Disclaimer:
Textual complexity features estimate structural and lexical difficulty of written text.
They do not directly measure a reader's physiological cognitive state, cognitive load,
or diagnose neurological conditions (e.g., ADHD, dyslexia).
"""

import re
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

FEATURE_SCHEMA_VERSION = "1.0.0"

FEATURE_COLUMNS: List[str] = [
    "avg_sentence_length",
    "avg_word_length",
    "word_count",
    "sentence_count",
    "complex_word_pct",
    "flesch_reading_ease",
    "flesch_kincaid_grade",
    "lexical_diversity",
    "syntactic_density"
]

FEATURE_DESCRIPTIONS: Dict[str, str] = {
    "avg_sentence_length": "Average number of words per sentence. Higher values indicate longer, more taxing clause structures.",
    "avg_word_length": "Average character count per word. Higher values correlate with multisyllabic, academic vocabulary.",
    "word_count": "Total word count in the paragraph.",
    "sentence_count": "Total sentence count in the paragraph.",
    "complex_word_pct": "Percentage of words containing 3 or more syllables (excluding common inflectional endings).",
    "flesch_reading_ease": "Flesch Reading Ease score (0-100, where lower scores indicate higher reading difficulty).",
    "flesch_kincaid_grade": "Flesch-Kincaid Grade Level index, estimating required formal education years.",
    "lexical_diversity": "Type-Token Ratio (unique word stems / total words). Reflects lexical variety vs repetition.",
    "syntactic_density": "Frequency of subordination, semicolon clauses, em-dashes, and transition connectors per sentence."
}

# Subordinating conjunctions and discourse connectives indicative of syntactic density
SYNTACTIC_MARKERS = {
    "however", "although", "nevertheless", "furthermore", "consequently",
    "whereas", "notwithstanding", "conversely", "specifically", "additionally",
    "subsequently", "accordingly", "inasmuch", "whereas", "furthermore", "thereby"
}


def count_syllables(word: str) -> int:
    """
    Estimates syllable count using deterministic morphological heuristics.
    Handles silent 'e', common suffixes ('-ed', '-es'), and vowel cluster patterns.
    """
    word = word.lower().strip(".:;?!'\"()[]{}")
    if not word:
        return 0
    if len(word) <= 3:
        return 1

    # Remove non-vocalic trailing endings
    word = re.sub(r'(?:[^laeiouy]|ed|es|e)$', '', word)
    word = re.sub(r'^y', '', word)
    matches = re.findall(r'[aeiouy]{1,2}', word)
    return max(1, len(matches))


def extract_features_from_text(text: Optional[str]) -> Dict[str, float]:
    """
    Extracts numerical feature dictionary from a single paragraph text string.
    Safely handles empty, null, or anomalous input without raising exceptions.
    """
    if not text or not isinstance(text, str) or not text.strip():
        return {
            "avg_sentence_length": 0.0,
            "avg_word_length": 0.0,
            "word_count": 0.0,
            "sentence_count": 0.0,
            "complex_word_pct": 0.0,
            "flesch_reading_ease": 70.0,
            "flesch_kincaid_grade": 5.0,
            "lexical_diversity": 0.0,
            "syntactic_density": 0.0
        }

    raw_sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text.strip()) if s.strip()]
    sentence_count = max(1, len(raw_sentences))

    # Extract clean alphabetical words
    words = re.findall(r'\b[A-Za-z]+\b', text)
    word_count = len(words)

    if word_count == 0:
        return {
            "avg_sentence_length": 0.0,
            "avg_word_length": 0.0,
            "word_count": 0.0,
            "sentence_count": float(sentence_count),
            "complex_word_pct": 0.0,
            "flesch_reading_ease": 70.0,
            "flesch_kincaid_grade": 5.0,
            "lexical_diversity": 0.0,
            "syntactic_density": 0.0
        }

    # 1. Length metrics
    avg_sentence_length = float(word_count) / float(sentence_count)
    total_characters = sum(len(w) for w in words)
    avg_word_length = float(total_characters) / float(word_count)

    # 2. Syllable & Complexity metrics
    syllable_counts = [count_syllables(w) for w in words]
    total_syllables = sum(syllable_counts)
    complex_words = sum(1 for syl in syllable_counts if syl >= 3)
    complex_word_pct = (float(complex_words) / float(word_count)) * 100.0

    # 3. Readability indexes
    # Flesch Reading Ease Formula: 206.835 - (1.015 * ASL) - (84.6 * (syllables / words))
    fre = 206.835 - (1.015 * avg_sentence_length) - (84.6 * (float(total_syllables) / float(word_count)))
    fre = max(0.0, min(100.0, fre))

    # Flesch-Kincaid Grade Level Formula: (0.39 * ASL) + (11.8 * (syllables / words)) - 15.59
    fkgl = (0.39 * avg_sentence_length) + (11.8 * (float(total_syllables) / float(word_count))) - 15.59
    fkgl = max(1.0, min(22.0, fkgl))

    # 4. Lexical Diversity (Type-Token Ratio using lowercased words)
    unique_words = set(w.lower() for w in words)
    lexical_diversity = float(len(unique_words)) / float(word_count)

    # 5. Syntactic Density: punctuation complexities (colons, semicolons, dashes) + syntactic discourse connectives
    punct_count = len(re.findall(r'[;:\-\—]', text))
    lowered_tokens = [w.lower() for w in words]
    marker_count = sum(1 for token in lowered_tokens if token in SYNTACTIC_MARKERS)
    syntactic_density = float(punct_count + marker_count) / float(sentence_count)

    return {
        "avg_sentence_length": round(avg_sentence_length, 4),
        "avg_word_length": round(avg_word_length, 4),
        "word_count": float(word_count),
        "sentence_count": float(sentence_count),
        "complex_word_pct": round(complex_word_pct, 4),
        "flesch_reading_ease": round(fre, 4),
        "flesch_kincaid_grade": round(fkgl, 4),
        "lexical_diversity": round(lexical_diversity, 4),
        "syntactic_density": round(syntactic_density, 4)
    }


def extract_features_df(texts: List[str]) -> pd.DataFrame:
    """
    Extracts features for a collection of texts into a validated pandas DataFrame
    matching FEATURE_COLUMNS exactly.
    """
    records = [extract_features_from_text(t) for t in texts]
    df = pd.DataFrame.from_records(records)
    # Ensure column ordering matches strict schema
    return df[FEATURE_COLUMNS].astype(np.float64)
