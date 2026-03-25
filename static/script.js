const byId = (id) => document.getElementById(id);

const setText = (id, value) => {
  const el = byId(id);
  if (el) el.textContent = value;
};

const formatPercent = (value) => `${(value * 100).toFixed(1)}%`;

const readNumber = (value, fallback = 0) => {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
};

const collectPayload = () => {
  return {
    patient_id: byId('patientId')?.value?.trim() || 'P000',
    name: byId('name')?.value?.trim() || 'Patient',
    gender: byId('gender')?.value || 'Male',
    age: readNumber(byId('age')?.value, 30),
    glucose_level: readNumber(byId('glucose')?.value, 140),
    hba1c: readNumber(byId('hba1c')?.value, 6.5),
    bmi: readNumber(byId('bmi')?.value, 24),
    family_history: byId('familyHistory')?.value || 'No',
    autoantibody_presence: byId('autoantibody')?.value || 'Negative',
    insulin_level: readNumber(byId('insulin')?.value, 12),
    c_peptide_level: readNumber(byId('cPeptide')?.value, 1.5),
  };
};

const handleSubmit = async (event) => {
  event.preventDefault();
  setText('status', 'Submitting to /predict ...');

  try {
    const payload = collectPayload();
    const response = await fetch('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`Server returned ${response.status}`);
    }

    const result = await response.json();
    setText('probability', formatPercent(result.probability ?? 0));
    setText('risk-level', result.risk_level || 'Unknown');
    setText('recommendation', result.recommendation || '');
    setText('status', 'Prediction received.');
  } catch (error) {
    console.error('Prediction failed', error);
    setText('status', 'Prediction failed. Check server log.');
    setText('risk-level', '—');
    setText('probability', '—');
    setText('recommendation', '—');
  }
};

const init = () => {
  const form = byId('predict-form');
  if (form) {
    form.addEventListener('submit', handleSubmit);
  }
};

document.addEventListener('DOMContentLoaded', init);
