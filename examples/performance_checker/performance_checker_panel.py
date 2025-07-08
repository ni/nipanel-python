"""A Streamlit visualization panel for the performance_checker.py example script."""

import statistics
import time
from typing import Any, Tuple

import streamlit as st
from streamlit_echarts import st_echarts

import nipanel


def profile_get_value(
    panel: "nipanel.StreamlitPanelValueAccessor", value_id: str, default_value: Any = None
) -> Tuple[Any, float]:
    """Measure the time it takes to get a value from the panel.

    Args:
        panel: The panel accessor object
        value_id: The ID of the value to get
        default_value: Default value if the value is not found

    Returns:
        A tuple of (value, time_ms) where time_ms is the time in milliseconds
    """
    start_time = time.time()
    value = panel.get_value(value_id, default_value)
    end_time = time.time()
    time_ms = (end_time - start_time) * 1000
    return value, time_ms


st.set_page_config(page_title="Performance Checker Example", page_icon="📈", layout="wide")
st.title("Performance Checker Example")

# Initialize refresh history list if it doesn't exist
if "refresh_history" not in st.session_state:
    st.session_state.refresh_history = []  # List of tuples (timestamp, refresh_time_ms)

# Store current timestamp and calculate time since last refresh
current_time = time.time()
if "last_refresh_time" not in st.session_state:
    st.session_state.last_refresh_time = current_time
    time_since_last_refresh = 0.0
else:
    time_since_last_refresh = (current_time - st.session_state.last_refresh_time) * 1000
    st.session_state.last_refresh_time = current_time

    # Store refresh times with timestamps, keeping only the last 1 second of data
    st.session_state.refresh_history.append((current_time, time_since_last_refresh))

    # Remove entries older than 1 second
    cutoff_time = current_time - 1.0  # 1 second ago
    st.session_state.refresh_history = [
        item for item in st.session_state.refresh_history if item[0] >= cutoff_time
    ]

# Extract just the refresh times for calculations
if st.session_state.refresh_history:
    refresh_history = [item[1] for item in st.session_state.refresh_history]
else:
    refresh_history = []

# Calculate statistics for refresh
min_refresh_time = min(refresh_history) if refresh_history else 0
max_refresh_time = max(refresh_history) if refresh_history else 0
avg_refresh_time = statistics.mean(refresh_history) if refresh_history else 0

panel = nipanel.get_panel_accessor()

# Measure time to get each value
time_points, time_points_ms = profile_get_value(panel, "time_points", [0.0])
sine_values, sine_values_ms = profile_get_value(panel, "sine_values", [0.0])
amplitude, amplitude_ms = profile_get_value(panel, "amplitude", 1.0)
frequency, frequency_ms = profile_get_value(panel, "frequency", 1.0)
unset_value, unset_value_ms = profile_get_value(panel, "unset_value", "default")

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

# Create columns for metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Amplitude", f"{amplitude:.2f}")
    st.metric("Frequency", f"{frequency:.2f} Hz")
with col2:
    st.metric("Refresh Time", f"{time_since_last_refresh:.1f} ms")
    st.metric("Min Refresh Time", f"{min_refresh_time:.1f} ms")
    st.metric("Max Refresh Time", f"{max_refresh_time:.1f} ms")
    st.metric("Avg Refresh Time", f"{avg_refresh_time:.1f} ms")
    st.metric("FPS", f"{len(refresh_history)}")

with col3:
    st.metric("get time_points", f"{time_points_ms:.1f} ms")
    st.metric("get sine_values", f"{sine_values_ms:.1f} ms")
    st.metric("get amplitude", f"{amplitude_ms:.1f} ms")
    st.metric("get frequency", f"{frequency_ms:.1f} ms")
    st.metric("get unset_value", f"{unset_value_ms:.1f} ms")
