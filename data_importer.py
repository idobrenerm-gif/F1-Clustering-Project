import requests
import pandas as pd

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




# 1. הגדרות (נשתמש במרוץ סילברסטון ובהמילטון לדוגמה)
target_session = 9558
target_driver = 44

# 2. משיכת הטלמטריה (מסננים מהירויות נמוכות מאוד כבר בשלב הבקשה)
telemetry_url = f"https://api.openf1.org/v1/car_data?session_key={target_session}&driver_number={target_driver}&speed>50"
telemetry_response = requests.get(telemetry_url)
df_telemetry = pd.DataFrame(telemetry_response.json())

# 3. זיהוי "פוטנציאל לפנייה"
# אנחנו מחפשים רגעים שבהם יש בלימה חזקה
potential_corners = df_telemetry[df_telemetry['brake'] > 80]

# נדפיס את 20 השורות הראשונות של רגעי בלימה חזקה
print("--- Potential Corner Entries (Strong Braking) ---")
print(potential_corners[['date', 'speed', 'brake', 'n_gear']].head(20))







import pandas as pd
import requests

def extract_corners(df_telemetry):
    """
    אלגוריתם שעובר על נתוני טלמטריה ומזהה אירועי פניות.
    מחזיר טבלה שבה כל שורה היא פנייה אחת נקייה.
    """
    corners = []
    in_corner = False
    corner_data = {}

    # מעבר על כל שורה בנתונים
    for index, row in df_telemetry.iterrows():
        
        # 1. זיהוי תחילת כניסה לפנייה (בלימה חזקה)
        if row['brake'] > 80 and not in_corner:
            in_corner = True
            corner_data = {
                'entry_speed': row['speed'],      # מהירות בתחילת הבלימה
                'apex_speed': row['speed'],       # יתעדכן למהירות המינימלית בהמשך
                'min_gear': row['n_gear'],        # ההילוך הנמוך ביותר בפנייה
                'start_time': row['date']
            }

        # 2. הנהג בתוך הפנייה - מחפשים את ה-Apex (המהירות הכי נמוכה)
        elif in_corner and row['brake'] > 0:
            if row['speed'] < corner_data['apex_speed']:
                corner_data['apex_speed'] = row['speed']
            if row['n_gear'] < corner_data['min_gear']:
                corner_data['min_gear'] = row['n_gear']

        # 3. סיום אירוע הבלימה והערכת התוצאה
        elif in_corner and row['brake'] == 0:
            speed_drop = corner_data['entry_speed'] - corner_data['apex_speed']
            
            # בדיקת אימות: פנייה אמיתית דורשת ירידת מהירות של לפחות 40 קמ"ש
            # זה מנקה לנו "רעשים" ונגיעות קטנות בבלם[cite: 1]
            if speed_drop > 40:
                corner_data['speed_drop'] = speed_drop
                corners.append(corner_data)
            
            # איפוס המשתנים לקראת הפנייה הבאה
            in_corner = False
            corner_data = {}

    # המרת רשימת הפניות לטבלה מסודרת
    return pd.DataFrame(corners)


# ==========================================
# הפעלת האלגוריתם
# ==========================================

print("1. Downloading telemetry data...")
# מושכים נתונים עם פילטר התחלתי למהירות > 50 כדי למנוע רעש של הפיטס[cite: 1]
url = "https://api.openf1.org/v1/car_data?session_key=9558&driver_number=44&speed>50"
response = requests.get(url)
df_raw = pd.DataFrame(response.json())

print("2. Running Corner Detection Algorithm...")
df_corners = extract_corners(df_raw)

print(f"\nSuccess! Found {len(df_corners)} valid corners.")
print("\n--- Here is a sample of the extracted corners ---")
print(df_corners[['start_time', 'entry_speed', 'apex_speed', 'speed_drop', 'min_gear']].head(15))







import matplotlib.pyplot as plt

# 1. פונקציית זיהוי הפניות (בדיוק כמו מקודם)
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
# הרצת הנתונים והגרפיקה
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
# המרת הזמנים לפורמט של תאריך כדי שפייתון יוכל להשוות ביניהם במדויק
df_loc['date'] = pd.to_datetime(df_loc['date'])
df_corners['start_time'] = pd.to_datetime(df_corners['start_time'])

# סידור לפי זמן (חובה לפני מיזוג)
df_loc = df_loc.sort_values('date')
df_corners = df_corners.sort_values('start_time')

# פעולת מיזוג חכמה: מחפשת לכל פנייה את ה-X וה-Y שהכי קרובים אליה בזמן
corners_with_location = pd.merge_asof(df_corners, df_loc, left_on='start_time', right_on='date', direction='nearest')

# יצירת הגרף (ציור המסלול והפניות)
plt.figure(figsize=(10, 6))

# ציור מסלול המרוץ כולו (באפור)
plt.plot(df_loc['x'], df_loc['y'], label='Silverstone Track', color='lightgray', linewidth=2)

# ציור הנקודות האדומות איפה שהאלגוריתם זיהה פניות
plt.scatter(corners_with_location['x'], corners_with_location['y'], color='red', s=50, label='Detected Corners', zorder=5)

plt.title('F1 Corner Detection Validation - Silverstone (Lewis Hamilton)')
plt.xlabel('X Coordinate')
plt.ylabel('Y Coordinate')
plt.legend()
plt.axis('equal') # שומר על פרופורציות אמיתיות של המסלול

# הצגת הגרף על המסך
plt.show()