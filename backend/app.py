import json
import os
import secrets
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import joblib
import numpy as np
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = BASE_DIR.parent / "models" / "t1d_logreg_mb.pkl"
USER_STORE = DATA_DIR / "users.json"
PATIENT_RECORDS_PATH = DATA_DIR / "patient_records.xlsx"

# Feature ordering must match training
FEATURE_COLUMNS: List[str] = [
    "Age",
    "Gender",
    "BMI",
    "Glucose_Level",
    "HbA1c",
    "Family_History",
    "Frequent_Urination",
    "Excessive_Thirst",
    "Unexplained_Weight_Loss",
    "Fatigue",
    "Blurred_Vision",
    "C_Peptide",
    "Autoantibodies",
]

NUMERIC_COLUMNS: List[str] = ["Age", "BMI", "Glucose_Level", "HbA1c", "C_Peptide", "Autoantibodies"]

SESSIONS: Dict[str, str] = {}

app = Flask(__name__)
CORS(app)


def load_model_bundle() -> Dict[str, Any]:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            "Model file not found. Run train_model.py first to generate the updated model bundle."
        )
    return joblib.load(MODEL_PATH)


MODEL_BUNDLE: Dict[str, Any] | None = None


def get_model_bundle() -> Dict[str, Any]:
    global MODEL_BUNDLE
    if MODEL_BUNDLE is None:
        MODEL_BUNDLE = load_model_bundle()
    return MODEL_BUNDLE


def load_user_store() -> Dict[str, Dict[str, Any]]:
    if not USER_STORE.exists():
        return {}
    try:
        return json.loads(USER_STORE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_user_store(store: Dict[str, Dict[str, Any]]) -> None:
    USER_STORE.parent.mkdir(parents=True, exist_ok=True)
    USER_STORE.write_text(json.dumps(store, indent=2), encoding="utf-8")


def require_auth() -> str | None:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.lower().startswith("bearer "):
        return None
    token = auth_header.split(" ", 1)[1].strip()
    return SESSIONS.get(token)


def encode_yes_no(value: Any) -> int:
    if value is None:
        return 0
    s = str(value).strip().lower()
    return 1 if s in {"yes", "y", "true", "1", "positive"} else 0


def encode_gender(value: Any) -> int:
    if value is None:
        return 0
    s = str(value).strip().lower()
    if s in {"male", "m", "1", "yes"}:
        return 1
    if s in {"female", "f", "0", "no"}:
        return 0
    return 0


def normalize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    def num_or_nan(key: str) -> float:
        val = payload.get(key)
        try:
            return float(val)
        except (TypeError, ValueError):
            return float("nan")

    def num_or_nan_value(val: Any) -> float:
        try:
            return float(val)
        except (TypeError, ValueError):
            return float("nan")

    glucose_val = (
        payload.get("glucose_level")
        if payload.get("glucose_level") is not None
        else payload.get("random_glucose", payload.get("fasting_glucose"))
    )
    glucose_num = num_or_nan_value(glucose_val)

    return {
        "Age": num_or_nan("age"),
        "Gender": encode_gender(payload.get("gender", "Unknown")),
        "BMI": num_or_nan("bmi"),
        "Glucose_Level": glucose_num if not np.isnan(glucose_num) else num_or_nan("glucose_level"),
        "HbA1c": num_or_nan("hba1c"),
        "Family_History": encode_yes_no(payload.get("family_history", "no")),
        "Frequent_Urination": encode_yes_no(payload.get("frequent_urination", "no")),
        "Excessive_Thirst": encode_yes_no(payload.get("excessive_thirst", "no")),
        "Unexplained_Weight_Loss": encode_yes_no(payload.get("unexplained_weight_loss", "no")),
        "Fatigue": encode_yes_no(payload.get("fatigue", "no")),
        "Blurred_Vision": encode_yes_no(payload.get("blurred_vision", "no")),
        "C_Peptide": num_or_nan("c_peptide"),
        "Autoantibodies": num_or_nan("autoantibodies"),
    }


def append_patient_record(raw_payload: Dict[str, Any], features: Dict[str, Any], indicator: int, confidence: float, user_email: str) -> None:
    try:
        symptoms_flags = {
            "Frequent_Urination": "Yes" if features.get("Frequent_Urination", 0) else "No",
            "Excessive_Thirst": "Yes" if features.get("Excessive_Thirst", 0) else "No",
            "Unexplained_Weight_Loss": "Yes" if features.get("Unexplained_Weight_Loss", 0) else "No",
            "Fatigue": "Yes" if features.get("Fatigue", 0) else "No",
            "Blurred_Vision": "Yes" if features.get("Blurred_Vision", 0) else "No",
        }

        symptoms_str = "; ".join([k for k, v in symptoms_flags.items() if v == "Yes"]) or "None"

        record = {
            "Patient_ID": secrets.token_hex(8),
            "Timestamp": datetime.utcnow().isoformat(),
            "Submitted_By": user_email,
            "Name": raw_payload.get("name", "Unknown"),
            "Age": features.get("Age", ""),
            "BMI": features.get("BMI", ""),
            "Glucose_Level": features.get("Glucose_Level", ""),
            "HbA1c": features.get("HbA1c", ""),
            "Symptoms": symptoms_str,
            "C_Peptide": features.get("C_Peptide", ""),
            "Autoantibodies": features.get("Autoantibodies", ""),
            "Prediction_Result": "Possible indicators" if indicator == 1 else "No strong indicators",
            "Model_Confidence": round(float(confidence), 4),
        }

        if PATIENT_RECORDS_PATH.exists():
            existing = pd.read_excel(PATIENT_RECORDS_PATH)
        else:
            existing = pd.DataFrame()

        updated = pd.concat([existing, pd.DataFrame([record])], ignore_index=True)
        PATIENT_RECORDS_PATH.parent.mkdir(parents=True, exist_ok=True)
        updated.to_excel(PATIENT_RECORDS_PATH, index=False)
    except Exception as exc:  # keep API response unaffected
        print(f"Failed to append patient record: {exc}")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json(force=True) or {}
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if not name or not email or not password:
        return jsonify({"error": "Name, email, and password are required."}), 400

    users = load_user_store()
    if email in users:
        return jsonify({"error": "Account already exists."}), 400

    password_hash = generate_password_hash(password)
    users[email] = {"name": name, "password_hash": password_hash, "created_at": datetime.utcnow().isoformat()}
    save_user_store(users)
    return jsonify({"message": "Registration successful."}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True) or {}
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    users = load_user_store()
    user = users.get(email)
    if not user:
        return jsonify({"error": "Account not found."}), 404

    if not check_password_hash(user.get("password_hash", ""), password):
        return jsonify({"error": "Incorrect password."}), 401

    token = secrets.token_urlsafe(32)
    SESSIONS[token] = email
    return jsonify({"message": "Login successful.", "token": token, "name": user.get("name", "")}), 200


@app.route("/predict", methods=["POST"])
def predict():
    user_email = require_auth()
    if not user_email:
        return jsonify({"error": "Unauthorized. Please login."}), 401

    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Invalid JSON payload"}), 400

    if not isinstance(data, dict):
        return jsonify({"error": "Payload must be a JSON object"}), 400

    try:
        features = normalize_payload(data)
    except Exception as exc:  # safeguard against bad types
        return jsonify({"error": f"Invalid input values: {exc}"}), 400

    try:
        bundle = get_model_bundle()
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 500

    try:
        feature_order = bundle.get("feature_names", FEATURE_COLUMNS)
        weights = np.asarray(bundle.get("weights"))
        bias = float(bundle.get("bias", 0))
        scaler = bundle.get("scaler", {})
        numeric_indices = scaler.get("numeric_indices", [])
        mean = np.asarray(scaler.get("mean", []))
        std = np.asarray(scaler.get("std", []))
        fill_values = scaler.get("fill_values", {})

        row = np.array([features.get(col, float("nan")) for col in feature_order], dtype=float)

        # Apply median fill for missing numeric values
        for idx, col in enumerate(feature_order):
            if idx in numeric_indices and (np.isnan(row[idx]) or row[idx] is None):
                row[idx] = fill_values.get(col, 0.0)

        if len(mean) and len(std) and len(numeric_indices):
            row[numeric_indices] = (row[numeric_indices] - mean) / std

        logit = float(row @ weights + bias)
        prob = 1 / (1 + np.exp(-logit))
        indicator_flag = int(prob >= 0.5)
        confidence = prob
    except Exception as exc:
        return jsonify({"error": f"Model prediction failed: {exc}"}), 500

    if indicator_flag == 1:
        result_msg = (
            "The provided health information shows patterns that may be associated with indicators often evaluated "
            "for Type 1 Diabetes. It is recommended to consult a healthcare professional for further medical evaluation."
        )
    else:
        result_msg = (
            "The provided information does not currently show strong indicators typically associated with Type 1 Diabetes. "
            "However, this tool is only a supportive screening system and not a medical diagnosis."
        )

    disclaimer = (
        "This system provides a screening indication based on the provided health parameters and does not constitute a "
        "medical diagnosis. Please consult a qualified healthcare professional for proper medical evaluation."
    )

    # Persist patient record to Excel
    append_patient_record(data, features, indicator_flag, float(confidence), user_email)

    return jsonify({
        "result": result_msg,
        "indicator": indicator_flag,
        "confidence": round(float(confidence), 4),
        "features": features,
        "disclaimer": disclaimer,
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
