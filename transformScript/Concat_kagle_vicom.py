import pandas as pd

df_vicom_kaggle = pd.read_csv("ALL_trip_data.csv")
df_VED = pd.read_csv("VED_trip_distance1.csv")

df_vicom_kaggle = df_vicom_kaggle.rename(columns={"route_id": "Trip"})

df_vicom_kaggle["source"] = "Vicom/Kaggle"
df_VED["source"] = "VED"

df_final = pd.concat([df_vicom_kaggle, df_VED], ignore_index=True)

df_final.to_csv("ALL_trip_data2.csv", index=False)