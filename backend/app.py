from flask import Flask, request, jsonify, send_from_directory, render_template_string
from flask_cors import CORS
import pickle, os, sys, json, logging, traceback
import numpy as np
import pandas as pd

# ── Setup ──────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR    = os.path.dirname(BASE_DIR)
MODELS_DIR  = os.path.join(ROOT_DIR, "models")
STATIC_DIR  = os.path.join(ROOT_DIR, "static")
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")
DATA_PATH   = os.path.join(ROOT_DIR, "data", "energy_data.csv")

sys.path.insert(0, os.path.join(BASE_DIR, "ml"))
from preprocessing import preprocess_single_input, get_valid_options

app = Flask(__name__, static_folder=STATIC_DIR)
CORS(app)  # Allow requests from frontend

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ── Load models at startup ─────────────────────────────────────────────────────
def load_model(path):
    with open(path, "rb") as f:
        return pickle.load(f)

try:
    rf_model = load_model(os.path.join(MODELS_DIR, "rf_model.pkl"))
    lr_model = load_model(os.path.join(MODELS_DIR, "lr_model.pkl"))
    logger.info("✅ Models loaded successfully.")
except Exception as e:
    logger.error(f"❌ Failed to load models: {e}")
    rf_model = lr_model = None


# ── Helper: Energy-saving suggestions ─────────────────────────────────────────
def get_suggestions(prediction_kwh, usage_level):
    tips = []
    if prediction_kwh > 300:
        tips.append("🔴 HIGH usage detected. Consider shifting non-critical loads to off-peak hours (10 PM – 6 AM).")
        tips.append("❄️  Check HVAC systems for efficiency. Clean AC filters and set thermostat to 24°C.")
    elif prediction_kwh > 150:
        tips.append("🟡 MEDIUM usage. Monitor peak hours between 11 AM – 3 PM.")
        tips.append("💡 Switch off idle computers and lights in unoccupied rooms.")
    else:
        tips.append("🟢 LOW usage. System is operating efficiently.")
        tips.append("✅ Continue current energy management practices.")

    if usage_level == "High":
        tips.append("⚡ Peak shaving recommended: Stagger high-load equipment start times.")
    return tips


# ── API Routes ─────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/<path:filename>")
def serve_frontend(filename):
    # Try frontend directory first
    full_path = os.path.join(FRONTEND_DIR, filename)
    if os.path.exists(full_path):
        return send_from_directory(FRONTEND_DIR, filename)
    return "File not found", 404

@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint — confirms server is running."""
    return jsonify({
        "status": "ok",
        "models_loaded": rf_model is not None,
        "message": "SEMS API is running"
    })

@app.route("/api/options", methods=["GET"])
def get_options():
    """Returns valid dropdown options for the prediction form."""
    try:
        options = get_valid_options()
        return jsonify({"success": True, "data": options})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/predict", methods=["POST"])
def predict():
    """
    Main prediction endpoint.

    Expects JSON body:
    {
        "building_name": "Computer Lab",
        "usage_level": "High",
        "month": 6,
        "day_of_week": 2
    }

    Returns predicted energy consumption in kWh plus suggestions.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No JSON body received"}), 400

        # ── Validate inputs ────────────────────────────────────────────────────
        required = ["building_name", "usage_level", "month", "day_of_week"]
        for field in required:
            if field not in data:
                return jsonify({"success": False, "error": f"Missing field: {field}"}), 400

        building_name = str(data["building_name"])
        usage_level   = str(data["usage_level"])
        month         = int(data["month"])
        day_of_week   = int(data["day_of_week"])

        if not (1 <= month <= 12):
            return jsonify({"success": False, "error": "month must be 1–12"}), 400
        if not (0 <= day_of_week <= 6):
            return jsonify({"success": False, "error": "day_of_week must be 0–6"}), 400

        # ── Preprocess and predict ─────────────────────────────────────────────
        features = preprocess_single_input(building_name, usage_level, month, day_of_week)
        rf_pred  = float(round(rf_model.predict(features)[0], 2))
        lr_pred  = float(round(lr_model.predict(features)[0], 2))
        suggestions = get_suggestions(rf_pred, usage_level)

        logger.info(f"Prediction: {building_name}, {usage_level}, m={month}, d={day_of_week} -> {rf_pred} kWh")

        return jsonify({
            "success": True,
            "input": {
                "building_name": building_name,
                "usage_level": usage_level,
                "month": month,
                "day_of_week": day_of_week
            },
            "prediction": {
                "random_forest_kwh": rf_pred,
                "linear_regression_kwh": lr_pred,
                "unit": "kWh",
                "model_used": "Random Forest Regressor"
            },
            "suggestions": suggestions
        })

    except ValueError as ve:
        logger.warning(f"Invalid input: {ve}")
        return jsonify({"success": False, "error": f"Invalid input value: {str(ve)}"}), 400
    except Exception as e:
        logger.error(traceback.format_exc())
        return jsonify({"success": False, "error": "Internal server error. Check server logs."}), 500


@app.route("/api/analytics", methods=["GET"])
def analytics():
    """
    Returns analytics data for charts:
    - Monthly average energy per building
    - Building-wise total consumption
    - Usage level distribution
    """
    try:
        df = pd.read_csv(DATA_PATH, parse_dates=["Date"])
        df["Month"] = df["Date"].dt.month

        # Monthly average
        monthly = df.groupby("Month")["Energy_Consumption_kWh"].mean().round(2).to_dict()

        # Building totals
        building_totals = df.groupby("Building_Name")["Energy_Consumption_kWh"].sum().round(2).to_dict()

        # Usage level counts
        usage_counts = df["Usage_Level"].value_counts().to_dict()

        # Top 5 high consumption days
        top5 = df.nlargest(5, "Energy_Consumption_kWh")[
            ["Date", "Building_Name", "Energy_Consumption_kWh", "Usage_Level"]
        ].copy()
        top5["Date"] = top5["Date"].astype(str)
        top5_list = top5.to_dict(orient="records")

        return jsonify({
            "success": True,
            "monthly_avg": monthly,
            "building_totals": building_totals,
            "usage_counts": usage_counts,
            "top5_high_consumption": top5_list
        })
    except Exception as e:
        logger.error(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/buildings", methods=["GET"])
def buildings_data():
    """Returns per-building statistics."""
    try:
        df = pd.read_csv(DATA_PATH)
        stats = df.groupby("Building_Name")["Energy_Consumption_kWh"].agg(
            ["mean", "max", "min", "sum"]
        ).round(2).reset_index()
        stats.columns = ["building", "avg_kwh", "max_kwh", "min_kwh", "total_kwh"]
        return jsonify({"success": True, "data": stats.to_dict(orient="records")})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ── Run server ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "="*50)
    print("  SEMS — Smart Energy Management System")
    print("  Flask Backend running at http://localhost:5000")
    print("="*50 + "\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
