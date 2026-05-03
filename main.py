import pandas as pd
from api_client import OpenF1Client
from feature_engineering import CornerDetector

def main():
    api = OpenF1Client()
    detector = CornerDetector()
    #list of session keys for the races we want to analyze: baharin, silverstone, spa, monza
    session_keys = [9468, 9558, 9564, 9582] 
    
    all_corners_data = []

    print("Starting huge data extraction for 4 races...")

    # external loop over the 4 race sessions
    for session_key in session_keys:
        print(f"\n{'='*40}")
        print(f"Processing Race Session: {session_key}")
        print(f"{'='*40}")
        
        df_drivers = api.get_drivers(session_key)
        
        #if there are no drivers for this session, skip to the next one
        if df_drivers.empty:
            print(f"No driver data for session {session_key}. Skipping.")
            continue
            
        driver_numbers = df_drivers['driver_number'].unique()
        
        # internal loop: iterate over drivers within the current racersession
        for drv in driver_numbers:
            print(f"  -> Extracting corners for driver {drv}...")
            
            df_tel = api.get_telemetry(session_key, drv)
            if df_tel.empty:
                continue
                
            df_corners = detector.extract_corners(df_tel)
            
            if not df_corners.empty:
                # recording driver and session info for later merging
                df_corners['driver_number'] = drv
                df_corners['session_key'] = session_key 
                
                all_corners_data.append(df_corners)

    print("\nStep 3: Combining all data and saving to CSV...")
    if all_corners_data:
        # unifying all detected corners into a single DataFrame
        final_dataset = pd.concat(all_corners_data, ignore_index=True)
        
        output_filename = "F1_4_Races_All_Corners.csv"
        final_dataset.to_csv(output_filename, index=False)
        
        print("-" * 40)
        print(f"SUCCESS! Total corners detected across all races: {len(final_dataset)}")
        print(f"Data saved to: {output_filename}")
        print("-" * 40)
    else:
        print("Warning: No corners were detected at all.")

if __name__ == "__main__":
    main()