from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium, folium_static
import seaborn as sns
import polars as pl
import json
import requests
import plotly.express as px

df = load_data()

    # Group traffic data by date
    traffic_daily = df.groupby("Toll Date")["CRZ Entries"].sum().reset_index()
    traffic_daily.rename(columns={"CRZ Entries": "daily_crz_entries"}, inplace=True)

    # Fetch weather data for unique dates
    unique_dates = traffic_daily["Toll Date"].unique()
    weather_records = []
    for date in unique_dates:
        weather_data = fetch_weather(date)
        if weather_data:
            weather_records.append(weather_data)

    # Create weather DataFrame
    weather_df = pd.DataFrame(weather_records)

    # Merge traffic and weather data
    merged_df = pd.merge(traffic_daily, weather_df, left_on="Toll Date", right_on="date", how="inner")

    # Map weather conditions to categories
    weather_category_map = {
        "Sunny": "Favorable",
        "Clear": "Favorable",
        "Partly cloudy": "Favorable",
        "Overcast": "Neutral",
        "Cloudy": "Neutral",
        "Patchy rain possible": "Neutral",
        "Light rain": "Neutral",
        "Heavy rain": "Unfavorable",
        "Moderate rain": "Unfavorable",
    }
    merged_df["weather_category"] = merged_df["condition"].apply(lambda cond: weather_category_map.get(cond, "Neutral"))

    # Convert date column to datetime
    merged_df['Toll Date'] = pd.to_datetime(merged_df['Toll Date'], format='%m/%d/%Y')

    # Generate the scatter plot
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=merged_df, x='avgtemp_c', y='daily_crz_entries', hue='weather_category', 
                    palette='Set1', s=100, edgecolor='black')
    sns.regplot(data=merged_df, x='avgtemp_c', y='daily_crz_entries', scatter=False, 
                color='black', line_kws={'linewidth': 1.5})
    plt.title('Daily Traffic Volume vs. Average Temperature')
    plt.xlabel('Average Temperature (°C)')
    plt.ylabel('Daily CRZ Entries')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title='Weather Category')
    plt.tight_layout()
    st.pyplot(plt)