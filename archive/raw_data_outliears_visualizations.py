import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def generate_telemetry_outlier_plots():
    print("--- Generating Telemetry Outlier Visualizations ---")
    
    # נתיב לקובץ הטלמטריה (קריאה בלבד)
    input_file = 'processed_data/New_Qualifying_fastest_laps_telemetry.csv'
    
    # יצירת תיקייה ייעודית לתמונות האלו
    output_dir = 'Telemetry_Outlier_Visuals'
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        print("  -> Loading large telemetry file...")
        df = pd.read_csv(input_file)
        print(f"  [OK] Loaded dataset with {len(df)} rows.")
    except FileNotFoundError:
        print(f"  [!] Error: Could not find '{input_file}'.")
        return

    # ==========================================
    # מניעת שגיאות: הפיכת שמות העמודות לאותיות קטנות
    # ==========================================
    original_cols = df.columns.tolist()
    df.columns = df.columns.str.lower()
    
    # תיקון למקרה ש-FastF1 שמר את זה כ-ngear במקום n_gear
    if 'ngear' in df.columns and 'n_gear' not in df.columns:
        df.rename(columns={'ngear': 'n_gear'}, inplace=True)

    # נבדוק אם קיימת עמודת מסלול (Track) כדי להפריד את הגרפים
    has_track = 'track' in df.columns

    # המאפיינים שנרצה לצייר להם את ה-Outliers
    features_to_plot = ['rpm', 'speed', 'throttle', 'brake', 'n_gear']
    
    sns.set_theme(style="whitegrid")
    
    for feature in features_to_plot:
        if feature in df.columns:
            plt.figure(figsize=(12, 6))
            
            # אם הבלם הגיע כ-True/False, נמיר אותו ל-0-100 נטו בשביל הגרף
            if feature == 'brake' and df[feature].dtype == bool:
                plot_data = df[feature].astype(int) * 100
            else:
                plot_data = df[feature]
                
            # ציור ה-Boxplot
            if has_track:
                sns.boxplot(x=df['track'], y=plot_data, palette="Set2", width=0.5, fliersize=4)
                plt.xlabel('Track', fontsize=12)
            else:
                # אם אין עמודת מסלול מאיזושהי סיבה, נצייר גרף כללי
                sns.boxplot(y=plot_data, color="royalblue", width=0.3, fliersize=4)
                plt.xlabel('All Tracks Combined', fontsize=12)
                
            # עיצוב חזותי
            clean_title = feature.replace('_', ' ').upper()
            plt.title(f'Raw Telemetry Outliers: {clean_title}', fontsize=16, fontweight='bold')
            plt.ylabel(f'{clean_title} Value', fontsize=12)
            
            # שמירת התמונה
            file_name = f"Telemetry_Outliers_{feature}.png"
            output_path = os.path.join(output_dir, file_name)
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"  [+] Saved: {file_name}")
        else:
            print(f"  [-] Skipped {feature} (column not found)")

    print(f"\n--- Process Complete ---")
    print(f"  [SUCCESS] All telemetry outlier graphs saved to '{output_dir}'.")

generate_telemetry_outlier_plots()