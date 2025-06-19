"""Streamlit application script for displaying values using nipanel package."""
import nipanel
import streamlit as st
import streamlit.components.v1 as components
from streamlit_echarts import st_echarts

panel = nipanel.StreamlitPanelValueAccessor(panel_id="nidaqmx_continuous_analog_input_panel")

add_refresh_component = components.declare_component(
            "panelRefreshComponent",
            url=f"http://localhost:42001/panels/refresh/{panel.panel_id}",)
add_refresh_component()


st.title("Analog Input - Voltage and Thermocouple in a Single Task")
voltage_tab, thermocouple_tab = st.tabs(["Voltage", "Thermocouple"])

st.markdown(
    """
    <style>
    div[data-baseweb="select"] {
        width: 190px !important; /* Adjust the width as needed */
    }
    </style>
    """,
    unsafe_allow_html=True
)


list_of_therm_amp = panel.get_value("amplitude")
list_of_voltage_amp = panel.get_value("Volts")

if "therm_history" not in st.session_state:
    st.session_state.therm_history = []
if "volts_history" not in st.session_state:
    st.session_state.volts_history = []

for therm_amp in list_of_therm_amp:
    st.session_state.therm_history.append(therm_amp)
for voltage_amp in list_of_voltage_amp:
    st.session_state.volts_history.append(voltage_amp)

therm_amp_graph = {
    "tooltip": {"trigger": "axis"},
    "legend": {"data": ["thermocouple_amplitude"]},
    "xAxis": {
        "type": "category",
        "data":list(range(len(st.session_state.therm_history))),
        "name": "Time"
    },
    "yAxis": {
        "type": "value",
        "name": "Thermocouple Amplitude"
    },
    "series": [
        {
            "name": "thermocouple_amplitude",
            "type": "line",
            "data": st.session_state.therm_history,
            "color": "red"
        },
     
        
    ],
}
st_echarts(options=therm_amp_graph, height="400px")

voltage_amp_graph = {
    "tooltip": {"trigger": "axis"},
    "legend": {"data": ["voltage_amplitude"]},
    "xAxis": {
        "type": "category",
        "data": list(range(len(st.session_state.volts_history))),
        "name": "Time"
    },
    "yAxis": {
        "type": "value",
        "name": "Voltage Amplitude"
    },
    "series": [
        {
            "name": "voltage_amplitude",
            "type": "line",
            "data": st.session_state.volts_history,
        },
        
    ],
}
st_echarts(options=voltage_amp_graph, height="400px")

st.header("Voltage & Thermocouple")
voltage_therm_graph = {
    "tooltip": {"trigger": "axis"},
    "legend": {"data": ["voltage_amplitude", "thermocouple_amplitude"]},
    "xAxis": {
        "type": "category",
        "data": list(range(len(st.session_state.volts_history))),
        "name": "Time"
    },
    "yAxis": {
        "type": "value",
        "name": "Voltage and Thermocouple Amplitude"
    },
    "series": [
        {
            "name": "voltage_amplitude",
            "type": "line",
            "data": st.session_state.volts_history,
            "emphasis": {"focus":"series"},
            "smooth": True,
            "seriesLayoutBy": "row",
        },
        {
            "name": "thermocouple_amplitude",
            "type": "line",
            "data": st.session_state.therm_history,
            "color": "red",
            "emphasis": {"focus":"series"},
            "smooth": True,
            "seriesLayoutBy": "row",
        },
    ],
}
st_echarts(options=voltage_therm_graph, height="400px")

with voltage_tab:
    left_volt_tab, center_volt_tab, right_volt_tab = st.columns(3)
    with left_volt_tab:
        st.selectbox(options=["Mod1/ai2"], label="Physical Channels", disabled=True)
        st.selectbox(options=["Off"], label="Logging Modes", disabled=False)
    with center_volt_tab:
        st.selectbox(options=["-5"],label="Min Value")
        st.selectbox(options=["5"],label="Max Value")
        st.selectbox(options=["1000"], label="Samples per Loops", disabled=False)
    with right_volt_tab:
        st.selectbox(options=["default"], label="Terminal Configurations")
        st.selectbox(options=["OnboardClock"], label="Sample Clock Sources", disabled=False)

        
thermocouple_tab.header("Thermocouple")
with thermocouple_tab:
    left, middle, right = st.columns(3)
    with left:
        st.selectbox(options=["Mod1/ai3"], label="Physical Channel", disabled=True)
        st.selectbox(options=["0"], label="Min", disabled=False)
        st.selectbox(options=["100"], label="Max", disabled=False)
        st.selectbox(options=["Off"], label="Logging Mode", disabled=False)
        
    with middle:
        st.selectbox(options=["Deg C"], label = "Units", disabled=False)
        st.selectbox(options=["J"], label="Thermocouple Type", disabled=False)
        st.selectbox(options=["Constant Value"], label="CJC Source", disabled=False)
        st.selectbox(options=["1000"], label="Samples per Loop", disabled=False)
    with right:
        st.selectbox(options=["25"],label="CJC Value", disabled=False)
        st.selectbox(options=["OnboardClock"], label="Sample Clock Source", disabled=False)
        st.selectbox(options=[" "], label="Actual Sample Rate", disabled=True)
    


 




    
  

