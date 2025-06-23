"""Streamlit application script for displaying values using nipanel package."""

import streamlit as st

import nipanel

panel = nipanel.get_panel_accessor()


st.set_page_config(page_title="Sample Panel Example", page_icon="📊", layout="wide")
st.title("Sample Panel Example")

col1, col2 = st.columns([0.4, 0.6])

with col1:
    st.write("String")
    st.write("Integer")
    st.write("Float")
    st.write("Boolean")
    st.write("List")

with col2:
    st.write(panel.get_value("sample_string", ""))
    st.write(panel.get_value("sample_int", 0))
    st.write(panel.get_value("sample_float", 0.0))
    st.write(panel.get_value("sample_bool", False))
    st.write(panel.get_value("float_values", []))
