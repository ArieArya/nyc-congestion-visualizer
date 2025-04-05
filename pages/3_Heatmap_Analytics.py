import streamlit as st
import plotly.express as px
from utils.data import load_data
import folium
import polars as pl
import json
import pandas as pd
from streamlit_folium import st_folium, folium_static
# Arie's map
# df = st.session_state.df

# df = df.groupby('Detection Region').agg({'CRZ Entries': 'sum', 'Latitude': 'first', 'Longitude': 'first'}).reset_index()

# fig = px.density_mapbox(df,
#                          lat='Latitude',
#                          lon='Longitude',
#                          z='CRZ Entries',
#                          radius=10,
#                          center=dict(lat=40.7128, lon=-74.0060),
#                          mapbox_style="carto-positron",
#                          title='Density of CRZ Entries Across Different Regions',
#                          height=1000)
# fig.update_layout(mapbox_zoom=10)

# st.plotly_chart(fig, use_container_width=True)

# Hubert's map
@st.cache_data
def load_location_coords():
    """Load location coordinates from detection_groups.json."""
    try:
        with open("data\detection_groups.json", "r") as f:
            location_coords = json.load(f)

        location_df = pl.DataFrame(
            {
                "Detection Group": list(location_coords.keys()),
                "Latitude": [v[0] for v in location_coords.values()],
                "Longitude": [v[1] for v in location_coords.values()],
            }
        )
        return location_df
    except Exception as e:
        st.error(f"Error loading location coordinates: {e}")
        return None


@st.cache_data
def preprocess_map_data(df, location_df):
    """Merge data with location coordinates and filter valid entries."""
    try:
        if not isinstance(df, pl.DataFrame):
            df = pl.from_pandas(df)

        df_merged = df.join(location_df, on="Detection Group", how="left")
        df_map = df_merged.filter(
            df_merged["Latitude"].is_not_null() & df_merged["Longitude"].is_not_null()
        )
        return df_map
    except Exception as e:
        st.error(f"Error preprocessing map data: {e}")
        return None

def generate_interactive_map(aggregated_data, style='Satellite'):
    """Render a folium map with CRZ markers and customizable tile style."""

    tile_styles = {
        'Satellite': {
            'tiles': 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            'attr': 'Tiles © Esri — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, etc.'
        },
        'Light': {
            'tiles': 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
            'attr': '&copy; <a href="https://carto.com/">CARTO</a>'
        },
        "Dark": {
            "tiles": "https://cartodb-basemaps-a.global.ssl.fastly.net/dark_all/{z}/{x}/{y}.png",
            "attr": "© OpenStreetMap contributors © CARTO"
        },
        'Standard': {
            'tiles': 'OpenStreetMap',
            'attr': None
        }
    }

    if style not in tile_styles:
        raise ValueError(f"Invalid map style: {style}. Choose from 'satellite', 'white', or 'regular'.")

    selected_style = tile_styles[style]

    m = folium.Map(
        location=[40.75, -73.97],
        zoom_start=12,
        tiles=selected_style['tiles'],
        attr=selected_style['attr'],
        width='100%',        # or a fixed size like '1200px'
        height='1000px',       # increase this for taller map
        radius=10,
    )


    for _, row in aggregated_data.iterrows():
        if pd.notna(row["Latitude"]) and pd.notna(row["Longitude"]):
            popup_html = f"""
            <div style="font-family: 'Helvetica Neue', sans-serif; font-size: 14px;">
                <b style="color: #2c3e50;">{row['Detection Group']}</b><br>
                <span style="color: #16a085;">Total CRZ Entries:</span> <b>{row['CRZ Entries']}</b>
            </div>
            """
            folium.Marker(
                location=[row["Latitude"], row["Longitude"]],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color="blue", icon="car", prefix="fa")
            ).add_to(m)

    # Add layer control for switching base maps
    # folium.LayerControl(position='topright', collapsed=False).add_to(m)

    return m

st.write("### Interactive Map")
df = load_data()
with st.container():
    location_df = load_location_coords()
    if location_df is None:
        st.error("Failed to load location coordinates.")
    else:
        df_map = preprocess_map_data(df, location_df)
        if df_map is None or df_map.is_empty():
            st.error("No valid data available for the map.")
        else:
            df_map_pandas = df_map.to_pandas()

            aggregated_data = (
                df_map_pandas.groupby(["Latitude", "Longitude", "Detection Group"])["CRZ Entries"]
                .sum()
                .reset_index()
            )
            col1, _ = st.columns([1, 4])  # Left column is smaller
            with col1:
                style_choice = st.selectbox("Choose map style:", ["Satellite", "Standard", "Light","Dark"])
            # Generate and display the map
            m = generate_interactive_map(aggregated_data, style=style_choice)
            folium_static(m)