import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Load data
file_path = 'processed_data/New_Qualifying_fastest_laps_telemetry.csv'
features = ['Track', 'driver_number', 'lap_duration', 'x', 'y', 'speed', 'brake', 'throttle', 'n_gear', 'drs']
df = pd.read_csv(file_path, usecols=features)

# Set global plotting style
sns.set_theme(style="whitegrid")

# 1. Feature distributions
def plot_distributions(data):
    numeric_cols = ['speed', 'brake', 'throttle', 'n_gear']
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Feature Distributions')
    
    for i, col in enumerate(numeric_cols):
        sns.histplot(data[col], kde=True, ax=axes[i//2, i%2], bins=30)
    plt.tight_layout()
    plt.show()

# 2. Differences between categories
def plot_category_differences(data):
    plt.figure(figsize=(14, 6))
    sns.boxplot(x='n_gear', y='speed', data=data)
    plt.title('Speed Distribution by Gear (n_gear)')
    plt.show()
    
    # Speed variance by Track (top 10 tracks if many exist)
    top_tracks = data['Track'].value_counts().index[:10]
    plt.figure(figsize=(14, 6))
    sns.violinplot(x='Track', y='speed', data=data[data['Track'].isin(top_tracks)])
    plt.title('Speed Distribution by Track')
    plt.xticks(rotation=45)
    plt.show()

# 3. Trends and patterns
def plot_trends_and_patterns(data):
    # Visualize the track layout based on x,y coordinates, colored by speed
    sample_lap = data.iloc[:5000] # Adjust slice based on lap frequency
    
    plt.figure(figsize=(10, 8))
    scatter = plt.scatter(sample_lap['x'], sample_lap['y'], c=sample_lap['speed'], 
                          cmap='coolwarm', s=10, alpha=0.7)
    plt.colorbar(scatter, label='Speed (km/h)')
    plt.title('Track Layout Pattern (X/Y) colored by Speed')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.axis('equal')
    plt.show()

# 4. Scatter and Pair plots
def plot_relationships(data):
    # Sample data to avoid memory issues and slow rendering on large datasets
    sample_df = data.sample(n=min(2000, len(data)), random_state=42)
    
    cols_to_pair = ['speed', 'throttle', 'brake', 'n_gear', 'drs']
    sns.pairplot(sample_df[cols_to_pair], diag_kind='kde', corner=True)
    plt.suptitle('Pairplot of Telemetry Features', y=1.02)
    plt.show()

# 5. Correlation Heatmap
def plot_correlation_heatmap(data):
    # Isolate numeric data for correlation calculation
    numeric_df = data.select_dtypes(include=[np.number])
    corr = numeric_df.corr()
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr, annot=True, cmap='vlag', fmt=".2f", linewidths=.5)
    plt.title('Correlation Heatmap Matrix')
    plt.show()

# Execute visualizations
#plot_distributions(df)
#plot_category_differences(df)
#plot_trends_and_patterns(df)
plot_relationships(df)
#plot_correlation_heatmap(df)