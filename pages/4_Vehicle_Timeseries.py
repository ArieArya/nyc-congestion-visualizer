import streamlit as st
import plotly.express as px
from utils.data import load_data
import matplotlib.pyplot as plt

df = load_data()

cars = df[df['Vehicle Class'] == '1 - Cars, Pickups and Vans']
trucks = df[df['Vehicle Class'].isin(['2 - Single-Unit Trucks', '3 - Multi-Unit Trucks'])]
motorcycles = df[df['Vehicle Class'] == '5 - Motorcycles']
taxis = df[df['Vehicle Class'] == 'TLC Taxi/FHV']

plt.figure(figsize=(10, 6))
bins = range(0, 25)  # Hours 0 to 24

plt.hist(cars['Hour of Day'], bins=bins, weights=cars['CRZ Entries'],
		alpha=0.5, label='Cars', edgecolor='black')
plt.hist(trucks['Hour of Day'], bins=bins, weights=trucks['CRZ Entries'],
		alpha=0.5, label='Trucks (Lorries)', edgecolor='black')
plt.hist(motorcycles['Hour of Day'], bins=bins, weights=motorcycles['CRZ Entries'],
		alpha=0.5, label='Motorcycles', edgecolor='black')
plt.hist(taxis['Hour of Day'], bins=bins, weights=taxis['CRZ Entries'],
		alpha=0.5, label='Taxis', edgecolor='black')

plt.xlabel("Hour of Day")
plt.ylabel("Number of Entries (Weighted by CRZ Entries)")
plt.title("Weighted Vehicle Entries by Hour of Day")
plt.legend()
plt.xticks(bins)
st.pyplot(plt)