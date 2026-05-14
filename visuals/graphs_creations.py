import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
import numpy as np
import os
# need fixing to corner plot and add in legend

# Function to plot the F1 track layout by speed for a given track name, works similar to the previous function but with a continuous color gradient based on speed
def plot_speed_map_continuous(track_name, file_path='processed_data/golden_laps_final.csv'):
    
    absolute_path = os.path.abspath(file_path)
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
    single_lap['speed'] = pd.to_numeric(single_lap['speed'], errors='coerce')
    single_lap = single_lap.dropna(subset=['x', 'y', 'speed'])

    single_lap = pd.concat([single_lap, single_lap.iloc[[0]]], ignore_index=True)

    if track_name in ['Monza', 'Spa']:
        temp_x = single_lap['x'].copy()
        single_lap['x'] = -single_lap['y']
        single_lap['y'] = temp_x
        
    elif track_name == 'Suzuka':
        angle_degrees = 45 
        theta = np.radians(angle_degrees)
        c = np.cos(theta)
        s = np.sin(theta)
        
        temp_x = single_lap['x'].copy()
        temp_y = single_lap['y'].copy()
        single_lap['x'] = temp_x * c - temp_y * s
        single_lap['y'] = temp_x * s + temp_y * c

    print(f"Creating Continuous Speed Map for {track_name} (Driver {first_driver})...")

    x = single_lap['x'].values
    y = single_lap['y'].values
    speed = single_lap['speed'].values

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    fig, ax = plt.subplots(figsize=(16, 12))

    # build the LineCollection object with the segments and speed as the color array
    norm = plt.Normalize(speed.min(), speed.max())
    lc = LineCollection(segments, cmap='RdYlGn', norm=norm)
    lc.set_array(speed)
    lc.set_linewidth(8) 
    lc.set_capstyle('round') 

    
    line = ax.add_collection(lc)
    
    # add colorbar
    cbar = fig.colorbar(line, ax=ax)
    cbar.set_label('Speed (km/h)', fontsize=14, fontweight='bold')
    
    ax.set_title(f"F1 Telemetry: {track_name} Speed Heatmap", fontsize=18, fontweight='bold')
    ax.set_xlabel("X Position (meters)")
    ax.set_ylabel("Y Position (meters)")

    ax.axis('equal') 
    ax.grid(True, linestyle='--', alpha=0.3)
    
    margin = 500
    ax.set_xlim(x.min() - margin, x.max() + margin)
    ax.set_ylim(y.min() - margin, y.max() + margin)
    start_x, start_y = x[0], y[0]
    ax.plot(start_x, start_y, marker='*', markersize=7, 
            color='black', markeredgecolor='black', markeredgewidth=0.5, zorder=10)

    plt.show()

# print the speed map for each track
#plot_speed_map_continuous('Monza')
#plot_speed_map_continuous('Singapore')
#plot_speed_map_continuous('Spa')
#plot_speed_map_continuous('Suzuka')

#--------------------------------------------------------------------------------------------

# Function to plot braking zones by coloring track segments red when brake > 0 and gray otherwise, works similar to the previous function but with a binary color scheme based on braking status
def plot_braking_zones(track_name, file_path='processed_data/golden_laps_final.csv'):
    
    # 1. Load data safely
    absolute_path = os.path.abspath(file_path)
    if not os.path.exists(file_path):
        print(f"[!] Error: File not found at {absolute_path}")
        return

    df = pd.read_csv(file_path)
    track_data = df[df['Track'] == track_name]
    
    if track_data.empty:
        print(f"[!] No data found for track: {track_name}")
        return

    # 2. Extract single lap for the first driver
    first_driver = track_data['driver_number'].iloc[0]
    single_lap = track_data[track_data['driver_number'] == first_driver].copy()

    # 3. Clean numeric data (x, y, and brake)
    single_lap['x'] = pd.to_numeric(single_lap['x'], errors='coerce')
    single_lap['y'] = pd.to_numeric(single_lap['y'], errors='coerce')
    single_lap['brake'] = pd.to_numeric(single_lap['brake'], errors='coerce')
    single_lap = single_lap.dropna(subset=['x', 'y', 'brake'])

    # 4. Close the track loop (connect last point to first point)
    single_lap = pd.concat([single_lap, single_lap.iloc[[0]]], ignore_index=True)

    # 5. Apply track rotation (same as before)
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

    print(f"Creating Braking Zones Map for {track_name} (Driver {first_driver})...")

    # 6. Prepare points for continuous line segments
    x = single_lap['x'].values
    y = single_lap['y'].values
    brake = single_lap['brake'].values

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    # 7. Define segment colors: Red if braking (>0), Gray if coasting/accelerating
    segment_colors = ['red' if b > 0 else 'lightgray' for b in brake[:-1]]

    # 8. Create the plot
    fig, ax = plt.subplots(figsize=(16, 12))
    
    # Build the LineCollection with the custom colors
    lc = LineCollection(segments, colors=segment_colors, linewidths=8, capstyle='round')
    ax.add_collection(lc)
    
    # 9. Style the chart
    ax.set_title(f"F1 Telemetry: {track_name} Braking Zones", fontsize=18, fontweight='bold')
    ax.set_xlabel("X Position (meters)")
    ax.set_ylabel("Y Position (meters)")

    ax.axis('equal') 
    ax.grid(True, linestyle='--', alpha=0.3)
    
    # Set limits for LineCollection
    margin = 500
    ax.set_xlim(x.min() - margin, x.max() + margin)
    ax.set_ylim(y.min() - margin, y.max() + margin)

    # 10. Add a custom legend
    custom_legend = [
        Line2D([0], [0], color='red', lw=6, label='Braking (Brake > 0)'),
        Line2D([0], [0], color='lightgray', lw=6, label='Full Throttle / Coasting')
    ]
    ax.legend(handles=custom_legend, loc='upper right', fontsize=12)
    start_x, start_y = x[0], y[0]
    ax.plot(start_x, start_y, marker='*', markersize=7, 
            color='black', markeredgecolor='black', markeredgewidth=0.5, zorder=10)

    plt.show()

# Run the function
#plot_braking_zones('Monza')
#plot_braking_zones('Singapore')
#plot_braking_zones('Spa')
#plot_braking_zones('Suzuka')

#--------------------------------------------------------------------------------------------
def plot_corners_by_geometry(track_name, file_path='processed_data/golden_laps_final.csv'):
    
    absolute_path = os.path.abspath(file_path)
    if not os.path.exists(file_path):
        print(f"[!] Error: File not found at {absolute_path}")
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
    single_lap = pd.concat([single_lap, single_lap.iloc[[0]]], ignore_index=True)

    # --- Rotation Logic ---
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

    print(f"Calculating Corner Geometry for {track_name} (Driver {first_driver})...")

    x = single_lap['x'].values
    y = single_lap['y'].values

    # --- CORNER DETECTION ALGORITHM (Heading Angle) ---
    
    # 1. Calculate the difference between consecutive points
    dx = np.gradient(x)
    dy = np.gradient(y)
    
    # 2. Calculate the heading angle (direction) at each point
    heading_angle = np.arctan2(dy, dx)
    
    # 3. Unwrap the angle to prevent sudden jumps from 180 to -180 degrees
    unwrapped_angle = np.unwrap(heading_angle)
    
    # 4. Calculate the rate of change of the angle (first derivative)
    angle_change = np.abs(np.gradient(unwrapped_angle))
    
    # 5. Smooth the data to ignore sensor noise (micro-steering)
    # Using pandas rolling mean to average the change over a window of points
    window_size = 5
    smoothed_change = pd.Series(angle_change).rolling(window=window_size, center=True, min_periods=1).mean().values
    
    # 6. Define the sensitivity threshold for what counts as a "Corner"
    corner_threshold = 0.08

    # Boolean array: True if it's a corner, False if it's a straight
    is_corner = smoothed_change > corner_threshold

    # --- PLOTTING ---
    
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    # Color corners in Bright Purple, straights in light gray
    segment_colors = ['blue' if c else 'lightgray' for c in is_corner[:-1]]

    fig, ax = plt.subplots(figsize=(16, 12))
    lc = LineCollection(segments, colors=segment_colors, linewidths=8, capstyle='round')
    ax.add_collection(lc)
    
    ax.set_title(f"F1 Track Curvature: {track_name} (Corner Detection)", fontsize=18, fontweight='bold')
    ax.set_xlabel("X Position (meters)")
    ax.set_ylabel("Y Position (meters)")
    ax.axis('equal') 
    ax.grid(True, linestyle='--', alpha=0.3)
    
    margin = 500
    ax.set_xlim(x.min() - margin, x.max() + margin)
    ax.set_ylim(y.min() - margin, y.max() + margin)

    # Add Legend
    custom_legend = [
        Line2D([0], [0], color='blue', lw=6, label=f'Corner Detected (Threshold > {corner_threshold})'),
        Line2D([0], [0], color='lightgray', lw=6, label='Straight / Flat-out')
    ]
    ax.legend(handles=custom_legend, loc='upper right', fontsize=12)

    plt.show()

# Run the algorithm and plot the corners for each track - need to adjust the threshold for each track to get the best results
#plot_corners_by_geometry('Monza') # - 0.06 ,5
#plot_corners_by_geometry('Singapore') # - 0.06 ,5 , has problem with starting point!
#plot_corners_by_geometry('Spa')  #- 0.04 ,5
#plot_corners_by_geometry('Suzuka') # - 0.08 ,5

#--------------------------------------------------------------------------------------------

def plot_gear_shifts(track_name, file_path='processed_data/golden_laps_final.csv'):
    
    absolute_path = os.path.abspath(file_path)
    if not os.path.exists(file_path):
        print(f"[!] Error: File not found at {absolute_path}")
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
    single_lap['n_gear'] = pd.to_numeric(single_lap['n_gear'], errors='coerce')
    single_lap = single_lap.dropna(subset=['x', 'y', 'n_gear'])

    single_lap = pd.concat([single_lap, single_lap.iloc[[0]]], ignore_index=True)

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

    print(f"Creating Gear Shift Map for {track_name} (Driver {first_driver})...")

    x = single_lap['x'].values
    y = single_lap['y'].values
    gears = single_lap['n_gear'].values

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    gear_colors = {
        1: 'red', # Red
        2: 'orangered', # OrangeRed
        3: 'orange', # Orange
        4: 'gold', # Gold
        5: 'greenyellow', # GreenYellow
        6: 'limegreen', # LimeGreen
        7: 'deepskyblue', # DeepSkyBlue
        8: 'blueviolet'  # BlueViolet
    }

    segment_colors = [gear_colors.get(g, 'lightgray') for g in gears[:-1]]

    fig, ax = plt.subplots(figsize=(16, 12))
    
    lc = LineCollection(segments, colors=segment_colors, linewidths=8, capstyle='round')
    ax.add_collection(lc)
    
    # --- Light Theme Setup ---
    bg_color = 'white'
    ax.set_facecolor(bg_color)
    fig.patch.set_facecolor(bg_color)
    
    ax.set_title(f"F1 Telemetry: {track_name} Gear Selection", fontsize=18, fontweight='bold', color='#333333')
    ax.set_xlabel("X Position (meters)", color='black')
    ax.set_ylabel("Y Position (meters)", color='black')

    ax.axis('equal') 
    ax.tick_params(colors='black')
    ax.grid(True, linestyle='--', alpha=0.5, color='lightgray')
    
    margin = 500
    ax.set_xlim(x.min() - margin, x.max() + margin)
    ax.set_ylim(y.min() - margin, y.max() + margin)

    # --- Legend Fix ---
    legend_elements = [Line2D([0], [0], color=color, lw=6, label=f'Gear {gear}') 
                       for gear, color in gear_colors.items()]
    
    ax.legend(handles=legend_elements, loc='lower right', 
              fontsize=12, facecolor='white', edgecolor='lightgray', 
              labelcolor='black', title='Gears', title_fontsize=14, framealpha=0.85)
    start_x, start_y = x[0], y[0]
    ax.plot(start_x, start_y, marker='*', markersize=7, 
            color='black', markeredgecolor='black', markeredgewidth=0.5, zorder=10)

    plt.tight_layout(pad=3.0)
    plt.show()

#plot_gear_shifts('Monza')
#plot_gear_shifts('Singapore')
#plot_gear_shifts('Spa')
#plot_gear_shifts('Suzuka')

#--------------------------------------------------------------------------------------------

def plot_throttle_zones(track_name, file_path='processed_data/golden_laps_final.csv'):
    
    # 1. Load data safely
    absolute_path = os.path.abspath(file_path)
    if not os.path.exists(file_path):
        print(f"[!] Error: File not found at {absolute_path}")
        return

    df = pd.read_csv(file_path)
    track_data = df[df['Track'] == track_name]
    
    if track_data.empty:
        print(f"[!] No data found for track: {track_name}")
        return

    # 2. Extract single lap for the first driver
    first_driver = track_data['driver_number'].iloc[0]
    single_lap = track_data[track_data['driver_number'] == first_driver].copy()

    # 3. Clean numeric data (x, y, and brake)
    single_lap['x'] = pd.to_numeric(single_lap['x'], errors='coerce')
    single_lap['y'] = pd.to_numeric(single_lap['y'], errors='coerce')
    single_lap['throttle'] = pd.to_numeric(single_lap['throttle'], errors='coerce')
    single_lap = single_lap.dropna(subset=['x', 'y', 'throttle'])

    # 4. Close the track loop (connect last point to first point)
    single_lap = pd.concat([single_lap, single_lap.iloc[[0]]], ignore_index=True)

    # 5. Apply track rotation (same as before)
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

    print(f"Creating Braking Zones Map for {track_name} (Driver {first_driver})...")

    # 6. Prepare points for continuous line segments
    x = single_lap['x'].values
    y = single_lap['y'].values
    throttle = single_lap['throttle'].values

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    # 7. Define segment colors: Lime if throttle (>0), Light  Gray if coasting/accelerating
    segment_colors = ['lime' if t > 0 else 'lightgray' for t in throttle[:-1]]

    # 8. Create the plot
    fig, ax = plt.subplots(figsize=(16, 12))
    
    # Build the LineCollection with the custom colors
    lc = LineCollection(segments, colors=segment_colors, linewidths=8, capstyle='round')
    ax.add_collection(lc)
    
    # 9. Style the chart
    ax.set_title(f"F1 Telemetry: {track_name} Throttle Zones", fontsize=18, fontweight='bold')
    ax.set_xlabel("X Position (meters)")
    ax.set_ylabel("Y Position (meters)")

    ax.axis('equal') 
    ax.grid(True, linestyle='--', alpha=0.3)
    
    # Set limits for LineCollection
    margin = 500
    ax.set_xlim(x.min() - margin, x.max() + margin)
    ax.set_ylim(y.min() - margin, y.max() + margin)

    # 10. Add a custom legend
    custom_legend = [
        Line2D([0], [0], color='lime', lw=6, label='Throttle (Throttle > 0)'),
        Line2D([0], [0], color='lightgray', lw=6, label='No Throttle / Coasting'),
        Line2D([0], [0], color='black', lw=6, label='Starting Point', marker='*', markersize=20, markeredgewidth=0.5)
    ]
    ax.legend(handles=custom_legend, loc='upper right', fontsize=12)

    start_x, start_y = x[0], y[0]
    ax.plot(start_x, start_y, marker='*', markersize=7, 
            color='black', markeredgecolor='black', markeredgewidth=0.5, zorder=10)

    plt.show()

# Run the function
#plot_throttle_zones('Monza')
#plot_throttle_zones('Singapore')
#plot_throttle_zones('Spa')
#plot_throttle_zones('Suzuka')
