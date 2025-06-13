"""Streamlit application script for displaying values using nipanel package."""

import streamlit as st

import nipanel

panel = nipanel.initialize_panel()

st.title("Sample Panel")

col1, col2 = st.columns([0.4, 0.6])

with col1:
    st.write("String")
    st.write("Integer")
    st.write("Float")
    st.write("Boolean")
    st.write("List")

    if st.button("Rerun app"):
        st.rerun()

with col2:
    st.write(panel.get_value("sample_string"))
    st.write(panel.get_value("sample_int"))
    st.write(panel.get_value("sample_float"))
    st.write(panel.get_value("sample_bool"))
    st.write(panel.get_value("float_values"))
