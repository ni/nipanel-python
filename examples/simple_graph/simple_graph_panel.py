"""A Streamlit visualization panel for the simple_graph.py example script."""

import streamlit as st
from streamlit_echarts import st_echarts  

import nipanel


panel = nipanel.get_panel_accessor()

st.set_page_config(page_title="Simple Graph Example", page_icon="📈", layout="wide")
st.title("Simple Graph Example")

time_points = panel.get_value("time_points", [0.0])
sine_values = panel.get_value("sine_values", [0.0])
amplitude = panel.get_value("amplitude", 1.0)
frequency = panel.get_value("frequency", 1.0)

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Amplitude", f"{amplitude:.2f}")
with col2:
    st.metric("Frequency", f"{frequency:.2f} Hz")
with col3:
    st.metric("Min Value", f"{min(sine_values):.3f}")
with col4:
    st.metric("Max Value", f"{max(sine_values):.3f}")
with col5:
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
st_echarts(options=options, height="400px")
