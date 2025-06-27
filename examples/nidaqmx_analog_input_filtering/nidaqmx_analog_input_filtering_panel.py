"""Streamlit visualization script to display data acquired by nidaqmx_continuous_analog_input.py."""

import streamlit as st
from streamlit_echarts import st_echarts
from settings_enum import  DigitalEdge, PauseWhen, Slopes, AnalogPause
import time
import nipanel


st.set_page_config(page_title="Analog Input Filtering", page_icon="📈", layout="wide")
st.title("Analog Input - Filtering")

panel = nipanel.get_panel_accessor() 


tabs = st.tabs(["Voltage", "Current", "Strain Gage"])

st.markdown(
    """
    <style>
    div[data-baseweb="select"] {
        width: 190px !important; /* Adjust the width as needed */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

streamlit_style = """
    <style>
    iframe[title="streamlit_echarts.st_echarts"]{ height: 400px; width:75%;} 
   </style>
    """
st.markdown(streamlit_style, unsafe_allow_html=True) 


source = panel.get_value("source", [])
analog_source = panel.get_value("analog_source", [])

voltage_data = panel.get_value("voltage_data", [0.0])
current_data = panel.get_value("current_data", [0.0])
strain_data = panel.get_value("strain_data", [0.0])

sample_rate = panel.get_value("sample_rate", 0.0)

col_chart, settings = st.columns([1,1.5])  # Chart wider than buttons
with settings:
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["No Trigger","Digital Start","Digital Pause","Digital Reference","Analog Start","Analog Pause", "Analog Reference", "Time Start"])
    with tab1:
        st.write("To enable triggers, select a tab above, and configure the settings. \n Not all hardware supports all trigger types. Refer to your device documentation for more information.")
    with tab2:
        nipanel.enum_selectbox(
            
        )
        # st.selectbox("Source->", source)
        # edge_digital = st.selectbox(
        # "Edge",
        # options=[(e.name, e.value) for e in DigitalEdge],
        # format_func=lambda x: x[0],
        # index=0,
        # )
        # edge_digital = DigitalEdge[edge_digital[0]]
        # panel.set_value("edge_digital", edge_digital)

    with tab3:
        st.selectbox("Source-", source)
        pause_when = st.selectbox(
        "Pause When",
        options=[(e.name, e.value) for e in PauseWhen],
        format_func=lambda x: x[0],
        index=0,
        )
        pause_when = PauseWhen[pause_when[0]]
        panel.set_value("pause_when", pause_when)
    with tab4:
        st.write("This trigger type is not supported in continuous sample timing. Refer to your device documentation for more information on which triggers are supported")
    with tab5:
        st.selectbox("Source:", analog_source)
        slope = st.selectbox(
        "Slope",
        options=[(e.name, e.value) for e in Slopes],
        format_func=lambda x: x[0],
        index=0,
        )
        slope = Slopes[slope[0]]
        panel.set_value("slope", slope)

        level = st.number_input("Level")
        panel.set_value("level", level)
        hysteriesis = st.number_input("Hysteriesis")
        panel.set_value("hysteriesis", hysteriesis)

    with tab6:
        st.selectbox("source:", analog_source)
        analog_pause = st.selectbox(
        "analog_pause",
        options=[(e.name, e.value) for e in AnalogPause],
        format_func=lambda x: x[0],
        index=0,
        ) 
        analog_pause = AnalogPause[analog_pause[0]]
        panel.set_value("analog_pause", analog_pause)       
      
    with tab7:
        st.write("This trigger type is not supported in continuous sample timing. Refer to your device documentation for more information on which triggers are supported.")
    with tab8:
        if st.button("Select time Manually"):
            time = st.time_input("When?")
            st.write(time)
        st.write("If time is not manually set, task will begin after 10 seconds")


with tabs[0]:
    graph = {
    "animation": False,
    "tooltip": {"trigger": "axis"},
    "legend": {"data": ["Voltage (V)"]},
    "xAxis": {
        "type": "category",
        "data": [x / sample_rate for x in range(len(voltage_data))],
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
            "name": "voltage_amplitude",
            "type": "line",
            "data": voltage_data,
            "emphasis": {"focus": "series"},
            "smooth": True,
            "seriesLayoutBy": "row",
        },
    ],
}
    st_echarts(options=graph, height="400px", key="graph", width="50%")
with tabs[1]:
    graph_2= {
    "animation": False,
    "tooltip": {"trigger": "axis"},
    "legend": {"data": ["Voltage (V)"]},
    "xAxis": {
        "type": "category",
        "data": [x / sample_rate for x in range(len(current_data))],
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
            "name": "voltage_amplitude",
            "type": "line",
            "data": current_data,
            "emphasis": {"focus": "series"},
            "smooth": True,
            "seriesLayoutBy": "row",
        },
    ],
}
    st_echarts(options=graph, height="400px", key="graph_2", width="50%")

with tabs[2]:
    graph_3 = {
    "animation": False,
    "tooltip": {"trigger": "axis"},
    "legend": {"data": ["Voltage (V)"]},
    "xAxis": {
        "type": "category",
        "data": [x / sample_rate for x in range(len(strain_data))],
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
            "name": "voltage_amplitude",
            "type": "line",
            "data": strain_data,
            "emphasis": {"focus": "series"},
            "smooth": True,
            "seriesLayoutBy": "row",
        },
    ],
}
    st_echarts(options=graph_3, height="400px", key="graph_3", width="50%")

  


