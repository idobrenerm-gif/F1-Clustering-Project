import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import seaborn as sns

def run_eda():
#loading the dataset
    print("Loading dataset...")
    df = pd.read_csv("F1_4_Races_All_Corners.csv")

    print("\n" + "="*40)
    print("1. MISSING VALUES CHECK")
    print("="*40)
    #Checking for missing values in the dataset
    missing_values = df.isnull().sum()
    if missing_values.sum() == 0:
        print(" Perfect! ZERO missing values found.")
    else:
        print("Missing values detected:\n", missing_values[missing_values > 0])

    

    print("\n" + "="*40)
    print("2. DESCRIPTIVE STATISTICS")
    print("="*40)
    stats = df[['entry_speed', 'apex_speed', 'speed_drop', 'min_gear']].describe()
   
    print(stats.round(2))


    print("\nDrawing Boxplots to find outliers...")
    
    plt.figure(figsize=(15, 6))
    
    # plot 1: entry speed
    plt.subplot(1, 3, 1)
    sns.boxplot(y=df['entry_speed'], color='skyblue')
    plt.title('Distribution of Entry Speed')
    plt.ylabel('Speed (km/h)')

    # plot 2: apex speed
    plt.subplot(1, 3, 2)
    sns.boxplot(y=df['apex_speed'], color='lightgreen')
    plt.title('Distribution of Apex Speed')
    plt.ylabel('Speed (km/h)')

    # plot 3: speed drop
    plt.subplot(1, 3, 3)
    sns.boxplot(y=df['speed_drop'], color='salmon')
    plt.title('Distribution of Speed Drop (Braking Force)')
    plt.ylabel('Speed Lost (km/h)')
    plt.tight_layout()
    
    plt.show()

if __name__ == "__main__":
    run_eda()