# ============================================================
# SEMS - Dataset Generator
# Generates a realistic energy consumption dataset for training
# Based on the research paper by Prachi Pimpalkar (ImCReTE 2026)
# ============================================================

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# ---- Configuration ----
NUM_ROWS = 1000  # Total data points to generate
START_DATE = datetime(2023, 1, 1)

# Buildings in an educational institution
BUILDINGS = [
    "Main Block",
    "Computer Lab",
    "Library",
    "Science Block",
    "Admin Block",
    "Canteen",
    "Sports Complex",
    "Hostel Block"
]

# Usage levels map to energy consumption ranges
USAGE_LEVELS = ["Low", "Medium", "High"]

# Base consumption per building (in kWh) - realistic values
BASE_CONSUMPTION = {
    "Main Block":      (150, 300),
    "Computer Lab":    (200, 400),
    "Library":         (80,  180),
    "Science Block":   (180, 350),
    "Admin Block":     (100, 220),
    "Canteen":         (120, 250),
    "Sports Complex":  (60,  150),
    "Hostel Block":    (130, 280),
}

# ---- Data Generation ----
records = []

for i in range(NUM_ROWS):
    # Random date within the year
    date = START_DATE + timedelta(days=random.randint(0, 364))
    day_of_week = date.weekday()  # 0=Monday, 6=Sunday

    building = random.choice(BUILDINGS)
    low, high = BASE_CONSUMPTION[building]

    # Weekday vs weekend affects consumption
    if day_of_week >= 5:  # Weekend
        multiplier = 0.5   # Less usage on weekends
        usage_level = "Low"
    elif day_of_week in [0, 4]:  # Monday/Friday
        multiplier = 0.85
        usage_level = "Medium"
    else:  # Tue-Thu peak days
        multiplier = 1.0
        usage_level = "High"

    # Calculate energy with some random noise
    base_energy = random.uniform(low, high) * multiplier
    noise = np.random.normal(0, 15)  # Add realistic noise
    energy = max(30, base_energy + noise)  # Minimum 30 kWh

    records.append({
        "Date": date.strftime("%Y-%m-%d"),
        "Building_Name": building,
        "Energy_Consumption_kWh": round(energy, 2),
        "Usage_Level": usage_level,
        "Day_of_Week": day_of_week,
        "Month": date.month
    })

# Create DataFrame
df = pd.DataFrame(records)

# Sort by date
df = df.sort_values("Date").reset_index(drop=True)

# Save to CSV
df.to_csv("energy_data.csv", index=False)

print("✅ Dataset generated successfully!")
print(f"   Total records: {len(df)}")
print(f"   Date range: {df['Date'].min()} to {df['Date'].max()}")
print(f"\nSample data:")
print(df.head(10))
print(f"\nStats:")
print(df["Energy_Consumption_kWh"].describe())
