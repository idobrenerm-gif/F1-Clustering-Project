import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
import numpy as np
import os

# has problem with the start/finish line in suzuka - need fixing! 

import pandas as pd
import numpy as np
import os

def add_is_corner_column_geofenced(file_path='processed_data/golden_laps_final.csv', output_path='processed_data/golden_laps_final.csv'):
    
    if not os.path.exists(file_path):
        print(f"[!] Error: File not found at {file_path}")
        return None

    df = pd.read_csv(file_path)
    processed_frames = []

    for track in df['Track'].unique():
        track_df = df[df['Track'] == track].copy()
        
        track_df['x'] = pd.to_numeric(track_df['x'], errors='coerce')
        track_df['y'] = pd.to_numeric(track_df['y'], errors='coerce')
        track_df = track_df.dropna(subset=['x', 'y'])

        # Calculate geometric features
        dx = np.gradient(track_df['x'])
        dy = np.gradient(track_df['y'])
        heading_angle = np.arctan2(dy, dx)
        unwrapped_angle = np.unwrap(heading_angle)
        angle_change = np.abs(np.gradient(unwrapped_angle))
        
        window_size = 5
        smoothed_change = pd.Series(angle_change).rolling(window=window_size, center=True, min_periods=1).mean().values
        if track == 'Suzuka':
            corner_threshold = 0.08
        else:
            corner_threshold = 0.06
        
        is_corner_raw = smoothed_change > corner_threshold

        # --- GEOFENCING FIX FOR START/FINISH LINE ---
        # 1. Identify the starting coordinates
        start_x = track_df['x'].iloc[0]
        start_y = track_df['y'].iloc[0]

        # 2. Calculate the distance of every point from the start line
        distances_to_start = np.sqrt((track_df['x'] - start_x)**2 + (track_df['y'] - start_y)**2)

        # 3. Define an exclusion radius (e.g., 200 meters around the start line)
        # Any point within this radius will be forced to False (straight line)
        exclusion_radius = 1000
        
        # 4. Apply the exclusion
        is_corner_raw = is_corner_raw & (distances_to_start > exclusion_radius)
        # --------------------------------------------

        track_df['is_corner'] = is_corner_raw
        processed_frames.append(track_df)

    final_df = pd.concat(processed_frames, ignore_index=True)
    final_df.to_csv(output_path, index=False)
    print(f"[SUCCESS] Added 'is_corner' column using geofencing. Saved to: {output_path}")
    
    return final_df

# הרצת הפונקציה
#updated_df = add_is_corner_column_geofenced()



def plot_corner_validation_map(track_name, file_path='processed_data/golden_laps_final.csv'):
    
    absolute_path = os.path.abspath(file_path)
    if not os.path.exists(file_path):
        print(f"[!] Error: File not found at {absolute_path}")
        return

    df = pd.read_csv(file_path)
    track_data = df[df['Track'] == track_name]
    
    if track_data.empty:
        print(f"[!] No data found for track: {track_name}")
        return

    # Extract single lap
    first_driver = track_data['driver_number'].iloc[0]
    single_lap = track_data[track_data['driver_number'] == first_driver].copy()

    # Clean numeric data, now including 'is_corner'
    single_lap['x'] = pd.to_numeric(single_lap['x'], errors='coerce')
    single_lap['y'] = pd.to_numeric(single_lap['y'], errors='coerce')
    # Fill NaN in is_corner with False just in case
    single_lap['is_corner'] = single_lap['is_corner'].fillna(False)
    single_lap = single_lap.dropna(subset=['x', 'y'])

    # Close the loop
    single_lap = pd.concat([single_lap, single_lap.iloc[[0]]], ignore_index=True)

    # Apply track rotation
    if track_name in ['Monza', 'Spa']:
        temp_x = single_lap['x'].copy()
        single_lap['x'] = -single_lap['y']
        single_lap['y'] = temp_x
        
    elif track_name == 'Suzuka':
        angle = np.radians(45)
        c, s = np.cos(angle), np.sin(angle)
        temp_x, temp_y = single_lap['x'].copy(), single_lap['y'].copy()
        single_lap['x'] = temp_x * c - temp_y * s
        single_lap['y'] = temp_x * s + temp_y * c

    print(f"Creating Corner Validation Map for {track_name} (Driver {first_driver})...")

    # Prepare data for LineCollection
    x = single_lap['x'].values
    y = single_lap['y'].values
    is_corner = single_lap['is_corner'].values

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    # Set segment colors based on the boolean column
    # Brown for corners, Light Gray for straights
    segment_colors = ['#8B4513' if corner else '#E0E0E0' for corner in is_corner[:-1]]

    # Create the plot
    fig, ax = plt.subplots(figsize=(16, 12))
    
    lc = LineCollection(segments, colors=segment_colors, linewidths=10, capstyle='round', zorder=5)
    ax.add_collection(lc)
    
    # Theme Setup (Light Theme for clarity)
    bg_color = 'white'
    ax.set_facecolor(bg_color)
    fig.patch.set_facecolor(bg_color)
    
    ax.set_title(f"F1 Telemetry: {track_name} Corner Validation", fontsize=20, fontweight='bold', color='#111111')
    ax.set_xlabel("X Position (meters)", color='#333333')
    ax.set_ylabel("Y Position (meters)", color='#333333')

    ax.axis('equal') 
    ax.tick_params(colors='#333333')
    ax.grid(True, linestyle='-', alpha=0.15, color='gray')
    
    margin = 500
    ax.set_xlim(x.min() - margin, x.max() + margin)
    ax.set_ylim(y.min() - margin, y.max() + margin)
  
    # --- Custom Legend ---
    legend_elements = [
        Line2D([0], [0], color='#8B4513', lw=8, label='Corner (is_corner = True)'),
        Line2D([0], [0], color='#E0E0E0', lw=8, label='Straight (is_corner = False)')
    ]
    ax.legend(handles=legend_elements, loc='upper right', 
              fontsize=14, facecolor='white', edgecolor='#CCCCCC', labelcolor='#333333')

    plt.tight_layout(pad=2.5)
    plt.show()

# Run the validation on Monza or Suzuka!
#plot_corner_validation_map('Monza')
#plot_corner_validation_map('Singapore')
#plot_corner_validation_map('Spa')
#plot_corner_validation_map('Suzuka')