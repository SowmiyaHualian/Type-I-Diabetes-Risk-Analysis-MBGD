"""Test script to verify ketone prediction fix."""

from predict import predict_risk

# Test Case: User scenario reported
# - Glucose: 130 (Normal)
# - Ketones: Absent (NOT present)
# - 2 symptoms present (e.g., polyuria, polydipsia)
test_payload = {
    "age": 30,
    "gender": "Male",
    "weightKg": 75,
    "heightCm": 180,
    "randomGlucose": 130,  # Normal glucose
    "hba1c": 5.5,
    "familyHistory": "No",
    "ketonePresence": "Absent",  # KEY FIX: Actual ketone presence from form
    "symptoms.polyuria": "true",  # Symptom 1
    "symptoms.polydipsia": "true",  # Symptom 2
    "symptoms.weightLoss": "false",
    "symptoms.fatigue": "false",
    "symptoms.blurredVision": "false",
    "cPeptideLevel": 0.9,
    "autoantibodyResult": "Negative",
}

print("=" * 70)
print("TEST CASE: Normal Glucose + No Ketones + 2 Symptoms")
print("=" * 70)
print(f"Input Glucose: 130 (Normal)")
print(f"Input Ketones: Absent")
print(f"Symptoms: Polyuria ✓, Polydipsia ✓ (2 present)")
print("-" * 70)

result = predict_risk(test_payload)

print(f"\nRisk Level: {result['risk_level']}")
print(f"Confidence: {result['confidence']:.2%}")
print(f"Glucose Classification: {result['glucose']}")
print(f"Ketones Classification: {result['ketones']}")  # Should be "Normal", NOT "Elevated"
print(f"BMI Classification: {result['bmi']}")
print(f"\nMedical Interpretation:")
print(f"  {result['medical_interpretation']}")

print("\n" + "=" * 70)
print("VERIFICATION:")
print("=" * 70)
if result['glucose'] == 'Normal' and result['ketones'] == 'Normal':
    print("✓ CORRECT: Glucose=Normal, Ketones=Normal (as expected)")
else:
    print(f"✗ INCORRECT: Glucose={result['glucose']}, Ketones={result['ketones']}")

print("=" * 70)

# Test Case 2: Ketones Present
print("\n\nTEST CASE 2: Normal Glucose + PRESENT Ketones + 1 Symptom")
print("=" * 70)

test_payload_2 = {
    "age": 28,
    "gender": "Female",
    "weightKg": 65,
    "heightCm": 165,
    "randomGlucose": 110,  # Normal
    "hba1c": 5.3,
    "familyHistory": "Yes",
    "ketonePresence": "Present",  # Ketones ARE present
    "symptoms.polyuria": "true",
    "symptoms.polydipsia": "false",
    "symptoms.weightLoss": "false",
    "symptoms.fatigue": "false",
    "symptoms.blurredVision": "false",
    "cPeptideLevel": 0.7,
    "autoantibodyResult": "Positive",
}

result_2 = predict_risk(test_payload_2)

print(f"Input Glucose: 110 (Normal)")
print(f"Input Ketones: Present")
print(f"Symptoms: Polyuria ✓ (1 present)")
print("-" * 70)
print(f"\nKetones Classification: {result_2['ketones']}")  # Should be "Elevated"
print(f"Medical Interpretation: {result_2['medical_interpretation']}")

if result_2['ketones'] == 'Elevated':
    print("\n✓ CORRECT: Ketones=Elevated (as expected when Present)")
else:
    print(f"\n✗ INCORRECT: Ketones={result_2['ketones']}")

print("=" * 70)
