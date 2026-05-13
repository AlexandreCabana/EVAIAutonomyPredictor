import pandas as pd
import numpy as np

# =========================
# Load datasets
# =========================

# Your corrected main dataset
df = pd.read_csv("ALL_trip_data_sources_fixed.csv")

# Kaggle weight file
df_weights = pd.read_csv("Kaggle_Vehicle_Weight.csv")

# =========================
# Make sure columns are strings
# =========================

df["route"] = df["route"].astype(str)
df_weights["route"] = df_weights["route"].astype(str)

# =========================
# Keep only Kaggle rows
# =========================

mask_kaggle = df["source"] == "Kaggle"

# =========================
# Assign weights IN ORDER
# =========================

# Get indices of Kaggle rows
kaggle_indices = df[mask_kaggle].index

# Get weights as a list
weights_list = df_weights["Vehicle_Weight_kg"].tolist()

# Safety check
n = min(len(kaggle_indices), len(weights_list))

# Assign weights row-by-row in order
for i in range(n):
    df.loc[kaggle_indices[i], "Vehicle_Weight_kg"] = weights_list[i]

# =========================
# Save final dataset
# =========================

df.to_csv("ALL_trip_data_complete.csv", index=False)

print("Weights successfully assigned to Kaggle routes.")
print(df.head())