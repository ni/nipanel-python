"""Streamlit application script for displaying values using nipanel package."""

import streamlit as st

import nipanel

panel = nipanel.StreamlitPanelValueAccessor(panel_id="sample_panel_2")

st.title("Sample Panel Two")

col1, col2 = st.columns([0.4, 0.6])

with col1:
    st.write("String")
    st.write("Integer")

with col2:
    st.write(panel.get_value("sample_string"))
    st.write(panel.get_value("sample_int"))
