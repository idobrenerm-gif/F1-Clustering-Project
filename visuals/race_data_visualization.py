import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('processed_data/golden_laps_final.csv')

def add_labels(ax, fmt='%.1f'):
    for container in ax.containers:
        ax.bar_label(container, fmt=fmt, padding=3, fontsize=9)

speed_stats = df.groupby('Track')['speed'].agg(['mean', 'median']).reset_index()
speed_melted = pd.melt(speed_stats, id_vars='Track', var_name='Metric', value_name='Speed')
track_order = speed_stats.sort_values('mean', ascending=False)['Track'].tolist()

plt.figure(figsize=(12, 6))
ax1 = sns.barplot(data=speed_melted, x='Track', y='Speed', hue='Metric', palette='viridis', order=track_order)
plt.title('Average and Median Speed by Track')
plt.ylabel('Speed (km/h)')
plt.xticks(rotation=45)
add_labels(ax1)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig('combined_speed.png')
plt.close()

avg_thr = df.groupby('Track')['throttle'].mean().sort_values(ascending=False).reset_index()
plt.figure(figsize=(10, 5))
ax2 = sns.barplot(data=avg_thr, x='Track', y='throttle', palette='flare')
plt.title('Average Throttle % by Track')
plt.ylabel('Throttle %')
plt.xticks(rotation=45)
add_labels(ax2)
plt.tight_layout()
plt.savefig('avg_throttle.png')
plt.close() 

df['is_braking'] = df['brake'] > 0
brake_pct = (df.groupby('Track')['is_braking'].mean() * 100).sort_values(ascending=False).reset_index()
plt.figure(figsize=(10, 5))
ax3 = sns.barplot(data=brake_pct, x='Track', y='is_braking', palette='crest')
plt.title('Percentage of Track Braking')
plt.ylabel('Brake Application (%)')
plt.xticks(rotation=45)
add_labels(ax3)
plt.tight_layout()
plt.savefig('brake_percent.png')
plt.close()

laps = df[['Track', 'driver_number', 'Lap_Time']].drop_duplicates()
avg_lap = laps.groupby('Track')['Lap_Time'].mean().sort_values(ascending=False).reset_index()
plt.figure(figsize=(10, 5))
ax4 = sns.barplot(data=avg_lap, x='Track', y='Lap_Time', palette='rocket')
plt.title('Average Lap Time by Track')
plt.ylabel('Lap Time (s)')
plt.xticks(rotation=45)
add_labels(ax4, fmt='%.3f')
plt.tight_layout()
plt.savefig('avg_lap_time.png')
plt.close()