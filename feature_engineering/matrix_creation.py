import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
import os

def build_clustering_feature_matrix_final():
    print("--- Starting Feature Engineering (Consensus Mode) ---")
    
    processed_data_dir = 'processed_data'
    input_file = os.path.join(processed_data_dir, 'New_Qualifying_fastest_laps_telemetry_with_corners.csv')
    output_file = os.path.join(processed_data_dir, 'Qualifying_final_clustering_matrix.csv')
    
    try:
        df = pd.read_csv(input_file)
        print(f"  [OK] Loaded dataset with {len(df)} rows.")
    except FileNotFoundError:
        print(f"  [!] Error: Could not find '{input_file}'. Please check the filename.")
        return

    # 1. Distances
    print("  -> Calculating distances...")
    df['dx'] = df.groupby(['Track', 'driver_number'])['x'].diff().fillna(0)
    df['dy'] = df.groupby(['Track', 'driver_number'])['y'].diff().fillna(0)
    df['dist_step'] = np.sqrt(df['dx']**2 + df['dy']**2)
    
    # 2. Local Corner Grouping
    print("  -> Grouping corners based on is_corner logic...")
    df['corner_change'] = df['is_corner'].astype(int).diff().fillna(0)
    df['corner_id'] = df.groupby(['Track', 'driver_number'])['corner_change'].transform(lambda x: (x == 1).cumsum())

    # 3. Extract Features
    print("  -> Extracting features...")
    features_list = []
    corners_df = df[df['is_corner'] == True].copy()
    
    for (track, driver, corner_id), corner_data in corners_df.groupby(['Track', 'driver_number', 'corner_id']):
        # Drop micro-glitches of just 1-2 points to avoid dividing by absolute zero
        if len(corner_data) < 3:
            continue
            
        apex_idx = corner_data['speed'].idxmin()
        apex_row = corner_data.loc[apex_idx]
        pre_apex = corner_data.loc[:apex_idx]
        post_apex = corner_data.loc[apex_idx:]
        
        pre_apex_dist = pre_apex['dist_step'].sum()
        post_apex_dist = post_apex['dist_step'].sum()
        corner_total_dist = corner_data['dist_step'].sum()
        
        braking_dist = pre_apex[pre_apex['brake'] > 0]['dist_step'].sum()
        braking_pct_before = braking_dist / pre_apex_dist if pre_apex_dist > 0 else 0
        
        trail_braking_dist = pre_apex[(pre_apex['brake'] > 0) & (pre_apex['throttle'] < 5)]['dist_step'].sum()
        trail_braking_pct = trail_braking_dist / pre_apex_dist if pre_apex_dist > 0 else 0
        
        full_throttle_data = post_apex[post_apex['throttle'] > 90]
        throttle_app_dist = post_apex.loc[:full_throttle_data.index[0]]['dist_step'].sum() if not full_throttle_data.empty else post_apex_dist
        throttle_app_pct_after = throttle_app_dist / post_apex_dist if post_apex_dist > 0 else 0
        
        coasting_dist = corner_data[(corner_data['brake'] == 0) & (corner_data['throttle'] < 10)]['dist_step'].sum()
        coasting_pct = coasting_dist / corner_total_dist if corner_total_dist > 0 else 0
        
        braking_time_pct = len(corner_data[corner_data['brake'] > 0]) / len(corner_data)
        
        features_list.append({
            'Track': track,
            'driver_number': driver,
            'Driver_Corner_Sequence': corner_id, 
            'Apex_X': apex_row['x'],
            'Apex_Y': apex_row['y'],
            
            'Entry_Speed': corner_data['speed'].iloc[0],
            'Apex_Speed': apex_row['speed'],
            'Exit_Speed': corner_data['speed'].iloc[-1],
            'Speed_Delta': corner_data['speed'].iloc[0] - apex_row['speed'],
            'Braking_Pct_Before_Apex': braking_pct_before,
            'Trail_Braking_Pct': trail_braking_pct,
            'Throttle_App_Pct_After_Apex': throttle_app_pct_after,
            'Coasting_Pct': coasting_pct,
            'Braking_Time_Pct': braking_time_pct,
            'Average_Throttle': corner_data['throttle'].mean(),
            'Min_Gear': corner_data['n_gear'].min(),
            'Corner_Distance_m': corner_total_dist,
            'Average_Speed': corner_data['speed'].mean()
        })

    final_features_df = pd.DataFrame(features_list)

    # 4. Global Mapping with gentle DBSCAN
    print("  -> Mapping physical corners globally...")
    final_features_df['Physical_Corner'] = -1
    for track in final_features_df['Track'].unique():
        track_mask = final_features_df['Track'] == track
        track_data = final_features_df[track_mask]
        
        db = DBSCAN(eps=100, min_samples=3)
        final_features_df.loc[track_mask, 'Physical_Corner'] = db.fit_predict(track_data[['Apex_X', 'Apex_Y']])

    final_features_df = final_features_df[final_features_df['Physical_Corner'] != -1].copy()

    # 5. THE CONSENSUS RULE (The Magic Fix)
    print("  -> Applying the Consensus Rule (>14 drivers per corner)...")
    driver_counts = final_features_df.groupby(['Track', 'Physical_Corner'])['driver_number'].nunique().reset_index()
    valid_clusters = driver_counts[driver_counts['driver_number'] >= 15]
    
    clean_features_df = final_features_df.merge(valid_clusters[['Track', 'Physical_Corner']], on=['Track', 'Physical_Corner'], how='inner')

    # 6. Assign Sequential Semantic IDs (101, 102...)
    print("  -> Assigning Sequential Global Corner IDs...")
    track_bases = {'Monza': 100, 'Singapore': 200, 'Spa': 300, 'Suzuka': 400}
    clean_features_df['Global_Corner_ID'] = 0
    
    for track in clean_features_df['Track'].unique():
        track_mask = clean_features_df['Track'] == track
        base_id = track_bases.get(track, 900)
        
        corner_chronological_order = clean_features_df[track_mask].groupby('Physical_Corner')['Driver_Corner_Sequence'].mean().sort_values()
        mapping = {phys_id: base_id + i + 1 for i, phys_id in enumerate(corner_chronological_order.index)}
        clean_features_df.loc[track_mask, 'Global_Corner_ID'] = clean_features_df.loc[track_mask, 'Physical_Corner'].map(mapping)

    # Cleanup and Save
    clean_features_df = clean_features_df.drop(columns=['Physical_Corner', 'Apex_X', 'Apex_Y', 'Driver_Corner_Sequence'])
    cols = ['Track', 'Global_Corner_ID', 'driver_number'] + [c for c in clean_features_df.columns if c not in ['Track', 'Global_Corner_ID', 'driver_number']]
    clean_features_df = clean_features_df[cols]
    clean_features_df = clean_features_df.sort_values(by=['Track', 'Global_Corner_ID', 'driver_number'])

    clean_features_df.to_csv(output_file, index=False)
    
    print(f"\n--- Process Complete ---")
    print(f"  [SUCCESS] Clustered feature matrix saved to: {output_file}")
    print("\nFinal Valid Technical Corners per Track:")
    for track in clean_features_df['Track'].unique():
        corners = clean_features_df[clean_features_df['Track']==track]['Global_Corner_ID'].unique()
        print(f"  {track}: {len(corners)} technical corners")

build_clustering_feature_matrix_final()