"""Manual logistic regression training with mini-batch gradient descent."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, train_test_split

# Config
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_PATH = Path(
    os.getenv("T1D_DATA_PATH", BASE_DIR.parent / "data" / "processed" / "final_preprocessed_type1_dataset.xlsx")
)
MODEL_PATH = BASE_DIR.parent / "models" / "t1d_logreg_mb.pkl"
PROCESSED_DATA_PATH = BASE_DIR.parent / "data" / "processed" / "validated_type1_dataset.csv"

# Features and schema
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

NUMERIC_COLUMNS: List[str] = [
    "Age",
    "BMI",
    "Glucose_Level",
    "HbA1c",
    "C_Peptide",
    "Autoantibodies",
]

BINARY_COLUMNS: List[str] = [
    "Gender",  # encoded Male=1, Female=0, unknown=0
    "Family_History",
    "Frequent_Urination",
    "Excessive_Thirst",
    "Unexplained_Weight_Loss",
    "Fatigue",
    "Blurred_Vision",
]

TARGET_COLUMN = "Type1_Diabetes_Indicator"

ALTERNATE_COLUMNS = {
    "Glucose_Level": ["Random_Glucose", "Fasting_Glucose"],
    "Frequent_Urination": ["Polyuria"],
    "Excessive_Thirst": ["Polydipsia"],
    "Unexplained_Weight_Loss": ["Weight_Loss"],
    "Type1_Diabetes_Indicator": ["Class_Label"],
}


def sigmoid(z: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-z))


class LogisticRegressionGD:
    """Binary logistic regression trained with mini-batch gradient descent."""

    def __init__(self, lr: float = 0.01, epochs: int = 100, batch_size: int = 32, seed: int = 42):
        self.lr = lr
        self.epochs = epochs
        self.batch_size = batch_size
        self.rng = np.random.default_rng(seed)
        self.weights: np.ndarray | None = None
        self.bias: float = 0.0

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if self.weights is None:
            raise ValueError("Model is not trained.")
        logits = X @ self.weights + self.bias
        return sigmoid(logits)

    def predict(self, X: np.ndarray) -> np.ndarray:
        probs = self.predict_proba(X)
        return (probs >= 0.5).astype(int)

    def _compute_loss(self, probs: np.ndarray, y: np.ndarray) -> float:
        eps = 1e-9
        return -np.mean(y * np.log(probs + eps) + (1 - y) * np.log(1 - probs + eps))

    def fit(self, X: np.ndarray, y: np.ndarray, sample_weights: np.ndarray | None = None) -> None:
        n_samples, n_features = X.shape
        self.weights = np.zeros(n_features)
        self.bias = 0.0

        if sample_weights is None:
            sample_weights = np.ones_like(y, dtype=float)

        for epoch in range(self.epochs):
            indices = self.rng.permutation(n_samples)
            X_shuffled = X[indices]
            y_shuffled = y[indices]
            w_shuffled = sample_weights[indices]

            for start in range(0, n_samples, self.batch_size):
                end = start + self.batch_size
                xb = X_shuffled[start:end]
                yb = y_shuffled[start:end]
                wb = w_shuffled[start:end]

                probs = self.predict_proba(xb)
                errors = (probs - yb) * wb

                grad_w = xb.T @ errors / len(yb)
                grad_b = errors.mean()

                self.weights -= self.lr * grad_w
                self.bias -= self.lr * grad_b

            if (epoch + 1) % 10 == 0:
                epoch_loss = self._compute_loss(self.predict_proba(X), y)
                print(f"Epoch {epoch+1}/{self.epochs} - loss: {epoch_loss:.4f}")


def _resolve_column(df: pd.DataFrame, target: str) -> pd.Series | None:
    if target in df.columns:
        return df[target]

    for alt in ALTERNATE_COLUMNS.get(target, []):
        if alt in df.columns:
            if target == TARGET_COLUMN and alt == "Class_Label":
                # Class_Label already encoded as 0/1 in the processed dataset
                return pd.to_numeric(df[alt], errors="coerce").fillna(0).astype(int)
            return df[alt]
    return None


def harmonize_dataset(raw_df: pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame()
    for col in FEATURE_COLUMNS + [TARGET_COLUMN]:
        series = _resolve_column(raw_df, col)
        if series is not None:
            df[col] = series
            continue

        if col in BINARY_COLUMNS:
            df[col] = "Unknown"
        elif col in NUMERIC_COLUMNS:
            df[col] = 0
        elif col == TARGET_COLUMN:
            raise ValueError("Could not derive target labels. Ensure the dataset has Type1_Diabetes_Indicator or Class_Label.")

    if TARGET_COLUMN not in df.columns:
        raise ValueError("Dataset missing target column after harmonization.")

    return df


def encode_binary(series: pd.Series, positive: Tuple[str, ...] = ("yes", "1", "true")) -> pd.Series:
    def _to_int(val: Any) -> int:
        if pd.isna(val):
            return 0
        s = str(val).strip().lower()
        return 1 if s in positive else 0

    return series.apply(_to_int).astype(int)


def encode_gender(series: pd.Series) -> pd.Series:
    def _to_gender(val: Any) -> int:
        if pd.isna(val):
            return 0
        s = str(val).strip().lower()
        if s in {"male", "m", "1", "yes"}:
            return 1
        if s in {"female", "f", "0", "no"}:
            return 0
        return 0

    return series.apply(_to_gender).astype(int)


def preprocess(
    df: pd.DataFrame,
) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any], List[int], pd.DataFrame]:
    df = df.copy()

    # Remove duplicate records and shuffle
    df = df.drop_duplicates().sample(frac=1.0, random_state=42).reset_index(drop=True)

    df["Gender"] = encode_gender(df["Gender"])
    for col in [c for c in BINARY_COLUMNS if c != "Gender"]:
        df[col] = encode_binary(df[col])

    # Normalize target to binary (handles strings like Positive/Negative)
    df[TARGET_COLUMN] = encode_binary(df[TARGET_COLUMN], positive=("yes", "1", "true", "positive", "pos", "type1", "t1d", "diagnosed", "present"))

    # Numeric conversions with median substitution
    fill_values: Dict[str, float] = {}
    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        median_val = float(df[col].median(skipna=True))
        if np.isnan(median_val):
            median_val = 0.0
        fill_values[col] = median_val
        df[col] = df[col].fillna(fill_values[col])

    X = df[FEATURE_COLUMNS].to_numpy(dtype=float)
    y = df[TARGET_COLUMN].astype(int).to_numpy()

    numeric_indices = [FEATURE_COLUMNS.index(col) for col in NUMERIC_COLUMNS]
    processed_df = df[FEATURE_COLUMNS + [TARGET_COLUMN]].copy()
    return X, y, fill_values, numeric_indices, processed_df


def validate_preprocessed(X: np.ndarray, y: np.ndarray) -> None:
    if np.isnan(X).any():
        raise ValueError("Preprocessed features contain NaN values after cleaning.")
    unique_labels = np.unique(y)
    if not set(unique_labels) >= {0, 1}:
        raise ValueError(f"Target labels must contain both classes 0 and 1. Found labels: {unique_labels}")


def load_dataset(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found at {path}. Set T1D_DATA_PATH or place the file accordingly.")
    if path.suffix.lower() in {".xlsx", ".xls"}:
        df = pd.read_excel(path)
    else:
        df = pd.read_csv(path)
    df = harmonize_dataset(df)
    return df


def evaluate(model: LogisticRegressionGD, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Any]:
    probs = model.predict_proba(X_test)
    preds = (probs >= 0.5).astype(int)
    roc_auc = None
    try:
        roc_auc = roc_auc_score(y_test, probs)
    except Exception:
        roc_auc = None
    return {
        "accuracy": accuracy_score(y_test, preds),
        "precision": precision_score(y_test, preds, zero_division=0),
        "recall": recall_score(y_test, preds, zero_division=0),
        "f1": f1_score(y_test, preds, zero_division=0),
        "confusion_matrix": confusion_matrix(y_test, preds).tolist(),
        "roc_auc": roc_auc,
    }


def compute_class_weights(y: np.ndarray) -> np.ndarray:
    pos = (y == 1).sum()
    neg = (y == 0).sum()
    if pos == 0 or neg == 0:
        return np.ones_like(y, dtype=float)
    pos_weight = neg / pos
    weights = np.where(y == 1, pos_weight, 1.0)
    return weights.astype(float)


def cross_val_score_params(
    lrs: List[float],
    epochs_list: List[int],
    batch_sizes: List[int],
    X: np.ndarray,
    y: np.ndarray,
    sample_weights: np.ndarray,
) -> Tuple[float, int, int, Dict[str, float]]:
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    best_params: Tuple[float, int, int] | None = None
    best_f1 = -1.0

    for lr in lrs:
        for epochs in epochs_list:
            for batch in batch_sizes:
                fold_f1: List[float] = []
                for train_idx, val_idx in skf.split(X, y):
                    model = LogisticRegressionGD(lr=lr, epochs=epochs, batch_size=batch, seed=42)
                    model.fit(X[train_idx], y[train_idx], sample_weights=sample_weights[train_idx])
                    fold_f1.append(f1_score(y[val_idx], model.predict(X[val_idx]), zero_division=0))
                mean_f1 = float(np.mean(fold_f1))
                if mean_f1 > best_f1:
                    best_f1 = mean_f1
                    best_params = (lr, epochs, batch)

    if best_params is None:
        best_params = (lrs[0], epochs_list[0], batch_sizes[0])
    best_lr, best_epochs, best_batch = best_params
    return best_lr, best_epochs, best_batch, {"cv_f1": best_f1}


def save_model(model: LogisticRegressionGD, scaler: Dict[str, Any]) -> None:
    bundle = {
        "weights": model.weights,
        "bias": model.bias,
        "feature_names": FEATURE_COLUMNS,
        "scaler": scaler,
    }
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")


def main() -> None:
    data_path = DEFAULT_DATA_PATH
    print(f"Loading dataset from {data_path}")
    df = load_dataset(data_path)

    X, y, fill_values, numeric_indices, processed_df = preprocess(df)
    validate_preprocessed(X, y)

    # Class balancing weights (higher weight to minority class)
    sample_weights = compute_class_weights(y)

    PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    processed_df.to_csv(PROCESSED_DATA_PATH, index=False)
    print(f"Preprocessed dataset saved to {PROCESSED_DATA_PATH}")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    sample_weights_train = compute_class_weights(y_train)

    mean = X_train[:, numeric_indices].mean(axis=0)
    std = X_train[:, numeric_indices].std(axis=0)
    std[std == 0] = 1

    def scale(arr: np.ndarray) -> np.ndarray:
        scaled = arr.copy()
        scaled[:, numeric_indices] = (arr[:, numeric_indices] - mean) / std
        return scaled

    X_train_scaled = scale(X_train)
    X_test_scaled = scale(X_test)

    # Hyperparameter search (goal: better F1/recall)
    lr_grid = [0.01, 0.005, 0.002]
    epoch_grid = [150, 200]
    batch_grid = [16, 32, 64]
    best_lr, best_epochs, best_batch, cv_stats = cross_val_score_params(
        lr_grid, epoch_grid, batch_grid, X_train_scaled, y_train, sample_weights_train
    )

    model = LogisticRegressionGD(lr=best_lr, epochs=best_epochs, batch_size=best_batch, seed=42)
    print(
        f"Training logistic regression with mini-batch GD (lr={best_lr}, epochs={best_epochs}, batch={best_batch})"
    )
    model.fit(X_train_scaled, y_train, sample_weights=sample_weights_train)

    metrics = evaluate(model, X_test_scaled, y_test)
    metrics.update(cv_stats)
    print("Evaluation metrics:")
    print(json.dumps(metrics, indent=2))

    scaler = {
        "mean": mean,
        "std": std,
        "numeric_indices": numeric_indices,
        "fill_values": fill_values,
    }
    save_model(model, scaler)
    print("Model retrained successfully using updated dataset")


if __name__ == "__main__":
    main()
