import FindingAltitude
import pandas as pd


from geopy.distance import geodesic


VICOM_df = pd.read_csv("../DATA/7777.csv")


VICOM_df["prev_long"] = VICOM_df.groupby("route_id")["longitude"].shift()
VICOM_df["prev_lat"] = VICOM_df.groupby("route_id")["latitude"].shift()

def calculer_distance(row):
    if pd.isna(row["prev_long"]):
        return 0
    return geodesic((row["prev_lat"], row["prev_long"]), (row["latitude"], row["longitude"])).meters

VICOM_df["distance[m]"]= VICOM_df.apply(calculer_distance,axis=1)

VICOM_df = VICOM_df.groupby("route_id").agg(total_distance=("distance[m]","sum"), timestamp = ("end_timestamp","last"), longitude_min = ("longitude","min"), latitude_min = ("latitude","min"), longitude_max = ("longitude","max"), latitude_max = ("latitude","max"), start_lat = ("latitude","first"), end_lat=("latitude","last"), start_long = ("longitude","first"), end_long = ("longitude","last"))

VICOM_df["start_altitude"] = VICOM_df.apply(lambda row: FindingAltitude.get_elevation_data(row["start_lat"], row["start_long"]), axis=1)
VICOM_df["end_altitude"] = VICOM_df.apply(lambda row: FindingAltitude.get_elevation_data(row["end_lat"], row["end_long"]), axis=1)

VICOM_df.to_csv("Vicom_trip_all_data.csv")
print(VICOM_df.columns)






