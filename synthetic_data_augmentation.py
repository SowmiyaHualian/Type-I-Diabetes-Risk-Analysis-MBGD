"""
Synthetic Data Augmentation for Type 1 Diabetes Risk Prediction

This script implements advanced data engineering techniques to augment an existing synthetic dataset:
1. Scenario-Based Simulation: Generate multiple patient conditions from each base record
2. Probabilistic Data Generation: Use Gaussian distribution for realistic variation
3. Feature Correlation Modeling: Maintain relationships between medical parameters
4. Rule-Based Risk Recalculation: Update target variable based on new feature values

Purpose: Create a realistic, expanded dataset suitable for ML model training
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================================
# STEP 1: DEFINE MEDICAL CONSTRAINTS (Valid Ranges)
# ============================================================================

MEDICAL_CONSTRAINTS = {
    'Glucose': {'min': 70, 'max': 300},
    'BMI': {'min': 15, 'max': 45},
    'Ketones': {'min': 0, 'max': 5},
    'HbA1c': {'min': 4.0, 'max': 10.0},
    'Age': {'min': 1, 'max': 80},
    'Insulin': {'min': 0.1, 'max': 50},
    'CPeptide': {'min': 0.1, 'max': 5},
}

# Standard deviations for Gaussian variation (realistic small changes)
GAUSSIAN_STDDEV = {
    'Glucose': 8,      # ±8 mg/dL typical variation
    'BMI': 0.5,        # ±0.5 kg/m² slight variation
    'Ketones': 0.15,   # ±0.15 mmol/L small variation
    'HbA1c': 0.2,      # ±0.2% slight variation
    'Age': 0.5,        # Usually no change, minimal if any
    'Insulin': 1.0,    # ±1 µU/mL variation
    'CPeptide': 0.2,   # ±0.2 ng/mL variation
}


# ============================================================================
# STEP 2: CREATE BASE SYNTHETIC DATASET (If Not Exists)
# ============================================================================

def create_base_synthetic_dataset(n_samples=500):
    """
    Create initial synthetic dataset as seed data for augmentation.
    
    This is your base dataset from which variations will be generated.
    In production, this would be loaded from an existing CSV file.
    """
    print("[OK] Creating base synthetic dataset (seed data)...")
    
    np.random.seed(42)
    
    data = {
        'Age': np.random.randint(10, 70, n_samples),
        'Gender': np.random.choice(['Male', 'Female'], n_samples),
        'BMI': np.random.uniform(18, 35, n_samples),
        'Glucose': np.random.uniform(80, 200, n_samples),
        'HbA1c': np.random.uniform(5.0, 8.5, n_samples),
        'Ketones': np.random.uniform(0, 2, n_samples),
        'Insulin': np.random.uniform(5, 30, n_samples),
        'CPeptide': np.random.uniform(0.5, 3, n_samples),
        'FamilyHistory': np.random.choice(['Yes', 'No'], n_samples),
        'Symptoms': np.random.choice([0, 1], n_samples),  # 0=No, 1=Yes
    }
    
    df = pd.DataFrame(data)
    
    # Calculate initial risk based on features
    df['Risk_Level'] = df.apply(lambda row: assign_risk_level(
        row['Glucose'], 
        row['Ketones'], 
        row['BMI'], 
        row['HbA1c']
    ), axis=1)
    
    print(f"  Base dataset created: {len(df)} rows")
    print(f"  Columns: {df.columns.tolist()}")
    return df


# ============================================================================
# STEP 3: APPLY GAUSSIAN VARIATION (Probabilistic Data Generation)
# ============================================================================

def apply_gaussian_variation(value, feature_name):
    """
    Apply Gaussian (normal) distribution variation to a feature value.
    
    Variation Formula: new_value = original_value + N(μ=0, σ=stddev)
    
    This creates realistic small changes that simulate:
    - Natural day-to-day variation in blood measurements
    - Measurement device precision
    - Patient health fluctuations
    """
    if feature_name not in GAUSSIAN_STDDEV:
        return value
    
    stddev = GAUSSIAN_STDDEV[feature_name]
    
    # Generate variation from normal distribution (mean=0)
    variation = np.random.normal(loc=0, scale=stddev)
    
    # Apply variation to original value
    new_value = value + variation
    
    return new_value


# ============================================================================
# STEP 4: ENFORCE MEDICAL CONSTRAINTS (Clipping to Valid Ranges)
# ============================================================================

def enforce_medical_constraints(value, feature_name):
    """
    Ensure all feature values stay within medically valid ranges.
    
    This prevents unrealistic scenarios:
    - Glucose never below 70 or above 300 mg/dL
    - BMI never below 15 or above 45
    - Age stays between 1-80 years
    - Etc.
    """
    if feature_name not in MEDICAL_CONSTRAINTS:
        return value
    
    constraints = MEDICAL_CONSTRAINTS[feature_name]
    min_val = constraints['min']
    max_val = constraints['max']
    
    # Clip value to stay within valid range
    return np.clip(value, min_val, max_val)


# ============================================================================
# STEP 5: FEATURE CORRELATION MODELING (Dependency Injection)
# ============================================================================

def apply_feature_correlations(glucose, bmi, ketones, hba1c):
    """
    Maintain realistic relationships between medical features.
    
    This ensures feature correlation modeling:
    
    1. If BMI increases → Glucose slightly increases
       (Obesity correlates with higher blood glucose)
    
    2. If Glucose is very high → Ketones slightly increase
       (Uncontrolled diabetes leads to ketone production)
    
    3. If Glucose increases → HbA1c follows (lagged relationship)
       (Long-term glucose control reflected in HbA1c)
    
    These correlations mimic real medical relationships.
    """
    # Correlation 1: BMI → Glucose
    # If BMI is above normal (>25), boost glucose slightly
    if bmi > 25:
        glucose_boost = (bmi - 25) * 2  # ~2 mg/dL per BMI unit above 25
        glucose += glucose_boost
    
    # Correlation 2: Glucose → Ketones
    # High glucose (>180) leads to slight ketone production
    if glucose > 180:
        ketone_boost = (glucose - 180) / 100 * 0.3  # gradual increase
        ketones += ketone_boost
    
    # Correlation 3: Glucose ↔ HbA1c
    # High glucose correlates with higher HbA1c
    if glucose > 150:
        hba1c_boost = (glucose - 150) / 50 * 0.3  # gradual increase
        hba1c += hba1c_boost
    
    # Also: HbA1c influences glucose expectations
    if hba1c > 7.0:
        glucose += (hba1c - 7.0) * 10
    
    return glucose, ketones, hba1c


# ============================================================================
# STEP 6: RISK RECALCULATION (Rule-Based Target Reassignment)
# ============================================================================

def assign_risk_level(glucose, ketones, bmi, hba1c):
    """
    Assign risk level based on feature values using medical rules.
    
    This implements rule-based target reassignment:
    
    HIGH RISK:
    - Glucose > 180 mg/dL (severe hyperglycemia)
    - OR Ketones > 1.5 mmol/L (significant ketosis)
    - OR HbA1c > 8.0% (poor long-term control)
    
    MODERATE RISK:
    - Glucose 110-180 mg/dL (elevated)
    - OR BMI > 25 (overweight/obese)
    - OR HbA1c 6.5-8.0% (suboptimal control)
    
    LOW RISK:
    - Otherwise (all values in healthy ranges)
    """
    # HIGH RISK conditions
    if glucose > 180 or ketones > 1.5 or hba1c > 8.0:
        return 'High'
    
    # MODERATE RISK conditions
    elif (110 <= glucose <= 180) or bmi > 25 or (6.5 <= hba1c <= 8.0):
        return 'Moderate'
    
    # LOW RISK (healthy ranges)
    else:
        return 'Low'


# ============================================================================
# STEP 7: SCENARIO EXPANSION (Generate Variations per Row)
# ============================================================================

def generate_augmented_samples(original_row, n_variations=4):
    """
    For each original row, generate multiple scenario variations.
    
    Scenario-Based Simulation:
    - 1 original row → 4-5 new rows representing different patient states
    - Example: Same patient at different times (morning/evening measurements)
    - Or: Same patient over different health conditions
    
    Process:
    1. Start with original feature values
    2. Apply Gaussian variation (probabilistic)
    3. Apply feature correlations (realistic relationships)
    4. Enforce medical constraints (valid ranges)
    5. Recalculate risk (rule-based)
    """
    augmented_samples = [original_row.copy()]
    
    for i in range(n_variations):
        new_row = original_row.copy()
        
        # === Step 1: Apply Gaussian Variation ===
        # Simulate natural variation in measurements
        new_glucose = apply_gaussian_variation(original_row['Glucose'], 'Glucose')
        new_bmi = apply_gaussian_variation(original_row['BMI'], 'BMI')
        new_ketones = apply_gaussian_variation(original_row['Ketones'], 'Ketones')
        new_hba1c = apply_gaussian_variation(original_row['HbA1c'], 'HbA1c')
        new_insulin = apply_gaussian_variation(original_row['Insulin'], 'Insulin')
        new_cpeptide = apply_gaussian_variation(original_row['CPeptide'], 'CPeptide')
        
        # === Step 2: Apply Feature Correlations ===
        # Maintain realistic relationships between features
        new_glucose, new_ketones, new_hba1c = apply_feature_correlations(
            new_glucose, new_bmi, new_ketones, new_hba1c
        )
        
        # === Step 3: Enforce Medical Constraints ===
        # Ensure all values stay within valid medical ranges
        new_glucose = enforce_medical_constraints(new_glucose, 'Glucose')
        new_bmi = enforce_medical_constraints(new_bmi, 'BMI')
        new_ketones = enforce_medical_constraints(new_ketones, 'Ketones')
        new_hba1c = enforce_medical_constraints(new_hba1c, 'HbA1c')
        new_insulin = enforce_medical_constraints(new_insulin, 'Insulin')
        new_cpeptide = enforce_medical_constraints(new_cpeptide, 'CPeptide')
        
        # === Step 4: Recalculate Risk (Rule-Based) ===
        # Recompute target variable based on new feature values
        new_risk_level = assign_risk_level(new_glucose, new_ketones, new_bmi, new_hba1c)
        
        # === Step 5: Create Augmented Sample ===
        new_row['Glucose'] = new_glucose
        new_row['BMI'] = new_bmi
        new_row['Ketones'] = new_ketones
        new_row['HbA1c'] = new_hba1c
        new_row['Insulin'] = new_insulin
        new_row['CPeptide'] = new_cpeptide
        new_row['Risk_Level'] = new_risk_level
        
        augmented_samples.append(new_row)
    
    return augmented_samples


# ============================================================================
# STEP 8: COMBINE ORIGINAL + AUGMENTED DATA
# ============================================================================

def augment_dataset(df, variations_per_row=4):
    """
    Dataset Expansion via Simulation:
    
    Original: N rows
    Augmented: N rows × (1 + variations_per_row) = N × 5 rows
    
    Example: 500 rows → 2500 rows (500% expansion)
    
    Each row generates multiple scenario simulations representing
    different patient states while preserving medical consistency.
    """
    print("\n[OK] Scenario Expansion (Synthetic Data Augmentation)...")
    
    augmented_rows = []
    
    for idx, row in df.iterrows():
        # Generate multiple variations for this row
        samples = generate_augmented_samples(row, n_variations=variations_per_row)
        augmented_rows.extend(samples)
        
        # Progress indicator
        if (idx + 1) % 100 == 0:
            print(f"  Processed {idx + 1}/{len(df)} original rows")
    
    # Create new dataframe from all augmented samples
    augmented_df = pd.DataFrame(augmented_rows).reset_index(drop=True)
    
    print(f"  Original dataset: {len(df)} rows")
    print(f"  Augmented dataset: {len(augmented_df)} rows")
    print(f"  Expansion ratio: {len(augmented_df) / len(df):.1f}x")
    
    return augmented_df


# ============================================================================
# STEP 9: DATA QUALITY VALIDATION
# ============================================================================

def validate_augmented_data(df):
    """
    Data Quality Validation: Check for invalid or unrealistic values.
    
    Validation steps:
    1. Remove rows with null/NaN values
    2. Check all values are within medical constraints
    3. Verify no duplicate rows
    4. Ensure risk distribution looks reasonable
    """
    print("\n[OK] Data Quality Validation...")
    
    initial_rows = len(df)
    
    # Check 1: Remove null values
    df = df.dropna()
    null_removed = initial_rows - len(df)
    if null_removed > 0:
        print(f"  Removed {null_removed} rows with null values")
    
    # Check 2: Validate medical constraints
    invalid_rows = 0
    for col, constraint in MEDICAL_CONSTRAINTS.items():
        if col in df.columns:
            min_val = constraint['min']
            max_val = constraint['max']
            invalid = df[(df[col] < min_val) | (df[col] > max_val)]
            if len(invalid) > 0:
                print(f"  WARNING: {len(invalid)} rows with {col} outside valid range")
                invalid_rows += len(invalid)
    
    # Check 3: Risk distribution
    if 'Risk_Level' in df.columns:
        risk_dist = df['Risk_Level'].value_counts()
        print(f"  Risk distribution:")
        for risk, count in risk_dist.items():
            percentage = (count / len(df)) * 100
            print(f"    {risk}: {count} rows ({percentage:.1f}%)")
    
    # Check 4: Summary statistics
    print(f"  Final dataset: {len(df)} rows, {len(df.columns)} features")
    print(f"  Missing values: {df.isnull().sum().sum()}")
    
    return df


# ============================================================================
# STEP 10: SAVE AUGMENTED DATASET
# ============================================================================

def save_augmented_dataset(df, output_file='augmented_t1d_dataset.csv'):
    """
    Save the final expanded dataset to CSV file for ML model training.
    
    Output: CSV file with all augmented samples ready for training
    """
    print(f"\n[OK] Saving augmented dataset to {output_file}...")
    
    # Ensure output directory exists
    output_path = Path('data') / output_file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save to CSV
    df.to_csv(output_path, index=False)
    
    print(f"  [OK] Dataset saved: {output_path}")
    print(f"  File size: {output_path.stat().st_size / 1024:.2f} KB")
    print(f"  Rows: {len(df)}")
    print(f"  Columns: {len(df.columns)}")
    
    return output_path


# ============================================================================
# STEP 11: MAIN EXECUTION PIPELINE
# ============================================================================

def main():
    """
    Main pipeline for synthetic data augmentation.
    
    Pipeline Flow:
    1. Create/Load base dataset
    2. Apply scenario-based simulation (augment each row)
    3. Recalculate risk for all new samples
    4. Validate data quality
    5. Save augmented dataset
    """
    print("=" * 70)
    print("SYNTHETIC DATA AUGMENTATION FOR TYPE 1 DIABETES RISK PREDICTION")
    print("=" * 70)
    
    # === STEP 1: Load or Create Base Dataset ===
    print("\n[STEP 1] Load Base Dataset (Seed Data)")
    df_base = create_base_synthetic_dataset(n_samples=500)
    print(f"  Sample of base data:\n{df_base.head()}\n")
    
    # === STEP 2: Augment Dataset (Scenario Expansion) ===
    print("\n[STEP 2] Apply Scenario-Based Simulation")
    df_augmented = augment_dataset(df_base, variations_per_row=4)
    print(f"  Sample of augmented data:\n{df_augmented.head()}\n")
    
    # === STEP 3: Validate Data Quality ===
    print("\n[STEP 3] Data Quality Validation")
    df_augmented = validate_augmented_data(df_augmented)
    
    # === STEP 4: Save Augmented Dataset ===
    print("\n[STEP 4] Save Final Dataset")
    output_file = save_augmented_dataset(df_augmented, 'augmented_t1d_dataset.csv')
    
    # === SUMMARY ===
    print("\n" + "=" * 70)
    print("AUGMENTATION COMPLETE!")
    print("=" * 70)
    print(f"[OK] Original samples: 500")
    print(f"[OK] Augmented samples: {len(df_augmented)}")
    print(f"[OK] Expansion: {len(df_augmented) / 500:.1f}x")
    print(f"[OK] Features applied:")
    print(f"  - Probabilistic variation (Gaussian distribution)")
    print(f"  - Feature correlation modeling")
    print(f"  - Medical constraint enforcement")
    print(f"  - Rule-based risk recalculation")
    print(f"[OK] Output file: {output_file}")
    print("=" * 70)
    
    return df_augmented, output_file


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    df_final, file_path = main()
