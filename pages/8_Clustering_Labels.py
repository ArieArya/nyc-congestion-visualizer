import streamlit as st
import plotly.express as px
from utils.data import load_data
import matplotlib.pyplot as plt
import pandas as pd

from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
import requests

df = load_data()
# Ensure 'Toll Date' is datetime
df['Toll Date'] = pd.to_datetime(df['Toll Date'], format='%m/%d/%Y')

# Create enhanced features (traffic, calendar, weather) and run clustering (as before)
daily_volume = df.groupby('Toll Date')['CRZ Entries'].sum().rename('total_volume')
hourly_pivot = df.groupby(['Toll Date', 'Hour of Day'])['CRZ Entries'].sum().unstack(fill_value=0)
    
peak_hours = [7, 8, 9, 17, 18, 19]
peak_volume = hourly_pivot[peak_hours].sum(axis=1)
peak_ratio = peak_volume / daily_volume
hourly_std = hourly_pivot.std(axis=1)
growth_rate = daily_volume.pct_change().fillna(0)
is_weekend = (daily_volume.index.weekday >= 5).astype(int)

API_KEY = "b1b230ed8664410080803403250504"
BASE_URL = "http://api.weatherapi.com/v1/history.json"

    
    
def fetch_weather(date_str, api_key=API_KEY, location="New York"):
    params = {"key": api_key, "q": location, "dt": date_str}
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    forecast_day = data["forecast"]["forecastday"][0]["day"]
    return {
        "date": date_str,
        "avgtemp_c": forecast_day["avgtemp_c"],
        "avghumidity": forecast_day["avghumidity"],
        "totalprecip_mm": forecast_day["totalprecip_mm"]
    }
    
unique_dates = daily_volume.index.strftime('%Y-%m-%d').unique()
weather_records = []
for date in unique_dates:
    try:
        weather_data = fetch_weather(date)
        weather_records.append(weather_data)
    except Exception as e:
        print(f"Failed to fetch weather for {date}: {e}")
    
weather_df = pd.DataFrame(weather_records)
weather_df['Toll Date'] = pd.to_datetime(weather_df['date'], format='%Y-%m-%d')
weather_df = weather_df.set_index('Toll Date')[['avgtemp_c','avghumidity','totalprecip_mm']]
weather_df['discomfort_index'] = weather_df['avgtemp_c'] - ((100 - weather_df['avghumidity'])/5)
    
features_df = pd.DataFrame({
    'total_volume': daily_volume,
    'peak_ratio': peak_ratio,
    'hourly_std': hourly_std,
    'growth_rate': growth_rate,
    'is_weekend': is_weekend
})
features_df = features_df.merge(weather_df, left_index=True, right_index=True, how='inner')
    
print("\nEnhanced Feature Set (first 5 rows):")
print(features_df.head())
    
scaler = StandardScaler()
X_scaled = scaler.fit_transform(features_df)
    
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
pca = PCA(n_components=0.95, random_state=42)
X_pca = pca.fit_transform(X_scaled)
print(f"Number of PCA components: {X_pca.shape[1]}")
    
sil_scores = {}
for k in range(2, 10):
    kmeans_temp = KMeans(n_clusters=k, random_state=42)
    labels = kmeans_temp.fit_predict(X_pca)
    score = silhouette_score(X_pca, labels)
    sil_scores[k] = score
    print(f"Silhouette score for k={k}: {score:.4f}")
optimal_k = max(sil_scores, key=sil_scores.get)
print(f"\nOptimal number of clusters: {optimal_k}")
    
kmeans = KMeans(n_clusters=optimal_k, random_state=42)
cluster_labels = kmeans.fit_predict(X_pca)
features_df['Cluster'] = cluster_labels
    
cluster_summary = features_df.groupby('Cluster').mean()
print("\nCluster Summary:")
print(cluster_summary)
    
plt.figure(figsize=(8,6))
plt.scatter(X_pca[:,0], X_pca[:,1], c=cluster_labels, cmap='viridis', s=50)
plt.xlabel("PC1")
plt.ylabel("PC2")
plt.title("PCA Projection of Enhanced Clusters")
plt.colorbar(label="Cluster")
plt.show()
    
descriptive_labels = {}
for cluster in cluster_summary.index:
    if cluster_summary.loc[cluster, 'is_weekend'] >= 0.5:
        descriptive_labels[cluster] = "Weekend/Low Demand"
    else:
        descriptive_labels[cluster] = "Weekday"
features_df['Pattern Type'] = features_df['Cluster'].map(descriptive_labels)
    
print("\nAssigned Cluster Descriptive Labels (first 5 rows):")
print(features_df[['Cluster', 'Pattern Type']].head())
    
# ---------------------------
# STEP C: Merge Cluster Labels with Hourly Traffic Data for Actionable Visualization
# ---------------------------
# Define daily_pattern: a pivot table of hourly CRZ Entries by Toll Date.
daily_pattern = df.groupby(['Toll Date', 'Hour of Day'])['CRZ Entries'].sum().unstack(fill_value=0)
print("\nDaily Traffic Pattern (first 5 rows):")
print(daily_pattern.head())
    
# Reset index to merge with features_df (which contains cluster labels)
daily_pattern_reset = daily_pattern.reset_index()  
features_reset = features_df.reset_index()  # features_df's index is Toll Date
    
# Merge the cluster labels into daily_pattern based on Toll Date.
merged_pattern = pd.merge(daily_pattern_reset, features_reset[['Toll Date', 'Cluster']], on='Toll Date', how='left')
merged_pattern.set_index('Toll Date', inplace=True)
    
# Group by cluster and calculate the average hourly traffic pattern.
hour_cols = [col for col in merged_pattern.columns if isinstance(col, (int, float))]
cluster_profiles_line = merged_pattern.groupby('Cluster')[hour_cols].mean()
    
# Plot the average daily traffic profile for each cluster.
plt.figure(figsize=(10,6))
for c_label in cluster_profiles_line.index:
    plt.plot(hour_cols, cluster_profiles_line.loc[c_label, hour_cols],
                label=f"{descriptive_labels.get(c_label, 'Unknown')}")
plt.xlabel("Hour of Day")
plt.ylabel("Average CRZ Entries")
plt.title("Average Daily Traffic Pattern by Enhanced Clusters")
plt.legend()
plt.show()
st.pyplot(plt)
    
print("\nEnhanced Temporal Signature Identification complete.")
print("These clusters incorporate traffic, weather, and calendar features to distinguish different types of days, visualized as hourly traffic profiles.")