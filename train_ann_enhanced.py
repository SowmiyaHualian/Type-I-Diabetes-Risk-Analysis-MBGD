"""Enhanced model training with comprehensive evaluation metrics."""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Tuple

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, roc_curve, auc, classification_report
)

from backend.train_model import (
    LogisticRegressionGD, preprocess, validate_preprocessed,
    compute_class_weights, cross_val_score_params, load_dataset
)
from database import get_db


class EnhancedModelEvaluator:
    """Comprehensive model evaluation with advanced metrics."""
    
    @staticmethod
    def evaluate_model(
        model: LogisticRegressionGD,
        X_test: np.ndarray,
        y_test: np.ndarray
    ) -> Dict[str, Any]:
        """Calculate comprehensive evaluation metrics."""
        
        probs = model.predict_proba(X_test)
        preds = (probs >= 0.5).astype(int)
        
        # Basic metrics
        accuracy = accuracy_score(y_test, preds)
        precision = precision_score(y_test, preds, zero_division=0)
        recall = recall_score(y_test, preds, zero_division=0)
        f1 = f1_score(y_test, preds, zero_division=0)
        
        # ROC-AUC Score
        try:
            roc_auc = roc_auc_score(y_test, probs)
        except:
            roc_auc = None
        
        # Confusion Matrix
        cm = confusion_matrix(y_test, preds)
        tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, 0)
        
        # Specificity and Sensitivity
        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        
        # Matthews Correlation Coefficient
        mcc_numerator = (tp * tn) - (fp * fn)
        mcc_denominator = np.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
        mcc = mcc_numerator / mcc_denominator if mcc_denominator > 0 else 0
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'roc_auc': roc_auc,
            'sensitivity': sensitivity,
            'specificity': specificity,
            'mcc': mcc,
            'confusion_matrix': cm.tolist(),
            'true_negatives': int(tn),
            'false_positives': int(fp),
            'false_negatives': int(fn),
            'true_positives': int(tp),
            'classification_report': classification_report(y_test, preds, output_dict=True),
        }
    
    @staticmethod
    def create_metrics_summary(metrics: Dict[str, Any]) -> str:
        """Create human-readable metrics summary."""
        summary = f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                        MODEL EVALUATION METRICS                           ║
╚════════════════════════════════════════════════════════════════════════════╝

CLASSIFICATION METRICS:
  • Accuracy:     {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)
  • Precision:    {metrics['precision']:.4f} ({metrics['precision']*100:.2f}%)
  • Recall:       {metrics['recall']:.4f} ({metrics['recall']*100:.2f}%)
  • F1-Score:     {metrics['f1_score']:.4f}

ADVANCED METRICS:
  • ROC-AUC:      {metrics.get('roc_auc', 'N/A')}
  • Sensitivity:  {metrics['sensitivity']:.4f} ({metrics['sensitivity']*100:.2f}%)
  • Specificity:  {metrics['specificity']:.4f} ({metrics['specificity']*100:.2f}%)
  • MCC:          {metrics['mcc']:.4f}

CONFUSION MATRIX:
  • True Negatives:   {metrics['true_negatives']}
  • False Positives:  {metrics['false_positives']}
  • False Negatives:  {metrics['false_negatives']}
  • True Positives:   {metrics['true_positives']}

PREDICTION DISTRIBUTION:
  • Actual Negatives: {metrics['true_negatives'] + metrics['false_positives']}
  • Actual Positives: {metrics['true_positives'] + metrics['false_negatives']}
  • Predicted Negatives: {metrics['true_negatives'] + metrics['false_negatives']}
  • Predicted Positives: {metrics['false_positives'] + metrics['true_positives']}
"""
        return summary
    
    @staticmethod
    def store_metrics_to_db(model_name: str, metrics: Dict[str, Any]) -> None:
        """Store metrics in database."""
        db = get_db()
        
        # Prepare metrics for storage
        storage_metrics = {
            'accuracy': metrics['accuracy'],
            'precision': metrics['precision'],
            'recall': metrics['recall'],
            'f1_score': metrics['f1_score'],
            'roc_auc': metrics.get('roc_auc'),
            'confusion_matrix': metrics['confusion_matrix'],
            'notes': f"Sensitivity: {metrics['sensitivity']:.4f}, Specificity: {metrics['specificity']:.4f}",
        }
        
        db.store_model_metrics(model_name, storage_metrics)


def train_and_evaluate_model(
    data_path: Path,
    model_name: str = "Type1_Diabetes_LogisticRegression_MBGD"
) -> Dict[str, Any]:
    """Complete training and evaluation pipeline."""
    
    print(f"\n{'='*80}")
    print(f"Training and Evaluating: {model_name}")
    print(f"{'='*80}\n")
    
    # Load and preprocess data
    print("Loading dataset...")
    df = load_dataset(data_path)
    
    X, y, fill_values, numeric_indices, processed_df = preprocess(df)
    validate_preprocessed(X, y)
    
    print(f"Dataset shape: {X.shape}")
    print(f"Class distribution: {np.bincount(y)}")
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Feature scaling
    mean = X_train[:, numeric_indices].mean(axis=0)
    std = X_train[:, numeric_indices].std(axis=0)
    std[std == 0] = 1
    
    def scale(arr):
        scaled = arr.copy()
        scaled[:, numeric_indices] = (arr[:, numeric_indices] - mean) / std
        return scaled
    
    X_train_scaled = scale(X_train)
    X_test_scaled = scale(X_test)
    
    # Hyperparameter tuning
    print("\nPerforming hyperparameter tuning...")
    sample_weights_train = compute_class_weights(y_train)
    
    lr_grid = [0.01, 0.005, 0.002]
    epoch_grid = [150, 200]
    batch_grid = [16, 32, 64]
    
    best_lr, best_epochs, best_batch, cv_stats = cross_val_score_params(
        lr_grid, epoch_grid, batch_grid, X_train_scaled, y_train, sample_weights_train
    )
    
    print(f"Best hyperparameters: lr={best_lr}, epochs={best_epochs}, batch={best_batch}")
    print(f"Cross-validation F1: {cv_stats['cv_f1']:.4f}")
    
    # Train final model
    print("\nTraining final model...")
    model = LogisticRegressionGD(lr=best_lr, epochs=best_epochs, batch_size=best_batch, seed=42)
    model.fit(X_train_scaled, y_train, sample_weights=sample_weights_train)
    
    # Evaluate model
    print("\nEvaluating model...")
    metrics = EnhancedModelEvaluator.evaluate_model(model, X_test_scaled, y_test)
    
    # Print summary
    summary = EnhancedModelEvaluator.create_metrics_summary(metrics)
    print(summary)
    
    # Store metrics
    try:
        EnhancedModelEvaluator.store_metrics_to_db(model_name, metrics)
        print("✓ Metrics stored in database")
    except Exception as e:
        print(f"⚠ Could not store metrics in database: {e}")
    
    # Save detailed report
    report = {
        'model_name': model_name,
        'training_date': str(pd.Timestamp.now()),
        'hyperparameters': {
            'learning_rate': best_lr,
            'epochs': best_epochs,
            'batch_size': best_batch,
        },
        'data_info': {
            'total_samples': len(X),
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'class_distribution': np.bincount(y).tolist(),
        },
        'cross_validation': cv_stats,
        'metrics': {
            key: (float(value) if isinstance(value, (np.floating, np.integer)) else value)
            for key, value in metrics.items()
        },
    }
    
    report_path = Path(__file__).parent / f"model_evaluation_{model_name}.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✓ Report saved to: {report_path}")
    
    return report


if __name__ == "__main__":
    # Example usage
    data_path = Path(__file__).parent.parent / "data" / "processed" / "final_preprocessed_type1_dataset.xlsx"
    
    if data_path.exists():
        report = train_and_evaluate_model(data_path)
        print("\n✓ Training and evaluation completed successfully")
    else:
        print(f"✗ Data file not found: {data_path}")
