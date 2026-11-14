"""
FocusFlow ACLI - Model Evaluation Module
========================================
Calculates comprehensive multi-class metrics (Accuracy, Macro P/R/F1, Per-Class P/R/F1,
Confusion Matrix) and evaluation visualizations for ACLI candidate and production models.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

from .dataset import VALID_CLASSES


def compute_metrics(y_true: List[int], y_pred: List[int]) -> Dict[str, Any]:
    """
    Computes rigorous evaluation metrics across the 4 difficulty classes.
    """
    class_indices = list(range(len(VALID_CLASSES)))
    acc = float(accuracy_score(y_true, y_pred))
    macro_prec = float(precision_score(y_true, y_pred, labels=class_indices, average="macro", zero_division=0))
    macro_rec = float(recall_score(y_true, y_pred, labels=class_indices, average="macro", zero_division=0))
    macro_f1 = float(f1_score(y_true, y_pred, labels=class_indices, average="macro", zero_division=0))

    cm = confusion_matrix(y_true, y_pred, labels=class_indices).tolist()

    report = classification_report(
        y_true,
        y_pred,
        labels=class_indices,
        target_names=VALID_CLASSES,
        output_dict=True,
        zero_division=0
    )

    per_class = {}
    for cls_name in VALID_CLASSES:
        if cls_name in report:
            per_class[cls_name] = {
                "precision": round(float(report[cls_name]["precision"]), 4),
                "recall": round(float(report[cls_name]["recall"]), 4),
                "f1": round(float(report[cls_name]["f1-score"]), 4),
                "support": int(report[cls_name]["support"])
            }
        else:
            per_class[cls_name] = {"precision": 0.0, "recall": 0.0, "f1": 0.0, "support": 0}

    return {
        "accuracy": round(acc, 4),
        "macro_precision": round(macro_prec, 4),
        "macro_recall": round(macro_rec, 4),
        "macro_f1": round(macro_f1, 4),
        "per_class": per_class,
        "confusion_matrix": cm,
        "class_labels": VALID_CLASSES
    }


def save_confusion_matrix_plot(cm: List[List[int]], output_path: Path, title: str = "ACLI Confusion Matrix") -> Path:
    """
    Generates and saves a clean confusion matrix heatmap figure.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cm_array = np.array(cm)
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(cm_array, interpolation="nearest", cmap=plt.cm.Blues)
    ax.figure.colorbar(im, ax=ax)

    ax.set(
        xticks=np.arange(cm_array.shape[1]),
        yticks=np.arange(cm_array.shape[0]),
        xticklabels=VALID_CLASSES,
        yticklabels=VALID_CLASSES,
        title=title,
        ylabel="Actual Label",
        xlabel="Predicted Label"
    )

    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # Annotate counts inside heatmap
    thresh = cm_array.max() / 2.0 if cm_array.max() > 0 else 1.0
    for i in range(cm_array.shape[0]):
        for j in range(cm_array.shape[1]):
            ax.text(
                j, i, format(cm_array[i, j], "d"),
                ha="center", va="center",
                color="white" if cm_array[i, j] > thresh else "black",
                fontweight="bold"
            )

    fig.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path
