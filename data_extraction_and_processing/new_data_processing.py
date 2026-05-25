import pandas as pd
import os

def generate_qualifying_fastest_laps():
    print("Starting data processing for Qualifying sessions...")
    
    raw_data_dir = 'raw_data_qualifying'
    processed_data_dir = 'processed_data'
    output_file = os.path.join(processed_data_dir, 'New_Qualifying_fastest_laps_telemetry.csv')
    
    os.makedirs(processed_data_dir, exist_ok=True)
    
    tracks = ['Monza', 'Singapore', 'Spa', 'Suzuka']
    all_pure_data = []
    
    for track in tracks:
        print(f"Processing track: {track}...")
        
        laps_path = os.path.join(raw_data_dir, f'{track}_raw_laps.csv')
        loc_path = os.path.join(raw_data_dir, f'{track}_raw_location.csv')
        tel_path = os.path.join(raw_data_dir, f'{track}_raw_telemetry.csv')
        
        if not (os.path.exists(laps_path) and os.path.exists(loc_path) and os.path.exists(tel_path)):
            print(f"  Warning: Missing data files for {track}. Skipping.")
            continue
            
        laps_df = pd.read_csv(laps_path)
        loc_df = pd.read_csv(loc_path)
        tel_df = pd.read_csv(tel_path)
        
        laps_df['date_start'] = pd.to_datetime(laps_df['date_start'], format='ISO8601')
        loc_df['date'] = pd.to_datetime(loc_df['date'], format='ISO8601')
        tel_df['date'] = pd.to_datetime(tel_df['date'], format='ISO8601')
        
        # 1. Keep only laps that are NOT out-laps AND have a valid lap duration
        valid_laps = laps_df[
            (~laps_df['is_pit_out_lap'].isin([True, 'True', 'true', 1])) & 
            (laps_df['lap_duration'].notna())
        ].copy()
        
        # 2. Find the absolute fastest lap for each driver (Naturally ignores slow in-laps)
        fastest_laps_indices = valid_laps.groupby('driver_number')['lap_duration'].idxmin()
        fastest_laps = valid_laps.loc[fastest_laps_indices]
        
        print(f"  Found {len(fastest_laps)} valid fastest laps.")
        
        for _, lap in fastest_laps.iterrows():
            driver = lap['driver_number']
            start_time = lap['date_start']
            end_time = start_time + pd.to_timedelta(lap['lap_duration'], unit='s')
            
            driver_loc = loc_df[(loc_df['driver_number'] == driver) & 
                                (loc_df['date'] >= start_time) & 
                                (loc_df['date'] <= end_time)].sort_values('date')
                                
            driver_tel = tel_df[(tel_df['driver_number'] == driver) & 
                                (tel_df['date'] >= start_time) & 
                                (tel_df['date'] <= end_time)].sort_values('date')
            
            if driver_loc.empty or driver_tel.empty:
                print(f"  Missing telemetry/location for driver {driver}. Skipping.")
                continue
                
            merged_lap = pd.merge_asof(driver_tel, driver_loc[['date', 'x', 'y']], 
                                       on='date', direction='nearest')
            
            merged_lap['Track'] = track
            merged_lap['lap_duration'] = lap['lap_duration']
            
            final_columns = [
                'Track', 'driver_number', 'lap_duration', 
                'x', 'y', 'speed', 'brake', 'throttle', 'n_gear', 'rpm', 'drs'
            ]
            merged_lap = merged_lap[final_columns]
            
            all_pure_data.append(merged_lap)
            
    if all_pure_data:
        final_df = pd.concat(all_pure_data, ignore_index=True)
        final_df.to_csv(output_file, index=False)
        print(f"\nSuccess! Qualifying data saved to: {output_file}")
        return final_df
    else:
        print("Error: No valid data found to merge.")
        return None

generate_qualifying_fastest_laps()