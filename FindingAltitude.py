import pandas as pd
import requests
import warnings

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
        try:
            data = result.json()
            elevation = data['value']
            return elevation
        except KeyError:
            return "Data pas dispo"
        except Exception:
            print(f"Something went wrong with param {lattitude}, {longitude}")
    else:
        warnings.warn(f"Request failed with status code {result.status_code}")
        return get_elevation_data(lattitude, longitude)

if __name__ == "__main__":
    lat = 45.536665
    lon = -73.674017
    altitude = get_elevation_data(lat, lon)

    print(f"The altitude at Latitude {lat}, Longitude {lon} is {altitude} meters.")




