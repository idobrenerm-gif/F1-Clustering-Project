import matplotlib.pyplot as plt
import pandas as pd

class TrackVisualizer:
    def draw_track_and_corners(self, df_corners, df_loc, driver_name="Driver"):
        """ממזג את נתוני המיקום עם הפניות ומצייר את המסלול"""
        
        # המרת זמנים
        df_loc['date'] = pd.to_datetime(df_loc['date'])
        df_corners['start_time'] = pd.to_datetime(df_corners['start_time'])

        # סידור ומיזוג
        df_loc = df_loc.sort_values('date')
        df_corners = df_corners.sort_values('start_time')
        corners_with_location = pd.merge_asof(df_corners, df_loc, left_on='start_time', right_on='date', direction='nearest')

        # ציור
        plt.figure(figsize=(10, 6))
        plt.plot(df_loc['x'], df_loc['y'], label='Track Layout', color='lightgray', linewidth=2)
        plt.scatter(corners_with_location['x'], corners_with_location['y'], color='red', s=50, label='Detected Corners', zorder=5)
        
        plt.title(f'Corner Detection Validation - {driver_name}')
        plt.xlabel('X Coordinate')
        plt.ylabel('Y Coordinate')
        plt.legend()
        plt.axis('equal')
        plt.show()