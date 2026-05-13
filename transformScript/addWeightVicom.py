import pandas as pd
import numpy as np

# =========================
# Load datasets
# =========================

df_all = pd.read_csv("ALL_trip_data2.csv")
df_vicom = pd.read_csv("Vicom_trip_all_data3.csv")

# =========================
# Keep only first 58 trips
# =========================

df_vicom_58 = df_vicom.iloc[:58].copy()

# =========================
# Vehicle weights (kg)
# =========================

# Dacia Spring Electric 33 kWh
# Approx curb weight: ~970 kg
# Sources report roughly 970-1045 kg depending on trim
DACIA_SPRING_WEIGHT = 970

# Nissan Leaf e+ 62 kWh
# Approx curb weight: ~1730-1760 kg
# Using representative value
LEAF_EPLUS_WEIGHT = 1735

# =========================
# Assign weights from vehicle_id
# =========================

def get_weight(vehicle_id):
    if vehicle_id == 6:
        return DACIA_SPRING_WEIGHT
    elif vehicle_id == 7:
        return LEAF_EPLUS_WEIGHT
    else:
        return np.nan

df_vicom_58["Vehicle_Weight_kg"] = df_vicom_58["vehicle_id"].apply(get_weight)

# =========================
# Prepare route IDs
# =========================

df_all["route"] = df_all["route"].astype(str)
df_vicom_58["route_id"] = df_vicom_58["route_id"].astype(str)

# =========================
# Create mapping
# =========================

weight_map = dict(
    zip(df_vicom_58["route_id"], df_vicom_58["Vehicle_Weight_kg"])
)

# =========================
# Update weights ONLY for matching routes
# =========================

mask = df_all["route"].isin(weight_map.keys())

df_all.loc[mask, "Vehicle_Weight_kg"] = (
    df_all.loc[mask, "route"].map(weight_map)
)

# =========================
# Save final dataset
# =========================

df_all.to_csv("ALL_trip_data_final_with_vicom_weights.csv", index=False)

print("Weights successfully added for first 58 Vicom trips.")
print(df_all[df_all["route"].isin(weight_map.keys())].head())