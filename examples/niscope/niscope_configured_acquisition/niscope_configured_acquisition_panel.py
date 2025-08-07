"""Streamlit dashboard for visualizing NI-SCOPE waveform data in real time."""

import extra_streamlit_components as stx  # type: ignore[import-untyped]
import niscope
import streamlit as st
from streamlit_echarts import st_echarts

import nipanel
from nipanel.controls import enum_selectbox

st.set_page_config(page_title="NI-SCOPE EX Configured Acquisition", page_icon="📈", layout="wide")
st.title("NI-SCOPE EX Configured Acquisition")
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
        if panel.get_value("is_running", False):
            st.button(r"⏹️ Stop", key="stop_button")
        elif not panel.get_value("is_running", False) and panel.get_value("scope_error", "") == "":
            run_button = st.button(r"▶️ Run", key="run_button")
        else:
            st.error(
                f"There was an error running the script. Fix the issue and re-run niscope_binary_acquisition.py \n\n {panel.get_value('scope_error', '')}"
            )

        st.text_input(
            label="Resource Name",
            value="Dev1",
            disabled=panel.get_value("is_running", False),
            key="resource_name",
        )
        st.number_input(
            "Channel",
            value=0,
            step=1,
            disabled=panel.get_value("is_running", False),
            key="channel_number",
        )
        st.number_input(
            "Timeout(s)",
            value=5.00,
            step=1.00,
            disabled=panel.get_value("is_running", False),
            key="timeout",
        )

        st.title("Vertical")
        st.number_input(
            "Vertical Range(V)",
            value=5.0,
            step=1.0,
            disabled=panel.get_value("is_running", False),
            key="vertical_range",
        )
        st.number_input(
            "Probe Attenuation",
            value=1.0,
            step=1.0,
            disabled=panel.get_value("is_running", False),
            key="probe_attenuation",
        )
        st.number_input(
            "Vertical Offset",
            value=0.0,
            step=1.0,
            disabled=panel.get_value("is_running", False),
            key="vertical_offset",
        )
        enum_selectbox(
            panel,
            label="Vertical Coupling",
            value=niscope.VerticalCoupling.DC,
            disabled=panel.get_value("is_running", False),
            key="vertical_coupling",
        )

        st.title("Channel")
        st.number_input(
            "Max. Input Frequency(Hz)",
            value=0.0,
            step=1.0,
            disabled=panel.get_value("is_running", False),
            key="max_input_frequency",
        )
        st.number_input(
            "Input Impedance",
            value=1.0e6,
            step=1000.0,
            disabled=panel.get_value("is_running", False),
            key="input_impedance",
        )

        st.title("Horizontal")
        st.radio(
            "Enforce Realtime",
            options=[True, False],
            disabled=panel.get_value("is_running", False),
            key="enforce_realtime",
        )

        sample_rate = st.number_input(
            "Min Sample Rate",
            value=10000000.0,
            step=1.0,
            disabled=panel.get_value("is_running", False),
            key="min_sample_rate",
        )
        st.number_input(
            "Actual Sample Rate",
            value=panel.get_value("actual_sample_rate", 1.0e7),
            step=1.0,
            disabled=True,
            key="actual_sample_rate",
        )
        record_length = st.number_input(
            "Min Record Length",
            value=1000,
            step=1,
            disabled=panel.get_value("is_running", False),
            key="min_record_length",
        )
        st.number_input(
            "Actual Record Length",
            value=panel.get_value("actual_record_length", 1000),
            step=1,
            disabled=True,
            key="actual_record_length",
        )


with right_col:
    with st.container(border=True):
        st.title("Waveform Graph")
        waveform_data = panel.get_value("waveform_data", [0])

        waveform_data = {
            "animation": False,
            "tooltip": {"trigger": "axis"},
            "legend": {"data": ["Amplitude (V)"]},
            "xAxis": {
                "type": "category",
                "data": [x / record_length for x in range(len(waveform_data))],  # change this
                "name": "Time (s)",
                "nameLocation": "center",
                "nameGap": 40,
            },
            "yAxis": {
                "type": "value",
                "name": "Amplitude(V)",
                "nameRotate": 90,
                "nameLocation": "center",
                "nameGap": 40,
            },
            "series": [
                {
                    "name": "niscope data",
                    "type": "line",
                    "data": waveform_data,
                    "emphasis": {"focus": "series"},
                    "smooth": True,
                    "seriesLayoutBy": "row",
                },
            ],
        }
        st_echarts(options=waveform_data, height="400px", width="75%", key="binary_graph")
        st.title("Trigger")
        trigger_type = stx.tab_bar(
            data=[
                stx.TabBarItemData(id=1, title="Immediate", description=""),
                stx.TabBarItemData(id=2, title="Edge", description=""),
                stx.TabBarItemData(id=3, title="Digital", description=""),
                stx.TabBarItemData(id=4, title="Window", description=""),
                stx.TabBarItemData(id=5, title="Hysteresis", description=""),
            ],
            default=1,
        )
        panel.set_value("trigger_type", trigger_type)

        if trigger_type == "1":
            with st.container(border=True):
                st.write(
                    "Note: When configured for Immediate reference trigger, this example does not configure any additional trigger settings - the acquisition is triggered as soon as possible after being initiated by driver software."
                )
        if trigger_type == "2":
            with st.container(border=True):
                st.number_input(
                    "Trigger Source",
                    value=0,
                    step=1,
                    disabled=panel.get_value("is_running", False),
                    key="edge_source",
                )
                st.number_input(
                    "Trigger Level",
                    value=0.0,
                    step=1.0,
                    disabled=panel.get_value("is_running", False),
                    key="edge_level",
                )
                enum_selectbox(
                    panel,
                    label="Trigger Slope",
                    value=niscope.TriggerSlope.POSITIVE,
                    disabled=panel.get_value("is_running", False),
                    key="edge_slope",
                )
                enum_selectbox(
                    panel,
                    label="Trigger Coupling",
                    value=niscope.TriggerCoupling.DC,
                    disabled=panel.get_value("is_running", False),
                    key="edge_coupling",
                )
        if trigger_type == "3":
            with st.container(border=True):
                st.text_input(
                    "Trigger Source",
                    value="PFI 1",
                    disabled=panel.get_value("is_running", False),
                    key="digital_source",
                )
                enum_selectbox(
                    panel,
                    label="Trigger Slope",
                    value=niscope.TriggerSlope.POSITIVE,
                    disabled=panel.get_value("is_running", False),
                    key="digital_slope",
                )
        if trigger_type == "4":
            with st.container(border=True):
                st.number_input(
                    "Trigger Source",
                    value=0,
                    step=1,
                    disabled=panel.get_value("is_running", False),
                    key="window_source",
                )
                enum_selectbox(
                    panel,
                    label="Window Mode",
                    value=niscope.TriggerWindowMode.ENTERING,
                    disabled=panel.get_value("is_running", False),
                    key="window_mode",
                )
                st.number_input(
                    "Window Low Level",
                    value=-0.1,
                    step=1.0,
                    disabled=panel.get_value("is_running", False),
                    key="window_low_level",
                )
                st.number_input(
                    "Window High Level",
                    value=0.1,
                    step=1.0,
                    disabled=panel.get_value("is_running", False),
                    key="window_high_level",
                )
                enum_selectbox(
                    panel,
                    label="Trigger Coupling",
                    value=niscope.TriggerCoupling.DC,
                    disabled=panel.get_value("is_running", False),
                    key="window_coupling",
                )

        if trigger_type == "5":
            with st.container(border=True):
                st.number_input(
                    "Trigger Source",
                    value=0,
                    step=1,
                    disabled=panel.get_value("is_running", False),
                    key="hysteresis_source",
                )
                st.number_input(
                    "Trigger Level",
                    value=0.0,
                    step=1.0,
                    disabled=panel.get_value("is_running", False),
                    key="hysteresis_trigger_level",
                )
                st.number_input(
                    "Hysteresis",
                    value=0.05,
                    step=1.0,
                    disabled=panel.get_value("is_running", False),
                    key="hysteresis",
                )
                enum_selectbox(
                    panel,
                    label="Trigger Slope",
                    value=niscope.TriggerSlope.POSITIVE,
                    disabled=panel.get_value("is_running", False),
                    key="hysteresis_slope",
                )
                enum_selectbox(
                    panel,
                    label="Trigger Coupling",
                    value=niscope.TriggerCoupling.DC,
                    disabled=panel.get_value("is_running", False),
                    key="hysteresis_coupling",
                )
        st.title("Common Trigger Settings")
        st.number_input(
            "Trigger Delay (s)",
            value=0.0,
            step=0.1,
            disabled=panel.get_value("is_running", False),
            key="trigger_delay",
        )
        st.number_input(
            "Ref Position",
            value=50.0,
            step=1.0,
            disabled=panel.get_value("is_running", False),
            key="ref_position",
        )
        if panel.get_value("auto_triggered", False):
            st.write("This acquisition is auto-triggered.")
        else:
            st.write("This acquisition is not auto-triggered.")
