import streamlit as st

def render_dataframe_viewer():
    st.subheader("Filtered Data (`filtered_df`)")
    st.dataframe(st.session_state.filtered_df.head(50))
