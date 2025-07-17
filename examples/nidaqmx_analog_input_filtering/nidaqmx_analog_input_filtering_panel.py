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
from settings_enum import AnalogPause, PauseWhen
from streamlit_echarts import st_echarts

import nipanel
from nipanel.controls import enum_selectbox

st.set_page_config(page_title="Analog Input Filtering", page_icon="📈", layout="wide")
st.title("Analog Input - Filtering")
panel = nipanel.get_panel_accessor()

left_col, right_col = st.columns(2)

with right_col:
    with st.container(border=True):
        st.title("Task Types")
        chosen_id = stx.tab_bar(
            data=[
                stx.TabBarItemData(id=1, title="Voltage", description=""),
                stx.TabBarItemData(id=2, title="Current", description=""),
                stx.TabBarItemData(id=3, title="Strain Gage", description=""),
            ],
            default=1,
        )
        tabs = st.tabs(["Voltage", "Current", "Strain Gage"])
        with st.container(border=True):
            with tabs[0]:
                st.title("Voltage Data")
                channel_left, channel_right = st.columns(2)
                with channel_left:
                    max_value_voltage = st.number_input(
                        "Max Value", value=5.0, step=0.1, disabled=panel.get_value("is_running", False)
                    )
                    panel.set_value("max_value_voltage", max_value_voltage)

                    min_value_voltage = st.number_input(
                        "Min Value", value=-5.0, step=0.1, disabled=panel.get_value("is_running", False)
                    )
                    panel.set_value("min_value_voltage", min_value_voltage)

            with tabs[1]:
                st.title("Current Data")
                channel_left, channel_right = st.columns(2)
                with channel_left:
                    enum_selectbox(
                        panel,
                        label="Shunt Resistor Location",
                        value=CurrentShuntResistorLocation.EXTERNAL,
                        disabled=panel.get_value("is_running", False),
                        key="shunt_location",
                    )
                    enum_selectbox(
                        panel,
                        label="Units",
                        value=CurrentUnits.AMPS,
                        disabled=panel.get_value("is_running", False),
                        key="units",
                    )
                    with st.expander("More current info", expanded=False):
                        min_value_current = st.number_input(
                            "Min Value",
                            value=-0.01,
                            step=0.001,
                            disabled=panel.get_value("is_running", False),
                        )
                        panel.set_value("min_value_current", min_value_current)
                        max_value_current = st.number_input(
                            "Max Value",
                            value=0.01,
                            step=1.0,
                            key="max_value_current",
                            disabled=panel.get_value("is_running", False),
                        )
                        current = panel.set_value("max_value_current", max_value_current)  # type:ignore
                        shunt_resistor_value = st.number_input(
                            "Shunt Resistor Value",
                            value=249.0,
                            step=1.0,
                            disabled=panel.get_value("is_running", False),
                        )
                        panel.set_value("shunt_resistor_value", shunt_resistor_value)
            with tabs[2]:
                st.title("Strain Gage Data")
                channel_left, channel_right = st.columns(2)
                with channel_left:
                    min_value_strain = st.number_input(
                        "Min Value",
                        value=-0.01,
                        step=0.01,
                    )
                    panel.set_value("min_value_strain", min_value_strain)
                    max_value_strain = st.number_input(
                        "Max Value", value=0.01, step=0.01, max_value=2.0
                    )
                    panel.set_value("max_value_strain", max_value_strain)
                    enum_selectbox(
                        panel,
                        label="Strain Units",
                        value=CurrentUnits.AMPS,
                        disabled=panel.get_value("is_running", False),
                        key="strain_units",
                    )
                    with st.expander("Strain Gage Information", expanded=False):
                        st.title("Strain Gage Information")
                        gage_factor = st.number_input(
                            "Gage Factor",
                            value=2.0,
                            step=1.0,
                            disabled=panel.get_value("is_running", False),
                        )
                        panel.set_value("gage_factor", gage_factor)
                        nominal_gage = st.number_input(
                            "nominal gage resistance",
                            value=350.0,
                            step=1.0,
                            disabled=panel.get_value("is_running", False),
                        )
                        panel.set_value("gage_resistance", nominal_gage)
                        poisson_ratio = st.number_input(
                            "poisson ratio",
                            value=0.3,
                            step=1.0,
                            disabled=panel.get_value("is_running", False),
                        )
                        panel.set_value("poisson_ratio", poisson_ratio)
                    with st.expander("Bridge Information", expanded=False):
                        st.title("Bridge Information")
                        enum_selectbox(
                            panel,
                            label="Strain Configuration",
                            value=StrainGageBridgeType.FULL_BRIDGE_I,
                            disabled=panel.get_value("is_running", False),
                            key="strain_configuration",
                        )
                        wire_resistance = st.number_input(
                            "lead wire resistance",
                            value=0.0,
                            step=1.0,
                        )
                        panel.set_value("wire_resistance", wire_resistance)
                        initial_voltage = st.number_input(
                            "initial bridge voltage",
                            value=0.0,
                            step=1.0,
                            disabled=panel.get_value("is_running", False),
                        )
                        panel.set_value("initial_voltage", initial_voltage)

                        st.selectbox(
                            label="voltage excitation source",
                            key="voltage_excit",
                            options=["External"],
                            disabled=True,
                        )
                        panel.set_value("voltage_excitation_source", "voltage_excit")
                        voltage_excit = st.number_input(
                            "voltage excitation value",
                            value=2.5,
                            step=1.0,
                            key="voltage_excitation_value",
                            disabled=panel.get_value("is_running", False),
                        )
                        panel.set_value("voltage_excitation_value", voltage_excit)

panel.set_value("chan_type", "1")

pages = st.container()
chan_type = chosen_id
panel.set_value("chan_type", chan_type)

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
            label="Terminal Configuration",
            value=TerminalConfiguration.DEFAULT,
            disabled=panel.get_value("is_running", False),
            key="terminal_configuration",
        )

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
            value=100,
            min_value=1,
            step=1,
            disabled=panel.get_value("is_running", False),
            key="total_samples",
        )
        st.number_input(
            "Actual Sample Rate",
            value= panel.get_value("actual_sample_rate", 1000.0),
            key = "actual_sample_rate",
            step = 1.0,
            disabled= True
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
        st.title("Filtering Settings")

        filter = st.selectbox("Filter", options=["No Filtering", "Filter"])
        panel.set_value("filter", filter)
        enum_selectbox(
            panel,
            label="Filter Response",
            value=FilterResponse.COMB,
            disabled=panel.get_value("is_running", False),
            key="filter_response",
        )

        filter_freq = st.number_input(
            "Filtering Frequency",
            value=1000.0,
            step=1.0,
            disabled=panel.get_value("is_running", False),
        )
        filter_order = st.number_input(
            "Filter Order",
            min_value=0,
            max_value=1,
            value=1,
            disabled=panel.get_value("is_running", False),
        )
        st.selectbox("Actual Filter Frequency", options=[panel.get_value("actual_filter_freq")], disabled=True)
        st.selectbox("Actual Filter Order", options=[panel.get_value("actual_filter_order")], disabled=True)



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
            st.selectbox("Source-", "/Dev1/PFI0")
            pause_when = st.selectbox(
                "Pause When",
                options=[(e.name, e.value) for e in PauseWhen],
                format_func=lambda x: x[0],
                index=0,
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
            st.selectbox("source:", "APFI0")
            analog_pause = st.selectbox(
                "analog_pause",
                options=[(e.name, e.value) for e in AnalogPause],
                format_func=lambda x: x[0],
                index=0,
            )
            analog_pause = AnalogPause[analog_pause[0]]  # type: ignore
            panel.set_value("analog_pause", analog_pause)

        with tab7:
            st.write(
                "This trigger type is not supported in continuous sample timing. Refer to your device documentation for more information on which triggers are supported."
            )

    
with right_col:
    with st.container(border=True):
        acquired_data = panel.get_value("acquired_data", [0.0])
        sample_rate = panel.get_value("sample_rate", 0.0)
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
