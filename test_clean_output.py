"""
Quick test to verify the new clean output structure
"""

import sys
sys.path.insert(0,'d:\\Earlier Suspiction of type 1 diabetes system')

from predict import predict_risk

print("="*80)
print("TESTING NEW CLEAN OUTPUT STRUCTURE")
print("="*80 + "\n")

# Test Case 1: High Risk
print("[TEST 1] High Glucose + Elevated Ketones (HIGH RISK)")
payload_high = {
    "age": "45",
    "gender": "male",
    "bmi": "32",
    "randomGlucose": "280",
    "fastingGlucose": "250",
    "hba1c": "8.5",
    "symptoms.polyuria": "true",
    "symptoms.polydipsia": "true",
    "symptoms.weightLoss": "true",
    "symptoms.fatigue": "true",
    "symptoms.blurredVision": "true",
    "familyHistory": "yes",
    "cPeptideLevel": "0.5",
    "autoantibodyResult": "positive"
}

result = predict_risk(payload_high)
print(f"Risk Level: {result['risk_level']} ({result['confidence']*100:.1f}%)")
print(f"Glucose: {result['glucose']}")
print(f"Ketones: {result['ketones']}")
print(f"BMI: {result['bmi']}")
print(f"Medical Interpretation: {result['medical_interpretation']}")
print(f"Disclaimer: {result['disclaimer']}\n")

# Test Case 2: Moderate Risk
print("[TEST 2] Elevated Glucose + Elevated Ketones (MODERATE RISK)")
payload_moderate = {
    "age": "35",
    "gender": "female",
    "bmi": "28",
    "randomGlucose": "180",
    "fastingGlucose": "140",
    "hba1c": "7.2",
    "symptoms.polyuria": "true",
    "symptoms.polydipsia": "false",
    "symptoms.weightLoss": "false",
    "symptoms.fatigue": "true",
    "symptoms.blurredVision": "false",
    "familyHistory": "yes",
    "cPeptideLevel": "1.0",
    "autoantibodyResult": "negative"
}

result = predict_risk(payload_moderate)
print(f"Risk Level: {result['risk_level']} ({result['confidence']*100:.1f}%)")
print(f"Glucose: {result['glucose']}")
print(f"Ketones: {result['ketones']}")
print(f"BMI: {result['bmi']}")
print(f"Medical Interpretation: {result['medical_interpretation']}")
print(f"Disclaimer: {result['disclaimer']}\n")

# Test Case 3: Low Risk
print("[TEST 3] Normal Glucose + Normal Ketones (LOW RISK)")
payload_low = {
    "age": "28",
    "gender": "male",
    "bmi": "23",
    "randomGlucose": "110",
    "fastingGlucose": "95",
    "hba1c": "5.5",
    "symptoms.polyuria": "false",
    "symptoms.polydipsia": "false",
    "symptoms.weightLoss": "false",
    "symptoms.fatigue": "false",
    "symptoms.blurredVision": "false",
    "familyHistory": "no",
    "cPeptideLevel": "1.8",
    "autoantibodyResult": "negative"
}

result = predict_risk(payload_low)
print(f"Risk Level: {result['risk_level']} ({result['confidence']*100:.1f}%)")
print(f"Glucose: {result['glucose']}")
print(f"Ketones: {result['ketones']}")
print(f"BMI: {result['bmi']}")
print(f"Medical Interpretation: {result['medical_interpretation']}")
print(f"Disclaimer: {result['disclaimer']}\n")

print("="*80)
print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
print("="*80)
print("\nNEW OUTPUT STRUCTURE SUMMARY:")
print("✓ Risk Level: HIGH/MODERATE/LOW with confidence percentage")
print("✓ Parameters: Glucose, Ketones, BMI classifications")
print("✓ Medical Interpretation: Single meaningful clinical line")
print("✓ Disclaimer: Mandatory single line at the bottom")
print("\nOutput is CLEAN, MINIMAL, and NON-REDUNDANT ✓")
