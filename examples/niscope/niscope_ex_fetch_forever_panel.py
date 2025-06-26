"""Streamlit dashboard for visualizing NI-SCOPE waveform data in real time."""

import streamlit as st
from streamlit_echarts import st_echarts

import nipanel

panel = nipanel.get_panel_accessor()

st.title("NIScope EX Fetch Forever")

waveform = panel.get_value("Waveform", [0])

graph = {
    "tooltip": {"trigger": "axis"},
    "legend": {"data": ["Amplitude (V)"]},
    "xAxis": {
        "type": "category",
        "data": list(range(len(waveform))),
        "name": "Samples",
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
            "data": waveform,
            "emphasis": {"focus": "series"},
            "smooth": True,
            "seriesLayoutBy": "row",
        },
    ],
}
st_echarts(options=graph, height="400px", width="75%")
