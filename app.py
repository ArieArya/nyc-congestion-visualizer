import streamlit as st
from components.dataframe_viewer import render_dataframe_viewer
from components.main_component import render_main_component
from utils.data import load_data

# App title
st.set_page_config(layout="wide")
st.title("MTA Congestion Relief Zone (CRZ) Data Explorer")

# Define pages in our application
pg = st.navigation([
	st.Page("pages/1_Data_Explorer.py"),
	st.Page("pages/2_Top_Entries_Analytics.py"),
	st.Page("pages/3_Heatmap_Analytics.py")])
pg.run()