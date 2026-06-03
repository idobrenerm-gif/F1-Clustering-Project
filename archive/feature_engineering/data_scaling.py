import pandas as pd
import os

def perform_per_corner_scaling():
    print("--- Starting Per-Corner Standardization (Z-Score) ---")
    
    # Define file paths
    input_file = 'processed_data/Qualifying_final_clustering_matrix.csv'
    output_dir = 'processed_data'
    output_file = os.path.join(output_dir, 'Qualifying_scaled_for_clustering.csv')
    
    try:
        print("  -> Loading final clustering matrix...")
        df = pd.read_csv(input_file)
        print(f"  [OK] Loaded dataset with {len(df)} rows.")
    except FileNotFoundError:
        print(f"  [!] Error: Could not find '{input_file}'.")
        return

    # Fix column names to lowercase just in case
    df.columns = df.columns.str.lower()
    
    # 1. Identify the columns
    # Grouping columns (Identifiers)
    group_cols = ['track', 'global_corner_id']
    
    # We want to keep driver_number but NOT scale it
    id_cols = group_cols + ['driver_number']
    
    # Find all numeric features to scale (excluding the identifiers)
    features_to_scale = [col for col in df.columns if col not in id_cols]
    
    print(f"  -> Found {len(features_to_scale)} features to scale.")

    # 2. Perform Group-wise Standardization (Per-Corner Z-Score)
    print("  -> Applying Group-wise Z-Score scaling...")
    
    # We create a copy to store the scaled results safely
    scaled_df = df.copy()
    
    for feature in features_to_scale:
        # Check if column contains numbers before math operations
        if pd.api.types.is_numeric_dtype(df[feature]):
            # Group by Track and Corner ID, then calculate (Value - Mean) / StdDev
            # We add a tiny number (1e-9) to StdDev to prevent "Divide by Zero" errors 
            # if all drivers did the exact same thing in a specific corner.
            scaled_df[feature] = df.groupby(group_cols)[feature].transform(
                lambda x: (x - x.mean()) / (x.std() + 1e-9)
            )

    # 3. Save the final scaled dataset
    scaled_df.to_csv(output_file, index=False)
    
    print(f"\n--- Scaling Complete ---")
    print(f"  [SUCCESS] Scaled data saved to: {output_file}")
    print("  [READY] You can now feed this file into the K-Means algorithm!")
    
    # Show a quick preview of the scaled data
    print("\n  Preview of scaled features (Values should be around -3 to +3):")
    print(scaled_df[features_to_scale].head())

perform_per_corner_scaling()