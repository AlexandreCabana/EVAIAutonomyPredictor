import requests

lat_i = 45.568724
lon_i= -73.678462

lat_f= 45.53811871433954
lon_f= -73.67624074543532

#OpenStreetMap
url = f"http://router.project-osrm.org/route/v1/driving/{lon_i},{lat_i};{lon_f},{lat_f}?overview=false"

response = requests.get(url)
data = response.json()

route = data["routes"][0]

distance = route["distance"]      # mètres
duration = route["duration"]      # secondes

print("Distance:", distance/1000, "km")
print("Temps:", duration/60, "minutes")