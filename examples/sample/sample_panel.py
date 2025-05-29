"""Streamlit application script for displaying values using nipanel package."""

import pandas as pd
import streamlit as st

import nipanel

panel = nipanel.StreamlitPanelValueAccessor(panel_id="sample_panel")

st.title("Sample Panel")

col1, col2 = st.columns([0.4, 0.6])

with col1:
    st.write("String")
    st.write("Integer")
    st.write("Float")
    st.write("Boolean")
    st.write("Line")

with col2:
    st.write(panel.get_value("sample_string"))
    st.write(panel.get_value("sample_int"))
    st.write(panel.get_value("sample_float"))
    st.write(panel.get_value("sample_bool"))
    st.line_chart(
        data = pd.DataFrame(
            {
                "x": panel.get_value("x_values"),
                "y": panel.get_value("y_values"),
            }
        ),
        x="x",
        y="y",
        x_label="x",
        y_label="sin(x)",
    )
