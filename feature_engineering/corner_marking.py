import pandas as pd
import numpy as np
import os

def add_is_corner_column(file_path='processed_data/New_Qualifying_fastest_laps_telemetry.csv', 
                                         output_path='processed_data/New_Qualifying_fastest_laps_telemetry_with_corners.csv'):
    
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

        # 1. Calculate geometric features
        dx = np.gradient(track_df['x'])
        dy = np.gradient(track_df['y'])
        heading_angle = np.arctan2(dy, dx)
        unwrapped_angle = np.unwrap(heading_angle)
        
        # We need the RAW gradient (with signs) to know left vs right
        raw_angle_change = np.gradient(unwrapped_angle)
        
        window_size = 5
        smoothed_raw_change = pd.Series(raw_angle_change).rolling(window=window_size, center=True, min_periods=1).mean().values
        
        # Absolute change for thresholding (Your original logic)
        smoothed_abs_change = np.abs(smoothed_raw_change)

        if track == 'Suzuka':
            corner_threshold = 0.08
        else:
            corner_threshold = 0.06
        
        # Base corner detection
        is_corner_raw = smoothed_abs_change > corner_threshold

        # --- THE FIX: CHICANE & ESSES SPLITTER ---
        # Map direction: +1 for Left, -1 for Right. 
        # Using 0.02 as a mini-threshold to ignore straight-line micro-vibrations
        direction = np.zeros_like(smoothed_raw_change)
        direction[smoothed_raw_change > 0.02] = 1
        direction[smoothed_raw_change < -0.02] = -1
        
        # Forward fill to maintain the current turn direction even if it drops slightly for a millisecond
        dir_series = pd.Series(direction).replace(0, np.nan).ffill().fillna(0)
        dir_shift = dir_series.shift(1).fillna(0)
        
        # Find exactly where direction flips from Left(1) to Right(-1) or vice versa
        flip_mask = (dir_series != dir_shift) & (dir_series != 0) & (dir_shift != 0)
        
        # Inject a micro-gap (False) at the exact transition point to split the sequence!
        flip_indices = np.where(flip_mask)[0]
        for idx in flip_indices:
            # Force False for 3 telemetry rows (about ~0.8 seconds gap) to ensure the grouping algorithm splits it
            start_gap = max(0, idx - 1)
            end_gap = min(len(is_corner_raw), idx + 2)
            is_corner_raw[start_gap:end_gap] = False
        # -----------------------------------------

        # --- GEOFENCING FIX FOR START/FINISH LINE ---
        start_x = track_df['x'].iloc[0]
        start_y = track_df['y'].iloc[0]
        distances_to_start = np.sqrt((track_df['x'] - start_x)**2 + (track_df['y'] - start_y)**2)
        exclusion_radius = 1000
        
        is_corner_raw = is_corner_raw & (distances_to_start > exclusion_radius)
        # --------------------------------------------

        track_df['is_corner'] = is_corner_raw
        processed_frames.append(track_df)

    final_df = pd.concat(processed_frames, ignore_index=True)
    final_df.to_csv(output_path, index=False)
    
    print(f"[SUCCESS] Advanced 'is_corner' added with Chicane Splitting!")
    print(f"Saved to: {output_path}")
    
    return final_df

add_is_corner_column()