# Render Deployment Guide - Type 1 Diabetes Prediction System

## Pre-Deployment Checklist ✅

- ✅ TensorFlow added to requirements.txt
- ✅ render.yaml configured with gunicorn
- ✅ App configured to handle Render PORT environment variable
- ✅ All ANN model files included in repository
- ✅ Feature scaler pickle file included
- ✅ All changes pushed to GitHub

---

## Step-by-Step Deployment to Render

### 1. **Create Render Account**
- Go to: https://render.com
- Sign up (if you don't have an account)
- Create new account or login

### 2. **Connect GitHub Repository**
1. Go to Render Dashboard
2. Click **"New +"** → Select **"Web Service"**
3. Click **"Connect a repository"**
4. Search for: `Type-I-Diabetes-Risk-Analysis-MBGD`
5. Click **"Select Repository"**

### 3. **Configure Deployment Settings**

**Name:**
```
type1-diabetes-screening
```

**Region:**
- Select your preferred region (e.g., US - Virginia)

**Branch:**
```
main
```

**Runtime:**
- Python 3

**Build Command:**
```
pip install --upgrade pip && pip install -r requirements.txt
```

**Start Command:**
```
gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 app:app
```

### 4. **Environment Variables**

Click **"Advanced"** and add:

| Key | Value |
|-----|-------|
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | *(Auto-generated)* Generate random string |

### 5. **Instance & Plan**

- **Instance Type:** Standard
- **Plan:** Free tier initially (0.5 GB RAM)
  - For production: Upgrade to Starter Pro ($12/month - 2 GB RAM recommended)

---

## What Gets Deployed

```
✅ Frontend
   - HTML templates (result.html, dashboard.html, etc.)
   - CSS/Styling
   - Bootstrap components

✅ Backend (Flask)
   - app.py (main Flask application)
   - predict.py (ANN prediction engine)

✅ AI Model
   - models/ann_model.h5 (97.06% accurate ANN)
   - models/feature_scaler.pkl
   - models/model_config.json

✅ Data
   - data/final_preprocessed_mixed.csv

✅ Dependencies (auto-installed)
   - TensorFlow 2.14.0 (for ANN inference)
   - Flask, Pandas, Numpy, Scikit-learn
   - Gunicorn (production server)
```

---

## Deployment Process

1. Click **"Create Web Service"**
2. Render will start building:
   - Installing dependencies (2-3 minutes)
   - Running build command
   - Starting the Flask app with gunicorn

3. **Wait for deployment to complete** (usually 5-10 minutes)
   - Status will show: "Your service is live"
   - You'll get a .onrender.com URL

---

## After Deployment ✅

**Your app will be live at:**
```
https://type1-diabetes-screening.onrender.com
```

### Test the Deployment

1. **Visit the landing page:**
   ```
   https://type1-diabetes-screening.onrender.com/
   ```

2. **Register a new account:**
   - Click "Register"
   - Enter email & password
   - Click "Create Account"

3. **Login and test prediction:**
   - Fill out the health screening form
   - Click "Get Risk Assessment"
   - Verify you see the new clean UI with:
     - Risk Level (HIGH/MODERATE/LOW)
     - Parameters (Glucose, Ketones, BMI)
     - What This Means
     - Recommended Care
     - Doctor Advice
     - Important Note

---

## Monitoring

**View Logs:**
1. Render Dashboard → Your Service
2. Click the **"Logs"** tab
3. Monitor for errors

**Key Indicators:**
- ✅ No Python import errors
- ✅ TensorFlow loading successfully
- ✅ ANN model predictions working
- ✅ User records saving properly

---

## Common Issues & Solutions

### Issue: "TensorFlow not found"
**Solution:** 
- Verify `requirements.txt` has `tensorflow==2.14.0`
- Redeploy with manual rebuild

### Issue: "Port binding error"
**Solution:**
- Use start command: `gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 app:app`
- Ensure `app.py` reads PORT from environment

### Issue: "Model file not found"
**Solution:**
- Verify `.gitignore` is not ignoring `models/` directory
- Commit all model files to GitHub
- Push before deploying

### Issue: "Build times out (>30 min)"
**Solution:**
- Start with Free tier to test build
- Upgrade to Starter tier for production (faster builds)

---

## Performance Tips

### For Free Tier:
- ✅ Single worker (current config)
- ✅ 120s timeout (enough for ANN inference)
- ✅ Acceptable for small user base

### For Production:
- Upgrade to Starter Pro ($12/month)
- Increase workers to 2-4
- Use 180s timeout
- Add environment monitoring

---

## API Endpoints

Your deployed app will have:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Landing page |
| `/login` | GET/POST | User login |
| `/register` | GET/POST | New registration |
| `/dashboard` | GET | Risk screening form |
| `/predict` | POST | ANN prediction API |
| `/result` | GET | Show prediction results |
| `/logout` | GET | Clear session |

---

## Deployment Verification

**Check everything worked:**

```bash
# SSH into Render container (if available)
# Or check the Logs tab for:

✅ "* Running on 0.0.0.0:PORT"
✅ "WARNING: This is a development server"
✅ No tensorflow ImportError
✅ Successfully loaded model: <Sequential...>
```

---

## GitHub Integration

Render automatically:
1. **Watches** your GitHub main branch
2. **Auto-deploys** when you push changes
3. **Auto-rebuilds** if you update requirements.txt

**To update after deployment:**
```bash
git add .
git commit -m "Your changes"
git push origin main
# Render automatically rebuilds and redeployes!
```

---

## Support & Resources

- **Render Docs:** https://render.com/docs
- **Flask Deployment:** https://flask.palletsprojects.com/deployment/
- **TensorFlow Serving:** https://www.tensorflow.org/serving
- **Our Repository:** https://github.com/Jjoana711/Type-I-Diabetes-Risk-Analysis-MBGD

---

## Success! 🚀

Your Type 1 Diabetes Prediction System is now live on Render with:
- ✅ **97.06% accurate ANN predictions**
- ✅ **User-friendly interface**
- ✅ **Production-ready deployment**
- ✅ **Automatic updates from GitHub**

Happy screening! 📊
