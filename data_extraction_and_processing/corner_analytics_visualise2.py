import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def load_data():
    """Load the golden laps dataset."""
    file_path = "archive/golden_laps_final.csv"
    if not os.path.exists(file_path):
        # Fallback in case the script is run from inside the processed_data folder
        file_path = "golden_laps_final.csv"
    df = pd.read_csv(file_path)
    return df

def get_unique_corners(df):
    """Adds a unique identifier to each continuous corner block so they can be counted."""
    # Sort data chronologically per track and driver
    df = df.sort_values(['Track', 'driver_number', 'date']).copy()
    
    # Identify boundaries where 'is_corner' changes state (True -> False or False -> True)
    condition = df['is_corner'] != df['is_corner'].shift()
    df['corner_block_id'] = condition.cumsum()
    return df

def plot_basic_corner_counts(df):
    """Plot 1: Bar chart showing the average number of detected corners per track."""
    print("Generating Plot 1: Corner Counts...")
    
    # Filter only the rows where the car is actively inside a corner
    corners_df = df[df['is_corner'] == True]
    
    # Count the unique corner blocks per track for each driver
    corner_counts = corners_df.groupby(['Track', 'driver_number'])['corner_block_id'].nunique().reset_index()
    
    # Calculate the average number of corners per lap (averaging across drivers)
    avg_corners_per_track = corner_counts.groupby('Track')['corner_block_id'].mean().round()

    plt.figure(figsize=(10, 6))
    ax = sns.barplot(x=avg_corners_per_track.index, y=avg_corners_per_track.values, palette='viridis')
    
    # Add value labels on top of the bars
    for i, v in enumerate(avg_corners_per_track.values):
        ax.text(i, v + 0.5, str(int(v)), ha='center', fontsize=12, fontweight='bold')

    plt.title('Average Number of Corners Detected per Lap', fontsize=16, fontweight='bold')
    plt.xlabel('Track', fontsize=14)
    plt.ylabel('Number of Corners', fontsize=14)
    plt.tight_layout()
    plt.savefig('basic_corner_counts.png', dpi=300)
    plt.show()

def plot_corner_vs_straight_time(df):
    """Plot 2: Pie charts showing the percentage of time spent in corners vs. straights."""
    print("Generating Plot 2: Time Distribution (Corners vs Straights)...")
    
    # Since telemetry is sampled at a constant rate, row count is equivalent to time spent
    time_dist = df.groupby(['Track', 'is_corner']).size().unstack(fill_value=0)
    
    # Calculate percentages
    time_dist['Total'] = time_dist[False] + time_dist[True]
    time_dist['Corner_%'] = (time_dist[True] / time_dist['Total']) * 100
    time_dist['Straight_%'] = (time_dist[False] / time_dist['Total']) * 100

    tracks = time_dist.index
    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    
    # Red for corners, Blue for straights
    colors = ['#FF9999', '#66B2FF'] 

    for i, track in enumerate(tracks):
        sizes = [time_dist.loc[track, 'Corner_%'], time_dist.loc[track, 'Straight_%']]
        axes[i].pie(sizes, labels=['Corners', 'Straights'], autopct='%1.1f%%', 
                    startangle=90, colors=colors, textprops={'fontsize': 12})
        axes[i].set_title(track, fontweight='bold', fontsize=14)

    plt.suptitle('Percentage of Lap Time: Corners vs. Straights', fontsize=18, fontweight='bold', y=1.05)
    plt.tight_layout()
    plt.savefig('basic_time_distribution.png', dpi=300)
    plt.show()

def plot_average_corner_speed(df):
    """Plot 3: Bar chart of the average speed specifically inside corners."""
    print("Generating Plot 3: Average Corner Speed...")
    
    corners_df = df[df['is_corner'] == True]
    avg_speed = corners_df.groupby('Track')['speed'].mean().reset_index()

    plt.figure(figsize=(10, 6))
    ax = sns.barplot(x='Track', y='speed', data=avg_speed, palette='magma')
    
    # Add value labels on top of the bars
    for i, v in enumerate(avg_speed['speed']):
        ax.text(i, v + 2, f"{int(v)} km/h", ha='center', fontsize=12, fontweight='bold')

    plt.title('Average Speed Inside Corners per Track', fontsize=16, fontweight='bold')
    plt.xlabel('Track', fontsize=14)
    plt.ylabel('Average Speed (km/h)', fontsize=14)
    
    # Add some padding to the top of the y-axis
    plt.ylim(0, avg_speed['speed'].max() + 30) 
    plt.tight_layout()
    plt.savefig('basic_avg_speed.png', dpi=300)
    plt.show()

def plot_corner_speed_drop(df):
    """Plot 4: Boxplot showing the distribution of Speed Drop (Braking Intensity) per track."""
    print("Generating Plot 4: Speed Drop Distribution...")
    
    # Filter only the corners
    corners_df = df[df['is_corner'] == True]
    
    # Calculate the Speed Drop for each distinct corner block:
    # Maximum speed (entry) minus minimum speed (apex) in the exact same corner
    corner_stats = corners_df.groupby(['Track', 'driver_number', 'corner_block_id']).agg(
        entry_speed=('speed', 'max'),
        apex_speed=('speed', 'min')
    ).reset_index()
    
    # Create the new speed_drop column
    corner_stats['speed_drop'] = corner_stats['entry_speed'] - corner_stats['apex_speed']
    
    # Draw the plot (Boxplot shows the distribution and outliers perfectly)
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='Track', y='speed_drop', data=corner_stats, palette='coolwarm')
    
    plt.title('Distribution of Speed Drop in Corners (Braking Intensity)', fontsize=16, fontweight='bold')
    plt.xlabel('Track', fontsize=14)
    plt.ylabel('Speed Drop (km/h)', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.4)
    plt.tight_layout()
    plt.savefig('basic_speed_drop.png', dpi=300)
    plt.show()

def main():
    print("=" * 50)
    print("F1 BASIC EDA VISUALIZER (CORNERS)")
    print("=" * 50)
    
    try:
        # Load and prepare data
        df = load_data()
        df = get_unique_corners(df)
        
        # Execute all plotting functions
        plot_basic_corner_counts(df)
        plot_corner_vs_straight_time(df)
        plot_average_corner_speed(df)
        plot_corner_speed_drop(df)
        
        print("\n[SUCCESS] All 4 basic EDA graphs saved successfully as PNG files.")
    except Exception as e:
        print(f"\n[ERROR] {e}")

if __name__ == "__main__":
    main()