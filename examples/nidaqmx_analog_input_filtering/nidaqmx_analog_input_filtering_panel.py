"""Streamlit visualization script to display data acquired by nidaqmx_continuous_analog_input.py."""

import streamlit as st
from streamlit_echarts import st_echarts
import extra_streamlit_components as stx
from settings_enum import  DigitalEdge, PauseWhen, Slopes, AnalogPause, TerminalConfig, ShuntLocation

import time
import nipanel


st.set_page_config(page_title="Analog Input Filtering", page_icon="📈", layout="wide")
st.title("Analog Input - Filtering")
# placeholder = 1
panel = nipanel.get_panel_accessor() 

panel.set_value("placeholder", "1")

chosen_id = stx.tab_bar(data=[
    stx.TabBarItemData(id=1, title="Voltage", description=""),
    stx.TabBarItemData(id=2, title="Current", description=""),
    stx.TabBarItemData(id=3, title="Strain Gage", description=""),
], default=1)



pages = st.container()
placeholder = chosen_id
panel.set_value("placeholder", placeholder)


def stop_run():
    panel.set_value("is_running", False)
def run_update():
    panel.set_value("is_running", True)
is_running = panel.get_value("is_running", True)

if is_running:
    st.button("Stop", key="stop_button",on_click=stop_run)
else:
    st.button("Run", key="run_button", on_click=run_update)


left_col, right_col = st.columns(2)




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
    iframe[title="streamlit_echarts.st_echarts"]{ height: 400px; width:100%;} 
   </style>
    """
st.markdown(streamlit_style, unsafe_allow_html=True) 

source = panel.get_value("source", [])
analog_source = panel.get_value("analog_source", [])

voltage_data = panel.get_value("voltage_data", [1.0])
current_data = panel.get_value("current_data", [1.0])
strain_data = panel.get_value("strain_data", [1.0])

sample_rate = panel.get_value("sample_rate", 0.0)
data_type = ""
with right_col:
    with st.container(border=True):

        st.title("Channel Settings")
        st.selectbox(options=["Mod3/ai10"], index=0, label="Physical Channels", disabled=True)

        terminal_config = st.selectbox(
        "terminal_config",
        options=[(e.name, e.value) for e in TerminalConfig],
        format_func=lambda x: x[0],
        index=0,
        ) 
        terminal_config = TerminalConfig[terminal_config[0]]
        
        panel.set_value("terminal_config", terminal_config)

        st.title("Timing Settings")
        st.selectbox("Sample Clock Source", options=["Onboard Clock"], index=0)
        st.number_input("Sample Rate", value=1000, min_value=1, step=1)
        st.number_input("Number of Samples", value=100, min_value=1, step=1)
        st.selectbox("Actual Sample Rate", options=[""], disabled=True)

        st.title("Logging Settings")
        st.selectbox("Logging Mode", options=["Off", "Log and Read"], index=0)
        st.text_input("TDMS File Path", value="data.tdms")
        
        st.title("Filtering Settings")
        filter = st.selectbox("Filter", options = ["No Filtering", "Filter"])
        panel.set_value("filter", filter)
        
        filter_freq = st.number_input("Filtering Frequency", value = 1000.0, step = 1.0)
        st.write(filter_freq)
        panel.set_value("filter_freq", filter_freq)
        filter_order = st.number_input("Filter Order",  min_value=0, max_value=1, value=0)
        panel.set_value("filter_order", filter_order)
        filter_response = st.selectbox("Filter Response", options=["Comb"])
        panel.set_value("filter_response", filter_response)
        if filter == "No Filtering":
            panel.set_value("filter_freq", 0.0)

        st.selectbox("Actual Filter Frequency", options=[""], disabled=True)
        st.selectbox("Actual Filter Order", options=[filter_order], disabled=True)
        st.selectbox("Actual Filter Response", options=[filter_response], disabled=True)
    


with left_col:
    with st.container(border=True):
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
                "name": "Volts",
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
        st_echarts(options=graph, height="400px", key="graph", width="100%")
with left_col:
    with st.container(border=True):
        tabs = st.tabs(["Voltage", "Current", "Strain Gage"])
with left_col:
    with st.container(border=True):
        with tabs[0]:
            data_type = "Voltage"
            st.title("Voltage Data")
            channel_left, channel_right = st.columns(2)
            with channel_left:
                max_value_voltage  = st.number_input(
                    "Max Value",
                    value=5.0,
                    step=0.1,
                )
                panel.set_value("max_value_voltage",max_value_voltage)

                min_value_voltage = st.number_input(
                    "Min Value",
                    value=-5.0,
                    step=0.1,
                )
                panel.set_value("min_value_voltage", min_value_voltage)

        with tabs[1]:
            st.title("Current Data")
            data_type = "Current"
            channel_left, channel_right = st.columns(2)
            with channel_left:
                shunt_location = st.selectbox(
                "shunt_location",
                options=[(e.name, e.value) for e in ShuntLocation],
                format_func=lambda x: x[0],
                index=0,
                )
                shunt_location = ShuntLocation[shunt_location[0]]
                panel.set_value("shunt_location", shunt_location)
                st.selectbox(options=["Amps"], label="Units", index=0, disabled=True)
                with st.expander("More current info", expanded=False):
                    min_value_current = st.number_input(
                        "Min Value",
                        value=-0.01,
                        step=0.001,
                    )
                    panel.set_value("min_value_current", min_value_current)
                    max_value_current = st.number_input(
                        "Max Value",
                        value=0.01,
                        step=1.0,
                        key="max_value_current",
                    )
                    current = panel.set_value("max_value_current", max_value_current)
                    shunt_resistor_value = st.number_input(
                        "Shunt Resistor Value",
                        value=249.0,
                        step=1.0,
                    )   
                    panel.set_value("shunt_resistor_value", shunt_resistor_value)
        with tabs[2]:
            data_type = "Strain"
            st.title("Strain Gage Data")
            channel_left, channel_right = st.columns(2)
            with channel_left:
                min_value_strain = st.number_input(
                    "Min Value",
                    value=-0.01,
                    step=0.01,
                )
                panel.set_value("min_value_strain", min_value_strain)
                max_value_strain = st.number_input(
                    "Max Value",
                    value=0.01,
                    step=0.01,
                    max_value=2.0
                )
                panel.set_value("max_value_strain", max_value_strain)
                with st.expander("strain gage information", expanded=False):
                    st.title("strain gage information")
                    gage_factor = st.number_input(
                        "Gage Factor",
                        value=2.0,
                        step=1.0,
                    )
                    panel.set_value("gage_factor", gage_factor)
                    nominal_gage = st.number_input(
                        "nominal gage resistance",
                        value=350.0,
                        step=1.0,
                    )
                    panel.set_value("gage_resistance",nominal_gage)
                    poisson_ratio = st.number_input(
                        "poisson ratio",
                        value=0.3,
                        step=1.0,
                    )
                    panel.set_value("poisson_ratio", poisson_ratio)
                with st.expander("strain gage information", expanded=False):
                    st.title("bridge information")
                    st.selectbox(label="strain configuration", options=["Full Bridge I", "Quarter Bridge", "Half Bridge II", "Half Bridge I", "Full Bridge III", "Full Bridge II"], key="strain_config",index=0, disabled=False)
                    panel.set_value("strain_config", "strain_config")
                    wire_resistance = st.number_input(
                        "lead wire resistance",
                        value=0.0,
                        step=1.0,
                    )
                    panel.set_value("wire_resistance", wire_resistance)
                    initial_voltage = st.number_input(
                        "initial bridge voltage",
                        value=0.0,
                        step=1.0,
                    )
                    panel.set_value("initial_voltage",initial_voltage)

                    st.selectbox(label="voltage excitation source", key = "voltage_excit",options=["External"], disabled=True)
                    panel.set_value("voltage_excitation_source", "voltage_excit")
                    voltage_excit = st.number_input(
                        "voltage excitation value",
                        value=2.5,
                        step=1.0,
                        key="voltage_excitation_value",
                    )
                    panel.set_value("voltage_excitation_value",voltage_excit)

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["No Trigger","Digital Start","Digital Pause","Digital Reference","Analog Start","Analog Pause", "Analog Reference", "Time Start"])
with tab1:
    st.write("To enable triggers, select a tab above, and configure the settings. \n Not all hardware supports all trigger types. Refer to your device documentation for more information.")
with tab2:
    st.selectbox("Source->", source)
    edge_digital = st.selectbox(
    "Edge",
    options=[(e.name, e.value) for e in DigitalEdge],
    format_func=lambda x: x[0],
    index=0,
    )
    edge_digital = DigitalEdge[edge_digital[0]]
    panel.set_value("edge_digital", edge_digital)

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
    date = st.date_input("Date", value=None)
    time_input = st.time_input("Time", value=None)
    st.write("If time is not manually set, task will begin after 10 seconds")



# graph_2= {
#     "animation": False,
#     "tooltip": {"trigger": "axis"},
#     "legend": {"data": ["Voltage (V)"]},
#     "xAxis": {
#         "type": "category",
#         "data": [x / sample_rate for x in range(len(current_data))],
#         "name": "Time",
#         "nameLocation": "center",
#         "nameGap": 40,
#     },
#     "yAxis": {
#         "type": "value",
#         "name": "Volts",
#         "nameRotate": 90,
#         "nameLocation": "center",
#         "nameGap": 40,
#     },
#     "series": [
#         {
#             "name": "voltage_amplitude",
#             "type": "line",
#             "data": current_data,
#             "emphasis": {"focus": "series"},
#             "smooth": True,
#             "seriesLayoutBy": "row",
#         },
#     ],
# }
# with tabs[1]:
#     st_echarts(options=graph_2, height="400px", key="graph_2", width="100%")
# graph_3 = {
#     "animation": False,
#     "tooltip": {"trigger": "axis"},
#     "legend": {"data": ["Voltage (V)"]},
#     "xAxis": {
#         "type": "category",
#         "data": [x / sample_rate for x in range(len(strain_data))],
#         "name": "Time",
#         "nameLocation": "center",
#         "nameGap": 40,
#     },
#     "yAxis": {
#         "type": "value",
#         "name": "Volts",
#         "nameRotate": 90,
#         "nameLocation": "center",
#         "nameGap": 40,
#     },
#     "series": [
#         {
#             "name": "voltage_amplitude",
#             "type": "line",
#             "data": strain_data,
#             "emphasis": {"focus": "series"},
#             "smooth": True,
#             "seriesLayoutBy": "row",
#         },
#     ],
# }
# with tabs[2]:
#     st_echarts(options=graph_3, height="400px", key="graph_3", width="100%")

  


