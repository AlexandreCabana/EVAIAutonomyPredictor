import pandas as pd
import requests

def get_elevation_data(lattitude, longitude):

    url = r'https://epqs.nationalmap.gov/v1/json?'

    params = {
        'output': 'json',
        'x': longitude,
        'y': lattitude,
        'units': 'Meters'
    }


    result = requests.get(url, params=params)

    if result.status_code == 200:
        data = result.json()
        try:
            elevation = data['value']
            return elevation
        except KeyError:
            return "Data pas dispo"
    else:
        return "Erreur de API"

if __name__ == "__main__":
    lat = 45.536665
    lon = -73.674017
    altitude = get_elevation_data(lat, lon)

    print(f"The altitude at Latitude {lat}, Longitude {lon} is {altitude} meters.")




