from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

import joblib
import numpy as np
import pandas as pd
from tensorflow import keras

# Use absolute path based on the module location, not working directory
MODULE_DIR = Path(__file__).parent
ANN_MODEL_PATH = MODULE_DIR / "models" / "ann_model.h5"
SCALER_PATH = MODULE_DIR / "models" / "feature_scaler.pkl"

RISK_BUCKETS = [
    (0.80, "strong", "Multiple strong indicators associated with early signs of Type 1 Diabetes have been identified. This may require immediate medical attention."),
    (0.65, "moderate", "Some notable indicators related to Type 1 Diabetes have been observed. While this does not confirm any condition, monitoring is important."),
    (0.0, "normal", "No significant indicators of Type 1 Diabetes have been identified based on the provided information."),
]

_ann_model = None
_scaler = None
_model_mtime = None


def load_model():
    """Load the ANN model and feature scaler, reloading if file changes."""
    global _ann_model, _scaler, _model_mtime

    if not ANN_MODEL_PATH.exists():
        return {"ann_model": None, "scaler": None}

    mtime = ANN_MODEL_PATH.stat().st_mtime
    if _ann_model is None or _model_mtime != mtime:
        # Load ANN model using Keras
        _ann_model = keras.models.load_model(str(ANN_MODEL_PATH))
        # Load feature scaler
        if SCALER_PATH.exists():
            _scaler = joblib.load(str(SCALER_PATH))
        _model_mtime = mtime
    
    return {"ann_model": _ann_model, "scaler": _scaler}


def bucket_risk(probability: float) -> Tuple[str, str]:
    for threshold, label, advice in RISK_BUCKETS:
        if probability >= threshold:
            return label, advice
    return "Low", RISK_BUCKETS[-1][2]


def _heuristic_probability(features: Dict[str, float]) -> float:
    # Lightweight fallback when the joblib model file is missing.
    # IMPORTANT: Be VERY conservative with predictions to avoid false alarms
    # Baseline is negative because most people are healthy (Type 1 is rare)
    score = -1.5  # Start with negative baseline (Type 1 is uncommon)
    
    # Glucose: normal up to 125 is good
    glucose = features["glucose_level"]
    if glucose > 200:
        score += 1.2
    elif glucose > 180:
        score += 0.9
    elif glucose > 160:
        score += 0.7
    elif glucose > 140:
        score += 0.5
    elif glucose > 125:
        score += 0.2
    # else <= 125, no additional score (normal fasting)
    
    # HbA1c: normal is < 5.7
    hba1c = features["hba1c"]
    if hba1c > 9.0:
        score += 1.0
    elif hba1c > 8.0:
        score += 0.8
    elif hba1c > 7.0:
        score += 0.6
    elif hba1c > 6.5:
        score += 0.4
    elif hba1c > 5.7:
        score += 0.2
    # else < 5.7, no score (normal)
    
    # BMI: less weight than metabolic factors
    bmi = features["bmi"]
    if bmi > 40:
        score += 0.2
    elif bmi > 35:
        score += 0.15
    elif bmi > 30:
        score += 0.1
    # else normal, no score
    
    # Family history: significant but not conclusive alone
    if str(features["family_history"]).lower().startswith("y"):
        score += 0.5
    
    # Autoantibodies: very strong indicator of Type 1
    if str(features["autoantibody_presence"]).lower().startswith("p"):
        score += 0.8
    
    # C-peptide: low c-peptide suggests beta cell dysfunction
    # BUT ONLY if it was actually provided (not 0)
    c_peptide = features["c_peptide_level"]
    if c_peptide > 0:  # Only if provided
        if c_peptide < 0.5:
            score += 0.7
        elif c_peptide < 0.8:
            score += 0.4
        elif c_peptide < 1.1:
            score += 0.1
        # else normal, no score
    
    # Convert score to probability using logistic function
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

    # Extract ketone presence from form (NOT the same as a symptom)
    ketone_presence_raw = str(payload.get("ketonePresence", "Absent")).strip().lower()
    ketones_present = 1 if ketone_presence_raw.startswith("p") else 0  # "Present" or "Positive" = 1, "Absent" = 0

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
    return feature_vector, symptoms, ketones_present




def _classify_glucose(glucose_level: float) -> str:
    """Classify glucose level as Normal, Elevated, or High."""
    if glucose_level < 120:
        return "Normal"
    elif glucose_level < 200:
        return "Elevated"
    else:
        return "High"


def _classify_ketones(ketone_flag: int) -> str:
    """Classify ketones as Normal (0) or Elevated/High (1)."""
    return "Elevated" if ketone_flag == 1 else "Normal"


def _classify_bmi(bmi: float) -> str:
    """Classify BMI as Underweight, Normal, or Overweight."""
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    else:
        return "Overweight"


def _generate_medical_interpretation(glucose_class: str, ketone_class: str, bmi_class: str) -> str:
    """Generate a single medical interpretation line based on glucose and ketone levels."""
    
    # CASE 1: High glucose + Elevated ketones
    if glucose_class == "High" and ketone_class == "Elevated":
        return "High glucose with elevated ketone levels suggests abnormal glucose metabolism with a possible insulin deficiency pattern."
    
    # CASE 2: High glucose + Normal ketones
    if glucose_class == "High" and ketone_class == "Normal":
        return "Elevated blood glucose without ketone increase suggests hyperglycemia without significant ketone involvement."
    
    # CASE 3: Elevated glucose + Elevated ketones
    if glucose_class == "Elevated" and ketone_class == "Elevated":
        return "Moderately elevated glucose and ketone levels indicate early metabolic imbalance requiring monitoring."
    
    # CASE 4: Normal glucose + Elevated ketones
    if glucose_class == "Normal" and ketone_class == "Elevated":
        return "Normal glucose with elevated ketones may indicate metabolic stress or dietary-related ketone production."
    
    # CASE 5: Normal glucose + Normal ketones
    if glucose_class == "Normal" and ketone_class == "Normal":
        return "Glucose and ketone levels are within normal limits, indicating stable metabolic condition."
    
    # CASE 6: High/Elevated glucose + Overweight BMI
    if glucose_class in ("High", "Elevated") and bmi_class == "Overweight":
        return "Elevated glucose along with higher BMI suggests a possible metabolic risk pattern."
    
    # DEFAULT CASE 7
    return "Parameter combination indicates mild metabolic variation; continued monitoring is recommended."


def _map_risk_level(risk_label: str) -> str:
    """Map old risk labels to new clean format: strong->HIGH, moderate->MODERATE, normal->LOW."""
    mapping = {
        "strong": "HIGH",
        "moderate": "MODERATE",
        "normal": "LOW"
    }
    return mapping.get(risk_label, "LOW")


def predict_risk(payload: Dict) -> Dict:
    models = load_model()
    ann_model = models.get("ann_model")
    scaler = models.get("scaler")
    feature_vector, symptoms, ketones_present = _map_payload_to_features(payload)

    probability: float

    if ann_model is not None:
        try:
            # Scale features if scaler is available
            X = feature_vector.copy().astype(np.float32)
            if scaler is not None:
                mean = scaler.get("mean", None)
                std = scaler.get("std", None)
                if mean is not None and std is not None:
                    X = (X - mean) / std
            
            # Use ANN model for prediction
            X_input = np.array([X], dtype=np.float32)
            prediction = ann_model.predict(X_input, verbose=0)
            probability = float(prediction[0][0])
        except Exception as e:
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

    # Get old risk level and map to new format
    old_risk_label, _ = bucket_risk(probability)
    risk_level = _map_risk_level(old_risk_label)

    # Extract vital parameters
    glucose_level = feature_vector[3]  # Index 3 is glucose_level
    ketone_flag = ketones_present  # Use actual ketone presence from form, NOT polyuria
    bmi = feature_vector[2]  # Index 2 is BMI

    # Classify parameters
    glucose_class = _classify_glucose(glucose_level)
    ketone_class = _classify_ketones(ketone_flag)
    bmi_class = _classify_bmi(bmi)

    # Generate medical interpretation
    medical_interpretation = _generate_medical_interpretation(glucose_class, ketone_class, bmi_class)

    return {
        "risk_level": risk_level,
        "confidence": probability,
        "glucose": glucose_class,
        "ketones": ketone_class,
        "bmi": bmi_class,
        "medical_interpretation": medical_interpretation,
        "disclaimer": "This system is for risk screening only and not a medical diagnosis.",
        "used_model": "ANN" if ann_model is not None else "Heuristic",
    }
