"""
FocusFlow ACLI - Production Inference Service
=============================================
Manages cached in-memory loading of the approved Random Forest model,
preprocessing scaler, and TreeExplainer. Ensures zero retraining or redundant
file reads during inference.
"""

import time
from typing import Dict, Any, Optional, List, Tuple
import numpy as np
import pandas as pd

from .features import extract_features_from_text, FEATURE_COLUMNS, FEATURE_SCHEMA_VERSION
from .dataset import VALID_CLASSES, INT_TO_CLASS, CLASS_TO_INT
from .registry import load_approved_artifacts, get_approved_model_metadata
from .explainer import ACLIExplainer
from .monitoring import log_prediction


class ACLIInferenceService:
    _instance: Optional["ACLIInferenceService"] = None

    def __init__(self):
        self.model: Optional[Any] = None
        self.scaler: Optional[Any] = None
        self.metadata: Optional[Dict[str, Any]] = None
        self.explainer: Optional[ACLIExplainer] = None
        self.loaded_version: Optional[str] = None
        self.load_model()

    @classmethod
    def get_instance(cls) -> "ACLIInferenceService":
        if cls._instance is None:
            cls._instance = ACLIInferenceService()
        return cls._instance

    def load_model(self) -> bool:
        """
        Loads the currently approved model and scaler from versioned artifact storage.
        """
        try:
            model, scaler, metadata = load_approved_artifacts()
            if model is not None and scaler is not None and metadata is not None:
                self.model = model
                self.scaler = scaler
                self.metadata = metadata
                self.loaded_version = metadata.get("version", "unknown")
                self.explainer = ACLIExplainer(self.model, feature_names=FEATURE_COLUMNS)
                print(f"[ACLI Service] Successfully loaded approved ACLI model v{self.loaded_version}")
                return True
            else:
                print("[ACLI Service Warning] No approved model found in registry.")
                self.model = None
                self.scaler = None
                self.metadata = None
                self.explainer = None
                self.loaded_version = None
                return False
        except Exception as e:
            print(f"[ACLI Service Error] Failed to load model artifacts: {e}")
            return False

    def is_ready(self) -> bool:
        return self.model is not None and self.scaler is not None

    def get_info(self) -> Dict[str, Any]:
        """
        Returns model metadata and serving status.
        """
        if not self.is_ready():
            return {
                "status": "unavailable",
                "message": "No approved ACLI model is currently loaded. Run training pipeline first.",
                "approved_version": None
            }

        return {
            "status": "ready",
            "model_version": self.loaded_version,
            "algorithm": self.metadata.get("algorithm", "RandomForestClassifier"),
            "dataset_version": self.metadata.get("dataset_version", "1.0.0"),
            "feature_schema_version": FEATURE_SCHEMA_VERSION,
            "training_duration_seconds": self.metadata.get("training_duration_seconds"),
            "accuracy": self.metadata.get("metrics", {}).get("accuracy"),
            "macro_f1": self.metadata.get("metrics", {}).get("macro_f1"),
            "features": FEATURE_COLUMNS,
            "classes": VALID_CLASSES
        }

    def predict(self, text: str) -> Dict[str, Any]:
        """
        Predicts cognitive difficulty (Easy, Medium, Hard, Very Hard) for a single paragraph.
        Returns predicted class, probabilities, feature values, and cognitive reading adjustments.
        """
        start_time = time.time()

        if not self.is_ready():
            # Try reloading in case model was recently trained
            if not self.load_model():
                return {
                    "status": "error",
                    "error": "ACLI model is currently unavailable.",
                    "predicted_difficulty": "Medium",
                    "confidence": 0.50,
                    "model_version": "unavailable",
                    "recommendations": []
                }

        if not text or not isinstance(text, str) or not text.strip():
            return {
                "status": "error",
                "error": "Input text cannot be empty.",
                "predicted_difficulty": "Easy",
                "confidence": 1.0,
                "model_version": self.loaded_version,
                "recommendations": ["Empty text detected. No cognitive adjustments required."]
            }

        try:
            # 1. Extract features matching schema
            features = extract_features_from_text(text)
            feature_vector = pd.DataFrame([[features[col] for col in FEATURE_COLUMNS]], columns=FEATURE_COLUMNS)

            # 2. Scale features using saved training scaler
            scaled_vector = self.scaler.transform(feature_vector)

            # 3. Model inference
            pred_idx = int(self.model.predict(scaled_vector)[0])
            pred_class = INT_TO_CLASS.get(pred_idx, "Medium")

            probabilities: Dict[str, float] = {}
            if hasattr(self.model, "predict_proba"):
                probs = self.model.predict_proba(scaled_vector)[0]
                confidence = float(probs[pred_idx])
                for idx, cname in enumerate(VALID_CLASSES):
                    probabilities[cname] = round(float(probs[idx]), 4) if idx < len(probs) else 0.0
            else:
                confidence = 1.0
                probabilities = {pred_class: 1.0}

            # 4. Determine reading recommendations based on difficulty
            recommendations = self._generate_recommendations(pred_class, features)

            latency_ms = (time.time() - start_time) * 1000.0

            # 5. Log inference telemetry to SQLite
            log_prediction(
                model_version=self.loaded_version or "v1.0.0",
                latency_ms=latency_ms,
                predicted_difficulty=pred_class,
                confidence=confidence,
                features=features,
                success=True
            )

            return {
                "status": "success",
                "predicted_difficulty": pred_class,
                "confidence": round(confidence, 4),
                "probabilities": probabilities,
                "model_version": self.loaded_version,
                "latency_ms": round(latency_ms, 2),
                "features": features,
                "recommendations": recommendations
            }

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000.0
            log_prediction(
                model_version=self.loaded_version or "v1.0.0",
                latency_ms=latency_ms,
                predicted_difficulty="Medium",
                confidence=0.0,
                features={},
                success=False,
                error_message=str(e)
            )
            return {
                "status": "error",
                "error": f"Inference failed: {str(e)}",
                "predicted_difficulty": "Medium",
                "confidence": 0.50,
                "model_version": self.loaded_version,
                "recommendations": ["Fallback recommendation: Read at a steady, comfortable pace."]
            }

    def explain(self, text: str) -> Dict[str, Any]:
        """
        Generates genuine SHAP local feature contributions for the given paragraph.
        """
        if not self.is_ready():
            if not self.load_model():
                return {
                    "available": False,
                    "error": "ACLI model is not available for explanation."
                }

        if not text or not isinstance(text, str) or not text.strip():
            return {
                "available": False,
                "error": "Text is empty; cannot compute SHAP explanation."
            }

        # Run prediction first
        pred_res = self.predict(text)
        if pred_res.get("status") == "error":
            return {
                "available": False,
                "error": pred_res.get("error", "Prediction failed before explanation.")
            }

        pred_class = pred_res["predicted_difficulty"]
        pred_idx = CLASS_TO_INT.get(pred_class, 1)
        pred_prob = pred_res["confidence"]
        raw_features = pred_res["features"]

        feature_vector = pd.DataFrame([[raw_features[col] for col in FEATURE_COLUMNS]], columns=FEATURE_COLUMNS)
        scaled_vector = self.scaler.transform(feature_vector)

        if not self.explainer or not self.explainer.is_ready():
            return {
                "available": False,
                "error": "SHAP TreeExplainer is not initialized for the current model."
            }

        shap_res = self.explainer.explain_sample(
            X_sample=scaled_vector,
            predicted_class_idx=pred_idx,
            predicted_class_name=pred_class,
            predicted_prob=pred_prob,
            raw_feature_values=raw_features
        )
        shap_res["model_version"] = self.loaded_version
        return shap_res

    def _generate_recommendations(self, pred_class: str, features: Dict[str, float]) -> List[str]:
        """
        Constructs educational cognitive adjustments according to predicted difficulty.
        Keeps reading adjustments distinct from LLM generation.
        """
        recs = []
        asl = features.get("avg_sentence_length", 15.0)
        cwp = features.get("complex_word_pct", 10.0)

        if pred_class == "Easy":
            recs.append("Read at your natural flow rate. Sentence and vocabulary complexity are well-balanced.")
            recs.append("Standard 80-word focus chunking is ideal for rapid comprehension.")
        elif pred_class == "Medium":
            recs.append("Standard expository prose. Maintain steady reading rhythm.")
            if asl > 20:
                recs.append("Punctuate with brief pauses at commas and semicolons to manage clause transitions.")
        elif pred_class == "Hard":
            recs.append("High cognitive friction detected. Consider reducing chunk size to 40-50 words to avoid visual regression.")
            if cwp > 20:
                recs.append(f"Elevated multisyllabic vocabulary ({cwp:.1f}% complex words). Review highlighted key concepts.")
            recs.append("If clause structures cause confusion, use the '⚡ Simplify Selection' tool for a plain-English analogy.")
        elif pred_class == "Very Hard":
            recs.append("Dense academic or theoretical prose. Switch to Focus Chunk Mode to isolate one unit at a time.")
            recs.append("Enable Bionic Saccadic Guides to anchor your eye tracking across dense sentence constructions.")
            recs.append("Use the '⚡ Simplify' assistant to translate abstract academic concepts into concrete mental models.")
            recs.append("Take intentional 15-second consolidation pauses after each paragraph to allow working memory buffers to reset.")

        return recs


def get_inference_service() -> ACLIInferenceService:
    return ACLIInferenceService.get_instance()
