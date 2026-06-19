# ⚡ SEMS — Smart Energy Management System
### For Educational Institutions | Final Year MCA Project

> **Author:** Prachi Rajesh Pimpalkar  
> **Institution:** KJEI's Trinity Academy of Engineering, Pune – 411048  
> **Guide:** Prof. Monika Shinde  
> **Published at:** ImCReTE 2026, 11th April 2026  
> **ISBN:** 978-81-999684-1-7

---

## 📌 Project Overview

The **Smart Energy Management System (SEMS)** is an AI-powered web application that
predicts and analyzes energy consumption in educational institutions using
**Random Forest Regression** and **Linear Regression** machine learning models.

### Key Features
- ⚡ ML-based energy consumption prediction
- 📊 Role-based dashboard (Admin / Student / User)
- 📈 Analytics with interactive Chart.js visualizations
- 🏢 Per-building energy statistics
- 💡 Smart energy-saving suggestions (peak shaving, load shifting)
- 📡 IoT integration architecture (MQTT + Zigbee simulation)
- 🔐 Simple authentication system

---

## 🗂 Folder Structure

```
SEMS/
├── backend/
│   ├── app.py                    ← Flask server (main entry point)
│   └── ml/
│       ├── preprocessing.py      ← Data cleaning & feature engineering
│       └── train_model.py        ← Model training script
├── data/
│   ├── generate_dataset.py       ← Script to create synthetic dataset
│   └── energy_data.csv           ← Generated dataset (5,848 records)
├── models/
│   ├── rf_model.pkl              ← Trained Random Forest model
│   ├── lr_model.pkl              ← Trained Linear Regression model
│   └── encoders.pkl              ← Label encoders for categorical data
├── static/
│   └── charts/
│       ├── actual_vs_predicted.png
│       └── feature_importance.png
├── frontend/
│   ├── index.html                ← Single-page app (all pages)
│   ├── css/style.css             ← Global stylesheet
│   └── js/app.js                 ← Frontend logic (Fetch API + Chart.js)
├── requirements.txt
└── README.md
```

---

## 🚀 Setup Instructions (Step-by-Step)

### Step 1: Install Python 3.9+
Download from https://python.org/downloads

### Step 2: Clone / Download this project
```
git clone https://github.com/yourusername/SEMS.git
cd SEMS
```

### Step 3: Install Python dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Generate dataset (run only once)
```bash
python data/generate_dataset.py
```

### Step 5: Train the ML model (run only once)
```bash
python backend/ml/train_model.py
```
This creates `models/rf_model.pkl`, `models/lr_model.pkl`, and `models/encoders.pkl`.

### Step 6: Start the Flask server
```bash
python backend/app.py
```
Server starts at: **http://localhost:5000**

### Step 7: Open the dashboard
Open your browser and go to: **http://localhost:5000**

---

## 🔐 Login Credentials

| Username | Password  | Role    |
|----------|-----------|---------|
| admin    | admin123  | Admin   |
| prachi   | sems2026  | Student |
| user     | user123   | User    |

---

## 🤖 ML Model Performance

| Algorithm         | R² Score | MAE (kWh) | Complexity | Status      |
|-------------------|----------|-----------|------------|-------------|
| Random Forest     | 0.81     | 41.77     | Medium     | ✅ Best Model|
| Linear Regression | 0.50     | 64.96     | Low        | Baseline    |
| LSTM              | ~0.90+   | ~20       | Very High  | Future Work |

**Random Forest** was selected because it provides the best balance between
accuracy and simplicity for this implementation.

---

## 🌐 API Endpoints

| Method | Endpoint          | Description                        |
|--------|-------------------|------------------------------------|
| GET    | /api/health       | Server health check                |
| GET    | /api/options      | Valid building names & usage levels|
| POST   | /api/predict      | Predict energy consumption         |
| GET    | /api/analytics    | Monthly, building, usage stats     |
| GET    | /api/buildings    | Per-building statistics            |

### Example: Prediction Request
```json
POST http://localhost:5000/api/predict
Content-Type: application/json

{
  "building_name": "Computer Lab",
  "usage_level": "High",
  "month": 6,
  "day_of_week": 2
}
```

### Example: Prediction Response
```json
{
  "success": true,
  "prediction": {
    "random_forest_kwh": 387.45,
    "linear_regression_kwh": 312.10,
    "unit": "kWh",
    "model_used": "Random Forest Regressor"
  },
  "suggestions": [
    "🔴 HIGH usage detected. Consider shifting non-critical loads...",
    "❄️  Check HVAC systems for efficiency..."
  ]
}
```

---

## 🏗 System Architecture

```
User Layer
    │
    ▼
Frontend Layer (HTML + CSS + JS + Chart.js)
    │  Fetch API (JSON)
    ▼
Flask Backend (app.py)
    │  REST API Endpoints
    ▼
ML Prediction Engine
    ├── preprocessing.py  (Label Encoding, Feature Extraction)
    ├── rf_model.pkl      (Random Forest — primary model)
    └── lr_model.pkl      (Linear Regression — baseline)
    │
    ▼
Dataset Layer (energy_data.csv — 5,848 records)
```

---

## ⚙️ System Design (3-Layer Architecture)

### 1. Data Collection Layer
- Smart meters and IoT sensors collect real-time data
- Features: Energy consumption, temperature, occupancy

### 2. Communication Layer
- **MQTT Protocol** — lightweight, efficient for IoT
- **Zigbee (IEEE 802.15.4)** — low-power wireless communication

### 3. Processing & Application Layer
- Cloud platform for data storage
- ML models for energy prediction
- Web dashboard for visualization and control

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| `FileNotFoundError: rf_model.pkl` | Run `python backend/ml/train_model.py` first |
| `CORS error in browser` | Make sure Flask server is running on port 5000 |
| `Prediction fails` | Ensure `encoders.pkl` exists in `/models/` folder |
| `Charts not loading` | Check browser console; verify API is returning data |

---

## 🔮 Future Scope
1. Integration with real IoT sensors (Raspberry Pi + smart meters)
2. LSTM deep learning model for better time-series prediction
3. Mobile app (Android/iOS) for real-time monitoring
4. Automated appliance control based on ML predictions
5. Renewable energy source integration (solar panels)
6. Email/SMS alerts for abnormal energy spikes

---

## 📚 References
1. Breiman, L. (2001). Random Forests. Machine Learning, 45(1), 5–32.
2. Jain et al., "AI-driven smart campus energy systems," 2023.
3. S. Elsisi et al., "Energy prediction using Random Forest," 2022.
4. Ministry of Power, India, "Energy consumption statistics," 2024.
5. Bureau of Energy Efficiency (BEE), India, 2023.
6. IEEE, "802.15.4 Zigbee Standard," 2022.
7. OASIS, "MQTT Protocol Specification," 2023.

---

*This project was developed as part of MCA Final Year Project at Trinity Academy of Engineering, Pune.*
