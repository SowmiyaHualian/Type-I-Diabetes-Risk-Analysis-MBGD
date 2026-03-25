from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

import joblib
import numpy as np
import pandas as pd

MODEL_PATH = Path("models/t1d_logreg_mb.pkl")

RISK_BUCKETS = [
    (0.7, "strong", "Multiple strong indicators associated with early signs of Type 1 Diabetes have been identified. This may require immediate medical attention."),
    (0.4, "moderate", "Some notable indicators related to Type 1 Diabetes have been observed. While this does not confirm any condition, monitoring is important."),
    (0.0, "normal", "No significant indicators of Type 1 Diabetes have been identified based on the provided information."),
]

_model_bundle = None
_model_mtime = None


def load_model():
    """Load the persisted joblib model once, reloading if file changes."""
    global _model_bundle, _model_mtime

    if not MODEL_PATH.exists():
        return None

    mtime = MODEL_PATH.stat().st_mtime
    if _model_bundle is None or _model_mtime != mtime:
        _model_bundle = joblib.load(MODEL_PATH)
        _model_mtime = mtime
    return _model_bundle


def bucket_risk(probability: float) -> Tuple[str, str]:
    for threshold, label, advice in RISK_BUCKETS:
        if probability >= threshold:
            return label, advice
    return "Low", RISK_BUCKETS[-1][2]


def _heuristic_probability(features: Dict[str, float]) -> float:
    # Lightweight fallback when the joblib model file is missing.
    score = 0.0
    score += (features["glucose_level"] - 110) / 70
    score += (features["hba1c"] - 5.4) / 1.5
    score += (features["bmi"] - 22) / 18
    score += 0.5 if str(features["family_history"]).lower().startswith("y") else 0.0
    score += 0.6 if str(features["autoantibody_presence"]).lower().startswith("p") else 0.0
    score += 0.2 if features["c_peptide_level"] < 0.8 else 0.0
    prob = float(1 / (1 + np.exp(-score)))
    return min(max(prob, 0.0), 1.0)


def _map_payload_to_features(payload: Dict) -> Tuple[np.ndarray, Dict[str, int]]:
    # Map incoming form-style payload to training feature order
    def encode_yes_no(val: object) -> int:
        if val is None:
            return 0
        s = str(val).strip().lower()
        return 1 if s in {"yes", "y", "true", "1", "positive"} else 0

    gender_raw = str(payload.get("gender", "")).strip().lower()
    gender = 1 if gender_raw in {"male", "m", "1", "yes"} else 0

    try:
        age = float(payload.get("age", 0) or 0)
    except Exception:
        age = 0.0

    def to_float(key: str) -> float:
        try:
            return float(payload.get(key, 0) or 0)
        except Exception:
            return 0.0

    bmi = to_float("bmi")
    if bmi == 0 and payload.get("weightKg") and payload.get("heightCm"):
        try:
            w = float(payload.get("weightKg"))
            h_cm = float(payload.get("heightCm"))
            h_m = h_cm / 100 if h_cm else 0
            bmi = w / (h_m * h_m) if h_m else 0.0
        except Exception:
            bmi = 0.0

    glucose_level = to_float("randomGlucose") or to_float("fastingGlucose")
    hba1c = to_float("hba1c")

    family_history_raw = payload.get("familyHistory")
    if family_history_raw is None:
        family_history_raw = payload.get("family_history")
    family_history = encode_yes_no(family_history_raw)

    symptoms = {
        "polyuria": str(payload.get("symptoms.polyuria", "false")).lower() in {"true", "1", "on", "yes"},
        "polydipsia": str(payload.get("symptoms.polydipsia", "false")).lower() in {"true", "1", "on", "yes"},
        "weightLoss": str(payload.get("symptoms.weightLoss", "false")).lower() in {"true", "1", "on", "yes"},
        "fatigue": str(payload.get("symptoms.fatigue", "false")).lower() in {"true", "1", "on", "yes"},
        "blurredVision": str(payload.get("symptoms.blurredVision", "false")).lower() in {"true", "1", "on", "yes"},
    }

    c_peptide = to_float("cPeptideLevel")
    autoantibody_res = str(payload.get("autoantibodyResult", "")).strip().lower()
    autoantibodies = 1 if autoantibody_res.startswith("pos") else 0

    feature_vector = np.array(
        [
            age,
            gender,
            bmi,
            glucose_level,
            hba1c,
            family_history,
            int(symptoms["polyuria"]),
            int(symptoms["polydipsia"]),
            int(symptoms["weightLoss"]),
            int(symptoms["fatigue"]),
            int(symptoms["blurredVision"]),
            c_peptide,
            autoantibodies,
        ],
        dtype=float,
    )
    return feature_vector, symptoms


def predict_risk(payload: Dict) -> Dict:
    model_bundle = load_model()
    feature_vector, symptoms = _map_payload_to_features(payload)

    probability: float

    if model_bundle:
        try:
            weights = np.asarray(model_bundle.get("weights"))
            bias = float(model_bundle.get("bias", 0))
            scaler = model_bundle.get("scaler", {})
            numeric_indices = scaler.get("numeric_indices", [])
            mean = np.asarray(scaler.get("mean", []))
            std = np.asarray(scaler.get("std", []))

            if len(mean) and len(std) and len(numeric_indices):
                feature_vector[numeric_indices] = (feature_vector[numeric_indices] - mean) / std

            logit = float(feature_vector @ weights + bias)
            probability = float(1 / (1 + np.exp(-logit)))
        except Exception:
            probability = _heuristic_probability({
                "glucose_level": feature_vector[3],
                "hba1c": feature_vector[4],
                "bmi": feature_vector[2],
                "family_history": "Yes" if feature_vector[5] else "No",
                "autoantibody_presence": "Positive" if feature_vector[12] == 1 else "Negative",
                "c_peptide_level": feature_vector[11],
            })
    else:
        probability = _heuristic_probability({
            "glucose_level": feature_vector[3],
            "hba1c": feature_vector[4],
            "bmi": feature_vector[2],
            "family_history": "Yes" if feature_vector[5] else "No",
            "autoantibody_presence": "Positive" if feature_vector[12] == 1 else "Negative",
            "c_peptide_level": feature_vector[11],
        })

    risk_level, recommendation = bucket_risk(probability)

    return {
        "risk_level": risk_level,
        "probability": probability,
        "recommendation": recommendation,
        "used_model": bool(model_bundle is not None),
    }
