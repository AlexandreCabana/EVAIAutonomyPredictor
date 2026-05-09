import requests
import numpy as np
import time

def get_elevation_data(latitude, longitude):
    url = "https://api.open-meteo.com/v1/elevation"
    params = {
        "latitude": latitude,
        "longitude": longitude
    }

    try:
        time.sleep(0.1)
        result = requests.get(url, params=params, timeout=10)
        result.raise_for_status()

        data = result.json()

        if "elevation" in data and len(data["elevation"]) > 0:
            return data["elevation"][0]

        return np.nan

    except (requests.exceptions.RequestException, ValueError, KeyError, IndexError):
        return np.nan