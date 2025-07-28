"""Streamlit visualization script to display data acquired by nidaqmx_continuous_analog_input.py."""

import streamlit as st
from nidaqmx.constants import (
    TerminalConfiguration,
    CJCSource,
    TemperatureUnits,
    ThermocoupleType,
    LoggingMode,
)
from streamlit_echarts import st_echarts

import nipanel
from nipanel.controls import enum_selectbox


st.set_page_config(page_title="NI-DAQmx Example", page_icon="📈", layout="wide")
st.title("Analog Input - Voltage and Thermocouple in a Single Task")

st.markdown(
    """
    <style>
    div[data-baseweb="select"] {
        max-width: 250px !important;
    }
    div.stNumberInput {
        max-width: 250px !important;
    }
    div.stTextInput {
        max-width: 250px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

panel = nipanel.get_streamlit_panel_accessor()
is_running = panel.get_value("is_running", False)

if is_running:
    st.button(r"⏹️ Stop", key="stop_button")
else:
    st.button(r"▶️ Run", key="run_button")

thermocouple_data = panel.get_value("thermocouple_data", [0.0])
voltage_data = panel.get_value("voltage_data", [0.0])
sample_rate = panel.get_value("sample_rate", 0.0)

# Create two-column layout for the entire interface
left_column, right_column = st.columns([1, 1])

# Left column - Channel tabs and Timing Settings
with left_column:
    # Channel Settings tabs
    with st.container(border=True):
        st.header("Channel Settings")
        voltage_tab, thermocouple_tab = st.tabs(["Voltage", "Thermocouple"])

        voltage_tab.header("Voltage")
        with voltage_tab:
            channel_left_column, channel_right_column = st.columns(2)
            with channel_left_column:
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
            with channel_right_column:
                enum_selectbox(
                    panel,
                    label="Terminal Configuration",
                    value=TerminalConfiguration.DEFAULT,
                    disabled=panel.get_value("is_running", False),
                    key="terminal_configuration",
                )

        thermocouple_tab.header("Thermocouple")
        with thermocouple_tab:
            channel_left_column, channel_middle_column, channel_right_column = st.columns(3)
            with channel_left_column:
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
            with channel_middle_column:
                enum_selectbox(
                    panel,
                    label="Units",
                    value=TemperatureUnits.DEG_C,
                    disabled=panel.get_value("is_running", False),
                    key="thermocouple_units",
                )
                enum_selectbox(
                    panel,
                    label="Thermocouple Type",
                    value=ThermocoupleType.K,
                    disabled=panel.get_value("is_running", False),
                    key="thermocouple_type",
                )
            with channel_right_column:
                enum_selectbox(
                    panel,
                    label="CJC Source",
                    value=CJCSource.CONSTANT_USER_VALUE,
                    disabled=panel.get_value("is_running", False),
                    key="thermocouple_cjc_source",
                )
                st.number_input(
                    "CJC Value",
                    value=25.0,
                    step=1.0,
                    disabled=panel.get_value("is_running", False),
                    key="thermocouple_cjc_val",
                )

    # Timing Settings section in left column
    with st.container(border=True):
        st.header("Timing Settings")
        timing_left_column, timing_right_column = st.columns(2)
        with timing_left_column:
            st.selectbox(
                options=["OnboardClock"],
                label="Sample Clock Source",
                disabled=True,
            )
            st.number_input(
                "Sample Rate",
                value=1000.0,
                step=100.0,
                min_value=1.0,
                disabled=panel.get_value("is_running", False),
                key="sample_rate_input",
            )
        with timing_right_column:
            st.number_input(
                "Samples per Loop",
                value=3000,
                step=100,
                min_value=10,
                disabled=panel.get_value("is_running", False),
                key="samples_per_channel",
            )
            st.text_input(
                label="Actual Sample Rate",
                value=str(sample_rate) if sample_rate else "",
                key="actual_sample_rate_display",
            )

# Right column - Graph and Logging Settings
with right_column:
    with st.container(border=True):
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
        st_echarts(options=voltage_therm_graph, height="446px", key="voltage_therm_graph")

    # Logging Settings section in right column
    with st.container(border=True):
        st.header("Logging Settings")
        logging_left_column, logging_right_column = st.columns(2)
        with logging_left_column:
            enum_selectbox(
                panel,
                label="Logging Mode",
                value=LoggingMode.OFF,
                disabled=panel.get_value("is_running", False),
                key="logging_mode",
            )
        with logging_right_column:
            left_sub_column, right_sub_column = st.columns([3, 1])
            with left_sub_column:
                tdms_file_path = st.text_input(
                    label="TDMS File Path",
                    disabled=panel.get_value("is_running", False),
                    value="data.tdms",
                    key="tdms_file_path",
                )
