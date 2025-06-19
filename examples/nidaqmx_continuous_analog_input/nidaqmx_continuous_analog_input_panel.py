"""Streamlit application script for displaying values using nipanel package."""

import streamlit as st
from streamlit_echarts import st_echarts

import nipanel

panel = nipanel.initialize_panel()

st.title("Analog Input - Voltage and Thermocouple in a Single Task")
voltage_tab, thermocouple_tab = st.tabs(["Voltage", "Thermocouple"])

st.markdown(
    """
    <style>
    div[data-baseweb="select"] {
        width: 190px !important; /* Adjust the width as needed */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

list_of_therm_amp = panel.get_value("thermocouple_data", [0.0])
list_of_voltage_amp = panel.get_value("voltage_data", [0.0])

st.header("Voltage & Thermocouple")
voltage_therm_graph = {
    "tooltip": {"trigger": "axis"},
    "legend": {"data": ["voltage_amplitude", "thermocouple_amplitude"]},
    "xAxis": {
        "type": "category",
        "data": list(range(len(list_of_voltage_amp))),
        "name": "Time",
    },
    "yAxis": {"type": "value", "name": "Voltage and Thermocouple Amplitude"},
    "series": [
        {
            "name": "voltage_amplitude",
            "type": "line",
            "data": list_of_voltage_amp,
            "emphasis": {"focus": "series"},
            "smooth": True,
            "seriesLayoutBy": "row",
        },
        {
            "name": "thermocouple_amplitude",
            "type": "line",
            "data": list_of_therm_amp,
            "color": "red",
            "emphasis": {"focus": "series"},
            "smooth": True,
            "seriesLayoutBy": "row",
        },
    ],
}
st_echarts(options=voltage_therm_graph, height="400px")

voltage_tab.header("Voltage")
with voltage_tab:
    left_volt_tab, center_volt_tab, right_volt_tab = st.columns(3)
    with left_volt_tab:
        st.selectbox(options=["Dev1/ai0"], label="Physical Channels", disabled=True)
        st.selectbox(options=["Off"], label="Logging Modes", disabled=False)
    with center_volt_tab:
        st.selectbox(options=["-5"], label="Min Value")
        st.selectbox(options=["5"], label="Max Value")
        st.selectbox(options=["1000"], label="Samples per Loops", disabled=False)
    with right_volt_tab:
        st.selectbox(options=["default"], label="Terminal Configurations")
        st.selectbox(options=["OnboardClock"], label="Sample Clock Sources", disabled=False)


thermocouple_tab.header("Thermocouple")
with thermocouple_tab:
    left, middle, right = st.columns(3)
    with left:
        st.selectbox(options=["Dev1/ai1"], label="Physical Channel", disabled=True)
        st.selectbox(options=["0"], label="Min", disabled=False)
        st.selectbox(options=["100"], label="Max", disabled=False)
        st.selectbox(options=["Off"], label="Logging Mode", disabled=False)

    with middle:
        st.selectbox(options=["Deg C"], label="Units", disabled=False)
        st.selectbox(options=["J"], label="Thermocouple Type", disabled=False)
        st.selectbox(options=["Constant Value"], label="CJC Source", disabled=False)
        st.selectbox(options=["1000"], label="Samples per Loop", disabled=False)
    with right:
        st.selectbox(options=["25"], label="CJC Value", disabled=False)
        st.selectbox(options=["OnboardClock"], label="Sample Clock Source", disabled=False)
        st.selectbox(options=[" "], label="Actual Sample Rate", disabled=True)
