import requests
import pandas as pd
import matplotlib.pyplot as plt


#define the api
url = "https://api.openf1.org/v1/sessions?year=2024&session_name=Race"
#send a request to the api
response = requests.get(url)
#convert the response to json format
data_json = response.json()
#convert the json data to a pandas DataFrame
df_sessions = pd.DataFrame(data_json)
#display the first few rows of the DataFrame
print(df_sessions.head())





#define the session key for bahrain race
target_session = 9468

#create the url for the drivers endpoint using the session key
drivers_url = f"https://api.openf1.org/v1/drivers?session_key={target_session}"

# send a request to the drivers endpoint
drivers_response = requests.get(drivers_url)
drivers_json = drivers_response.json()

#create a DataFrame for the drivers data
df_drivers = pd.DataFrame(drivers_json)

# display the desired columns
print(df_drivers[['driver_number', 'full_name', 'team_name']])






# define the target driver number (for example, Lewis Hamilton's number is 44)  
target_driver = 44

# create the url for the telemetry endpoint using the session key and driver number
# add a filter to only get telemetry data where speed is greater than 0
telemetry_url = f"https://api.openf1.org/v1/car_data?session_key={target_session}&driver_number={target_driver}&speed>0"

# send the request
telemetry_response = requests.get(telemetry_url)
telemetry_json = telemetry_response.json()

# convert to DataFrame
df_telemetry = pd.DataFrame(telemetry_json)

# display the first 10 rows of the telemetry data
print(df_telemetry[['date', 'speed', 'brake', 'throttle', 'rpm', 'n_gear']].head(10))




# define the target session and driver
target_session = 9558
target_driver = 44

# Downloading telemetry data with a filter for speed > 50 to reduce noise from pit lane
telemetry_url = f"https://api.openf1.org/v1/car_data?session_key={target_session}&driver_number={target_driver}&speed>50"
telemetry_response = requests.get(telemetry_url)
df_telemetry = pd.DataFrame(telemetry_response.json())

# looking for potential corners based on strong braking events
potential_corners = df_telemetry[df_telemetry['brake'] > 80]

#printing the potential corner entries to analyze them further
print("--- Potential Corner Entries (Strong Braking) ---")
print(potential_corners[['date', 'speed', 'brake', 'n_gear']].head(20))





def extract_corners(df_telemetry):
    """
   algorithm to extract corners based on braking and speed drop patterns in the telemetry data.
    """
    corners = []
    in_corner = False
    corner_data = {}

    # passing through the telemetry data row by row to identify corners
    for index, row in df_telemetry.iterrows():
        
        # detecting the start of a corner: strong braking event
        if row['brake'] > 80 and not in_corner:
            in_corner = True
            corner_data = {
                'entry_speed': row['speed'],      # Speed at the moment of heavy braking (potential corner entry)
                'apex_speed': row['speed'],       # initially set to entry speed, will be updated to the lowest speed during the corner
                'min_gear': row['n_gear'],        # initially set to the gear at entry, will be updated if the driver shifts down during the corner
                'start_time': row['date']
            }

        # tracking the corner: while the driver is still braking, we check for the lowest speed (apex) and the lowest gear used
        elif in_corner and row['brake'] > 0:
            if row['speed'] < corner_data['apex_speed']:
                corner_data['apex_speed'] = row['speed']
            if row['n_gear'] < corner_data['min_gear']:
                corner_data['min_gear'] = row['n_gear']

        # detecting the end of a corner: when braking stops, we check if the speed drop is significant enough to be considered a valid corner
        elif in_corner and row['brake'] == 0:
            speed_drop = corner_data['entry_speed'] - corner_data['apex_speed']
            
            # considering it a valid corner only if the speed drop is greater than 40 km/h (this threshold can be adjusted based on further analysis)
            if speed_drop > 40:
                corner_data['speed_drop'] = speed_drop
                corners.append(corner_data)
            
            # resetting the corner detection state
            in_corner = False
            corner_data = {}

    # returning the detected corners as a DataFrame
    return pd.DataFrame(corners)


# ==========================================
# algorithm execution
# ==========================================

print("1. Downloading telemetry data...")
# creating the url for telemetry data with a filter for speed > 50 to focus on relevant data and reduce noise
url = "https://api.openf1.org/v1/car_data?session_key=9558&driver_number=44&speed>50"
response = requests.get(url)
df_raw = pd.DataFrame(response.json())

print("2. Running Corner Detection Algorithm...")
df_corners = extract_corners(df_raw)

print(f"\nSuccess! Found {len(df_corners)} valid corners.")
print("\n--- Here is a sample of the extracted corners ---")
print(df_corners[['start_time', 'entry_speed', 'apex_speed', 'speed_drop', 'min_gear']].head(15))







# defining the target session and driver for location data
def extract_corners(df_telemetry):
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
# execution
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
df_loc['date'] = pd.to_datetime(df_loc['date'])
df_corners['start_time'] = pd.to_datetime(df_corners['start_time'])

# sorting both DataFrames by their respective time columns to prepare for the asof merge
df_loc = df_loc.sort_values('date')
df_corners = df_corners.sort_values('start_time')

# merging the corners with the location data based on the nearest timestamp to get the corresponding X, Y coordinates for each detected corner
corners_with_location = pd.merge_asof(df_corners, df_loc, left_on='start_time', right_on='date', direction='nearest')

# plotting the track layout and the detected corners
plt.figure(figsize=(10, 6))

#plotting the track layout in light gray
plt.plot(df_loc['x'], df_loc['y'], label='Silverstone Track', color='lightgray', linewidth=2)

# plotting the detected corners as red points on top of the track layout
plt.scatter(corners_with_location['x'], corners_with_location['y'], color='red', s=50, label='Detected Corners', zorder=5)

plt.title('F1 Corner Detection Validation - Silverstone (Lewis Hamilton)')
plt.xlabel('X Coordinate')
plt.ylabel('Y Coordinate')
plt.legend()
plt.axis('equal') # keeping the aspect ratio of the plot equal to accurately represent the track layout

# displaying the plot
plt.show()