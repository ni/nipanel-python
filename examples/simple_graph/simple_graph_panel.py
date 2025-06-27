"""A Streamlit visualization panel for the simple_graph.py example script."""

import streamlit as st
from amplitude_enum import AmplitudeEnum
from streamlit_echarts import st_echarts

import nipanel

st.set_page_config(page_title="Simple Graph Example", page_icon="📈", layout="wide")
st.title("Simple Graph Example")
col1, col2, col3, col4, col5, col6 = st.columns(6)
panel = nipanel.get_panel_accessor()

with col1:
    amplitude_tuple = st.selectbox(
        "Amplitude",
        options=[(e.name, e.value) for e in AmplitudeEnum],
        format_func=lambda x: x[0],
        index=0,
    )
    amplitude_enum = AmplitudeEnum[amplitude_tuple[0]]
    panel.set_value("amplitude_enum", amplitude_enum)
with col2:
    base_frequency = st.number_input("Base Frequency", value=1.0, step=0.1)
    panel.set_value("base_frequency", base_frequency)
with col3:
    frequency = panel.get_value("frequency", 0.0)
    st.metric("Frequency", f"{frequency:.2f} Hz")

time_points = panel.get_value("time_points", [0.0])
sine_values = panel.get_value("sine_values", [0.0])
with col4:
    st.metric("Min Value", f"{min(sine_values):.3f}")

with col5:
    st.metric("Max Value", f"{max(sine_values):.3f}")
with col6:
    st.metric("Data Points", len(sine_values))
# Prepare data for echarts
data = [{"value": [x, y]} for x, y in zip(time_points, sine_values)]

# Configure the chart options
options = {
    "animation": False,  # Disable animation for smoother updates
    "title": {"text": "Sine Wave"},
    "tooltip": {"trigger": "axis"},
    "xAxis": {"type": "value", "name": "Time (s)", "nameLocation": "middle", "nameGap": 30},
    "yAxis": {
        "type": "value",
        "name": "Amplitude",
        "nameLocation": "middle",
        "nameGap": 30,
    },
    "series": [
        {
            "data": data,
            "type": "line",
            "showSymbol": True,
            "smooth": True,
            "lineStyle": {"width": 2, "color": "#1f77b4"},
            "areaStyle": {"color": "#1f77b4", "opacity": 0.3},
            "name": "Sine Wave",
        }
    ],
}

# Display the chart
st_echarts(options=options, height="400px", key="graph")
