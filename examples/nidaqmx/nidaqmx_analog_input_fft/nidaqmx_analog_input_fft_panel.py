"""Streamlit visualization script to display data acquired by nidaqmx_continuous_analog_input.py."""

from typing import cast

import hightime as ht
import streamlit as st
from nidaqmx.constants import (
    TerminalConfiguration,
)
from nitypes.waveform import AnalogWaveform
from streamlit_echarts import st_echarts

import nipanel
from nipanel.controls import enum_selectbox

st.set_page_config(
    page_title="NI-DAQmx - Analog Input - Voltage with FFT", page_icon="📈", layout="wide"
)

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


def _click_start() -> None:
    panel.set_value("is_running", True)


def _click_stop() -> None:
    panel.set_value("is_running", False)


panel = nipanel.get_streamlit_panel_accessor()

st.header("NI-DAQmx - Analog Input - Voltage with FFT")
if panel.get_value("is_running", False):
    st.button(r"⏹️ Stop", key="stop_button", on_click=_click_stop)
else:
    st.button(r"▶️ Run", key="run_button", on_click=_click_start)

sample_rate = panel.get_value("sample_rate", 0.0)

# Create two-column layout for the entire interface
left_column, right_column = st.columns([1, 1])

# Left column - Channel tabs and Timing Settings
with left_column:
    # Channel Settings tabs
    with st.container(border=True):
        st.header("Channel Settings")
        voltage_tab = st.tabs(["Voltage"])[0]

        voltage_tab.header("Voltage")
        with voltage_tab:
            channel_left_column, channel_right_column = st.columns(2)
            with channel_left_column:
                st.selectbox(
                    options=panel.get_value("available_voltage_channels", [""]),
                    index=0,
                    label="Voltage Channel",
                    disabled=panel.get_value("is_running", False),
                    key="voltage_channel",
                )
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
                "Samples to Read",
                value=1000,
                step=100,
                min_value=10,
                disabled=panel.get_value("is_running", False),
                key="samples_per_channel",
            )
            st.text_input(
                label="Actual Sample Rate",
                value=str(sample_rate) if sample_rate else "",
                disabled=True,
            )

# Right column - Graph
with right_column:
    if panel.get_value("daq_error", "") != "":
        st.error(
            f"There was an error running the script. Fix the issue and click Run again. \n\n {panel.get_value('daq_error', '')}"
        )
    else:
        with st.container(border=True):
            # Voltage Data Graph section
            st.header("Acquired Data")

            voltage_waveform = panel.get_value("voltage_waveform", AnalogWaveform())
            if voltage_waveform.sample_count == 0:
                time_labels = ["00:00:00.000"]
            else:
                timestamps = cast(
                    list[ht.datetime],
                    list(voltage_waveform.timing.get_timestamps(0, voltage_waveform.sample_count)),
                )
                time_labels = [
                    f"{ts.hour:02d}:{ts.minute:02d}:{ts.second:02d}.{ts.microsecond//1000:03d}"
                    for ts in timestamps
                ]

            voltage_graph = {
                "animation": False,
                "tooltip": {"trigger": "axis"},
                "legend": {"data": [voltage_waveform.units]},
                "xAxis": {
                    "type": "category",
                    "data": time_labels,
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
                        "name": voltage_waveform.units,
                        "type": "line",
                        "data": list(voltage_waveform.scaled_data),
                        "emphasis": {"focus": "series"},
                        "smooth": True,
                        "seriesLayoutBy": "row",
                    },
                ],
            }
            st_echarts(options=voltage_graph, height="300px", key="voltage_graph")

            frequencies = panel.get_value("fft_freqs", [0.0])
            magnitudes = panel.get_value("fft_mags", [0.0])
            fft_data = [{"value": [x, y]} for x, y in zip(frequencies, magnitudes)]

            fft_graph = {
                "animation": False,
                "tooltip": {"trigger": "axis"},
                "legend": {"data": ["Magnitude"]},
                "xAxis": {
                    "type": "value",
                    "name": "Frequency",
                    "nameLocation": "center",
                    "nameGap": 40,
                },
                "yAxis": {
                    "type": "value",
                    "name": "Magnitude",
                    "nameRotate": 90,
                    "nameLocation": "center",
                    "nameGap": 40,
                },
                "series": [
                    {
                        "name": "Magnitude",
                        "type": "line",
                        "data": fft_data,
                        "emphasis": {"focus": "series"},
                        "smooth": True,
                        "seriesLayoutBy": "row",
                    },
                ],
            }
            st_echarts(options=fft_graph, height="300px", key="fft_graph")
