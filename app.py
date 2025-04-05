import streamlit as st
from components.dataframe_viewer import render_dataframe_viewer
from components.main_component import render_main_component
from utils.data import load_data

# App title
st.set_page_config(layout="wide")
st.title("MTA Congestion Relief Zone (CRZ) Data Explorer")

# Load and cache dataset
if "filtered_df" not in st.session_state:
    df = load_data()
    st.session_state.filtered_df = df
    st.session_state.df_history = []

# Render UI sections
render_dataframe_viewer()
render_main_component()