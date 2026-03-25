# Type 1 Diabetes Early Risk Analysis System

A professional web-based screening platform for early detection of Type 1 Diabetes indicators using machine learning (Logistic Regression with Mini-Batch Gradient Descent).

## Features

✅ **User Authentication** - Secure login and registration system  
✅ **Dynamic Screening Form** - Conditional glucose input selector (Fasting/Random/Both)  
✅ **ML-Powered Predictions** - 3-level risk classification (Strong/Moderate/Normal indicators)  
✅ **Personalized Results** - Risk-stratified clinical interpretations and 7 rehabilitation measures  
✅ **Data Persistence** - Patient records stored securely (Excel-based)  
✅ **Professional UI** - Responsive design with clinical color scheme (Teal theme)  
✅ **Clinical Disclaimers** - Mandatory medical disclaimers on results page  

## Tech Stack

- **Backend**: Flask 3.1.3 (Python 3.10)
- **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript
- **ML Model**: scikit-learn Logistic Regression
- **Data**: pandas, Excel persistence (openpyxl)
- **Deployment**: Render (cloud platform)

## Project Structure

```
├── app.py                          # Flask application (main entry point)
├── predict.py                      # ML prediction module
├── backend/
│   └── train_model.py              # Model training pipeline
├── frontend/
│   ├── index.html                  # Landing page
│   ├── login.html                  # Authentication
│   ├── register.html               # User registration
│   ├── dashboard.html              # Screening form
│   └── result.html                 # Results with recommendations
├── models/
│   └── t1d_logreg_mb.pkl          # Pre-trained logistic regression model
├── data/
│   ├── raw/                        # Training dataset location
│   └── processed/                  # Processed dataset
├── requirements.txt                # Python dependencies
├── Procfile                        # Render deployment config
├── render.yaml                     # Alternative Render config
└── DEPLOYMENT_GUIDE.md             # Detailed deployment instructions
```

## Quick Start (Local)

### Installation
```bash
# Clone or download the project
cd "d:\Earlier Suspiction of type 1 diabetes system"

# Create virtual environment (if not exists)
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run Application
```bash
python app.py
# Opens automatically at http://localhost:<PORT>
```

### Access
- **Landing**: http://localhost:PORT
- **Register**: Create new account
- **Login**: Use registered credentials
- **Screening**: Complete health questionnaire
- **Results**: View personalized risk assessment

## Deployment

### Deploy to Render (Recommended)

Your project is ready to deploy! All necessary files are included:
- ✅ `requirements.txt` - Dependencies
- ✅ `Procfile` - Startup configuration
- ✅ `render.yaml` - Render-specific config
- ✅ App configured for cloud environment

**See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for step-by-step instructions.**

### Expected Deployment Time: 15-30 minutes

Once deployed, your app will be accessible at:
```
https://type1-diabetes-screening.onrender.com
```

## Model Details

### Algorithm
- **Type**: Logistic Regression with Mini-Batch Gradient Descent
- **Training Features**: 13 clinical indicators
- **Target**: Binary classification (Type 1 Diabetes risk)
- **Optimization**: Hyperparameter tuning via 5-fold Stratified Cross-Validation

### Features Used
1. Age
2. Gender
3. BMI
4. Glucose Level
5. HbA1c
6. Family History
7. Polyuria (Frequent Urination)
8. Polydipsia (Excessive Thirst)
9. Weight Loss
10. Fatigue
11. Blurred Vision
12. C-Peptide Level
13. Autoantibodies

### Risk Categories
| Risk Level | Probability | Recommendation |
|-----------|------------|-----------------|
| **Strong** | ≥ 70% | Immediate medical consultation |
| **Moderate** | 40-70% | Schedule doctor visit |
| **Normal** | < 40% | Continue routine check-ups |

### Performance
- Accuracy: Model evaluated on test set
- F1-Score: Optimized for balanced precision/recall
- ROC-AUC: Binary classification performance metric
- Class Balancing: Weighted to handle imbalanced data

## Training Dataset

The model is trained on a Type 1 Diabetes indicator dataset with:
- Balanced positive/negative class examples
- 13 clinical features per patient record
- Standardized preprocessing pipeline
- Stratified train-test split (80/20)

**Note**: Dataset location: `data/raw/` (preprocessed: `data/processed/validated_type1_dataset.csv`)

## Security & Privacy

✅ **Secure Authentication** - Password-based login system  
✅ **Session Management** - Secure Flask sessions  
✅ **Data Storage** - Excel files with username/email/password  
✅ **HTTPS Ready** - Render provides automatic SSL certificates  
⚠️ **Note**: For production, consider database encryption and GDPR compliance

## Configuration

### Environment Variables (Production)
```
FLASK_ENV = production
SECRET_KEY = (auto-generated by Render)
PORT = (auto-assigned by Render)
```

### Local Development
```bash
# No special configuration needed
# Auto-runs on random available port
```

## Testing

### Test Patient Data (Moderate Risk)
- Age: 35
- BMI: 24.2
- Glucose: 130-180 mg/dL
- HbA1c: 6.5%
- Symptoms: 3 selected
- Family History: No
- Ketones: Absent

**Expected**: Moderate Indicators Found (orange result)

## Troubleshooting

### Files Not Found
- Excel files (`patient_records.xlsx`, `users.xlsx`) are created automatically on first use

### Model File Missing
- Fallback heuristic formula is used if model can't be loaded
- Predictions still function (less optimized)

### Port Already in Use
- App automatically finds next available port on local run

### Deployment Issues
- Check Render **Logs** tab for detailed error messages
- Common fixes: verify `requirements.txt`, check `Procfile`

## Future Enhancements

- [ ] Database persistence (PostgreSQL)
- [ ] Email verification for registration
- [ ] Advanced ML models (Random Forest, SVM)
- [ ] Mobile app (React Native)
- [ ] Doctor dashboard with patient records
- [ ] Multi-language support
- [ ] API endpoint for external integrations
- [ ] Real-time model retraining

## Legal & Medical Disclaimer

⚠️ **IMPORTANT**: This system is for **educational and screening purposes only**. It is **NOT** a medical diagnosis tool.

- This screening tool provides early indicators based on health information
- Results do NOT constitute medical diagnosis
- Consult qualified healthcare professionals for accurate diagnosis
- Type 1 Diabetes requires confirmatory testing and clinical assessment
- Always follow medical advice from licensed practitioners

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

This project is available for educational use. Modify and distribute as needed.

## Support

For issues or questions:
1. Check [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for deployment help
2. Review code comments for feature-specific details
3. Check Render logs for runtime errors

## Author

Developed as a Type 1 Diabetes screening and awareness system.
Health-tech project combining machine learning with clinical decision support.

---

**Current Version**: 1.0  
**Last Updated**: March 2026  
**Status**: Ready for Production Deployment ✅
