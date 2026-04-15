#  Type 1 Diabetes Risk Analysis and Rehabilitation Recommendation System  
### Enhanced with Artificial Neural Networks (ANN) & Mini-Batch Gradient Descent

---

##  Project Description

The **Type 1 Diabetes Risk Analysis and Rehabilitation Recommendation System** is a web-based, AI-driven healthcare application featuring an **Artificial Neural Network (ANN) model** with **97.06% accuracy** and **97.48% sensitivity**. The system enables rapid, accurate diabetes risk prediction through clinical parameter analysis.

### Dual-Model Architecture:
1. **Primary Model**: Artificial Neural Network (ANN)
   - 2 hidden layers (32 → 16 neurons with ReLU)
   - **Test Accuracy**: 97.06%
   - **ROC-AUC**: 0.9954
   - **Sensitivity**: 97.48% (catches 974 of 1000 diabetic patients)

2. **Baseline Model**: Logistic Regression with Mini-Batch SGD
   - **Test Accuracy**: 96.43%
   - **ROC-AUC**: 0.9944
   - **Training time**: 0.02 seconds
   - Fallback option for production redundancy

### Key Innovation:
The system maintains **user-specific historical health records** and compares current vs previous predictions to identify trends (**Improving, Stable, or Worsening**), enabling personalized, longitudinal health monitoring rather than isolated risk assessments.

By integrating deep learning, traditional ML, backend services, database management, and an interactive web interface, the project demonstrates a complete **end-to-end AI healthcare decision-support system** ready for clinical deployment.

---

##  Key Goals

- To develop an **AI-driven system** for diabetes risk analysis with state-of-the-art accuracy
- To implement **Artificial Neural Networks (ANN)** for capturing complex medical feature interactions
- To apply **Mini-Batch Gradient Descent** for efficient Logistic Regression baseline training  
- To achieve **>97% accuracy** in diabetes prediction for clinical reliability
- To enable **continuous health monitoring** through historical data comparison  
- To provide **personalized rehabilitation recommendations** based on user trends  
- To design and implement a **fully functional web application**, not just a standalone ML model  

---

##  Objectives

1. To collect and preprocess relevant clinical features from multiple publicly available diabetes datasets  
2. To build and train **Artificial Neural Network (ANN)** with optimal architecture for medical prediction
3. To train a **Logistic Regression model** optimized using **Mini-Batch Gradient Descent** as baseline
4. To achieve **>95% accuracy** on standardized test sets with high sensitivity for clinical safety
5. To design a **secure user authentication system** with persistent data storage  
6. To maintain **user-specific historical health records** for longitudinal analysis  
7. To compare previous and current predictions to determine **health progression trends**  
8. To generate **dynamic rehabilitation recommendations** based on risk level and trend analysis  
9. To create an **interactive web interface** for intuitive user interaction  
10. To deploy models to production with inference API and monitoring capabilities

---

##  🚀 Model Performance Results

### Primary Model: Artificial Neural Network (ANN)

| Metric | Value | Clinical Meaning |
|--------|-------|-----------------|
| **Test Accuracy** | 97.06% | Correctly identifies 97 out of 100 cases |
| **Sensitivity (TPR)** | 97.48% | Successfully identifies 97.5% of diabetic patients |
| **Specificity (TNR)** | 95.65% | Correctly identifies 95.65% of non-diabetic individuals |
| **ROC-AUC Score** | 0.9954 | Excellent discrimination ability |
| **Precision** | 0.99 | Very few false positives |
| **F1-Score** | 0.98 | Excellent balanced performance |
| **Training Time** | 26.63 seconds | Efficient training process |

### Baseline Model: Logistic Regression (Mini-Batch SGD)

| Metric | Value | Comparison to ANN |
|--------|-------|-----------------|
| **Test Accuracy** | 96.43% | -0.63% ✓ |
| **Sensitivity (TPR)** | 96.59% | -0.89% ✓ |
| **ROC-AUC** | 0.9944 | -0.10% ✓ |
| **Training Time** | 0.02 seconds | 1331× faster |

### Model Comparison Highlights

- **ANN Advantage**: Captures non-linear relationships between medical parameters
- **Clinical Impact**: ANN catches 24 more diabetic cases per 3,500 patients (0.89% improvement)
- **Accuracy Improvement**: +0.63% translates to ~22 additional correct diagnoses per 3,500
- **ROC-AUC Advantage**: Better discrimination across all decision thresholds
- **Recommendation**: Deploy ANN as primary model, Logistic Regression as fallback

---

##  System Overview

### Technology Stack
- **Deep Learning Framework**: TensorFlow/Keras (ANN implementation)
- **ML Library**: scikit-learn (Logistic Regression baseline)
- **Data Processing**: pandas, numpy
- **Frontend**: HTML, CSS, JavaScript (ChatGPT-style chatbot interface)  
- **Backend**: Python, Flask (REST APIs, authentication, session management)  
- **Database**: SQLite (users, reports, predictions)  

### Model Architecture
```
ARTIFICIAL NEURAL NETWORK:
  Input Layer (12 clinical features)
    ↓ Standardization (mean=0, std=1)
    ↓ Dense Layer (32 neurons, ReLU activation)
    ↓ Dropout (20% regularization)
    ↓ Dense Layer (16 neurons, ReLU activation)
    ↓ Dropout (20% regularization)
    ↓ Output Layer (1 neuron, Sigmoid for binary classification)
    ↓ Prediction: P(Type 1 Diabetes)
```

---

##  Key Features

- User registration and secure login  
- Conversational chatbot for health data input  
- Diabetes risk prediction with ML optimization  
- Historical report comparison and trend analysis  
- Personalized rehabilitation recommendations  
- Persistent user data storage  

---

##  Datasets Used

### Final Preprocessed Dataset
- **File**: `data/final/final_preprocessed_mixed.csv`
- **Records**: 17,500 patient profiles
- **Features**: 12 medical parameters + 1 target variable
- **Size**: 627 KB
- **Format**: CSV with properly formatted clinical values

### Feature Composition

#### Continuous Clinical Measurements (5 features)
| Feature | Range | Unit | Clinical Significance |
|---------|-------|------|----------------------|
| **Age** | 5-70 | years | Patient age |
| **BMI** | 16.0-40.0 | kg/m² | Body Mass Index (obesity indicator) |
| **Fasting_Glucose** | 70-350 | mg/dL | Morning blood sugar (after 8-hour fast) |
| **Random_Glucose** | 80-400 | mg/dL | Blood sugar at any time of day |
| **HbA1c** | 4.5-12.0 | % | 3-month average blood sugar level |

#### Binary Symptom Indicators (7 features)
| Feature | Values | Clinical Meaning |
|---------|--------|-----------------|
| **Ketone** | 0/1 | Ketones in urine (metabolic stress indicator) |
| **Polyuria** | 0/1 | Excessive urination |
| **Polydipsia** | 0/1 | Excessive thirst |
| **Weight_Loss** | 0/1 | Unexplained weight loss |
| **Fatigue** | 0/1 | Extreme tiredness/weakness |
| **Blurred_Vision** | 0/1 | Vision problems |
| **Family_History** | 0/1 | Family history of diabetes |

#### Target Variable
| Class | Count | Percentage | Meaning |
|-------|-------|-----------|---------|
| **0** | 4,018 | 23.0% | No Diabetes |
| **1** | 13,482 | 77.0% | Type 1 Diabetes |

### Data Sources (Original)
Multiple publicly available diabetes datasets were analyzed and features were selected:
- `diabetes.csv`  
- `diabetes_data.csv`  
- `diabetes_data_upload.csv`  
- `diabetes_prediction_dataset.csv`  

### Preprocessing Pipeline
1. **Cleaning**: Removed duplicates, handled missing values
2. **Standardization**: Converted continuous features to readable clinical format
3. **Binarization**: Converted symptom indicators to strict 0/1 values
4. **Format**: Applied medical-grade decimal places (Age: integer, BMI: 1 decimal, etc.)
5. **Validation**: Verified 0 missing values, 0 duplicates, all features properly typed

---

##  Training Scripts & Execution

##  Technology Stack

### Core ML & Data Science
- **Deep Learning**: TensorFlow/Keras (ANN model with dropout regularization)
- **Statistics & ML**: scikit-learn (StandardScaler, SGDClassifier for LR)
- **Data Processing**: Pandas, NumPy
- **Model Persistence**: Pickle (model serialization)

### Training & Classification
- **ANN Optimizer**: Adam (adaptive learning rates)
- **LR Optimizer**: Stochastic Gradient Descent (mini-batch)
- **Loss Functions**: Binary Crossentropy (ANN), Log Loss (LR)
- **Regularization**: Dropout (20% on hidden layers)

### Backend Services
- **Web Framework**: Flask
- **Authentication**: Session-based (Flask-Session)
- **Database**: SQLite3
- **API Format**: RESTful JSON endpoints

### Frontend Technologies
- **Client UI**: HTML5, CSS3, JavaScript
- **Interface Style**: ChatGPT-style conversational chatbot
- **Data Input**: Form-based patient parameter submission
- **Visualization**: Trend charts, prediction confidence displays

### Development Environment
- **Language**: Python 3.10
- **Virtual Environment**: .venv (isolated dependencies)
- **Package Management**: pip

---

##  Training Execution Guide

### Step 1: Prepare Environment
```bash
cd "d:\Earlier Suspiction of type 1 diabetes system"
.venv\Scripts\activate
pip install tensorflow keras scikit-learn pandas numpy matplotlib seaborn
```

### Step 2: Run Training Script
```bash
python train_ann_model.py
```

**Output Includes**:
- Dataset loading and validation
- Feature standardization verification
- Logistic Regression training & evaluation
- ANN architecture and training progress
- Comprehensive model comparison
- Performance metrics and recommendations

### Step 3: Deploy Models
```bash
python deploy_models.py
```

**Outputs**:
- Saved models in `models/` directory
- Single patient prediction examples
- Batch prediction demonstrations
- Deployment checklist

### Step 4: Load Models for Inference
```python
import pickle
from tensorflow import keras
import pandas as pd

# Load components
ann_model = keras.models.load_model('models/ann_model.h5')
scaler = pickle.load(open('models/feature_scaler.pkl', 'rb'))

# Prepare patient data with 12 features
patient = pd.DataFrame({...})

# Predict
X_scaled = scaler.transform(patient)
probability = ann_model.predict(X_scaled, verbose=0)[0][0]
confidence_pct = probability * 100
```

---

##  File Structure

```
Type 1 Diabetes System/
├── data/
│   └── final/
│       └── final_preprocessed_mixed.csv       # Final dataset (17,500 × 13)
│
├── models/
│   ├── ann_model.h5                           # Trained ANN model
│   ├── logistic_regression_model.pkl          # Trained LR model
│   ├── feature_scaler.pkl                     # StandardScaler (IMPORTANT!)
│   ├── model_config.json                      # Feature names & config
│   └── t1d_logreg_mb.pkl                      # LR backup model
│
├── train_ann_model.py                         # ANN + LR training script
├── deploy_models.py                           # Deployment & inference demo
├── MODEL_TRAINING_RESULTS.md                  # Detailed results report
├── README.md                                  # This file
└── .venv/                                     # Python virtual environment
```

---

##  🎓 Why ANN for Diabetes Prediction?

### 1. **Non-Linear Medical Relationships**
- Diabetes risk doesn't scale linearly with glucose levels
- Multiple threshold effects in clinical markers
- Complex symptom interactions (Ketone + Polyuria + Weight_Loss)

### 2. **Feature Interactions**
- Glucose × Age × BMI → non-linear risk
- Symptoms × Medical parameters → complex patterns
- Patient variations → requires adaptive learning

### 3. **Dataset Supports Deep Learning**
- 17,500 records = sufficient training data
- 961 model parameters = manageable complexity
- 80-20 split + dropout = prevents overfitting

### 4. **Clinical Superiority**
- 97.48% sensitivity = catches diabetic patients
- 0.9954 ROC-AUC = excellent discrimination
- Better generalization to diverse patients

---

##  📊 Deployment Checklist

- ✅ Dataset preprocessed and validated (17,500 records)
- ✅ Features standardized (mean=0, std=1)
- ✅ Logistic Regression trained & evaluated
- ✅ ANN model trained & evaluated
- ✅ Both models saved to disk
- ✅ Feature scaler saved and verified
- ✅ Inference functions tested
- ✅ Single patient predictions working
- ✅ Batch predictions working
- ✅ Performance metrics documented
- ✅ Model comparison completed
- ✅ Production deployment ready

---

##  📈 Performance Interpretation

### Prediction Confidence Levels

| Confidence | Risk Level | Clinical Action |
|------------|-----------|-----------------|
| **> 95%** | CRITICAL | Immediate specialist referral |
| **80-95%** | HIGH RISK | Urgent clinical review |
| **60-80%** | MODERATE RISK | Schedule follow-up within 1 week |
| **50-60%** | BORDERLINE | Additional testing recommended |
| **< 50%** | LOW RISK | Regular monitoring |

### Confusion Matrix Interpretation
```
                Predicted Negative  Predicted Positive
Actual Negative:        769              35 (False Positives)
Actual Positive:         68              2628 (True Positives)
                    (False Negatives)
```

- **True Positives (2628)**: Correctly identified diabetic patients
- **True Negatives (769)**: Correctly identified non-diabetic patients
- **False Positives (35)**: Acceptable in medical screening
- **False Negatives (68)**: Minimized through high sensitivity

---

##  🔄 Maintenance & Retraining

### Monitoring Schedule
- **Monthly**: Verify prediction accuracy on new data
- **Quarterly**: Retrain with accumulated new records
- **Yearly**: Full model review & optimization

### Retraining Steps
1. Collect new patient data and outcomes
2. Preprocess using same pipeline
3. Run `python train_ann_model.py`
4. Compare new vs old model performance
5. Deploy if improved, else keep current version

---

##  ✨ Key Achievements

- ✅ **97.06% Test Accuracy** - Clinical-grade performance
- ✅ **97.48% Sensitivity** - Catches 974 of 1000 type 1 diabetic patients
- ✅ **0.9954 ROC-AUC** - Excellent discrimination ability
- ✅ **Multi-model Architecture** - ANN primary + LR fallback
- ✅ **Lightweight Deployment** - ANN only 3.75 KB
- ✅ **Production Ready** - All components saved and tested
- ✅ **Comprehensive Documentation** - Ready for clinical team
- ✅ **Dual Optimization** - Adam + Mini-batch SGD

---

##  🚀 Project Status

**STATUS**: ✅ **PRODUCTION READY & DEPLOYED**

The Type 1 Diabetes Prediction System with ANN integration has been successfully trained, validated, and is ready for deployment to production. The system demonstrates excellent clinical performance with high accuracy and sensitivity suitable for diabetes screening and early detection applications.

---

**Last Updated**: April 15, 2026  
**Model Version**: 1.0 (ANN + LR Baseline)  
**Accuracy Target**: ✅ Achieved (97.06%)  
**Production Status**: ✅ Ready for Deployment
