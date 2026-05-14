import requests
import pandas as pd
import os
import time

def download_full_track_data_smart():
    base_dir = "raw_data_2"
    os.makedirs(base_dir, exist_ok=True)

    track_keys = {
        'Monza': {'meeting_key': 1218, 'session_key': 9153},
        'Spa': {'meeting_key': 1216, 'session_key': 9135},
        'Singapore': {'meeting_key': 1219, 'session_key': 9161},
        'Suzuka': {'meeting_key': 1220, 'session_key': 9169}
    }

    drivers = [1, 2, 3, 4, 10, 11, 14, 16, 18, 20, 22, 23, 24, 27, 31, 40, 44, 55, 63, 77, 81]

    print("--- Starting SMART Data Ingestion (Skips Existing Files) ---")

    for track_name, keys in track_keys.items():
        session_id = keys['session_key']
        meeting_id = keys['meeting_key']
        print(f"\n[Processing] Track: {track_name} | Meeting: {meeting_id} | Session: {session_id}")
        
        # Define expected file paths
        loc_path = os.path.join(base_dir, f"{track_name}_raw_location.csv")
        car_path = os.path.join(base_dir, f"{track_name}_raw_telemetry.csv")
        laps_path = os.path.join(base_dir, f"{track_name}_raw_laps.csv")
        
        # Check what needs to be downloaded
        need_loc = not os.path.exists(loc_path)
        need_car = not os.path.exists(car_path)
        need_laps = not os.path.exists(laps_path)

        if not need_loc and not need_car and not need_laps:
            print(f"  [SKIPPED] All files for {track_name} already exist in {base_dir}. Moving to next.")
            continue

        track_location_data = []
        track_car_data = []
        track_laps_data = []

        for driver in drivers:
            print(f"  -> Fetching remaining data for Driver {driver}...", end="\r")
            
            try:
                # 1. Location (Only if missing)
                if need_loc:
                    loc_url = f"https://api.openf1.org/v1/location?meeting_key={meeting_id}&session_key={session_id}&driver_number={driver}"
                    loc_res = requests.get(loc_url, timeout=30)
                    if loc_res.status_code == 200 and len(loc_res.json()) > 0:
                        track_location_data.append(pd.DataFrame(loc_res.json()))

                # 2. Telemetry (Only if missing)
                if need_car:
                    car_url = f"https://api.openf1.org/v1/car_data?meeting_key={meeting_id}&session_key={session_id}&driver_number={driver}"
                    car_res = requests.get(car_url, timeout=30)
                    if car_res.status_code == 200 and len(car_res.json()) > 0:
                        track_car_data.append(pd.DataFrame(car_res.json()))
                    
                # 3. Laps (Only if missing)
                if need_laps:
                    laps_url = f"https://api.openf1.org/v1/laps?meeting_key={meeting_id}&session_key={session_id}&driver_number={driver}"
                    laps_res = requests.get(laps_url, timeout=30)
                    if laps_res.status_code == 200 and len(laps_res.json()) > 0:
                        track_laps_data.append(pd.DataFrame(laps_res.json()))
                
                # Delay only if we actually made requests
                if need_loc or need_car or need_laps:
                    time.sleep(0.5)
                
            except Exception as e:
                print(f"\n  [!] Network timeout for driver {driver}. Moving to next.")

        print(f"  -> Download complete for {track_name}! Merging missing files...       ")

        if need_loc and track_location_data:
            final_loc_df = pd.concat(track_location_data, ignore_index=True)
            final_loc_df.to_csv(loc_path, index=False)
            print(f"  [SUCCESS] Location data saved: {loc_path}")
        elif not need_loc:
            print(f"  [INFO] Location data already exists. Skipped.")

        if need_car and track_car_data:
            final_car_df = pd.concat(track_car_data, ignore_index=True)
            final_car_df.to_csv(car_path, index=False)
            print(f"  [SUCCESS] Telemetry data saved: {car_path}")
        elif not need_car:
            print(f"  [INFO] Telemetry data already exists. Skipped.")
            
        if need_laps and track_laps_data:
            final_laps_df = pd.concat(track_laps_data, ignore_index=True)
            final_laps_df.to_csv(laps_path, index=False)
            print(f"  [SUCCESS] Laps data saved: {laps_path}")
        elif not need_laps:
            print(f"  [INFO] Laps data already exists. Skipped.")

    print("\n--- All Data Downloaded & Verified Successfully ---")

if __name__ == "__main__":
    download_full_track_data_smart()