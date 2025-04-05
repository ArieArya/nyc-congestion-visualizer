import streamlit as st
import plotly.express as px
from utils.data import load_data

df = load_data()

df = df.groupby('Detection Region').agg({'CRZ Entries': 'sum', 'Latitude': 'first', 'Longitude': 'first'}).reset_index()

fig = px.density_mapbox(df,
                         lat='Latitude',
                         lon='Longitude',
                         z='CRZ Entries',
                         radius=10,
                         center=dict(lat=40.7128, lon=-74.0060),
                         mapbox_style="carto-positron",
                         title='Density of CRZ Entries Across Different Regions',
                         height=1000)
fig.update_layout(mapbox_zoom=10)

st.plotly_chart(fig, use_container_width=True)