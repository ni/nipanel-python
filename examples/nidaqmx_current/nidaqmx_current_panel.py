"""Streamlit visualization script to display data acquired by nidaqmx_analog_input_filtering.py."""

import extra_streamlit_components as stx  # type: ignore[import-untyped]
import streamlit as st
from nidaqmx.constants import (
    CurrentShuntResistorLocation,
    CurrentUnits,
    Edge,
    FilterResponse,
    LoggingMode,
    Slope,
    StrainGageBridgeType,
    TerminalConfiguration,
)
from settings import AnalogPause, PauseWhen
from streamlit_echarts import st_echarts

import nipanel
from nipanel.controls import enum_selectbox

st.set_page_config(page_title="Current - Continuous Input", page_icon="📈", layout="wide")
st.title("Current - Continuous Input")
panel = nipanel.get_panel_accessor()

left_col, right_col = st.columns(2)


is_running = panel.get_value("is_running", True)
with left_col:
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
    </style>
    """,
    unsafe_allow_html=True,
)

streamlit_style = """
    <style>
    iframe[title="streamlit_echarts.st_echarts"]{ height: 400px; width:100%;} 
   </style>
    """
st.markdown(streamlit_style, unsafe_allow_html=True)


with left_col:
    with st.container(border=True):

        st.title("Channel Settings")
        st.selectbox(options=["Mod3/ai10"], index=0, label="Physical Channels", disabled=True)

        enum_selectbox(
            panel,
            label="Shunt Resistor",
            value=CurrentShuntResistorLocation.EXTERNAL,
            disabled=panel.get_value("is_running", False),
            key="shunt_location",
        )
        min_value_current = st.number_input(
            "Min Current (A)",
            value=0.0,
            step=0.001,
            disabled=panel.get_value("is_running", False),
        )
        panel.set_value("min_value_current", min_value_current)
        max_value_current = st.number_input(
            "Max Current (A)",
            value=0.02,
            step=1.0,
            key="max_value_current",
            disabled=panel.get_value("is_running", False),
        )
        current = panel.set_value("max_value_current", max_value_current)  # type:ignore
        shunt_resistor_value = st.number_input(
            "Shunt Resistor Value (Ohm)",
            value=249.0,
            step=1.0,
            disabled=panel.get_value("is_running", False),
        )
        panel.set_value("shunt_resistor_value", shunt_resistor_value)

        st.title("Timing Settings")

        st.selectbox("Sample Clock Source", options=["Onboard Clock"], index=0, disabled=True)
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
            key="num_of_samps",
        )
        st.selectbox(
            "Actual Sample Rate", options=[panel.get_value("sample_rate", 100.0)], disabled=True
        )

        st.title("Logging Settings")
        enum_selectbox(
            panel,
            label="Logging Mode",
            value=LoggingMode.OFF,
            disabled=panel.get_value("is_running", False),
            key="logging_mode",
        )
        tdms_file_path = st.text_input(
            label="TDMS File Path",
            disabled=panel.get_value("is_running", False),
            value="data.tdms",
            key="tdms_file_path",
        )

with right_col:
    with st.container(border=True):
        st.title("Trigger Settings")
        id = stx.tab_bar(
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
        trigger_type = id
        panel.set_value("trigger_type", trigger_type)
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
            [
                "No Trigger",
                "Digital Start",
                "Digital Pause",
                "Digital Reference",
                "Analog Start",
                "Analog Pause",
                "Analog Reference",
            ]
        )
        with tab1:
            st.write(
                "To enable triggers, select a tab above, and configure the settings. \n Not all hardware supports all trigger types. Refer to your device documentation for more information."
            )
        with tab2:
            st.selectbox("Source->", " /Dev1/PFI0")
            enum_selectbox(
                panel,
                label="Edge",
                value=Edge.FALLING,
                disabled=panel.get_value("is_running", False),
                key="edge",
            )
        with tab3:
            st.write(
                "This trigger type is not supported in continuous sample timing. Refer to your device documentation for more information on which triggers are supported."
            )

            pause_when = PauseWhen[pause_when[0]]  # type: ignore
            panel.set_value("pause_when", pause_when)
        with tab4:
            st.write(
                "This trigger type is not supported in continuous sample timing. Refer to your device documentation for more information on which triggers are supported"
            )
        with tab5:
            st.selectbox("Source:", "APFI0")
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
                "Hysteriesis", disabled=panel.get_value("is_running", False)
            )
            panel.set_value("hysteriesis", hysteriesis)

        with tab6:
            st.write(
                "This trigger type is not supported in continuous sample timing. Refer to your device documentation for more information on which triggers are supported."
            )

       
        with tab7:
            st.write(
                "This trigger type is not supported in continuous sample timing. Refer to your device documentation for more information on which triggers are supported."
            )


with right_col:
    current_data = panel.get_value("current_data", [1.0])
    sample_rate = panel.get_value("sample_rate", 0.0)
with right_col:
    with st.container(border=True):
        graph = {
            "animation": False,
            "tooltip": {"trigger": "axis"},
            "legend": {"data": ["Current Data"]},
            "xAxis": {
                "type": "category",
                "data": [x / sample_rate for x in range(len(current_data))],
                "name": "Time",
                "nameLocation": "center",
                "nameGap": 40,
            },
            "yAxis": {
                "type": "value",
                "name": "Amps",
                "nameRotate": 90,
                "nameLocation": "center",
                "nameGap": 40,
            },
            "series": [
                {
                    "name": "voltage_amplitude",
                    "type": "line",
                    "data": current_data,
                    "emphasis": {"focus": "series"},
                    "smooth": True,
                    "seriesLayoutBy": "row",
                },
            ],
        }
        st_echarts(options=graph, height="400px", key="graph", width="100%")
