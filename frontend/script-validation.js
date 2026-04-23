/**
 * ENHANCED VALIDATION AND PREDICTION SYSTEM
 * Real-time input validation with visual feedback
 * Improved UX with loading indicators and detailed results
 */

// ============================================
// VALIDATION RULES AND RANGES
// ============================================

const VALIDATION_RULES = {
  patientId: {
    required: true,
    pattern: /.{1,}/,
    message: 'Patient ID is required',
    warningMessage: null,
  },
  name: {
    required: true,
    pattern: /.{1,}/,
    message: 'Patient name is required',
    warningMessage: null,
  },
  gender: {
    required: true,
    valid: ['Male', 'Female', 'Other'],
    message: 'Gender is required',
    warningMessage: null,
  },
  age: {
    required: true,
    min: 1,
    max: 120,
    message: 'Age is required (1-120 years)',
    warningMin: 10,
    warningMessage: 'Very young age detected - ensure data accuracy',
  },
  bmi: {
    required: true,
    min: 10,
    max: 60,
    message: 'BMI is required (10-60 kg/m²)',
    warningMin: 18.5,
    warningMax: 30,
    warningMessage: 'BMI outside normal range (18.5-25)',
  },
  glucose: {
    required: true,
    min: 50,
    max: 400,
    message: 'Glucose is required (50-400 mg/dL)',
    warningMin: 100,
    warningMax: 126,
    warningMessage: 'Glucose level elevated',
  },
  hba1c: {
    required: true,
    min: 3,
    max: 14,
    message: 'HbA1c is required (3-14%)',
    warningMin: 5.7,
    warningMax: 6.5,
    warningMessage: 'HbA1c indicates prediabetes range',
  },
  insulin: {
    required: false,
    min: 0,
    max: 1000,
    message: 'Insulin must be non-negative',
    warningMin: 5,
    warningMax: 25,
    warningMessage: 'Insulin level outside typical fasting range',
  },
  cPeptide: {
    required: false,
    min: 0,
    max: 10,
    message: 'C-Peptide must be in range 0-10 ng/mL',
    warningMin: 0.8,
    warningMax: 3.1,
    warningMessage: 'C-Peptide outside normal range',
  },
  familyHistory: {
    required: true,
    valid: ['Yes', 'No'],
    message: 'Family history selection is required',
  },
  autoantibody: {
    required: true,
    valid: ['Positive', 'Negative'],
    message: 'Autoantibody status is required',
  },
};

// ============================================
// DOM ELEMENT HELPERS
// ============================================

const byId = (id) => document.getElementById(id);

const setText = (id, value) => {
  const el = byId(id);
  if (el) el.textContent = value;
};

const addClass = (id, className) => {
  const el = byId(id);
  if (el) el.classList.add(className);
};

const removeClass = (id, className) => {
  const el = byId(id);
  if (el) el.classList.remove(className);
};

const hide = (id) => {
  const el = byId(id);
  if (el) el.classList.add('hidden');
};

const show = (id) => {
  const el = byId(id);
  if (el) el.classList.remove('hidden');
};

// ============================================
// VALIDATION FUNCTIONS
// ============================================

const validateField = (fieldId) => {
  const element = byId(fieldId);
  if (!element) return { valid: true, warnings: [] };

  const value = element.value.trim();
  const rules = VALIDATION_RULES[fieldId];
  const errorEl = byId(`${fieldId}-error`);

  if (!rules) return { valid: true, warnings: [] };

  let errors = [];
  let warnings = [];

  // Check required
  if (rules.required && !value) {
    errors.push(rules.message);
  }

  // Check pattern
  if (value && rules.pattern && !rules.pattern.test(value)) {
    errors.push(rules.message);
  }

  // Check valid options
  if (value && rules.valid && !rules.valid.includes(value)) {
    errors.push(rules.message);
  }

  // Check numeric ranges
  if (value && (rules.min !== undefined || rules.max !== undefined)) {
    const numValue = parseFloat(value);
    if (rules.min !== undefined && numValue < rules.min) {
      errors.push(rules.message);
    }
    if (rules.max !== undefined && numValue > rules.max) {
      errors.push(rules.message);
    }

    // Check warnings
    if (rules.warningMin !== undefined && numValue < rules.warningMin) {
      warnings.push(rules.warningMessage || `Value below recommended (${rules.warningMin})`);
    }
    if (rules.warningMax !== undefined && numValue > rules.warningMax) {
      warnings.push(rules.warningMessage || `Value above recommended (${rules.warningMax})`);
    }
  }

  // Update error display
  if (errorEl) {
    errorEl.textContent = errors.length > 0 ? errors[0] : '';
  }

  // Update input styling
  if (errors.length > 0) {
    addClass(fieldId, 'is-invalid');
    removeClass(fieldId, 'is-valid');
    removeClass(fieldId, 'is-warning');
  } else if (warnings.length > 0 && value) {
    addClass(fieldId, 'is-warning');
    removeClass(fieldId, 'is-invalid');
    removeClass(fieldId, 'is-valid');
  } else if (value) {
    addClass(fieldId, 'is-valid');
    removeClass(fieldId, 'is-invalid');
    removeClass(fieldId, 'is-warning');
  } else {
    removeClass(fieldId, 'is-invalid');
    removeClass(fieldId, 'is-valid');
    removeClass(fieldId, 'is-warning');
  }

  return {
    valid: errors.length === 0,
    warnings: warnings,
    errors: errors,
  };
};

const validateForm = () => {
  const fieldIds = Object.keys(VALIDATION_RULES);
  let allValid = true;
  let allErrors = [];

  for (const fieldId of fieldIds) {
    const result = validateField(fieldId);
    if (!result.valid) {
      allValid = false;
      allErrors.push(result.errors[0]);
    }
  }

  // Show/hide validation alert
  const alertEl = byId('validation-alert');
  const errorListEl = byId('error-list');

  if (!allValid) {
    show('validation-alert');
    errorListEl.innerHTML = allErrors
      .map((err) => `<li>${err}</li>`)
      .join('');
  } else {
    hide('validation-alert');
  }

  return allValid;
};

// ============================================
// UTILITY FUNCTIONS
// ============================================

const formatPercent = (value) => {
  if (typeof value !== 'number') return '—';
  return `${(value * 100).toFixed(1)}%`;
};

const readNumber = (value, fallback = 0) => {
  const parsed = parseFloat(value);
  return Number.isFinite(parsed) ? parsed : fallback;
};

const getRiskStyling = (riskLevel) => {
  const levelMap = {
    'No Risk': {
      emoji: '✅',
      class: 'risk-no-risk',
      description: 'Low likelihood of Type 1 Diabetes based on current metrics.',
    },
    'Moderate': {
      emoji: '⚠️',
      class: 'risk-moderate',
      description: 'Moderate likelihood of Type 1 Diabetes. Medical evaluation recommended.',
    },
    'High': {
      emoji: '⛔',
      class: 'risk-high',
      description: 'High likelihood of Type 1 Diabetes. Urgent medical consultation recommended.',
    },
  };

  return levelMap[riskLevel] || levelMap['Moderate'];
};

// ============================================
// RESULT DISPLAY FUNCTIONS
// ============================================

const displayResults = (result) => {
  hide('loading-indicator');
  show('result-cards');

  const styling = getRiskStyling(result.risk_level);

  // Update risk card
  const riskCard = byId('risk-card');
  riskCard.className = `p-6 rounded-xl border-2 transition-all ${styling.class}`;

  setText('result-risk-level', result.risk_level);
  setText('result-risk-description', styling.description);

  const iconEl = byId('risk-icon');
  iconEl.textContent = styling.emoji;

  // Update metrics
  setText('result-confidence', formatPercent(result.probability));
  setText('result-glucose-class', result.glucose_class || '—');
  setText('result-bmi-class', result.bmi_class || '—');
  setText('result-model', result.used_model ? 'ANN' : 'Fallback');

  // Update recommendation
  setText('result-recommendation', result.recommendation || 'Consult a healthcare provider.');

  // Update interpretation
  const interpretation = result.medical_interpretation
    || `Risk level: ${result.risk_level}. Your current metrics suggest a ${result.risk_level.toLowerCase()} risk status.`;
  setText('result-interpretation', interpretation);

  // Handle abnormal parameters
  const abnormalCard = byId('abnormal-card');
  const abnormalList = byId('abnormal-list');

  if (result.abnormal_params && result.abnormal_params.length > 0) {
    show('abnormal-card');
    abnormalList.innerHTML = result.abnormal_params
      .map((param) => `<li>${param}</li>`)
      .join('');
  } else {
    hide('abnormal-card');
  }

  // Scroll to results
  setTimeout(() => {
    byId('result-cards')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, 300);
};

// ============================================
// FORM SUBMISSION
// ============================================

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

  if (!validateForm()) {
    setText('status', '❌ Please fix the errors above and try again.');
    return;
  }

  hide('result-cards');
  show('loading-indicator');
  setText('status', '');

  const submitBtn = byId('submit-btn');
  const originalHTML = submitBtn.innerHTML;
  submitBtn.disabled = true;

  try {
    const payload = collectPayload();
    const response = await fetch('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `Server error: ${response.status}`);
    }

    const result = await response.json();
    displayResults(result);
    setText('status', '✅ Risk assessment completed successfully.');
  } catch (error) {
    console.error('Prediction error:', error);
    hide('result-cards');
    hide('loading-indicator');
    setText('status', `❌ ${error.message || 'Failed to get prediction. Please try again.'}`);
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = originalHTML;
  }
};

// ============================================
// INITIALIZATION
// ============================================

const addValidationListeners = () => {
  const fieldIds = Object.keys(VALIDATION_RULES);

  for (const fieldId of fieldIds) {
    const element = byId(fieldId);
    if (!element) continue;

    element.addEventListener('blur', () => validateField(fieldId));

    if (element.tagName === 'SELECT') {
      element.addEventListener('change', () => validateField(fieldId));
    }

    if (element.tagName === 'INPUT') {
      let timeout;
      element.addEventListener('input', () => {
        clearTimeout(timeout);
        timeout = setTimeout(() => validateField(fieldId), 300);
      });
    }
  }

  const form = byId('predict-form');
  const submitBtn = byId('submit-btn');

  const updateSubmitButtonState = () => {
    submitBtn.disabled = !validateForm();
  };

  if (form) {
    form.addEventListener('input', updateSubmitButtonState);
    form.addEventListener('change', updateSubmitButtonState);
    updateSubmitButtonState();
  }
};

const init = () => {
  const form = byId('predict-form');
  if (form) {
    form.addEventListener('submit', handleSubmit);
    addValidationListeners();
  }
};

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
