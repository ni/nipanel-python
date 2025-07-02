"""Streamlit visualization script to display data acquired by nidaqmx_continuous_analog_input.py."""

import streamlit as st
from nidaqmx.constants import TerminalConfiguration
from streamlit_echarts import st_echarts

import nipanel


st.set_page_config(page_title="NI-DAQmx Example", page_icon="📈", layout="wide")
st.title("Analog Input - Voltage and Thermocouple in a Single Task")

panel = nipanel.get_panel_accessor()

is_running = panel.get_value("is_running", False)
if is_running:
    st.button("Stop", key="stop_button")
else:
    st.button("Run", key="run_button")

st.markdown(
    """
    <style>
    div[data-baseweb="select"] {
        width: 190px !important; /* Adjust the width as needed */
    }
    div.stNumberInput {
        width: 190px !important;
    }
    div.stTextInput {
        width: 190px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

thermocouple_data = panel.get_value("thermocouple_data", [0.0])
voltage_data = panel.get_value("voltage_data", [0.0])

sample_rate = panel.get_value("sample_rate", 0.0)

# Create two-column layout for the entire interface
left_col, right_col = st.columns([1, 1])

# Left column - Channel tabs and Timing Settings
with left_col:
    # Channel Settings tabs
    st.header("Channel Settings")
    voltage_tab, thermocouple_tab = st.tabs(["Voltage", "Thermocouple"])

    voltage_tab.header("Voltage")
    with voltage_tab:
        channel_left, channel_right = st.columns(2)
        with channel_left:
            st.selectbox(options=["Dev1/ai0"], label="Physical Channels", disabled=True)
            st.number_input(
                "Min Value",
                value=-5.0,
                step=0.1,
                disabled=panel.get_value("is_running", False),
                key="voltage_min_value",
            )
            st.number_input(
                "Max Value",
                value=5.0,
                step=0.1,
                disabled=panel.get_value("is_running", False),
                key="voltage_max_value",
            )
        with channel_right:
            nipanel.enum_selectbox(
                panel,
                label="Terminal Configuration",
                value=TerminalConfiguration.DEFAULT,
                disabled=panel.get_value("is_running", False),
                key="terminal_configuration",
            )

    thermocouple_tab.header("Thermocouple")
    with thermocouple_tab:
        channel_left, channel_middle, channel_right = st.columns(3)
        with channel_left:
            st.selectbox(options=["Dev1/ai1"], label="Physical Channel", disabled=True)
            st.number_input(
                "Min Value",
                value=0.0,
                step=1.0,
                disabled=panel.get_value("is_running", False),
                key="thermocouple_min_value",
            )
            st.number_input(
                "Max Value",
                value=100.0,
                step=1.0,
                disabled=panel.get_value("is_running", False),
                key="thermocouple_max_value",
            )
        with channel_middle:
            st.selectbox(options=["Deg C"], label="Units", disabled=False)
            st.selectbox(options=["J"], label="Thermocouple Type", disabled=False)
        with channel_right:
            st.selectbox(options=["Constant Value"], label="CJC Source", disabled=False)
            st.selectbox(options=["25"], label="CJC Value", disabled=False)

    # Timing Settings section in left column
    st.header("Timing Settings")
    timing_left, timing_right = st.columns(2)
    with timing_left:
        st.selectbox(options=["OnboardClock"], label="Sample Clock Source", disabled=False)
        st.selectbox(options=["1000"], label="Samples per Loop", disabled=False)
    with timing_right:
        st.selectbox(options=[" "], label="Actual Sample Rate", disabled=True)
        st.text_input(
            label="Sample Rate",
            disabled=True,
            value=str(sample_rate) if sample_rate else "",
            key="sample_rate_display",
        )

# Right column - Graph and Logging Settings
with right_col:
    # Graph section
    st.header("Voltage & Thermocouple")
    voltage_therm_graph = {
        "animation": False,
        "tooltip": {"trigger": "axis"},
        "legend": {"data": ["Voltage (V)", "Temperature (C)"]},
        "xAxis": {
            "type": "category",
            "data": [
                x / sample_rate if sample_rate > 0.001 else x for x in range(len(voltage_data))
            ],
            "name": "Time",
            "nameLocation": "center",
            "nameGap": 40,
        },
        "yAxis": {
            "type": "value",
            "name": "Measurement",
            "nameRotate": 90,
            "nameLocation": "center",
            "nameGap": 40,
        },
        "series": [
            {
                "name": "voltage_amplitude",
                "type": "line",
                "data": voltage_data,
                "emphasis": {"focus": "series"},
                "smooth": True,
                "seriesLayoutBy": "row",
            },
            {
                "name": "thermocouple_amplitude",
                "type": "line",
                "data": thermocouple_data,
                "color": "red",
                "emphasis": {"focus": "series"},
                "smooth": True,
                "seriesLayoutBy": "row",
            },
        ],
    }
    st_echarts(options=voltage_therm_graph, height="400px", key="voltage_therm_graph")

    # Logging Settings section in right column
    st.header("Logging Settings")
    logging_left, logging_right = st.columns(2)
    with logging_left:
        st.selectbox(options=["Off"], label="Logging Mode", disabled=False)
    with logging_right:
        st.text_input(
            label="TDMS File Path",
            disabled=panel.get_value("is_running", False),
            value="",
            key="tdms_file_path",
        )
