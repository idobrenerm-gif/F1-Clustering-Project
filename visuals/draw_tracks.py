import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

def plot_f1_track(track_name, file_path='data/processed_data/New_Qualifying_fastest_laps_telemetry_with_corners.csv'):
    
    absolute_path = os.path.abspath(file_path)
    print(f"\n[DEBUG] Loading file from: {absolute_path}")
    
    if not os.path.exists(file_path):
        print(f"[!] Error: File not found. Please check the path.")
        return

    df = pd.read_csv(file_path)
    
    track_data = df[df['Track'] == track_name]
    
    if track_data.empty:
        print(f"[!] No data found for track: {track_name}")
        return

    first_driver = track_data['driver_number'].iloc[0]
    single_lap = track_data[track_data['driver_number'] == first_driver].copy()

    single_lap['x'] = pd.to_numeric(single_lap['x'], errors='coerce')
    single_lap['y'] = pd.to_numeric(single_lap['y'], errors='coerce')
    single_lap = single_lap.dropna(subset=['x', 'y'])

    # Close the gap at the finish line
    single_lap = pd.concat([single_lap, single_lap.iloc[[0]]], ignore_index=True)

    # --- ROTATION LOGIC ---
    
    # 1. 90-degree left rotation for Monza and Spa
    if track_name in ['Monza', 'Spa']:
        print(f"[INFO] Applying 90-degree left rotation for {track_name}...")
        temp_x = single_lap['x'].copy()
        single_lap['x'] = -single_lap['y']
        single_lap['y'] = temp_x
        
    # 2. 45-degree rotation for Suzuka
    elif track_name == 'Suzuka':
        print(f"[INFO] Applying exact angle rotation for {track_name}...")
        
        # Define the rotation angle in degrees
        angle_degrees = 45 
        theta = np.radians(angle_degrees)
        
        c = np.cos(theta)
        s = np.sin(theta)
        
        temp_x = single_lap['x'].copy()
        temp_y = single_lap['y'].copy()
        
        # Apply the 2D rotation matrix formula
        single_lap['x'] = temp_x * c - temp_y * s
        single_lap['y'] = temp_x * s + temp_y * c

    print(f"Printing {track_name} track for driver number: {first_driver}...")

    plt.figure(figsize=(16, 12))
    plt.plot(single_lap['x'], single_lap['y'], color='gray', linewidth=3, label='Track Path')
    
    plt.title(f"F1 Track Layout: {track_name}", fontsize=16, fontweight='bold')
    plt.xlabel("X Position (meters)")
    plt.ylabel("Y Position (meters)")

    plt.axis('equal') 
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    plt.show()

# print the track layout for each track
plot_f1_track('Monza')
plot_f1_track('Singapore')
plot_f1_track('Spa')
plot_f1_track('Suzuka')