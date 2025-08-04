"""Streamlit visualization script to display data acquired by nidaqmx_analog_input_filtering.py."""

import streamlit as st
from streamlit_echarts import st_echarts

import nipanel

st.set_page_config(page_title="NiSCOPE Binary", page_icon="📈", layout="wide")
st.title("NiScope Binary Acquisition")
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
        elif not panel.get_value("is_running", False) and panel.get_value("daq_error", "") == "":
            run_button = st.button(r"▶️ Run", key="run_button")
        else:
            st.error(
                f"There was an error running the script. Fix the issue and re-run niscope_binary_acquisition.py \n\n {panel.get_value('daq_error', '')}"
            )

        st.text_input(
            label="Resource Name",
            value="Dev1",
            key="resource_name",
            disabled=panel.get_value("is_running", False),
        )
        st.number_input(
            "Channel",
            value=0,
            step=1,
            disabled=panel.get_value("is_running", False),
            key="channel",
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
            "Vertical Offset",
            value=0.0,
            step=1.0,
            disabled=panel.get_value("is_running", False),
            key="vertical_offset",
        )
        st.title("Horizontal")
        st.number_input(
            "Min Sample Rate",
            value=20000000.0,
            step=1.0,
            disabled=panel.get_value("is_running", False),
            key="min_sample_rate",
        )
        st.number_input(
            "Min Record Length",
            value=1000,
            step=1,
            disabled=panel.get_value("is_running", False),
            key="min_record_length",
        )
        data_size = st.selectbox(
            "Binary Data Size",
            options=[8, 16, 32],
            disabled=panel.get_value("is_running", False),
            key="data_size",
        )
        st.number_input(
            "Actual Binary Data Size",
            value=panel.get_value("actual_binary_data_size", 16),
            step=1,
            disabled=True,
            key="actual_binary_data_size",
        )
        st.title("Scaling Calculation")
        st.number_input(
            "Gain Factor",
            value=panel.get_value("gain_factor", 0.0000),
            step=0.0001,
            disabled=True,
            format="%.10f",
            key="gain_factor",
        )
        st.number_input(
            "Offset",
            value=panel.get_value("offset", 0.0000),
            step=0.0001,
            disabled=True,
            key="offset",
        )


with right_col:
    with st.container(border=True):
        st.title("Binary Waveform Graph")
        binary_data = panel.get_value("binary_data", [0])

        binary_graph = {
            "animation": False,
            "tooltip": {"trigger": "axis"},
            "legend": {"data": ["Amplitude (ADC Codes)"]},
            "xAxis": {
                "type": "category",
                "data": list(range(len(binary_data))),
                "name": "Samples",
                "nameLocation": "center",
                "nameGap": 40,
            },
            "yAxis": {
                "type": "value",
                "name": "Amplitude(ADC Codes)",
                "nameRotate": 90,
                "nameLocation": "center",
                "nameGap": 40,
            },
            "series": [
                {
                    "name": "niscope data",
                    "type": "line",
                    "data": binary_data,
                    "emphasis": {"focus": "series"},
                    "smooth": True,
                    "seriesLayoutBy": "row",
                },
            ],
        }
        st_echarts(options=binary_graph, height="400px", width="75%", key="binary_graph")
    with st.container(border=True):
        st.title("Scaled Voltage Graph")
        scaled_voltage_data = panel.get_value("scaled_voltage_data", [0])
        scaled_voltage_graph = {
            "animation": False,
            "tooltip": {"trigger": "axis"},
            "legend": {"data": ["Amplitude (V)"]},
            "xAxis": {
                "type": "category",
                "data": list(range(len(scaled_voltage_data))),
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
                    "data": scaled_voltage_data,
                    "emphasis": {"focus": "series"},
                    "smooth": True,
                    "seriesLayoutBy": "row",
                },
            ],
        }
        st_echarts(
            options=scaled_voltage_graph, height="400px", width="75%", key="scaled_voltage_graph"
        )
