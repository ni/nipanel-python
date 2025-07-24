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
from streamlit_echarts import st_echarts

import nipanel
from nipanel.controls import enum_selectbox

st.set_page_config(page_title="Analog Input Filtering", page_icon="📈", layout="wide")
st.title("Analog Input - Filtering")
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
        if panel.get_value("daq_error", "") == "":
            pass
        else:
            st.error(panel.get_value("daq_error", ""))

        st.title("Channel Settings")
        physical_channel = st.selectbox(
            options=panel.get_value("available_channel_names", ["Mod2/ai0"]),
            index=0,
            label="Physical Channels",
            disabled=panel.get_value("is_running", False),
        )
        panel.set_value("physical_channel", physical_channel)
        enum_selectbox(
            panel,
            label="Terminal Configuration",
            value=TerminalConfiguration.DEFAULT,
            disabled=panel.get_value("is_running", False),
            key="terminal_configuration",
        )

        st.title("Timing Settings")

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
            value=100,
            min_value=1,
            step=1,
            disabled=panel.get_value("is_running", False),
            key="total_samples",
        )
        st.number_input(
            "Actual Sample Rate",
            value=panel.get_value("sample_rate", 1000.0),
            key="actual_sample_rate",
            step=1.0,
            disabled=True,
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

        filter = st.selectbox(
            "Filter",
            options=["No Filtering", "Filter"],
            disabled=panel.get_value("is_running", False),
        )
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
        st.selectbox(
            "Actual Filter Frequency",
            options=[panel.get_value("actual_filter_freq", 0.0)],
            disabled=True,
        )
        st.selectbox(
            "Actual Filter Order",
            options=[panel.get_value("actual_filter_order", 0)],
            disabled=True,
        )

with right_col:
    st.title("Task Types")
    chan_type = stx.tab_bar(
        data=[
            stx.TabBarItemData(id=1, title="Voltage", description=""),
            stx.TabBarItemData(id=2, title="Current", description=""),
            stx.TabBarItemData(id=3, title="Strain Gage", description=""),
        ],
        default=1,
    )

    panel.set_value("chan_type", chan_type)

    if chan_type == "1":
        with st.container(border=True):
            st.title("Voltage Data")
            channel_left, channel_right = st.columns(2)
            with channel_left:
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

    if chan_type == "2":
        with st.container(border=True):
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
                    max_value_current = st.number_input(
                        "Max Value",
                        value=0.01,
                        step=1.0,
                        key="max_value_current",
                        disabled=panel.get_value("is_running", False),
                    )
                    shunt_resistor_value = st.number_input(
                        "Shunt Resistor Value",
                        value=249.0,
                        step=1.0,
                        disabled=panel.get_value("is_running", False),
                    )
    if chan_type == "3":
        with st.container(border=True):
            st.title("Strain Gage Data")
            channel_left, channel_right = st.columns(2)
            with channel_left:
                min_value_strain = st.number_input(
                    "Min Value",
                    value=-0.01,
                    step=0.01,
                    key="min_value_strain",
                )
                max_value_strain = st.number_input(
                    "Max Value",
                    value=0.01,
                    step=0.01,
                    max_value=2.0,
                    key="max_value_strain",
                )
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
                        key="gage_factor",
                    )
                    nominal_gage = st.number_input(
                        "nominal gage resistance",
                        value=350.0,
                        step=1.0,
                        disabled=panel.get_value("is_running", False),
                        key="gage_resistance",
                    )
                    poisson_ratio = st.number_input(
                        "poisson ratio",
                        value=0.3,
                        step=1.0,
                        disabled=panel.get_value("is_running", False),
                        key="poisson_ratio",
                    )
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
                        key="wire_resistance",
                    )
                    initial_voltage = st.number_input(
                        "initial bridge voltage",
                        value=0.0,
                        step=1.0,
                        disabled=panel.get_value("is_running", False),
                        key="initial_voltage",
                    )

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
                "Source->", options=panel.get_value("available_trigger_sources", [""])
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
            analog_source = st.text_input("Source:", "APFI0", key="analog_source")
            enum_selectbox(
                panel,
                label="Slope",
                value=Slope.FALLING,
                disabled=panel.get_value("is_running", False),
                key="slope",
            )

            level = st.number_input("Level", key="level")
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
        acquired_data = panel.get_value("acquired_data", [0.0])
        sample_rate = panel.get_value("sample_rate", 100.0)
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
