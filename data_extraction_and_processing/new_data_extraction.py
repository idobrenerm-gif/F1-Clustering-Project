import requests
import pandas as pd
import os
import time

def get_drivers_for_session(meeting_id, session_id):
    """Fetches the exact list of drivers that participated in a specific session."""
    url = f"https://api.openf1.org/v1/sessions?meeting_key={meeting_id}&session_key={session_id}"
    try:
        res = requests.get(url, timeout=30)
        if res.status_code == 200 and len(res.json()) > 0:
            drivers_url = f"https://api.openf1.org/v1/drivers?meeting_key={meeting_id}&session_key={session_id}"
            d_res = requests.get(drivers_url, timeout=30)
            if d_res.status_code == 200:
                return [d['driver_number'] for d in d_res.json()]
    except Exception as e:
        print(f"  [!] Failed to fetch drivers for session {session_id}: {e}")
    return []

def fetch_with_retry(url, max_retries=3):
    """Attempts to fetch data from a URL with automatic retries on failure."""
    for attempt in range(max_retries):
        try:
            res = requests.get(url, timeout=45) 
            if res.status_code == 200:
                return res.json()
            elif res.status_code == 429: # Too many requests limit
                print(f"    [Rate Limit] Sleeping for 2s... (Attempt {attempt+1}/{max_retries})")
                time.sleep(2)
            else:
                return []
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                print(f"\n    [!] Permanent timeout after {max_retries} retries for URL: {url}")
                return []
    return []

def download_full_track_data_smart():
    # Set the new target directory for Qualifying data
    base_dir = "raw_data_qualifying" 
    os.makedirs(base_dir, exist_ok=True)

    # 2023 Qualifying Sessions identifiers
    track_keys = {
        'Monza': {'meeting_key': 1218, 'session_key': 9153}, 
        'Spa': {'meeting_key': 1216, 'session_key': 9135},
        'Singapore': {'meeting_key': 1219, 'session_key': 9161},
        'Suzuka': {'meeting_key': 1220, 'session_key': 9169}
    }

    print(f"--- Starting Data Ingestion into '{base_dir}' folder ---")

    for track_name, keys in track_keys.items():
        session_id = keys['session_key']
        meeting_id = keys['meeting_key']
        print(f"\n[Processing] Track: {track_name} | Meeting: {meeting_id} | Session: {session_id}")
        
        # Define expected file paths in the new directory
        loc_path = os.path.join(base_dir, f"{track_name}_raw_location.csv")
        car_path = os.path.join(base_dir, f"{track_name}_raw_telemetry.csv")
        laps_path = os.path.join(base_dir, f"{track_name}_raw_laps.csv")
        
        need_loc = not os.path.exists(loc_path)
        need_car = not os.path.exists(car_path)
        need_laps = not os.path.exists(laps_path)

        if not need_loc and not need_car and not need_laps:
            print(f"  [SKIPPED] All files for {track_name} already exist in {base_dir}.")
            continue

        # Dynamically fetch the drivers who actually participated
        session_drivers = get_drivers_for_session(meeting_id, session_id)
        if not session_drivers:
            print(f"  [!] Could not fetch dynamic drivers. Falling back to default list.")
            session_drivers = [1, 2, 3, 4, 10, 11, 14, 16, 18, 20, 22, 23, 24, 27, 31, 40, 44, 55, 63, 77, 81]

        print(f"  -> Found {len(session_drivers)} drivers for this session.")

        track_location_data = []
        track_car_data = []
        track_laps_data = []

        for driver in session_drivers:
            print(f"  -> Fetching data for Driver {driver}...", end="\r")
            
            # 1. Location Data
            if need_loc:
                loc_url = f"https://api.openf1.org/v1/location?meeting_key={meeting_id}&session_key={session_id}&driver_number={driver}"
                data = fetch_with_retry(loc_url)
                if data: track_location_data.append(pd.DataFrame(data))

            # 2. Telemetry Data
            if need_car:
                car_url = f"https://api.openf1.org/v1/car_data?meeting_key={meeting_id}&session_key={session_id}&driver_number={driver}"
                data = fetch_with_retry(car_url)
                if data: track_car_data.append(pd.DataFrame(data))
                
            # 3. Laps Data
            if need_laps:
                laps_url = f"https://api.openf1.org/v1/laps?meeting_key={meeting_id}&session_key={session_id}&driver_number={driver}"
                data = fetch_with_retry(laps_url)
                if data: track_laps_data.append(pd.DataFrame(data))
            
            # Brief pause to respect API limits
            time.sleep(0.5)

        print(f"  -> Download complete for {track_name}! Merging files...                       ")

        # Save merged files into the new directory
        if need_loc and track_location_data:
            pd.concat(track_location_data, ignore_index=True).to_csv(loc_path, index=False)
            print(f"  [SUCCESS] Location data saved.")

        if need_car and track_car_data:
            pd.concat(track_car_data, ignore_index=True).to_csv(car_path, index=False)
            print(f"  [SUCCESS] Telemetry data saved.")
            
        if need_laps and track_laps_data:
            pd.concat(track_laps_data, ignore_index=True).to_csv(laps_path, index=False)
            print(f"  [SUCCESS] Laps data saved.")

    print("\n--- All Data Downloaded & Saved Successfully to 'raw_data_qualifying' ---")

#download_full_track_data_smart()