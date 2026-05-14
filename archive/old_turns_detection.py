import pandas as pd

class CornerDetector:
    def extract_corners(self, df_telemetry):
        """get corners based on braking and speed drop"""
        corners = []
        in_corner = False
        corner_data = {}

        for index, row in df_telemetry.iterrows():
            if row['brake'] > 80 and not in_corner:
                in_corner = True
                corner_data = {
                    'start_time': row['date'],
                    'entry_speed': row['speed'],
                    'apex_speed': row['speed'],
                    'min_gear': row['n_gear']
                }
            elif in_corner and row['brake'] > 0:
                if row['speed'] < corner_data['apex_speed']:
                    corner_data['apex_speed'] = row['speed']
                if row['n_gear'] < corner_data['min_gear']:
                    corner_data['min_gear'] = row['n_gear']
            elif in_corner and row['brake'] == 0:
                speed_drop = corner_data['entry_speed'] - corner_data['apex_speed']
                if speed_drop > 40:
                    corner_data['speed_drop'] = speed_drop
                    corners.append(corner_data)
                
                in_corner = False
                corner_data = {}
                
        return pd.DataFrame(corners)