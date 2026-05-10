import requests
import pandas as pd
import matplotlib.pyplot as plt

def extract_corners(df_telemetry):
    """
    Algorithm to extract corners based on braking and speed drop patterns.
    """
    corners = []
    in_corner = False
    corner_data = {}

    for index, row in df_telemetry.iterrows():
        if row['brake'] > 80 and not in_corner:
            in_corner = True
            corner_data = {
                'start_time': row['date'],
                'entry_speed': row['speed'],
                'apex_speed': row['speed']
            }
        elif in_corner and row['brake'] > 0:
            if row['speed'] < corner_data['apex_speed']:
                corner_data['apex_speed'] = row['speed']
        elif in_corner and row['brake'] == 0:
            speed_drop = corner_data['entry_speed'] - corner_data['apex_speed']
            if speed_drop > 40:
                corner_data['speed_drop'] = speed_drop
                corners.append(corner_data)
            in_corner = False
            corner_data = {}
            
    return pd.DataFrame(corners)

# ==========================================
# Execution
# ==========================================
session_key = 9558
driver_number = 44

print("1. Downloading Telemetry Data...")
tel_url = f"https://api.openf1.org/v1/car_data?session_key={session_key}&driver_number={driver_number}&speed>50"
df_tel = pd.DataFrame(requests.get(tel_url).json())

print("2. Running Corner Detection...")
df_corners = extract_corners(df_tel)

print("3. Downloading Location Data (X, Y)...")
loc_url = f"https://api.openf1.org/v1/location?session_key={session_key}&driver_number={driver_number}"
df_loc = pd.DataFrame(requests.get(loc_url).json())

print("4. Merging and Drawing the Track...")
# converting date columns to datetime for accurate merging
df_loc['date'] = pd.to_datetime(df_loc['date'], format='ISO8601')
df_corners['start_time'] = pd.to_datetime(df_corners['start_time'], format='ISO8601')

# sorting both DataFrames by their respective time columns to prepare for the asof merge
df_loc = df_loc.sort_values('date')
df_corners = df_corners.sort_values('start_time')

# merging the corners with the location data based on the nearest timestamp
corners_with_location = pd.merge_asof(df_corners, df_loc, left_on='start_time', right_on='date', direction='nearest')

# plotting the track layout and the detected corners
plt.figure(figsize=(10, 6))

# plotting the track layout in light gray
plt.plot(df_loc['x'], df_loc['y'], label='Silverstone Track', color='lightgray', linewidth=2)

# plotting the detected corners as red points on top of the track layout
plt.scatter(corners_with_location['x'], corners_with_location['y'], color='red', s=50, label='Detected Corners', zorder=5)

plt.title('F1 Corner Detection Validation - Silverstone (Lewis Hamilton)')
plt.xlabel('X Coordinate')
plt.ylabel('Y Coordinate')
plt.legend()
plt.axis('equal') 

# displaying the plot
plt.show()