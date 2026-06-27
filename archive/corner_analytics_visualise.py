import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

def load_and_prepare_data(file_path="../F1-Clustering-Project/data/raw_data_qualifying/golden_laps_final.csv"):
    """Load the dataset and ensure correct data types."""
    if not os.path.exists(file_path):
        # Fallback to current directory if not in processed_data folder
        file_path = "golden_laps_final.csv"
        if not os.path.exists(file_path):
            raise FileNotFoundError("Could not find golden_laps_final.csv")
            
    print(f"Loading dataset from: {file_path}")
    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['date'])
    return df

def identify_corner_events(df):
    """Group continuous rows of is_corner==True into unique corner IDs."""
    df = df.sort_values(['Track', 'driver_number', 'date']).copy()
    # Create a unique ID for each contiguous block of corner points
    condition = df['is_corner'] != df['is_corner'].shift()
    df['corner_block_id'] = condition.cumsum()
    return df

def plot_corner_telemetry_anatomy(df):
    """Plot 1: Show Speed, Throttle, and Brake over time for one clear corner."""
    print("Generating Plot 1: Corner Telemetry Anatomy...")
    
    # Filter for a major braking corner in Monza or Spa
    corner_pts = df[(df['is_corner'] == True) & (df['brake'] > 90) & (df['Track'] == 'Monza')]
    if corner_pts.empty:
        corner_pts = df[df['is_corner'] == True]
        
    # Pick a specific corner block to visualize
    sample_block = corner_pts['corner_block_id'].iloc[0]
    
    # Get the data for this corner and include a few rows before and after for context
    start_idx = df[df['corner_block_id'] == sample_block].index.min() - 5
    end_idx = df[df['corner_block_id'] == sample_block].index.max() + 10
    df_corner = df.loc[start_idx:end_idx].copy()
    
    # Normalize time axis to seconds from start of sequence
    df_corner['time_sec'] = (df_corner['date'] - df_corner['date'].min()).dt.total_seconds()
    
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    # Plot Speed on the left Y-axis
    color = '#1f77b4'
    ax1.set_xlabel('Time (Seconds)', fontsize=12)
    ax1.set_ylabel('Speed (km/h)', color=color, fontsize=12)
    line1 = ax1.plot(df_corner['time_sec'], df_corner['speed'], color=color, linewidth=3, label='Speed')
    ax1.tick_params(axis='y', labelcolor=color)
    
    # Highlight the exact segment identified as 'is_corner'
    corner_only = df_corner[df_corner['is_corner'] == True]
    ax1.plot(corner_only['time_sec'], corner_only['speed'], color='red', linewidth=4, label='Detected Corner Phase')

    # Create a second Y-axis for Throttle and Brake pedals
    ax2 = ax1.twinx()  
    color_throttle = '#2ca02c'
    color_brake = '#d62728'
    ax2.set_ylabel('Pedal Input (%)', color='black', fontsize=12)
    line2 = ax2.plot(df_corner['time_sec'], df_corner['throttle'], color=color_throttle, linestyle='--', linewidth=2, label='Throttle %')
    line3 = ax2.plot(df_corner['time_sec'], df_corner['brake'], color=color_brake, linestyle=':', linewidth=2, label='Brake %')
    ax2.tick_params(axis='y', labelcolor='black')
    ax2.set_ylim(-5, 105)

    # Combined Legend
    lines = line1 + line2 + line3
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='lower left', fontsize=11)
    
    plt.title("The Anatomy of a Corner: Telemetry Breakdown Phase\nHeavy Braking -> Apex Speed Minimum -> Throttle Re-application", fontsize=14, fontweight='bold', pad=15)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("corner_anatomy.png", dpi=300)
    plt.show()

def plot_track_profiles(df):
    """Plot 2: Compare corner speeds and gears across the 4 different tracks."""
    print("Generating Plot 2: Track Corner Comparison Profiles...")
    
    # Isolate only rows when the cars are inside a corner
    df_corners_only = df[df['is_corner'] == True]
    
    plt.figure(figsize=(14, 6))
    
    # Subplot A: Speed distributions in corners
    plt.subplot(1, 2, 1)
    sns.boxplot(data=df_corners_only, x='Track', y='speed', palette='Set2')
    plt.title('Cornering Speed Profiles per Track', fontsize=12, fontweight='bold')
    plt.xlabel('Circuit Layout', fontsize=11)
    plt.ylabel('Speed Inside Corner (km/h)', fontsize=11)
    
    # Subplot B: Gear distribution in corners
    plt.subplot(1, 2, 2)
    sns.boxplot(data=df_corners_only, x='Track', y='n_gear', palette='Pastel1')
    plt.title('Gears Used inside Corners per Track', fontsize=12, fontweight='bold')
    plt.xlabel('Circuit Layout', fontsize=11)
    plt.ylabel('Gear Number', fontsize=11)
    
    plt.suptitle("Track Profiling: Low-Speed Chicanes (Singapore) vs High-Speed Sweepers (Spa/Suzuka)", fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout()
    plt.savefig("track_profiles.png", dpi=300)
    plt.show()

def plot_driver_cornering_styles(df):
    """Plot 3: Overlay telemetry of different drivers in the exact same track corner location."""
    print("Generating Plot 3: Driver Cornering Style Comparison...")
    
    # Filter a window in Monza where multiple drivers are present
    track_name = 'Monza'
    df_track = df[(df['Track'] == track_name) & (df['is_corner'] == True)]
    
    # Find a coordinate zone that represents a major corner
    # Grouping by x rounding to find a highly populated corner zone
    df_track['x_round'] = df_track['x'].round(-2)
    top_zone = df_track['x_round'].value_counts().index[0]
    
    # Extract continuous sector around this zone
    df_zone = df[(df['Track'] == track_name) & (df['x'] >= top_zone - 200) & (df['x'] <= top_zone + 200)].copy()
    
    # Select 3 prominent drivers to compare if available
    available_drivers = df_zone['driver_number'].unique()
    drivers_to_plot = available_drivers[:3]
    
    plt.figure(figsize=(11, 6))
    colors = ['#FF8700', '#00D2BE', '#DC0000']
    
    for idx, drv in enumerate(drivers_to_plot):
        df_drv = df_zone[df_zone['driver_number'] == drv].sort_values('date')
        if len(df_drv) > 3:
            # Plot speed against spatial X coordinate to sync their physical track location
            plt.plot(df_drv['x'], df_drv['speed'], label=f'Driver {drv}', color=colors[idx % 3], linewidth=2.5)
            
    plt.title(f"Driver Style Discrepancy: Speed Profile Over Same Track Section ({track_name})", fontsize=14, fontweight='bold')
    plt.xlabel("Track X Position (Meters)", fontsize=11)
    plt.ylabel("Car Speed (km/h)", fontsize=11)
    plt.legend(fontsize=11)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    plt.savefig("driver_styles.png", dpi=300)
    plt.show()

def plot_clustering_preparation(df):
    """Plot 4: Feature extraction scatter plot demonstrating natural grouping for Clustering."""
    print("Generating Plot 4: Clustering Feature Preparation space...")
    
    # Isolate corners and extract summary statistics per unique corner block
    df_corners_only = df[df['is_corner'] == True]
    
    # Group by corner block ID to calculate feature attributes for each corner event
    corner_features = df_corners_only.groupby(['Track', 'corner_block_id']).agg(
        min_speed=('speed', 'min'),
        max_brake=('brake', 'max'),
        avg_gear=('n_gear', 'mean'),
        points_count=('speed', 'count') # Proxy for duration/length of corner
    ).reset_index()
    
    # Filter out single-point noises
    corner_features = corner_features[corner_features['points_count'] > 2]
    
    plt.figure(figsize=(11, 6))
    
    # Scatter plot: Minimum Apex Speed vs Corner Point Count (Duration)
    sns.scatterplot(
        data=corner_features, 
        x='min_speed', 
        y='points_count', 
        hue='Track', 
        palette='Set1', 
        s=80, 
        alpha=0.7
    )
    
    plt.title("Corner Feature Space: Preparing for Clustering Analysis", fontsize=14, fontweight='bold')
    plt.xlabel("Apex Speed (Minimum Speed in Corner - km/h)", fontsize=11)
    plt.ylabel("Corner Duration Proxy (Telemetry Points Count)", fontsize=11)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(title='Track Layout', fontsize=11)
    plt.tight_layout()
    plt.savefig("clustering_prep.png", dpi=300)
    plt.show()

def main():
    print("=" * 50)
    print("F1 CORNER ANALYTICS AND VISUALIZATION PIPELINE")
    print("=" * 50)
    
    try:
        # Step 1: Load and format the cleaned data
        df = load_and_prepare_data()
        
        # Step 2: Build corner sequence groups
        df = identify_corner_events(df)
        
        # Step 3: Run all analytical plots
        plot_corner_telemetry_anatomy(df)
        plot_track_profiles(df)
        plot_driver_cornering_styles(df)
        plot_clustering_preparation(df)
        
        print("\n[SUCCESS] All 4 charts generated and saved as PNG files!")
        print("You can now copy-paste these visualizations into your Sunday presentation.")
        
    except Exception as e:
        print(f"\n[!] An error occurred during execution: {e}")
        print("Please verify that 'golden_laps_final.csv' contains columns: Track, driver_number, speed, brake, throttle, n_gear, is_corner")

if __name__ == "__main__":
    main()