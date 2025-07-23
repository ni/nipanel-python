"""Streamlit visualization script to display data acquired by nidaqmx_analog_output_voltage.py."""

import extra_streamlit_components as stx  # type: ignore[import-untyped]
import streamlit as st
from nidaqmx.constants import Edge, Slope
from streamlit_echarts import st_echarts

import nipanel
from nipanel.controls import enum_selectbox

st.set_page_config(page_title="Analog Output Continuous Voltage", page_icon="📈", layout="wide")
st.title("Analog Output - Voltage")
panel = nipanel.get_streamlit_panel_accessor()

left_col, right_col = st.columns(2)

st.markdown(
    """
    <style>
     div.stNumberInput {
        max-width: 190px !important;
    }
    div.stTextInput {
        max-width: 190px !important;
    }
   
    div[data-baseweb="select"] {
        width: 190px !important; /* Adjust the width as needed */
    }
    </style>
    <style>
    iframe[title="streamlit_echarts.st_echarts"]{ height: 400px; width:100%;} 
   </style>
    """,
    unsafe_allow_html=True,
)

with left_col:
    with st.container(border=True):
        is_running = panel.get_value("is_running", True)
        if is_running:
            st.button("Stop", key="stop_button")
        else:
            st.button("Run", key="run_button")
        st.title("Channel Settings")
        physical_channel = st.selectbox(
            options=panel.get_value("available_channel_names", ["Mod2/ai0"]),
            index=0,
            label="Physical Channels",
            disabled=panel.get_value("is_running", False),
        )
        panel.set_value("physical_channel", physical_channel)

        max_value_voltage = st.number_input(
            "Max Value",
            value=5.0,
            step=0.1,
            disabled=panel.get_value("is_running", False),
            key="max_value_voltage",
        )

        min_value_voltage = st.number_input(
            "Min Value",
            value=-5.0,
            step=0.1,
            disabled=panel.get_value("is_running", False),
            key="min_value_voltage",
        )
        st.title("Timing and Buffer Settings")

        st.selectbox(
            "Sample Clock Source",
            options=panel.get_value("available_trigger_sources", [""]),
            index=0,
            disabled=panel.get_value("is_running", False),
        )
        st.number_input(
            "Sample Rate",
            value=1000.0,
            min_value=1.0,
            step=1.0,
            disabled=panel.get_value("is_running", False),
            key="rate",
        )
        st.number_input(
            "Number of Samples",
            value=1000,
            min_value=1,
            step=1,
            disabled=panel.get_value("is_running", False),
            key="total_samples",
        )
        st.number_input(
            "Actual Sample Rate",
            value=panel.get_value("actual_sample_rate", 1000.0),
            key="actual_sample_rate",
            step=1.0,
            disabled=True,
        )
        st.title("Waveform Settings")
        st.number_input(
            "Frequency",
            value=panel.get_value("frequency", 10.0),
            key="frequency",
            step=1.0,
            disabled=panel.get_value("is_running", False),
        )
        st.number_input(
            "Amplitude",
            value=panel.get_value("amplitude", 1.0),
            key="amplitude",
            step=1.0,
            disabled=panel.get_value("is_running", False),
        )
        st.selectbox(
            label="Wave Type",
            options=["Sine Wave", "Triangle Wave", "Square Wave"],
            key="wave_type",
        )


with right_col:
    with st.container(border=True):
        st.title("Trigger Settings")
        trigger_type = stx.tab_bar(
            data=[
                stx.TabBarItemData(id=1, title="No Trigger", description=""),
                stx.TabBarItemData(id=2, title="Digital Start", description=""),
                stx.TabBarItemData(id=3, title="Digital Pause", description=""),
                stx.TabBarItemData(id=4, title="Digital Reference", description=""),
                stx.TabBarItemData(id=5, title="Analog Start", description=""),
                stx.TabBarItemData(id=6, title="Analog Pause", description=""),
                stx.TabBarItemData(id=7, title="Analog Reference", description=""),
            ],
            default=1,
        )
        panel.set_value("trigger_type", trigger_type)

        if trigger_type == "1":
            with st.container(border=True):
                st.write(
                    "To enable triggers, select a tab above, and configure the settings. \n Not all hardware supports all trigger types. Refer to your device documentation for more information."
                )
        if trigger_type == "2":
            with st.container(border=True):
                source = st.selectbox(
                    "Source:", options=panel.get_value("available_trigger_sources", [""])
                )
                panel.set_value("digital_source", source)
                enum_selectbox(
                    panel,
                    label="Edge",
                    value=Edge.FALLING,
                    disabled=panel.get_value("is_running", False),
                    key="edge",
                )
        if trigger_type == "3":
            with st.container(border=True):
                st.write(
                    "This trigger type is not supported in continuous sample timing. Refer to your device documentation for more information on which triggers are supported"
                )
        if trigger_type == "4":
            with st.container(border=True):
                st.write(
                    "This trigger type is not supported in continuous sample timing. Refer to your device documentation for more information on which triggers are supported"
                )
        if trigger_type == "5":
            with st.container(border=True):
                analog_source = st.text_input("Source:", "APFI0")
                panel.set_value("analog_source", analog_source)
                enum_selectbox(
                    panel,
                    label="Slope",
                    value=Slope.FALLING,
                    disabled=panel.get_value("is_running", False),
                    key="slope",
                )

                level = st.number_input("Level")
                panel.set_value("level", level)
                hysteriesis = st.number_input(
                    "Hysteriesis",
                    disabled=panel.get_value("is_running", False),
                    key="hysteriesis",
                )

        if trigger_type == "6":
            with st.container(border=True):
                st.write(
                    "This trigger type is not supported in continuous sample timing. Refer to your device documentation for more information on which triggers are supported"
                )
        if trigger_type == "7":
            with st.container(border=True):
                st.write(
                    "This trigger type is not supported in continuous sample timing. Refer to your device documentation for more information on which triggers are supported."
                )

        with st.container(border=True):
            acquired_data = panel.get_value("data", [0.0])
            sample_rate = panel.get_value("sample_rate", 1000.0)
            acquired_data_graph = {
                "animation": False,
                "tooltip": {"trigger": "axis"},
                "legend": {"data": ["Voltage (V)"]},
                "xAxis": {
                    "type": "category",
                    "data": [x / sample_rate for x in range(len(acquired_data))],
                    "name": "Time",
                    "nameLocation": "center",
                    "nameGap": 40,
                },
                "yAxis": {
                    "type": "value",
                    "name": "Volts",
                    "nameRotate": 90,
                    "nameLocation": "center",
                    "nameGap": 40,
                },
                "series": [
                    {
                        "name": "voltage_amplitude",
                        "type": "line",
                        "data": acquired_data,
                        "emphasis": {"focus": "series"},
                        "smooth": True,
                        "seriesLayoutBy": "row",
                    },
                ],
            }
            st_echarts(options=acquired_data_graph, height="400px", key="graph", width="100%")
