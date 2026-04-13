import numpy as np
import FindingAltitudeOpenMeteo
import pandas as pd


from geopy.distance import geodesic


VED_df = pd.read_csv("DATA/VED_all_ELECTRIC.csv")

VED_df["prev_long"] = VED_df["Longitude[deg]"].shift()
VED_df["prev_lat"] = VED_df["Latitude[deg]"].shift()

def calculer_distance(row):
    if pd.isna(row["prev_long"]):
        return 0
    return geodesic((row["prev_long"], row["prev_lat"]),(row["Longitude[deg]"],row["Latitude[deg]"])).meters

VED_df["distance[m]"] = VED_df.apply(calculer_distance,axis=1)

output = VED_df.groupby("Trip").agg(total_distance=("distance[m]","sum"),
                                    timestamp = ("Timestamp(ms)","max"),
                                    start_lat = ("Latitude[deg]","first"),
                                    end_lat=("Latitude[deg]","last"),
                                    start_long = ("Longitude[deg]","first"),
                                    end_long = ("Longitude[deg]","last"),
                                    speed = ("Vehicle Speed[km/h]","mean"),
                                    temperature = ("OAT[DegC]","mean"),
                                    chargeDebut = ("HV Battery SOC[%]", "first"),
                                    chargeFin = ("HV Battery SOC[%]", "last"))
output["start_altitude"] = output.apply(lambda row: FindingAltitudeOpenMeteo.get_elevation_data(row["start_lat"], row["start_long"]), axis=1)
output["end_altitude"] = output.apply(lambda row: FindingAltitudeOpenMeteo.get_elevation_data(row["end_lat"], row["end_long"]), axis=1)
output["total_distance"] = output["total_distance"]/1000
print(output.dtypes)
output["consumedElectric"] = (output["chargeDebut"].astype(float)-output["chargeFin"].astype(float))
output["slope"]=(output["end_altitude"].astype(float)-output["start_altitude"].astype(float))/output["total_distance"]
output.drop(["timestamp","start_lat","end_lat","start_long","end_long","start_altitude","end_altitude","chargeDebut","chargeFin"],axis=1,inplace=True)
output.to_csv("transform/VED_trip_distance.csv")

lat = 45.536665
lon = -73.674017
print(output.columns)





