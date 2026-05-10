# Import required libraries
import requests
import pandas as pd
import os
import time

# Base URL for the OpenF1 API
BASE_URL = "https://api.openf1.org/v1/"

# Headers to simulate a real web browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def fetch_openf1(endpoint, params=None, retries=3):
    # Try the request multiple times in case of failure
    for attempt in range(retries):
        try:
            # Send GET request to the API
            response = requests.get(BASE_URL + endpoint, params=params, headers=HEADERS, timeout=15)
            
            # If successful, return the data as a pandas DataFrame
            if response.status_code == 200:
                return pd.DataFrame(response.json())
            else:
                print(f"  [Attempt {attempt+1}] Server returned status code: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            # Catch network errors
            print(f"  [Attempt {attempt+1}] Network error: {e}")
            
        # Wait 2 seconds before trying again
        time.sleep(2)
        
    # Return an empty DataFrame if all attempts fail
    print(f"Failed to fetch {endpoint} after {retries} attempts.")
    return pd.DataFrame()


def download_raw_data(sessions_dict):
    # Create the 'raw_data' folder if it doesn't exist
    os.makedirs("raw_data", exist_ok=True)
    
    for track_name, session_key in sessions_dict.items():
        expected_file = f"raw_data/{track_name}_raw_laps.csv"
        
        # Check if the data is already downloaded
        if os.path.exists(expected_file):
            print(f"[!] Skipping {track_name}: Data already exists in 'raw_data' folder.")
            continue
            
        print(f"Downloading RAW data for {track_name} (Session {session_key})...")
        
        # Fetch lap data for the current session
        laps_df = fetch_openf1("laps", {"session_key": session_key})
        
        # Skip to the next track if no lap data is found
        if laps_df.empty or 'driver_number' not in laps_df.columns:
            print(f"  [!] Warning: No valid lap data found for {track_name}. Skipping to next track...")
            continue 
        
        # Save lap data to a CSV file
        laps_df.to_csv(f"raw_data/{track_name}_raw_laps.csv", index=False)
        
        # Get a list of unique drivers in this session
        drivers = laps_df['driver_number'].unique()
        
        all_telemetry = []
        all_location = []
        
        # Fetch telemetry and location data for each driver
        for driver in drivers:
            print(f"  Fetching driver {driver}...")
            tel_df = fetch_openf1("car_data", {"session_key": session_key, "driver_number": driver})
            loc_df = fetch_openf1("location", {"session_key": session_key, "driver_number": driver})
            
            # Add valid data to our lists
            if not tel_df.empty:
                all_telemetry.append(tel_df)
            if not loc_df.empty:
                all_location.append(loc_df)
            
        # Combine all driver data and save to CSV files
        if all_telemetry and all_location:
            pd.concat(all_telemetry, ignore_index=True).to_csv(f"raw_data/{track_name}_raw_telemetry.csv", index=False)
            pd.concat(all_location, ignore_index=True).to_csv(f"raw_data/{track_name}_raw_location.csv", index=False)
        
        print(f"Finished downloading RAW data for {track_name}.\n")

# Dictionary of track names and their session keys
target_sessions = {
    'Monza': 9158,        
    'Spa': 9141,          
    'Singapore': 9159,    
    'Suzuka': 9165        
}

# Start the download process
download_raw_data(target_sessions)