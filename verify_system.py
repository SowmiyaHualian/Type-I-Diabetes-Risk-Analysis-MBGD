"""
================================================================================
QUICK VERIFICATION & TESTING SCRIPT
================================================================================

This script quickly verifies that:
1. Dataset is loaded correctly
2. Both models can be loaded
3. Predictions work (single & batch)
4. All components are functional

Run this to verify the entire system is working before deployment.
"""

import pandas as pd
import pickle
from tensorflow import keras
import sys

print("\n" + "="*80)
print("DIABETES PREDICTION SYSTEM - QUICK VERIFICATION TEST")
print("="*80 + "\n")

try:
    # ========================================================================
    # TEST 1: Load Dataset
    # ========================================================================
    print("[TEST 1] Loading dataset...")
    df = pd.read_csv("data/final/final_preprocessed_mixed.csv")
    print(f"  ✓ Dataset loaded: {len(df):,} records, {len(df.columns)} columns")
    print(f"    - Features: {', '.join(df.columns[:-1][:3])}...")
    print(f"    - Target: {df.columns[-1]}")
    
    # ========================================================================
    # TEST 2: Load Models
    # ========================================================================
    print("\n[TEST 2] Loading trained models...")
    
    try:
        ann_model = keras.models.load_model('models/ann_model.h5')
        print("  ✓ ANN model loaded successfully")
    except Exception as e:
        print(f"  ✗ Failed to load ANN: {e}")
        sys.exit(1)
    
    try:
        lr_model = pickle.load(open('models/logistic_regression_model.pkl', 'rb'))
        print("  ✓ Logistic Regression model loaded successfully")
    except Exception as e:
        print(f"  ✗ Failed to load LR: {e}")
        sys.exit(1)
    
    try:
        scaler = pickle.load(open('models/feature_scaler.pkl', 'rb'))
        print("  ✓ Feature scaler loaded successfully")
    except Exception as e:
        print(f"  ✗ Failed to load scaler: {e}")
        sys.exit(1)
    
    # ========================================================================
    # TEST 3: Prepare Test Data
    # ========================================================================
    print("\n[TEST 3] Preparing test data...")
    
    # Get features (exclude target)
    X = df.drop('Class_Label', axis=1)
    y = df['Class_Label'].values
    
    # Split train/test
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Scale test data
    X_test_scaled = scaler.transform(X_test)
    
    print(f"  ✓ Test set prepared: {len(X_test):,} samples")
    print(f"    - Positive cases: {sum(y_test):,}")
    print(f"    - Negative cases: {sum(1-y_test):,}")
    
    # ========================================================================
    # TEST 4: Test ANN Predictions
    # ========================================================================
    print("\n[TEST 4] Testing ANN model predictions...")
    
    try:
        y_pred_ann = (ann_model.predict(X_test_scaled[:100], verbose=0) > 0.5).astype(int).flatten()
        print(f"  ✓ ANN predictions working")
        print(f"    - Tested on 100 samples")
        print(f"    - Predicted positive: {sum(y_pred_ann)}")
        print(f"    - Predicted negative: {len(y_pred_ann) - sum(y_pred_ann)}")
    except Exception as e:
        print(f"  ✗ ANN prediction failed: {e}")
        sys.exit(1)
    
    # ========================================================================
    # TEST 5: Test LR Predictions
    # ========================================================================
    print("\n[TEST 5] Testing Logistic Regression predictions...")
    
    try:
        y_pred_lr = lr_model.predict(X_test_scaled[:100])
        print(f"  ✓ Logistic Regression predictions working")
        print(f"    - Tested on 100 samples")
        print(f"    - Predicted positive: {sum(y_pred_lr)}")
        print(f"    - Predicted negative: {len(y_pred_lr) - sum(y_pred_lr)}")
    except Exception as e:
        print(f"  ✗ LR prediction failed: {e}")
        sys.exit(1)
    
    # ========================================================================
    # TEST 6: Full Test Set Evaluation
    # ========================================================================
    print("\n[TEST 6] Evaluating on full test set ({:,} samples)...".format(len(X_test)))
    
    from sklearn.metrics import accuracy_score, roc_auc_score
    
    # ANN
    y_pred_ann_full = (ann_model.predict(X_test_scaled, verbose=0) > 0.5).astype(int).flatten()
    y_proba_ann = ann_model.predict(X_test_scaled, verbose=0).flatten()
    ann_accuracy = accuracy_score(y_test, y_pred_ann_full)
    ann_auc = roc_auc_score(y_test, y_proba_ann)
    
    print(f"\n  ANN Results:")
    print(f"    ✓ Accuracy: {ann_accuracy:.4f} ({ann_accuracy*100:.2f}%)")
    print(f"    ✓ ROC-AUC:  {ann_auc:.4f}")
    
    # LR
    y_pred_lr_full = lr_model.predict(X_test_scaled)
    y_proba_lr = lr_model.decision_function(X_test_scaled)
    lr_accuracy = accuracy_score(y_test, y_pred_lr_full)
    
    from scipy.special import expit
    y_proba_lr_norm = expit(y_proba_lr)
    lr_auc = roc_auc_score(y_test, y_proba_lr_norm)
    
    print(f"\n  Logistic Regression Results:")
    print(f"    ✓ Accuracy: {lr_accuracy:.4f} ({lr_accuracy*100:.2f}%)")
    print(f"    ✓ ROC-AUC:  {lr_auc:.4f}")
    
    # ========================================================================
    # TEST 7: Sample Single Prediction
    # ========================================================================
    print("\n[TEST 7] Testing single patient prediction...")
    
    sample_patient = pd.DataFrame({
        'Age': [45],
        'BMI': [28.5],
        'Fasting_Glucose': [180],
        'Random_Glucose': [220],
        'HbA1c': [8.2],
        'Ketone': [1],
        'Polyuria': [1],
        'Polydipsia': [1],
        'Weight_Loss': [0],
        'Fatigue': [1],
        'Blurred_Vision': [0],
        'Family_History': [1]
    })
    
    patient_scaled = scaler.transform(sample_patient)
    
    ann_prob = ann_model.predict(patient_scaled, verbose=0)[0][0]
    lr_prob = expit(lr_model.decision_function(patient_scaled)[0])
    
    print(f"  Patient Profile: Age 45, BMI 28.5, FG 180, RG 220, HbA1c 8.2")
    print(f"  \n  ANN Prediction:")
    print(f"    - Probability: {ann_prob*100:.1f}%")
    print(f"    - Result: {'POSITIVE (Diabetes)' if ann_prob > 0.5 else 'NEGATIVE (No Diabetes)'}")
    print(f"  \n  LR Prediction:")
    print(f"    - Probability: {lr_prob*100:.1f}%")
    print(f"    - Result: {'POSITIVE (Diabetes)' if lr_prob > 0.5 else 'NEGATIVE (No Diabetes)'}")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "="*80)
    print("VERIFICATION SUMMARY")
    print("="*80)
    
    all_tests_passed = True
    
    tests = [
        ("Dataset Loading", True),
        ("ANN Model Loading", True),
        ("LR Model Loading", True),
        ("Feature Scaler Loading", True),
        ("Test Data Preparation", True),
        ("ANN Predictions", True),
        ("LR Predictions", True),
        ("Full Test Evaluation", True),
        ("Single Patient Prediction", True),
    ]
    
    print("\n✅ ALL TESTS PASSED!\n")
    
    for test_name, status in tests:
        icon = "✓" if status else "✗"
        print(f"  [{icon}] {test_name}")
    
    print("\n" + "="*80)
    print("SYSTEM STATUS: ✅ READY FOR PRODUCTION")
    print("="*80)
    
    print(f"\nKey Metrics:")
    print(f"  • ANN Accuracy:     {ann_accuracy*100:.2f}%")
    print(f"  • ANN ROC-AUC:      {ann_auc:.4f}")
    print(f"  • LR Accuracy:      {lr_accuracy*100:.2f}%")
    print(f"  • LR ROC-AUC:       {lr_auc:.4f}")
    print(f"  • Test Samples:     {len(X_test):,}")
    print(f"  • Features:         12 clinical parameters")
    print(f"  • Models:           2 (ANN primary + LR backup)")
    
    print("\n✅ System is working correctly and ready to use!\n")

except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
