"""Test script to predict Type 1 Diabetes suspicion from sample inputs."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from predict import predict_risk


def test_case_1():
    """Test Case 1: High Risk (classic T1D indicators)"""
    print("\n" + "="*70)
    print("TEST CASE 1: High Risk Scenario")
    print("="*70)
    
    payload = {
        "age": 25,
        "gender": "Male",
        "weightKg": 65,
        "heightCm": 175,
        "bmi": 21.2,
        "fastingGlucose": 180,
        "randomGlucose": 250,
        "hba1c": 8.5,
        "familyHistory": "Yes",
        "symptoms.polyuria": "true",
        "symptoms.polydipsia": "true",
        "symptoms.weightLoss": "true",
        "symptoms.fatigue": "true",
        "symptoms.blurredVision": "false",
        "cPeptideLevel": 0.5,
        "autoantibodyResult": "Positive",
    }
    
    result = predict_risk(payload)
    
    print(f"Input Parameters:")
    print(f"  Age: 25 years | Gender: Male | BMI: 21.2")
    print(f"  Blood Glucose (Fasting): 180 mg/dL | Blood Glucose (Random): 250 mg/dL")
    print(f"  HbA1c: 8.5% | Family History: Yes")
    print(f"  Symptoms: Frequent urination, Excessive thirst, Weight loss, Fatigue")
    print(f"  Advanced Tests: C-Peptide 0.5 ng/mL, Autoantibody: Positive")
    print()
    print(f"PREDICTION OUTPUT:")
    print(f"  Risk Level: {result['risk_level']}")
    print(f"  Probability: {result['probability']:.4f} ({result['probability']*100:.2f}%)")
    print(f"  Recommendation: {result['recommendation']}")
    print(f"  Model Used: {'Trained Model' if result['used_model'] else 'Heuristic Fallback'}")


def test_case_2():
    """Test Case 2: Medium Risk (some indicators)"""
    print("\n" + "="*70)
    print("TEST CASE 2: Medium Risk Scenario")
    print("="*70)
    
    payload = {
        "age": 35,
        "gender": "Female",
        "weightKg": 72,
        "heightCm": 165,
        "bmi": 26.4,
        "fastingGlucose": 120,
        "randomGlucose": 160,
        "hba1c": 6.2,
        "familyHistory": "No",
        "symptoms.polyuria": "true",
        "symptoms.polydipsia": "false",
        "symptoms.weightLoss": "false",
        "symptoms.fatigue": "true",
        "symptoms.blurredVision": "false",
        "cPeptideLevel": 1.2,
        "autoantibodyResult": "Negative",
    }
    
    result = predict_risk(payload)
    
    print(f"Input Parameters:")
    print(f"  Age: 35 years | Gender: Female | BMI: 26.4")
    print(f"  Blood Glucose (Fasting): 120 mg/dL | Blood Glucose (Random): 160 mg/dL")
    print(f"  HbA1c: 6.2% | Family History: No")
    print(f"  Symptoms: Frequent urination, Fatigue")
    print(f"  Advanced Tests: C-Peptide 1.2 ng/mL, Autoantibody: Negative")
    print()
    print(f"PREDICTION OUTPUT:")
    print(f"  Risk Level: {result['risk_level']}")
    print(f"  Probability: {result['probability']:.4f} ({result['probability']*100:.2f}%)")
    print(f"  Recommendation: {result['recommendation']}")
    print(f"  Model Used: {'Trained Model' if result['used_model'] else 'Heuristic Fallback'}")


def test_case_3():
    """Test Case 3: Low Risk (healthy indicators)"""
    print("\n" + "="*70)
    print("TEST CASE 3: Low Risk Scenario")
    print("="*70)
    
    payload = {
        "age": 45,
        "gender": "Male",
        "weightKg": 78,
        "heightCm": 180,
        "bmi": 24.1,
        "fastingGlucose": 95,
        "randomGlucose": 110,
        "hba1c": 5.2,
        "familyHistory": "No",
        "symptoms.polyuria": "false",
        "symptoms.polydipsia": "false",
        "symptoms.weightLoss": "false",
        "symptoms.fatigue": "false",
        "symptoms.blurredVision": "false",
        "cPeptideLevel": 2.5,
        "autoantibodyResult": "Negative",
    }
    
    result = predict_risk(payload)
    
    print(f"Input Parameters:")
    print(f"  Age: 45 years | Gender: Male | BMI: 24.1")
    print(f"  Blood Glucose (Fasting): 95 mg/dL | Blood Glucose (Random): 110 mg/dL")
    print(f"  HbA1c: 5.2% | Family History: No")
    print(f"  Symptoms: None reported")
    print(f"  Advanced Tests: C-Peptide 2.5 ng/mL, Autoantibody: Negative")
    print()
    print(f"PREDICTION OUTPUT:")
    print(f"  Risk Level: {result['risk_level']}")
    print(f"  Probability: {result['probability']:.4f} ({result['probability']*100:.2f}%)")
    print(f"  Recommendation: {result['recommendation']}")
    print(f"  Model Used: {'Trained Model' if result['used_model'] else 'Heuristic Fallback'}")


def test_case_4():
    """Test Case 4: Custom Input (User can modify)"""
    print("\n" + "="*70)
    print("TEST CASE 4: Custom Input Example")
    print("="*70)
    
    payload = {
        "age": 30,
        "gender": "Female",
        "weightKg": 68,
        "heightCm": 168,
        "bmi": 24.1,
        "fastingGlucose": 110,
        "randomGlucose": 145,
        "hba1c": 6.8,
        "familyHistory": "Yes",
        "symptoms.polyuria": "true",
        "symptoms.polydipsia": "true",
        "symptoms.weightLoss": "false",
        "symptoms.fatigue": "true",
        "symptoms.blurredVision": "true",
        "cPeptideLevel": 0.8,
        "autoantibodyResult": "Positive",
    }
    
    result = predict_risk(payload)
    
    print(f"Input Parameters:")
    print(f"  Age: 30 years | Gender: Female | BMI: 24.1")
    print(f"  Blood Glucose (Fasting): 110 mg/dL | Blood Glucose (Random): 145 mg/dL")
    print(f"  HbA1c: 6.8% | Family History: Yes")
    print(f"  Symptoms: Frequent urination, Excessive thirst, Fatigue, Blurred vision")
    print(f"  Advanced Tests: C-Peptide 0.8 ng/mL, Autoantibody: Positive")
    print()
    print(f"PREDICTION OUTPUT:")
    print(f"  Risk Level: {result['risk_level']}")
    print(f"  Probability: {result['probability']:.4f} ({result['probability']*100:.2f}%)")
    print(f"  Recommendation: {result['recommendation']}")
    print(f"  Model Used: {'Trained Model' if result['used_model'] else 'Heuristic Fallback'}")


if __name__ == "__main__":
    print("\n" + "🔬 TYPE 1 DIABETES EARLY RISK PREDICTION SYSTEM - TEST SUITE 🔬".center(70))
    
    test_case_1()
    test_case_2()
    test_case_3()
    test_case_4()
    
    print("\n" + "="*70)
    print("Test suite completed. Model predictions displayed above.")
    print("="*70 + "\n")
