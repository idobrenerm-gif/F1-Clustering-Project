import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
import numpy as np
import os

# has problem with the start/finish line in suzuka - need fixing! 

def add_is_corner_column(file_path='processed_data/golden_laps_final.csv', output_path='processed_data/golden_laps_final.csv'):
    
    if not os.path.exists(file_path):
        print(f"[!] Error: File not found at {file_path}")
        return None

    # טעינת הנתונים
    df = pd.read_csv(file_path)
    
    # ניצור רשימה ריקה לאחסון התוצאות לכל מסלול בנפרד
    processed_frames = []

    # אנחנו מעבדים כל מסלול בנפרד כדי ששינויי הזווית לא "יקפצו" במעבר בין מסלולים
    for track in df['Track'].unique():
        track_df = df[df['Track'] == track].copy()
        
        # המרה למספרים וניקוי
        track_df['x'] = pd.to_numeric(track_df['x'], errors='coerce')
        track_df['y'] = pd.to_numeric(track_df['y'], errors='coerce')
        track_df = track_df.dropna(subset=['x', 'y'])

        # חישוב וקטור הכיוון (dx, dy)
        dx = np.gradient(track_df['x'])
        dy = np.gradient(track_df['y'])
        
        # חישוב זווית הכיוון (Heading Angle)
        heading_angle = np.arctan2(dy, dx)
        
        # מניעת קפיצות חדות בחישוב הזווית (Unwrap)
        unwrapped_angle = np.unwrap(heading_angle)
        
        # חישוב קצב שינוי הזווית (הנגזרת הראשונה)
        angle_change = np.abs(np.gradient(unwrapped_angle))
        
        # החלקה של הנתונים כדי למנוע רעשי חיישן (Rolling Mean)
        # השתמשנו בחלון של 30 כפי שמצאנו שמתאים ללכידת קורבה גרנדה
        window_size = 5
        smoothed_change = pd.Series(angle_change).rolling(window=window_size, center=True, min_periods=1).mean().values
        
        # קביעת הסף לזיהוי פנייה
        corner_threshold = 0.06
        if track == 'Suzuka':
            corner_threshold = 0.08  # סף מעט נמוך יותר לסוזוקה בגלל פניות חדות יותר
        
        # יצירת העמודה החדשה
        # יצירת העמודה החדשה
        track_df['is_corner'] = smoothed_change > corner_threshold
        
        # --- FIX FOR FALSE CORNER AT START/FINISH LINE ---
        # נניח ש-10 הדגימות הראשונות והאחרונות הן תמיד בישורת הזינוק
        # (זה מכסה את אזור ה"תפר" המלאכותי שיצרנו)
        track_df.iloc[:10, track_df.columns.get_loc('is_corner')] = False
        track_df.iloc[-10:, track_df.columns.get_loc('is_corner')] = False
        # -------------------------------------------------
        
        processed_frames.append(track_df)

    # איחוד כל המסלולים חזרה ל-Dataframe אחד
    final_df = pd.concat(processed_frames, ignore_index=True)
    
    # שמירה לקובץ חדש
    final_df.to_csv(output_path, index=False)
    print(f"[SUCCESS] Added 'is_corner' column. Saved to: {output_path}")
    
    return final_df

# הרצת הפונקציה
#updated_df = add_is_corner_column()



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