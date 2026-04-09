import numpy as np
import FindingAltitude
import pandas as pd


from geopy.distance import geodesic

geodesic
VED_df = pd.read_csv("VED_all_ELECTRIC.csv")
VICOM_df = pd.read_csv("Vicomtech_all_ELECTRIC.csv")


VED_df["prev_long"] = VED_df["Longitude[deg]"].shift()
VED_df["prev_lat"] = VED_df["Latitude[deg]"].shift()

def calculer_distance(row):
    if pd.isna(row["prev_long"]):
        return 0
    return geodesic((row["prev_long"], row["prev_lat"]),(row["Longitude[deg]"],row["Latitude[deg]"])).meters

VED_df["distance[m]"] = VED_df.apply(calculer_distance,axis=1)

output = VED_df.groupby("Trip").agg(total_distance=("distance[m]","sum"), timestamp = ("Timestamp(ms)","max"), longitude_min = ("Longitude[deg]","min"), latitude_min = ("Latitude[deg]","min"), longitude_max = ("Longitude[deg]","max"), latitude_max = ("Latitude[deg]","max"), start_lat = ("Latitude[deg]","first"), end_lat=("Latitude[deg]","last"), start_long = ("Longitude[deg]","first"), end_long = ("Longitude[deg]","last"))
output["start_altitude"] = output.apply(lambda row: FindingAltitude.get_elevation_data(row["start_lat"], row["start_long"]), axis=1)
output["end_altitude"] = output.apply(lambda row: FindingAltitude.get_elevation_data(row["end_lat"], row["end_long"]), axis=1)


output.to_csv("VED_trip_distance.csv")

lat = 45.536665
lon = -73.674017
print(geodesic((lon, lat), (lon+1, lat)).kilometers)





