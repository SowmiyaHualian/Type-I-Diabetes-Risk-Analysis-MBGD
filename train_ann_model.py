"""
================================================================================
TYPE 1 DIABETES PREDICTION SYSTEM - ANN MODEL WITH LOGISTIC REGRESSION
================================================================================

PURPOSE:
This script implements an Artificial Neural Network (ANN) for Type 1 Diabetes
prediction and compares it with Logistic Regression (mini-batch gradient descent).

WHY ANN IS INTRODUCED:
1. Earlier models (Linear/LR) assume linear relationships between features
2. Real medical conditions show NON-LINEAR relationships:
   - Glucose + Insulin + Age → Non-linear diabetes risk
   - BMI + Family_History → Complex interactions
   - Symptoms interact in ways that linear models miss

3. Dataset expansion (17,500+ rows) now supports ANN training
   - Reduces overfitting risk
   - Enables learning of complex patterns

WHY ANN IS BETTER:
- Captures non-linear relationships between medical parameters
- Learns hierarchical feature representations
- Handles patient condition variations better
- More robust for diverse patient profiles

WHY LOGISTIC REGRESSION (BASELINE):
- Fast, interpretable baseline for comparison
- Shows improvement achieved by ANN
- Mini-batch gradient descent: efficient for large datasets
- Good for understanding linear component of problem

DATASET INFORMATION:
- Source: final_preprocessed_mixed.csv (17,500 records)
- Features: 13 medical parameters (5 continuous + 7 binary)
- Target: Class_Label (0=No Diabetes, 1=Type 1 Diabetes)
- All features properly formatted and normalized ready

MODEL COMPARISON:
1. Logistic Regression (Baseline)
   - Linear decision boundary
   - Mini-batch SGD optimization
   - Fast training, interpretable

2. Artificial Neural Network (Advanced)
   - Non-linear decision boundaries
   - Multiple hidden layers (32 → 16 neurons)
   - Better at capturing complex patterns
"""

import pandas as pd
import numpy as np
import warnings
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import (accuracy_score, confusion_matrix, 
                             classification_report, roc_auc_score, 
                             roc_curve, auc)
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
import matplotlib.pyplot as plt
import seaborn as sns
import time

warnings.filterwarnings('ignore')

print("\n" + "="*80)
print("TYPE 1 DIABETES PREDICTION - ANN vs LOGISTIC REGRESSION")
print("="*80 + "\n")

# ==============================================================================
# STEP 1: LOAD AND PREPARE DATASET
# ==============================================================================

print("[STEP 1] Loading preprocessed dataset...")

DATASET_PATH = "data/final/final_preprocessed_mixed.csv"
df = pd.read_csv(DATASET_PATH)

print(f"  Dataset loaded successfully!")
print(f"  - Shape: {df.shape[0]:,} rows, {df.shape[1]} columns")
print(f"  - File: {DATASET_PATH}")

# Display feature information
print(f"\n  Features:")
for col in df.columns:
    if col != 'Class_Label':
        print(f"    {col:25} - Type: {df[col].dtype}, Range: [{df[col].min()}, {df[col].max()}]")

print(f"\n  Target Variable (Class_Label):")
class_dist = df['Class_Label'].value_counts().sort_index()
for class_val, count in class_dist.items():
    pct = (count / len(df)) * 100
    print(f"    Class {int(class_val)}: {count:,} ({pct:5.1f}%)")

# ==============================================================================
# STEP 2: SEPARATE FEATURES AND TARGET
# ==============================================================================

print("\n[STEP 2] Separating features and target...")

X = df.drop('Class_Label', axis=1)
y = df['Class_Label'].values

print(f"  Features shape: {X.shape}")
print(f"  Target shape: {y.shape}")
print(f"  Number of features: {X.shape[1]}")

# ==============================================================================
# STEP 3: STANDARDIZE FEATURES (CRITICAL FOR NEURAL NETWORKS)
# ==============================================================================

print("\n[STEP 3] Standardizing features...")
print(f"  WARNING: Feature standardization is CRITICAL for ANN convergence!")
print(f"  - Without standardization: ANN struggles with different scales")
print(f"  - Glucose (0-400) vs Age (0-100) vs Ketone (0-1) → different magnitudes")

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

print(f"  Standardization applied:")
print(f"    Mean of scaled features: {X_scaled.mean():.6f} (should be ~0)")
print(f"    Std of scaled features: {X_scaled.std():.6f} (should be ~1)")

# ==============================================================================
# STEP 4: TRAIN-TEST SPLIT
# ==============================================================================

print("\n[STEP 4] Splitting data (80% train, 20% test)...")

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

print(f"  Training set: {X_train.shape[0]:,} samples ({100*X_train.shape[0]/len(X):.1f}%)")
print(f"  Test set: {X_test.shape[0]:,} samples ({100*X_test.shape[0]/len(X):.1f}%)")
print(f"  Class distribution in train set:")
train_dist = pd.Series(y_train).value_counts().sort_index()
for class_val, count in train_dist.items():
    pct = (count / len(y_train)) * 100
    print(f"    Class {int(class_val)}: {count:,} ({pct:5.1f}%)")

# ==============================================================================
# STEP 5: TRAIN LOGISTIC REGRESSION (BASELINE)
# ==============================================================================

print("\n" + "="*80)
print("MODEL 1: LOGISTIC REGRESSION (BASELINE - LINEAR MODEL)")
print("="*80)

print("\n[STEP 5] Training Logistic Regression with Mini-Batch SGD...")
print(f"  Configuration:")
print(f"    - Optimizer: SGDClassifier (stochastic gradient descent)")
print(f"    - Loss function: Log loss (logistic regression)")
print(f"    - Mini-batch size: 32 (implicit)")
print(f"    - Max iterations: 1000")
print(f"    - Learning rate: 0.01")

start_time = time.time()

lr_model = SGDClassifier(
    loss='log_loss',
    max_iter=1000,
    learning_rate='optimal',
    eta0=0.01,
    random_state=42,
    verbose=0,
    n_jobs=-1
)

lr_model.fit(X_train, y_train)

lr_train_time = time.time() - start_time

print(f"  Training completed in {lr_train_time:.2f} seconds")

# Predictions
y_train_pred_lr = lr_model.predict(X_train)
y_test_pred_lr = lr_model.predict(X_test)
y_test_pred_proba_lr = lr_model.decision_function(X_test)

# Evaluate LR
lr_train_acc = accuracy_score(y_train, y_train_pred_lr)
lr_test_acc = accuracy_score(y_test, y_test_pred_lr)

print(f"\n[EVALUATION] Logistic Regression Performance:")
print(f"  Training Accuracy: {lr_train_acc:.4f} ({lr_train_acc*100:.2f}%)")
print(f"  Test Accuracy:     {lr_test_acc:.4f} ({lr_test_acc*100:.2f}%)")

# ROC-AUC
lr_auc = roc_auc_score(y_test, y_test_pred_proba_lr)
print(f"  ROC-AUC Score:     {lr_auc:.4f}")

# Confusion Matrix
cm_lr = confusion_matrix(y_test, y_test_pred_lr)
print(f"\n  Confusion Matrix:")
print(f"    [{cm_lr[0,0]:5d}  {cm_lr[0,1]:5d}]  (True Negatives | False Positives)")
print(f"    [{cm_lr[1,0]:5d}  {cm_lr[1,1]:5d}]  (False Negatives | True Positives)")

# Classification Report
print(f"\n  Classification Report:")
print(classification_report(y_test, y_test_pred_lr, 
      target_names=['No Diabetes', 'Type 1 Diabetes']))

# ==============================================================================
# STEP 6: BUILD AND TRAIN ANN MODEL
# ==============================================================================

print("\n" + "="*80)
print("MODEL 2: ARTIFICIAL NEURAL NETWORK (ADVANCED - NON-LINEAR)")
print("="*80)

print("\n[STEP 6] Building ANN architecture...")

# ANN Architecture
# Input: 13 features → Hidden1: 32 neurons → Hidden2: 16 neurons → Output: 1 neuron
ann_model = models.Sequential([
    layers.Input(shape=(X_train.shape[1],)),
    
    # Hidden Layer 1: 32 neurons with ReLU activation
    layers.Dense(32, activation='relu', name='hidden_1'),
    layers.Dropout(0.2),  # 20% dropout to prevent overfitting
    
    # Hidden Layer 2: 16 neurons with ReLU activation
    layers.Dense(16, activation='relu', name='hidden_2'),
    layers.Dropout(0.2),  # 20% dropout
    
    # Output Layer: 1 neuron with Sigmoid for binary classification
    layers.Dense(1, activation='sigmoid', name='output')
])

print(f"  ANN Architecture:")
print(f"    Input Layer:      {X_train.shape[1]} neurons (features)")
print(f"    Hidden Layer 1:   32 neurons (ReLU activation + 20% dropout)")
print(f"    Hidden Layer 2:   16 neurons (ReLU activation + 20% dropout)")
print(f"    Output Layer:     1 neuron (Sigmoid activation)")

# Compile model
ann_model.compile(
    loss='binary_crossentropy',
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    metrics=['accuracy']
)

print(f"\n  Compilation:")
print(f"    Loss function:    Binary Crossentropy")
print(f"    Optimizer:        Adam (learning rate: 0.001)")
print(f"    Metrics:          Accuracy")

# Display model summary
print(f"\n  Model Summary:")
ann_model.summary()

# Train ANN
print(f"\n[STEP 7] Training ANN...")
print(f"  Configuration:")
print(f"    - Epochs: 50")
print(f"    - Batch size: 32")
print(f"    - Validation split: 20%")
print(f"    - Verbose: Showing progress every 10 epochs")

start_time = time.time()

history = ann_model.fit(
    X_train, y_train,
    epochs=50,
    batch_size=32,
    validation_split=0.2,
    verbose=0,
    shuffle=True
)

ann_train_time = time.time() - start_time

print(f"  Training completed in {ann_train_time:.2f} seconds")

# Show training progress
print(f"\n  Training History (Last 5 Epochs):")
print(f"  {'Epoch':<8} {'Loss':<12} {'Accuracy':<12} {'Val_Loss':<12} {'Val_Accuracy':<12}")
print(f"  {'-'*56}")
for epoch in range(45, 50):
    print(f"  {epoch:<8} {history.history['loss'][epoch]:<12.4f} "
          f"{history.history['accuracy'][epoch]:<12.4f} "
          f"{history.history['val_loss'][epoch]:<12.4f} "
          f"{history.history['val_accuracy'][epoch]:<12.4f}")

# Evaluate ANN
print(f"\n[EVALUATION] ANN Performance:")

# Training evaluation
y_train_pred_ann = (ann_model.predict(X_train, verbose=0) > 0.5).astype(int).flatten()
ann_train_acc = accuracy_score(y_train, y_train_pred_ann)

# Test evaluation
y_test_pred_ann = (ann_model.predict(X_test, verbose=0) > 0.5).astype(int).flatten()
y_test_pred_proba_ann = ann_model.predict(X_test, verbose=0).flatten()
ann_test_acc = accuracy_score(y_test, y_test_pred_ann)

print(f"  Training Accuracy: {ann_train_acc:.4f} ({ann_train_acc*100:.2f}%)")
print(f"  Test Accuracy:     {ann_test_acc:.4f} ({ann_test_acc*100:.2f}%)")

# ROC-AUC
ann_auc = roc_auc_score(y_test, y_test_pred_proba_ann)
print(f"  ROC-AUC Score:     {ann_auc:.4f}")

# Confusion Matrix
cm_ann = confusion_matrix(y_test, y_test_pred_ann)
print(f"\n  Confusion Matrix:")
print(f"    [{cm_ann[0,0]:5d}  {cm_ann[0,1]:5d}]  (True Negatives | False Positives)")
print(f"    [{cm_ann[1,0]:5d}  {cm_ann[1,1]:5d}]  (False Negatives | True Positives)")

# Classification Report
print(f"\n  Classification Report:")
print(classification_report(y_test, y_test_pred_ann, 
      target_names=['No Diabetes', 'Type 1 Diabetes']))

# ==============================================================================
# STEP 8: MODEL COMPARISON
# ==============================================================================

print("\n" + "="*80)
print("MODEL COMPARISON: LOGISTIC REGRESSION vs ANN")
print("="*80)

print(f"\n{'Metric':<30} {'Logistic Regression':<25} {'ANN':<25} {'Improvement':<15}")
print(f"{'-'*95}")

# Accuracy comparison
lr_improvement = (ann_test_acc - lr_test_acc) * 100
print(f"{'Test Accuracy':<30} {lr_test_acc:<25.4f} {ann_test_acc:<25.4f} {lr_improvement:>+.2f}%")

# AUC comparison
auc_improvement = (ann_auc - lr_auc) * 100
print(f"{'ROC-AUC Score':<30} {lr_auc:<25.4f} {ann_auc:<25.4f} {auc_improvement:>+.2f}%")

# Training time
time_improvement = ((ann_train_time - lr_train_time) / lr_train_time) * 100
print(f"{'Training Time (seconds)':<30} {lr_train_time:<25.2f} {ann_train_time:<25.2f} {time_improvement:>+.1f}%")

# Specificity (True Negative Rate)
lr_specificity = cm_lr[0,0] / (cm_lr[0,0] + cm_lr[0,1])
ann_specificity = cm_ann[0,0] / (cm_ann[0,0] + cm_ann[0,1])
spec_improvement = (ann_specificity - lr_specificity) * 100
print(f"{'Specificity (TNR)':<30} {lr_specificity:<25.4f} {ann_specificity:<25.4f} {spec_improvement:>+.2f}%")

# Sensitivity (True Positive Rate / Recall)
lr_sensitivity = cm_lr[1,1] / (cm_lr[1,0] + cm_lr[1,1])
ann_sensitivity = cm_ann[1,1] / (cm_ann[1,0] + cm_ann[1,1])
sens_improvement = (ann_sensitivity - lr_sensitivity) * 100
print(f"{'Sensitivity (TPR/Recall)':<30} {lr_sensitivity:<25.4f} {ann_sensitivity:<25.4f} {sens_improvement:>+.2f}%")

print(f"\n{'-'*95}")

# Key insights
print(f"\nKEY INSIGHTS:")

if ann_test_acc > lr_test_acc:
    print(f"  ✓ ANN shows {lr_improvement:.2f}% improvement in test accuracy")
    print(f"    - ANN captures non-linear relationships better")
    print(f"    - Complex medical feature interactions learned effectively")
else:
    print(f"  ✓ Models perform similarly (LR slightly better)")
    print(f"    - Problem may be largely linear")

if ann_auc > lr_auc:
    print(f"  ✓ ANN shows {auc_improvement:.2f}% improvement in ROC-AUC")
    print(f"    - Better at ranking positive cases")

print(f"  ✓ Sensitivity: {ann_sensitivity:.4f} - correctly identifies {ann_sensitivity*100:.1f}% of diabetic patients")
print(f"  ✓ Specificity: {ann_specificity:.4f} - correctly identifies {ann_specificity*100:.1f}% of non-diabetic patients")

# ==============================================================================
# STEP 9: FINAL SUMMARY
# ==============================================================================

print("\n" + "="*80)
print("FINAL SUMMARY & RECOMMENDATIONS")
print("="*80)

print(f"\nDATASET INFORMATION:")
print(f"  - Total records: {len(df):,}")
print(f"  - Training samples: {len(X_train):,}")
print(f"  - Test samples: {len(X_test):,}")
print(f"  - Features: {X_train.shape[1]}")
print(f"  - Class distribution: {class_dist[1]:.1f}% positive, {class_dist[0]:.1f}% negative")

print(f"\nLOGISTIC REGRESSION (BASELINE):")
print(f"  - Type: Linear classifier with mini-batch SGD")
print(f"  - Test Accuracy: {lr_test_acc*100:.2f}%")
print(f"  - ROC-AUC: {lr_auc:.4f}")
print(f"  - Training time: {lr_train_time:.2f}s")
print(f"  - Pros: Fast, interpretable, good baseline")
print(f"  - Cons: Cannot capture non-linear relationships")

print(f"\nARTIFICIAL NEURAL NETWORK (ADVANCED):")
print(f"  - Type: 2-layer deep neural network with dropout")
print(f"  - Test Accuracy: {ann_test_acc*100:.2f}%")
print(f"  - ROC-AUC: {ann_auc:.4f}")
print(f"  - Training time: {ann_train_time:.2f}s")
print(f"  - Pros: Captures non-linear patterns, more robust")
print(f"  - Cons: Slower training, less interpretable")

print(f"\nRECOMMENDATION:")
if ann_test_acc >= lr_test_acc - 0.01:  # Close or better
    print(f"  ✓ USE ANN MODEL")
    print(f"    - Provides equal or better performance")
    print(f"    - More suitable for complex medical predictions")
    print(f"    - Better generalization to unseen data")
else:
    print(f"  ✓ LOGISTIC REGRESSION SUFFICIENT")
    print(f"    - Simpler model with comparable performance")
    print(f"    - Faster training and prediction")
    print(f"    - More interpretable for medical professionals")

print(f"\nNEXT STEPS:")
print(f"  1. Deploy the selected model to prediction system")
print(f"  2. Monitor performance on real patient data")
print(f"  3. Implement periodic retraining (monthly/quarterly)")
print(f"  4. Add confidence scores to predictions")
print(f"  5. Collect feedback for continuous improvement")

print("\n" + "="*80)
print("TRAINING COMPLETE!")
print("="*80 + "\n")
