import pandas as pd


df = pd.read_csv("ALL_trip_data_final_with_vicom_weights.csv")


df.loc[df["source"] == "VED", "Vehicle_Weight_kg"] = 3500


df.to_csv("ALL_trip_data_with_VED_Vicom.csv", index=False)

print("VED weights updated to 3500 kg.")
print(df[df["source"] == "VED"][["route", "source", "Vehicle_Weight_kg"]].head())