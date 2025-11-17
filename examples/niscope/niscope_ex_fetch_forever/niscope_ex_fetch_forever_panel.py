"""Streamlit dashboard for visualizing NI-SCOPE waveform data in real time."""

import streamlit as st
from streamlit_echarts import st_echarts

import nipanel

st.set_page_config(page_title="NI-SCOPE Example", page_icon="📈", layout="wide")
st.title("NIScope EX Fetch Forever")

panel = nipanel.get_streamlit_panel_accessor()

waveform = panel.get_value("Waveform", [0])

graph = {
    "animation": False,
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
st_echarts(options=graph, height="400px", width="75%", key="graph")
