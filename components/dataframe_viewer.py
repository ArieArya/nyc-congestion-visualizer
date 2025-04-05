import streamlit as st

def render_dataframe_viewer():
    st.subheader("Data")
    st.dataframe(st.session_state.filtered_df.head(10000))
