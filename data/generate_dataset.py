"""
generate_dataset.py
-------------------
Generates a synthetic energy consumption dataset for SEMS.
Run this ONCE to create energy_data.csv before training.
"""

import pandas as pd
import numpy as np
import os

np.random.seed(42)

# Buildings in a typical educational institution
buildings = [
    "Main Block", "Science Lab", "Computer Lab",
    "Library", "Canteen", "Admin Block",
    "Sports Complex", "Hostel Block"
]

usage_levels = ["Low", "Medium", "High"]

records = []

# Generate 2 years of daily data per building
dates = pd.date_range(start="2023-01-01", end="2024-12-31", freq="D")

for building in buildings:
    for date in dates:
        month = date.month
        day_of_week = date.dayofweek  # 0=Monday, 6=Sunday

        # Weekend = lower consumption
        if day_of_week >= 5:
            base = np.random.uniform(40, 100)
            usage = "Low"
        # Summer months = higher AC usage
        elif month in [4, 5, 6]:
            base = np.random.uniform(200, 400)
            usage = "High"
        # Winter = moderate
        elif month in [11, 12, 1]:
            base = np.random.uniform(100, 200)
            usage = "Medium"
        else:
            base = np.random.uniform(120, 280)
            usage = np.random.choice(usage_levels)

        # Building-specific multiplier
        multipliers = {
            "Computer Lab": 1.8,
            "Science Lab": 1.6,
            "Main Block": 1.3,
            "Library": 1.0,
            "Admin Block": 1.1,
            "Canteen": 0.9,
            "Sports Complex": 0.7,
            "Hostel Block": 1.4,
        }

        energy = round(base * multipliers.get(building, 1.0) + np.random.normal(0, 10), 2)
        energy = max(10, energy)  # No negative energy

        records.append({
            "Date": date.strftime("%Y-%m-%d"),
            "Building_Name": building,
            "Energy_Consumption_kWh": energy,
            "Usage_Level": usage
        })

df = pd.DataFrame(records)
output_path = os.path.join(os.path.dirname(__file__), "energy_data.csv")
df.to_csv(output_path, index=False)

print(f"✅ Dataset generated successfully!")
print(f"   Total records : {len(df)}")
print(f"   Columns       : {list(df.columns)}")
print(f"   Saved at      : {output_path}")
print(df.head())
