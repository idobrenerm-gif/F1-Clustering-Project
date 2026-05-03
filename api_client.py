import requests
import pandas as pd

class OpenF1Client:
    def __init__(self):
        self.base_url = "https://api.openf1.org/v1"

    def _fetch_data(self, endpoint, params=None):
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        else:
            print(f"Error fetching data from {endpoint}")
            return pd.DataFrame()

    def get_sessions(self, year=2024, session_name="Race"):
        return self._fetch_data("sessions", {"year": year, "session_name": session_name})

    def get_drivers(self, session_key):
        return self._fetch_data("drivers", {"session_key": session_key})

    def get_telemetry(self, session_key, driver_number, min_speed=50):
        endpoint = f"car_data?speed>{min_speed}"
        return self._fetch_data(endpoint, {"session_key": session_key, "driver_number": driver_number})

    def get_location(self, session_key, driver_number):
        return self._fetch_data("location", {"session_key": session_key, "driver_number": driver_number})