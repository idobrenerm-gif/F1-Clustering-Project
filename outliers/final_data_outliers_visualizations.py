import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def create_outlier_visualizations():
    print("--- Generating Outlier Visualizations ---")
    
    # נתיב לקובץ הפיצ'רים הסופי
    input_file = 'processed_data/Qualifying_final_clustering_matrix.csv'
    
    # תיקיית היעד לתמונות שייווצרו
    output_dir = 'outlier_visualizations'
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        df = pd.read_csv(input_file)
        print(f"  [OK] Loaded dataset with {len(df)} rows.")
    except FileNotFoundError:
        print(f"  [!] Error: Could not find '{input_file}'.")
        return

    # רשימת המאפיינים (בשמות החדשים) שנרצה לבדוק
    features = [
        'entry_speed', 'apex_speed', 'exit_speed', 'speed_drop',
        'braking_pct_before_apex', 'trail_braking_pct', 
        'throttle_app_pct_after_apex', 'coasting_pct', 
        'braking_time_pct', 'average_throttle', 'min_gear', 'average_speed'
    ]
    
    # וידוא שהעמודות באמת קיימות בקובץ
    available_features = [f for f in features if f in df.columns]
    
    if not available_features:
        print("  [!] Error: Could not find the specified columns. Check column names.")
        return

    # הגדרת סגנון ויזואלי נקי ומקצועי
    sns.set_theme(style="whitegrid")
    
    for feature in available_features:
        # פתיחת חלון ציור חדש
        plt.figure(figsize=(12, 6))
        
        # 1. יצירת Boxplot (תרשים קופסה). נקודות שיוצאות מחוץ ל"שפמים" הן Outliers טהורים
        sns.boxplot(x='track', y=feature, data=df, palette="Set2", width=0.5, fliersize=6)
        
        # 2. הוספת פיזור הנקודות עצמן (Jitter) כדי להבין כמה נתונים יש בכל אזור
        sns.stripplot(x='track', y=feature, data=df, color=".25", alpha=0.3, size=3, jitter=True)
        
        # עיצוב הכותרות
        clean_title = feature.replace("_", " ").title()
        plt.title(f'Outlier Detection: {clean_title} by Track', fontsize=16, fontweight='bold')
        plt.xlabel('Track', fontsize=12)
        plt.ylabel(clean_title, fontsize=12)
        
        # שמירת התמונה לתיקייה
        file_name = f"Outliers_{feature}.png"
        output_path = os.path.join(output_dir, file_name)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  [+] Saved: {file_name}")

    print(f"\n--- Process Complete ---")
    print(f"  [SUCCESS] All outlier visualizations saved to the '{output_dir}' folder.")

create_outlier_visualizations()