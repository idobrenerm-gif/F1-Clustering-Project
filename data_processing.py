import pandas as pd
import os

def process_golden_laps(tracks):
    # Create output folder if it doesn't exist
    os.makedirs("processed_data", exist_ok=True)
    all_golden_data = [] 
    
    for track_name in tracks:
        print(f"Processing data for {track_name}...")
        
        # Define file paths
        laps_file = f"raw_data_2/{track_name}_raw_laps.csv"
        tel_file = f"raw_data_2/{track_name}_raw_telemetry.csv"
        loc_file = f"raw_data_2/{track_name}_raw_location.csv"

        print(f"  Loading files for {track_name}...")
        # Load CSV files into DataFrames
        laps_df = pd.read_csv(laps_file)
        tel_df = pd.read_csv(tel_file)
        loc_df = pd.read_csv(loc_file)
        
        print(f"  Converting and syncing timezones...")
        # Convert dates to standard timezone-aware format
        laps_df['date_start'] = pd.to_datetime(laps_df['date_start'], utc=True, format='mixed')
        tel_df['date'] = pd.to_datetime(tel_df['date'], utc=True, format='mixed')
        loc_df['date'] = pd.to_datetime(loc_df['date'], utc=True, format='mixed')
        
        print(f"  Calculating lap times and merging...")
        # Calculate end time of the lap if missing
        if 'date_end' not in laps_df.columns:
            laps_df['date_end'] = laps_df['date_start'] + pd.to_timedelta(laps_df['lap_duration'], unit='s')
        else:
            laps_df['date_end'] = pd.to_datetime(laps_df['date_end'], utc=True, format='mixed')      
       
        # Keep only laps with a valid duration
        valid_laps = laps_df.dropna(subset=['lap_duration'])
        if valid_laps.empty:
            continue
            
        # Find the fastest lap for each driver
        best_lap_indices = valid_laps.groupby('driver_number')['lap_duration'].idxmin()
        golden_laps = valid_laps.loc[best_lap_indices]
        
        for _, row in golden_laps.iterrows():
            driver = row['driver_number']
            t_start = row['date_start']
            t_end = row['date_end']
            
            # Filter telemetry data for this specific lap
            driver_tel = tel_df[(tel_df['driver_number'] == driver) & 
                                (tel_df['date'] >= t_start) & 
                                (tel_df['date'] <= t_end)].sort_values('date')
                                
            # Filter location data for this specific lap
            driver_loc = loc_df[(loc_df['driver_number'] == driver) & 
                                (loc_df['date'] >= t_start) & 
                                (loc_df['date'] <= t_end)].sort_values('date')
            
            if not driver_tel.empty and not driver_loc.empty:
                # Merge telemetry and location by closest timestamp
                merged_lap = pd.merge_asof(
                    left=driver_tel, 
                    right=driver_loc[['date', 'x', 'y', 'z']], 
                    on='date', 
                    direction='nearest', 
                    tolerance=pd.Timedelta(milliseconds=300)
                )
                
                # Remove rows with missing coordinates
                merged_lap = merged_lap.dropna(subset=['x', 'y'])
                
                # Add track name and lap time
                merged_lap['Track'] = track_name
                merged_lap['Lap_Time'] = row['lap_duration']
                
                # Save the processed data
                all_golden_data.append(merged_lap)
                
    if not all_golden_data:
        print("No data was processed. Check your raw_data folder.")
        return None
        
    # Combine all processed laps into one DataFrame
    final_dataset = pd.concat(all_golden_data, ignore_index=True)
    
    # Reorder columns to a clean format
    cols_order = ['Track', 'driver_number', 'Lap_Time', 'date', 'x', 'y', 'speed', 'throttle', 'brake', 'n_gear']
    cols_order = [c for c in cols_order if c in final_dataset.columns]
    final_dataset = final_dataset[cols_order]
    
    # Save the final dataset to a CSV file
    output_path = "processed_data/golden_laps_final.csv"
    final_dataset.to_csv(output_path, index=False)
    print(f"\nSuccess! Processed data saved to {output_path} with {len(final_dataset)} rows.")
    return final_dataset

# List of tracks to process
tracks_to_process = ['Monza', 'Spa', 'Singapore', 'Suzuka']
process_golden_laps(tracks_to_process)