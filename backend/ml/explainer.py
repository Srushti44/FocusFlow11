"""
FocusFlow ACLI - SHAP Explainability Engine
===========================================
Generates local instance-level feature contributions and global feature-importance
summaries using shap.TreeExplainer for the trained Random Forest ACLI model.

Adheres strictly to MLOps explainability principles:
- Computes actual SHAP values (never fabricated or mocked).
- Extracts per-class contributions for multi-class classifiers.
- Synthesizes clear, grounded natural language explanations from real contributions.
- Controlled error and unavailable states if model or explainer is uninitialized.
"""

from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
import shap

from .features import FEATURE_COLUMNS, FEATURE_DESCRIPTIONS
from .dataset import VALID_CLASSES, CLASS_TO_INT, INT_TO_CLASS


class ACLIExplainer:
    def __init__(self, model: Any, feature_names: Optional[List[str]] = None):
        """
        Initializes TreeExplainer for the trained Random Forest classifier.
        """
        self.model = model
        self.feature_names = feature_names or FEATURE_COLUMNS
        self.explainer: Optional[shap.TreeExplainer] = None

        if hasattr(model, "predict_proba"):
            try:
                self.explainer = shap.TreeExplainer(model)
            except Exception as e:
                print(f"[ACLIExplainer Warning] Failed to initialize TreeExplainer: {e}")
                self.explainer = None

    def is_ready(self) -> bool:
        return self.explainer is not None

    def explain_sample(
        self,
        X_sample: np.ndarray,
        predicted_class_idx: int,
        predicted_class_name: str,
        predicted_prob: float,
        raw_feature_values: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Computes local SHAP explanation for a single paragraph prediction.
        Extracts feature contributions specifically towards the predicted class.
        """
        if not self.is_ready():
            return {
                "available": False,
                "error": "SHAP TreeExplainer is not initialized for the current model.",
                "feature_contributions": [],
                "human_explanation": "Model explainability is currently unavailable."
            }

        if X_sample.ndim == 1:
            X_sample = X_sample.reshape(1, -1)

        try:
            # TreeExplainer on multi-class RF returns ndarray (1, n_features, n_classes) or list of arrays
            sv = self.explainer.shap_values(X_sample)

            if isinstance(sv, list):
                # Older SHAP or list output: list of arrays of length n_classes
                class_shap = sv[predicted_class_idx][0]
            elif isinstance(sv, np.ndarray):
                if sv.ndim == 3 and sv.shape[2] == len(VALID_CLASSES):
                    # Shape: (1, n_features, n_classes)
                    class_shap = sv[0, :, predicted_class_idx]
                elif sv.ndim == 3 and sv.shape[1] == len(VALID_CLASSES):
                    # Shape: (1, n_classes, n_features)
                    class_shap = sv[0, predicted_class_idx, :]
                elif sv.ndim == 2:
                    class_shap = sv[0, :]
                else:
                    raise ValueError(f"Unrecognized SHAP output array shape: {sv.shape}")
            else:
                raise TypeError(f"Unrecognized SHAP output type: {type(sv)}")

            # Extract base value for this class
            base_value = 0.25
            if hasattr(self.explainer, "expected_value"):
                ev = self.explainer.expected_value
                if isinstance(ev, (list, np.ndarray)) and len(ev) > predicted_class_idx:
                    base_value = float(ev[predicted_class_idx])
                elif isinstance(ev, (float, int, np.floating)):
                    base_value = float(ev)

            # Build structured contribution objects
            contributions: List[Dict[str, Any]] = []
            for i, feat_name in enumerate(self.feature_names):
                shap_val = float(class_shap[i])
                raw_val = float(raw_feature_values.get(feat_name, 0.0))
                contributions.append({
                    "feature": feat_name,
                    "description": FEATURE_DESCRIPTIONS.get(feat_name, feat_name),
                    "raw_value": round(raw_val, 4),
                    "shap_value": round(shap_val, 4),
                    "impact": "increases_difficulty" if shap_val > 0 else "decreases_difficulty",
                    "abs_impact": round(abs(shap_val), 4)
                })

            # Sort by absolute SHAP value (descending)
            contributions.sort(key=lambda x: x["abs_impact"], reverse=True)

            # Synthesize natural language explanation
            narrative = self._generate_narrative(
                predicted_class_name=predicted_class_name,
                predicted_prob=predicted_prob,
                contributions=contributions
            )

            return {
                "available": True,
                "predicted_class": predicted_class_name,
                "confidence": round(predicted_prob, 4),
                "base_value": round(base_value, 4),
                "feature_contributions": contributions,
                "human_explanation": narrative
            }

        except Exception as e:
            return {
                "available": False,
                "error": f"Failed to compute SHAP values: {str(e)}",
                "feature_contributions": [],
                "human_explanation": "An error occurred while computing SHAP feature contributions."
            }

    def _generate_narrative(
        self,
        predicted_class_name: str,
        predicted_prob: float,
        contributions: List[Dict[str, Any]]
    ) -> str:
        """
        Derives an honest, human-readable narrative explanation directly from actual top SHAP values.
        """
        positives = [c for c in contributions if c["shap_value"] > 0]
        negatives = [c for c in contributions if c["shap_value"] < 0]

        pct = round(predicted_prob * 100, 1)
        narrative_parts = [
            f"The ACLI model categorized this paragraph as '{predicted_class_name}' with {pct}% confidence."
        ]

        if positives:
            top_pos = positives[:2]
            pos_strs = [
                f"{c['feature']} ({c['raw_value']}, SHAP +{c['shap_value']})"
                for c in top_pos
            ]
            narrative_parts.append(
                f"The primary factors driving this difficulty classification were: {', '.join(pos_strs)}."
            )

        if negatives:
            top_neg = negatives[:2]
            neg_strs = [
                f"{c['feature']} ({c['raw_value']}, SHAP {c['shap_value']})"
                for c in top_neg
            ]
            narrative_parts.append(
                f"Factors that mitigated or pulled away from higher difficulty included: {', '.join(neg_strs)}."
            )

        return " ".join(narrative_parts)

    def compute_global_importance(self, X_eval: np.ndarray) -> Dict[str, Any]:
        """
        Calculates global feature importance across an entire evaluation dataset
        using mean absolute SHAP values.
        """
        if not self.is_ready():
            return {"available": False, "error": "Explainer not initialized"}

        try:
            sv = self.explainer.shap_values(X_eval)
            if isinstance(sv, list):
                # sv is list of arrays [n_samples, n_features] per class
                mean_abs_per_class = [np.mean(np.abs(arr), axis=0) for arr in sv]
                global_vals = np.mean(mean_abs_per_class, axis=0)
            elif isinstance(sv, np.ndarray):
                if sv.ndim == 3:
                    # Shape: (n_samples, n_features, n_classes) or (n_samples, n_classes, n_features)
                    if sv.shape[2] == len(VALID_CLASSES):
                        global_vals = np.mean(np.abs(sv), axis=(0, 2))
                    else:
                        global_vals = np.mean(np.abs(sv), axis=(0, 1))
                else:
                    global_vals = np.mean(np.abs(sv), axis=0)
            else:
                return {"available": False, "error": "Unknown SHAP return format"}

            ranking = []
            for i, name in enumerate(self.feature_names):
                val = float(global_vals[i])
                ranking.append({
                    "feature": name,
                    "mean_abs_shap": round(val, 4),
                    "description": FEATURE_DESCRIPTIONS.get(name, name)
                })
            ranking.sort(key=lambda x: x["mean_abs_shap"], reverse=True)

            return {
                "available": True,
                "global_feature_importance": ranking
            }
        except Exception as e:
            return {"available": False, "error": str(e)}
