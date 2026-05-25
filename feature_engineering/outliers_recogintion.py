import pandas as pd
import numpy as np

def detect_outliers_report(df):
    """
    This function scans the dataset and prints a detailed report 
    of statistical and logical outliers.
    """
    print("="*50)
    print("OUTLIERS DETECTION REPORT")
    print("="*50)

    # 1. Detect Logical Outliers
    print("\n--- 1. Domain/Logical Outliers (Physics Violations) ---")
    
    # Impossible speeds (above 380 km/h or below 0 km/h)
    invalid_speed = df[(df['apex_speed'] > 380) | (df['apex_speed'] < 0) | (df['entry_speed'] > 380)]
    print(f"-> Found {len(invalid_speed)} rows with physically impossible speeds (<0 or >380 km/h).")
    
    # Invalid gear (must be between 1 and 8)
    if 'minimum_gear' in df.columns:
        invalid_gear = df[(df['minimum_gear'] < 1) | (df['minimum_gear'] > 8)]
        print(f"-> Found {len(invalid_gear)} rows with invalid gears (must be 1-8).")
        
    # Extreme corner duration (less than 0.2 seconds or more than 20 seconds)
    if 'corner_duration' in df.columns:
        invalid_duration = df[(df['corner_duration'] < 0.2) | (df['corner_duration'] > 20)]
        print(f"-> Found {len(invalid_duration)} rows with illogical corner durations.")

    # 2. Detect Statistical Outliers using the IQR method
    print("\n--- 2. Statistical Outliers (IQR Method) ---")
    
    # List of numeric columns we want to check for outliers
    numeric_columns = [
        'max_curvature', 'corner_duration', 'apex_speed', 
        'braking_distance_to_apex', 'trail_braking_duration', 
        'throttle_application_point', 'coasting_time'
    ]
    
    # Use a 'set' to avoid counting the same row multiple times
    total_statistical_outliers = set() 
    
    for col in numeric_columns:
        if col in df.columns:
            # Calculate Q1 (25th percentile) and Q3 (75th percentile)
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            # Define the normal lower and upper limits
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            # Find the rows that are outside these limits
            outlier_rows = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
            
            if len(outlier_rows) > 0:
                print(f"{col}: {len(outlier_rows)} outliers (Normal range: {lower_bound:.2f} to {upper_bound:.2f})")
                total_statistical_outliers.update(outlier_rows.index)
            else:
                print(f"{col}: 0 outliers.")
                
    print(f"\n[!] Total unique rows with at least one statistical outlier: {len(total_statistical_outliers)}")
    print(f"Which is ~{(len(total_statistical_outliers) / len(df)) * 100:.2f}% of the dataset.")
    print("="*50)
    
    return list(total_statistical_outliers)

