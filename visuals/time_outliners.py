import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def plot_lap_times(track_name):
    print(f"Loading data for track: {track_name}...")
    
    # 1. Define the correct path to the file
    processed_data_dir = 'processed_data'
    file_name = 'New_Qualifying_fastest_laps_telemetry.csv'
    file_path = os.path.join(processed_data_dir, file_name)
    
    # 2. Read the data directly from the correct path
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: The file '{file_name}' was not found in the '{processed_data_dir}' directory.")
        print(f"Attempted path: {file_path}")
        return

    # 3. Filter data for the requested track
    track_df = df[df['Track'] == track_name].copy()
    
    if track_df.empty:
        print(f"No data found for the track: {track_name}")
        return
        
    # 4. Extract lap duration for each driver (taking the first value from the telemetry sequence)
    driver_times = track_df.groupby('driver_number')['lap_duration'].first().reset_index()
    
    # Filter out drivers with missing lap times
    driver_times = driver_times.dropna(subset=['lap_duration'])
    
    # 5. Sort from fastest to slowest to easily identify outliers
    driver_times = driver_times.sort_values('lap_duration')
    
    # 6. Plot the graph
    plt.figure(figsize=(14, 6))
    
    sns.barplot(
        data=driver_times, 
        x='driver_number', 
        y='lap_duration', 
        order=driver_times['driver_number'], 
        color='royalblue'
    )
    
    # Styling the plot
    plt.title(f'Lap Times per Driver - {track_name}', fontsize=16, fontweight='bold')
    plt.xlabel('Driver Number', fontsize=12)
    plt.ylabel('Lap Duration (Seconds)', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add the exact time above each bar
    for index, row in enumerate(driver_times.itertuples()):
        plt.text(
            index, 
            row.lap_duration + 0.5, 
            f'{row.lap_duration:.2f}', 
            color='black', 
            ha="center", 
            fontsize=9,
            rotation=45
        )
        
    plt.tight_layout()
    plt.show()

# Example usage:
plot_lap_times('Monza')
plot_lap_times('Singapore')
plot_lap_times('Spa')
plot_lap_times('Suzuka')