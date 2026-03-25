"""Flask server with multi-page flow (landing -> login/register -> dashboard -> result)."""

import os
import socket
import threading
import time
import webbrowser
from datetime import datetime
from pathlib import Path

import pandas as pd
from flask import Flask, redirect, render_template, render_template_string, request, session, url_for

from predict import predict_risk

# Use absolute paths based on the module location
APP_DIR = Path(__file__).parent
app = Flask(__name__, static_folder=str(APP_DIR / "frontend"), template_folder=str(APP_DIR / "frontend"))
app.secret_key = os.getenv("SECRET_KEY", "secret123")  # Use environment variable in production


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def open_browser(url: str) -> None:
    def _open():
        time.sleep(1)
        webbrowser.open(url)

    threading.Thread(target=_open, daemon=True).start()


def require_login():
    return "user" in session


# -----------------
# User persistence
# -----------------
USERS_FILE = APP_DIR / "users.xlsx"


def load_users() -> pd.DataFrame:
    if USERS_FILE.exists():
        try:
            return pd.read_excel(USERS_FILE)
        except Exception:
            return pd.DataFrame(columns=["username", "password", "name"])
    return pd.DataFrame(columns=["username", "password", "name"])


def save_users(df: pd.DataFrame) -> None:
    df.to_excel(USERS_FILE, index=False)


# -------------------------
# Patient record persistence
# -------------------------
PATIENT_RECORDS_FILE = APP_DIR / "patient_records.xlsx"
PATIENT_RECORD_COLUMNS = [
    "Record_ID",
    "Timestamp",
    "User_Name",
    "User_Email",
    "User_Password",
    "Age",
    "BMI",
    "Fasting_Glucose",
    "Random_Glucose",
    "HbA1c",
    "Ketone",
    "Polyuria",
    "Polydipsia",
    "Weight_Loss",
    "Fatigue",
    "Blurred_Vision",
    "C_Peptide (optional)",
    "Autoantibodies (optional)",
    "Prediction_Result",
    "Model_Confidence",
]


def _load_patient_records() -> pd.DataFrame:
    if PATIENT_RECORDS_FILE.exists():
        try:
            return pd.read_excel(PATIENT_RECORDS_FILE)
        except Exception:
            pass
    return pd.DataFrame(columns=PATIENT_RECORD_COLUMNS)


def _parse_number(value):
    try:
        if value is None or value == "":
            return ""
        return float(value)
    except Exception:
        return ""


def _symptom_flag(form_data: dict, key: str) -> str:
    return "Yes" if str(form_data.get(key, "")).lower() in {"true", "1", "on", "yes"} else "No"


def _compute_bmi(form_data: dict) -> float | str:
    bmi_val = _parse_number(form_data.get("bmi"))
    if bmi_val not in ("", None) and bmi_val != 0:
        return bmi_val

    try:
        weight = float(form_data.get("weightKg", 0) or 0)
        height_cm = float(form_data.get("heightCm", 0) or 0)
        height_m = height_cm / 100 if height_cm else 0
        if height_m:
            return round(weight / (height_m * height_m), 2)
    except Exception:
        pass
    return ""


def save_patient_record(user: dict, form_data: dict, prediction: dict) -> None:
    df = _load_patient_records()

    try:
        max_id = pd.to_numeric(df.get("Record_ID", pd.Series(dtype="int")), errors="coerce").max()
        next_id = int(max_id) + 1 if pd.notna(max_id) else 1
    except Exception:
        next_id = 1

    # Retrieve user password from users file
    user_password = ""
    try:
        users_df = load_users()
        user_email = user.get("email", "").lower()
        matching_user = users_df[users_df["username"].str.lower() == user_email]
        if not matching_user.empty:
            user_password = matching_user.iloc[0]["password"]
    except Exception:
        user_password = ""

    record = {
        "Record_ID": next_id,
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "User_Name": user.get("name", ""),
        "User_Email": user.get("email", ""),
        "User_Password": user_password,
        "Age": _parse_number(form_data.get("age")),
        "BMI": _compute_bmi(form_data),
        "Fasting_Glucose": _parse_number(form_data.get("fastingGlucose")),
        "Random_Glucose": _parse_number(form_data.get("randomGlucose")),
        "HbA1c": _parse_number(form_data.get("hba1c")),
        "Ketone": form_data.get("ketonePresence", ""),
        "Polyuria": _symptom_flag(form_data, "symptoms.polyuria"),
        "Polydipsia": _symptom_flag(form_data, "symptoms.polydipsia"),
        "Weight_Loss": _symptom_flag(form_data, "symptoms.weightLoss"),
        "Fatigue": _symptom_flag(form_data, "symptoms.fatigue"),
        "Blurred_Vision": _symptom_flag(form_data, "symptoms.blurredVision"),
        "C_Peptide (optional)": _parse_number(form_data.get("cPeptideLevel")),
        "Autoantibodies (optional)": form_data.get("autoantibodyResult", ""),
        "Prediction_Result": prediction.get("risk_level", ""),
        "Model_Confidence": round(float(prediction.get("probability", 0)), 4) if prediction.get("probability") is not None else "",
    }

    ordered_record = {col: record.get(col, "") for col in PATIENT_RECORD_COLUMNS}
    df = pd.concat([df, pd.DataFrame([ordered_record])], ignore_index=True)
    df.to_excel(PATIENT_RECORDS_FILE, index=False)


@app.route("/")
def landing():
    # Serve main entry from the frontend folder
    return render_template("index.html")


# Public marketing pages
@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


# Redirect legacy direct-file paths to routed pages
@app.route("/login.html")
def login_html():
    return redirect(url_for("login"))


@app.route("/register.html")
def register_html():
    return redirect(url_for("register"))


@app.route("/dashboard.html")
def dashboard_html():
    return redirect(url_for("dashboard"))


@app.route("/result.html")
def result_html():
    return redirect(url_for("result_view"))


@app.route("/about.html")
def about_html():
    return redirect(url_for("about"))


@app.route("/contact.html")
def contact_html():
    return redirect(url_for("contact"))


@app.route("/login", methods=["GET", "POST"])
def login():
    """Validate user credentials against users.xlsx and create session."""

    error = None
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "").strip()
        login_id = email or username

        users = load_users()
        match = users[(users["username"].str.lower() == login_id) & (users["password"] == password)]
        if not match.empty:
            user_row = match.iloc[0]
            session["user"] = {"name": user_row.get("name") or user_row["username"], "email": user_row["username"]}
            return redirect(url_for("dashboard"))

        error = "Invalid credentials"

    return render_template("login.html", error=error)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user into users.xlsx and start a session."""

    error = None
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        confirm = request.form.get("confirmPassword", "").strip()

        if not all([name, email, password, confirm]):
            error = "Please fill in all fields."
        elif "@" not in email:
            error = "Please enter a valid email."
        elif password != confirm:
            error = "Passwords do not match."
        elif len(password) < 6:
            error = "Password must be at least 6 characters."
        else:
            users = load_users()
            existing = users["username"].str.lower().values if not users.empty else []
            if email in existing:
                error = "User already exists."
            else:
                new_row = {"username": email, "password": password, "name": name}
                users = pd.concat([users, pd.DataFrame([new_row])], ignore_index=True)
                save_users(users)
                session["user"] = {"name": name, "email": email}
                return redirect(url_for("dashboard"))

    return render_template("register.html", error=error)


@app.route("/dashboard")
def dashboard():
    if not require_login():
        return redirect(url_for("login"))
    return render_template("dashboard.html")


@app.route("/predict", methods=["POST"])
def predict():
    if not require_login():
        return redirect(url_for("login"))
    data = request.form.to_dict()
    result = predict_risk(data)
    try:
        save_patient_record(session.get("user", {}), data, result)
    except Exception as exc:
        # Fail gracefully so prediction flow continues even if logging encounters an issue
        print(f"Failed to save patient record: {exc}")
    session["result"] = result
    session["form_data"] = data
    return redirect(url_for("result_view"))


@app.route("/result")
def result_view():
    if not require_login():
        return redirect(url_for("login"))

    result = session.get("result")
    form_data = session.get("form_data")

    if result is None:
        return redirect(url_for("dashboard"))

    return render_template("result.html", result=result, form_data=form_data)


@app.route("/view-records")
def view_records():
        if not require_login():
                return redirect(url_for("login"))

        df = _load_patient_records()
        table_html = df.to_html(index=False, classes="records-table") if not df.empty else "<p>No records found.</p>"

        return render_template_string(
                """
                <!doctype html>
                <html lang=\"en\">
                    <head>
                        <meta charset=\"UTF-8\">
                        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
                        <title>Patient Records</title>
                        <style>
                            body { font-family: Arial, sans-serif; margin: 32px; color: #0f172a; }
                            h1 { margin-bottom: 16px; }
                            table { border-collapse: collapse; width: 100%; }
                            th, td { border: 1px solid #cbd5e1; padding: 8px 10px; text-align: left; }
                            th { background: #e2e8f0; }
                            tr:nth-child(even) td { background: #f8fafc; }
                            a { color: #0f6c74; text-decoration: none; }
                        </style>
                    </head>
                    <body>
                        <h1>Stored Patient Records</h1>
                        <p><a href=\"{{ url_for('dashboard') }}\">Back to Dashboard</a></p>
                        {{ table|safe }}
                    </body>
                </html>
                """,
                table=table_html,
        )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


def main():
    # Get port from environment variable (for Render deployment) or find free port (local development)
    port = int(os.getenv("PORT", find_free_port()))
    # Check if PORT is set (Render) or if FLASK_ENV is production - both indicate cloud deployment
    is_production = bool(os.getenv("PORT")) or os.getenv("FLASK_ENV") == "production"
    host = "0.0.0.0" if is_production else "127.0.0.1"
    
    url = f"http://{host}:{port}"
    print(f"\nServer running at {url}\n")
    
    # Only open browser in local development
    if not is_production:
        open_browser(f"http://127.0.0.1:{port}")
    
    app.run(host=host, port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
