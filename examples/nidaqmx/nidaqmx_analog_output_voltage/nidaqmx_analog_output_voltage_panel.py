"""Streamlit visualization script to display data acquired by nidaqmx_analog_output_voltage.py."""

from typing import cast

import extra_streamlit_components as stx  # type: ignore[import-untyped]
import hightime as ht
import streamlit as st
from nidaqmx.constants import Edge
from nitypes.waveform import AnalogWaveform
from streamlit_echarts import st_echarts

import nipanel
from nipanel.controls import enum_selectbox


def _click_start() -> None:
    panel.set_value("is_running", True)


def _click_stop() -> None:
    panel.set_value("is_running", False)


st.set_page_config(page_title="NI-DAQmx - Analog Output - Voltage", page_icon="📈", layout="wide")
panel = nipanel.get_streamlit_panel_accessor()

st.markdown(
    """
    <style>
     div.stNumberInput {
        max-width: 250px !important;
    }
    div.stTextInput {
        max-width: 250px !important;
    }
   
    div[data-baseweb="select"] {
        width: 250px !important; /* Adjust the width as needed */
    }
    </style>
    <style>
    iframe[title="streamlit_echarts.st_echarts"]{ height: 400px; width:100%;} 
   </style>
    """,
    unsafe_allow_html=True,
)

st.header("NI-DAQmx - Analog Output - Voltage")
if panel.get_value("is_running", False):
    st.button("⏹️ Stop", key="stop_button", on_click=_click_stop)
else:
    st.button("▶️ Run", key="run_button", on_click=_click_start)

left_col, right_col = st.columns(2)

with left_col:
    with st.container(border=True):
        st.header("Channel Settings")
        st.selectbox(
            options=panel.get_value("available_channel_names", [""]),
            index=0,
            label="Physical Channels",
            disabled=panel.get_value("is_running", False),
            key="physical_channel",
        )

        max_value_voltage = st.number_input(
            "Max Value",
            value=5.0,
            step=1.0,
            disabled=panel.get_value("is_running", False),
            key="max_value_voltage",
        )

        min_value_voltage = st.number_input(
            "Min Value",
            value=-5.0,
            step=1.0,
            disabled=panel.get_value("is_running", False),
            key="min_value_voltage",
        )
        st.header("Timing and Buffer Settings")

        source = st.selectbox(
            "Sample Clock Source",
            options=panel.get_value("available_trigger_sources", [""]),
            index=0,
            disabled=panel.get_value("is_running", False),
        )
        panel.set_value("source", source)
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
        st.header("Waveform Settings")
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
        wave_type = st.selectbox(
            label="Wave Type",
            options=["Sine Wave", "Triangle Wave", "Square Wave"],
            key="wave_type",
            disabled=panel.get_value("is_running", False),
        )
        panel.set_value("wave_type", wave_type)

with right_col:
    if panel.get_value("daq_error", "") != "":
        st.error(
            f"There was an error running the script. Fix the issue and click Run again. \n\n {panel.get_value('daq_error', '')}"
        )
    else:
        with st.container(border=True):
            st.header("Output")

            waveform = panel.get_value("waveform", AnalogWaveform())
            if waveform.sample_count == 0:
                time_labels = ["0.000"]
            else:
                timestamps = cast(
                    list[ht.datetime],
                    list(waveform.timing.get_timestamps(0, waveform.sample_count)),
                )
                time_labels = [f"{ts.second}.{ts.microsecond//1000:03d}" for ts in timestamps]

            graph = {
                "animation": False,
                "tooltip": {"trigger": "axis"},
                "legend": {"data": [waveform.units]},
                "xAxis": {
                    "type": "category",
                    "data": time_labels,
                    "name": "Time (s)",
                    "nameLocation": "center",
                    "nameGap": 40,
                },
                "yAxis": {
                    "type": "value",
                    "name": waveform.units,
                    "nameRotate": 90,
                    "nameLocation": "center",
                    "nameGap": 40,
                },
                "series": [
                    {
                        "name": waveform.units,
                        "type": "line",
                        "data": list(waveform.scaled_data),
                        "emphasis": {"focus": "series"},
                        "smooth": True,
                        "seriesLayoutBy": "row",
                    },
                ],
            }
            st_echarts(options=graph, height="400px", key="graph", width="100%")

    with st.container(border=True):
        st.header("Trigger Settings")
        trigger_type = stx.tab_bar(
            data=[
                stx.TabBarItemData(id=1, title="No Trigger", description=""),
                stx.TabBarItemData(id=2, title="Digital Start", description=""),
            ],
            default=1,
        )
        trigger_type = int(trigger_type)  # pyright: ignore[reportArgumentType]
        panel.set_value("trigger_type", trigger_type)

        if trigger_type == 1:
            with st.container(border=True):
                st.write(
                    "To enable triggers, select a tab above, and configure the settings. Not all hardware supports all trigger types. Refer to your device documentation for more information."
                )
        if trigger_type == 2:
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
