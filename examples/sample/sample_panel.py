"""Streamlit application script for displaying values using nipanel package."""

import streamlit as st

import nipanel

panel = nipanel.initialize_panel()

st.title("Sample Panel")

col1, col2, col3 = st.columns([0.4, 0.3, 0.3])

with col1:
    st.markdown("**Type**")
    st.write("String")
    st.write("Integer")
    st.write("Float")
    st.write("Boolean")
    st.write("List")

with col2:
    st.markdown("**Set Values**")
    st.write(panel.get_value("sample_string"))
    st.write(panel.get_value("sample_int"))
    st.write(panel.get_value("sample_float"))
    st.write(panel.get_value("sample_bool"))
    st.write(panel.get_value("float_values"))

with col3:
    st.markdown("**Default Values**")
    st.write(panel.get_value("missing_string", "0"))
    st.write(panel.get_value("missing_int", 0))
    st.write(panel.get_value("missing_float", 0.0))
    st.write(panel.get_value("missing_bool", False))
    st.write(panel.get_value("missing_list", [0.0]))
