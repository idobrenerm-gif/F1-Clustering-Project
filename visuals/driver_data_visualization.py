import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('processed_data/f1_drivers_data_2023.csv')

#Age distribution
plt.figure(figsize=(8, 5))
sns.histplot(df['age_in_2023'], bins=8, kde=True, color='blue')
plt.title('Age Distribution of F1 Drivers (2023)')
plt.xlabel('Age')
plt.ylabel('Count')
plt.savefig('age_distribution.png')
plt.close()

#Height vs Weight
fig, axes = plt.subplots(1, 2, figsize=(10, 5))

sns.boxplot(data=df, y='height_cm', ax=axes[0], color='skyblue')
axes[0].set_title('Height Distribution (cm)')
axes[0].set_ylabel('Height (cm)')

sns.boxplot(data=df, y='weight_kg', ax=axes[1], color='lightgreen')
axes[1].set_title('Weight Distribution (kg)')
axes[1].set_ylabel('Weight (kg)')

plt.tight_layout()
plt.savefig('height_weight_boxplot.png')
plt.close()

#Kids distribution
plt.figure(figsize=(6, 4))
sns.countplot(data=df, x='has_kids', palette='Set2')
plt.title('F1 Drivers: With vs Without Kids (2023)')
plt.xlabel('Has Kids')
plt.ylabel('Number of Drivers')
plt.savefig('kids_distribution.png')
plt.close()

#Marital status distribution
df['marital_status_clean'] = df['marital_status'].str.lower()
df['is_single'] = df['marital_status_clean'].apply(lambda x: 'Single' if x == 'single' else 'Not Single')
plt.figure(figsize=(6, 4))
sns.countplot(data=df, x='is_single', palette='Pastel1')
plt.title('F1 Drivers: Single vs Not Single (2023)')
plt.xlabel('Relationship Status')
plt.ylabel('Number of Drivers')
plt.savefig('marital_status_distribution.png')
plt.close()