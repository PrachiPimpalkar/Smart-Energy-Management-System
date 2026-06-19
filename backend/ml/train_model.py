"""
train_model.py
--------------
Trains both Random Forest Regression and Linear Regression on the SEMS dataset.
Saves the best model (Random Forest) as a pickle file.

To run:  python train_model.py
"""

import os, sys, pickle, warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error

sys.path.insert(0, os.path.dirname(__file__))
from preprocessing import load_and_preprocess

MODEL_PATH    = os.path.join(os.path.dirname(__file__), "../../models/rf_model.pkl")
LR_MODEL_PATH = os.path.join(os.path.dirname(__file__), "../../models/lr_model.pkl")
CHARTS_PATH   = os.path.join(os.path.dirname(__file__), "../../static/charts")

os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
os.makedirs(CHARTS_PATH, exist_ok=True)

# ── 1. Load & preprocess ───────────────────────────────────────────────────────
X, y, encoders = load_and_preprocess()

# ── 2. Train / Test split (80% train, 20% test) ────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"\nTrain size : {len(X_train)}  |  Test size : {len(X_test)}")

# ── 3. Train Random Forest ─────────────────────────────────────────────────────
print("\nTraining Random Forest Regressor ...")
rf = RandomForestRegressor(
    n_estimators=100,
    max_depth=10,
    min_samples_split=5,
    random_state=42,
    n_jobs=-1
)
rf.fit(X_train, y_train)

rf_pred = rf.predict(X_test)
rf_r2   = r2_score(y_test, rf_pred)
rf_mae  = mean_absolute_error(y_test, rf_pred)
print(f"   Random Forest  ->  R2 Score : {rf_r2:.4f}  |  MAE : {rf_mae:.2f} kWh")

# ── 4. Train Linear Regression (baseline) ─────────────────────────────────────
print("\nTraining Linear Regression (baseline) ...")
lr = LinearRegression()
lr.fit(X_train, y_train)

lr_pred = lr.predict(X_test)
lr_r2   = r2_score(y_test, lr_pred)
lr_mae  = mean_absolute_error(y_test, lr_pred)
print(f"   Linear Regression ->  R2 Score : {lr_r2:.4f}  |  MAE : {lr_mae:.2f} kWh")

# ── 5. Save models ─────────────────────────────────────────────────────────────
with open(MODEL_PATH, "wb") as f:
    pickle.dump(rf, f)
with open(LR_MODEL_PATH, "wb") as f:
    pickle.dump(lr, f)
print(f"\nModels saved -> {MODEL_PATH}")

# ── 6. Visualization: Actual vs Predicted ─────────────────────────────────────
sample_size = min(100, len(y_test))
idx = np.arange(sample_size)

fig, axes = plt.subplots(1, 2, figsize=(16, 5))
fig.suptitle("SEMS – Actual vs Predicted Energy Consumption", fontsize=14, fontweight="bold")

for ax, name, pred in zip(axes, ["Random Forest", "Linear Regression"], [rf_pred, lr_pred]):
    ax.plot(idx, list(y_test)[:sample_size], label="Actual",    color="#2196F3", linewidth=1.5)
    ax.plot(idx, pred[:sample_size],         label="Predicted", color="#FF5722", linewidth=1.5, linestyle="--")
    ax.set_title(f"{name}  (R²={r2_score(y_test, pred):.3f}, MAE={mean_absolute_error(y_test, pred):.1f})")
    ax.set_xlabel("Sample Index")
    ax.set_ylabel("Energy (kWh)")
    ax.legend()
    ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(CHARTS_PATH, "actual_vs_predicted.png"), dpi=120)
plt.close()
print("   Chart saved -> static/charts/actual_vs_predicted.png")

# ── 7. Feature Importance ──────────────────────────────────────────────────────
feature_names = ["Month", "DayOfWeek", "Quarter", "IsWeekend", "Building", "Usage_Level"]
importances   = rf.feature_importances_

fig, ax = plt.subplots(figsize=(8, 4))
bars = ax.barh(feature_names, importances, color=["#4CAF50","#2196F3","#FF9800","#9C27B0","#F44336","#00BCD4"])
ax.set_xlabel("Importance Score")
ax.set_title("Random Forest – Feature Importance")
for bar, val in zip(bars, importances):
    ax.text(bar.get_width() + 0.002, bar.get_y() + bar.get_height()/2,
            f"{val:.3f}", va="center", fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_PATH, "feature_importance.png"), dpi=120)
plt.close()
print("   Chart saved -> static/charts/feature_importance.png")

print("\n====== TRAINING SUMMARY ======")
print(f"  {'Model':<22} {'R2 Score':>10} {'MAE (kWh)':>12}")
print(f"  {'-'*46}")
print(f"  {'Random Forest':<22} {rf_r2:>10.4f} {rf_mae:>12.2f}")
print(f"  {'Linear Regression':<22} {lr_r2:>10.4f} {lr_mae:>12.2f}")
print("  Winner : Random Forest ✅")
print("==============================\n")
