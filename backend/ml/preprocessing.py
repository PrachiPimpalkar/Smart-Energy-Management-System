"""
preprocessing.py  —  SEMS Data Preprocessing
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import pickle
import os

DATA_PATH    = os.path.join(os.path.dirname(__file__), "../../data/energy_data.csv")
ENCODER_PATH = os.path.join(os.path.dirname(__file__), "../../models/encoders.pkl")

FEATURE_COLS = ["Month", "DayOfWeek", "Quarter", "IsWeekend",
                "Building_Name_encoded", "Usage_Level_encoded"]

def load_and_preprocess(filepath=DATA_PATH):
    print("Loading dataset...")
    df = pd.read_csv(filepath)
    initial = len(df)
    df.dropna(inplace=True)
    print(f"   Rows after cleaning: {len(df)} (removed {initial-len(df)})")

    df["Date"]      = pd.to_datetime(df["Date"])
    df["Month"]     = df["Date"].dt.month
    df["DayOfWeek"] = df["Date"].dt.dayofweek
    df["Quarter"]   = df["Date"].dt.quarter
    df["IsWeekend"] = (df["DayOfWeek"] >= 5).astype(int)

    encoders = {}
    for col in ["Building_Name", "Usage_Level"]:
        le = LabelEncoder()
        df[col + "_encoded"] = le.fit_transform(df[col])
        encoders[col] = le
        mapping = dict(zip(le.classes_, le.transform(le.classes_).tolist()))
        print(f"   Encoded '{col}': {mapping}")

    X = df[FEATURE_COLS]
    y = df["Energy_Consumption_kWh"]

    os.makedirs(os.path.dirname(ENCODER_PATH), exist_ok=True)
    with open(ENCODER_PATH, "wb") as f:
        pickle.dump(encoders, f)
    print(f"   Encoders saved -> {ENCODER_PATH}")
    return X, y, encoders


def preprocess_single_input(building_name, usage_level, month, day_of_week):
    with open(ENCODER_PATH, "rb") as f:
        encoders = pickle.load(f)

    building_enc = int(encoders["Building_Name"].transform([building_name])[0])
    usage_enc    = int(encoders["Usage_Level"].transform([usage_level])[0])
    quarter      = (month - 1) // 3 + 1
    is_weekend   = 1 if day_of_week >= 5 else 0

    # Return DataFrame (same column names as training) to avoid sklearn warning
    return pd.DataFrame([[month, day_of_week, quarter, is_weekend, building_enc, usage_enc]],
                        columns=FEATURE_COLS)


def get_valid_options():
    with open(ENCODER_PATH, "rb") as f:
        encoders = pickle.load(f)
    return {
        "buildings":    list(encoders["Building_Name"].classes_),
        "usage_levels": list(encoders["Usage_Level"].classes_)
    }
