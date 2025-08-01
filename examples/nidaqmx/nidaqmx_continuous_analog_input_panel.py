"""Streamlit visualization script to display data acquired by nidaqmx_continuous_analog_input.py."""

import streamlit as st
from nidaqmx.constants import (
    TerminalConfiguration,
    CJCSource,
    TemperatureUnits,
    ThermocoupleType,
    LoggingMode,
)
from streamlit_echarts import st_echarts

import nipanel
from nipanel.controls import enum_selectbox


st.set_page_config(page_title="NI-DAQmx Example", page_icon="📈", layout="wide")
st.title("Analog Input - Voltage and Thermocouple in a Single Task")

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

panel = nipanel.get_streamlit_panel_accessor()
is_running = panel.get_value("is_running", False)

if is_running:
    st.button(r"⏹️ Stop", key="stop_button")
else:
    st.button(r"▶️ Run", key="run_button")

thermocouple_data = panel.get_value("thermocouple_data", [0.0])
voltage_data = panel.get_value("voltage_data", [0.0])
sample_rate = panel.get_value("sample_rate", 0.0)

# Create two-column layout for the entire interface
left_column, right_column = st.columns([1, 1])

# Left column - Channel tabs and Timing Settings
with left_column:
    # Channel Settings tabs
    with st.container(border=True):
        st.header("Channel Settings")
        voltage_tab, thermocouple_tab = st.tabs(["Voltage", "Thermocouple"])

        voltage_tab.header("Voltage")
        with voltage_tab:
            channel_left_column, channel_right_column = st.columns(2)
            with channel_left_column:
                st.selectbox(options=["Dev1/ai0"], label="Physical Channels", disabled=True)
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

        thermocouple_tab.header("Thermocouple")
        with thermocouple_tab:
            channel_left_column, channel_middle_column, channel_right_column = st.columns(3)
            with channel_left_column:
                st.selectbox(options=["Dev1/ai1"], label="Physical Channel", disabled=True)
                st.number_input(
                    "Min Value",
                    value=0.0,
                    step=1.0,
                    disabled=panel.get_value("is_running", False),
                    key="thermocouple_min_value",
                )
                st.number_input(
                    "Max Value",
                    value=100.0,
                    step=1.0,
                    disabled=panel.get_value("is_running", False),
                    key="thermocouple_max_value",
                )
            with channel_middle_column:
                enum_selectbox(
                    panel,
                    label="Units",
                    value=TemperatureUnits.DEG_C,
                    disabled=panel.get_value("is_running", False),
                    key="thermocouple_units",
                )
                enum_selectbox(
                    panel,
                    label="Thermocouple Type",
                    value=ThermocoupleType.K,
                    disabled=panel.get_value("is_running", False),
                    key="thermocouple_type",
                )
            with channel_right_column:
                enum_selectbox(
                    panel,
                    label="CJC Source",
                    value=CJCSource.CONSTANT_USER_VALUE,
                    disabled=panel.get_value("is_running", False),
                    key="thermocouple_cjc_source",
                )
                st.number_input(
                    "CJC Value",
                    value=25.0,
                    step=1.0,
                    disabled=panel.get_value("is_running", False),
                    key="thermocouple_cjc_val",
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
                "Samples per Loop",
                value=3000,
                step=100,
                min_value=10,
                disabled=panel.get_value("is_running", False),
                key="samples_per_channel",
            )
            st.text_input(
                label="Actual Sample Rate",
                value=str(sample_rate) if sample_rate else "",
                key="actual_sample_rate_display",
            )

# Right column - Graph and Logging Settings
with right_column:
    with st.container(border=True):
        # Graph section
        st.header("Voltage & Thermocouple")
        voltage_therm_graph = {
            "animation": False,
            "tooltip": {"trigger": "axis"},
            "legend": {"data": ["Voltage (V)", "Temperature (C)"]},
            "xAxis": {
                "type": "category",
                "data": [
                    x / sample_rate if sample_rate > 0.001 else x for x in range(len(voltage_data))
                ],
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
                {
                    "name": "thermocouple_amplitude",
                    "type": "line",
                    "data": thermocouple_data,
                    "color": "red",
                    "emphasis": {"focus": "series"},
                    "smooth": True,
                    "seriesLayoutBy": "row",
                },
            ],
        }
        st_echarts(options=voltage_therm_graph, height="446px", key="voltage_therm_graph")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1")
        # st_echarts(options=voltage_therm_graph, height="446px", key="2")
        # st_echarts(options=voltage_therm_graph, height="446px", key="3")
        # st_echarts(options=voltage_therm_graph, height="446px", key="4")
        # st_echarts(options=voltage_therm_graph, height="446px", key="5")
        # st_echarts(options=voltage_therm_graph, height="446px", key="6")
        # st_echarts(options=voltage_therm_graph, height="446px", key="7")
        # st_echarts(options=voltage_therm_graph, height="446px", key="8")
        # st_echarts(options=voltage_therm_graph, height="446px", key="9")
        # st_echarts(options=voltage_therm_graph, height="446px", key="10")
        # st_echarts(options=voltage_therm_graph, height="446px", key="11")
        # st_echarts(options=voltage_therm_graph, height="446px", key="12")
        # st_echarts(options=voltage_therm_graph, height="446px", key="13")
        # st_echarts(options=voltage_therm_graph, height="446px", key="14")
        # st_echarts(options=voltage_therm_graph, height="446px", key="15")
        # st_echarts(options=voltage_therm_graph, height="446px", key="16")
        # st_echarts(options=voltage_therm_graph, height="446px", key="17")
        # st_echarts(options=voltage_therm_graph, height="446px", key="18")
        # st_echarts(options=voltage_therm_graph, height="446px", key="19")
        # st_echarts(options=voltage_therm_graph, height="446px", key="20")
        # st_echarts(options=voltage_therm_graph, height="446px", key="21")
        # st_echarts(options=voltage_therm_graph, height="446px", key="22")
        # st_echarts(options=voltage_therm_graph, height="446px", key="23")
        # st_echarts(options=voltage_therm_graph, height="446px", key="24")
        # st_echarts(options=voltage_therm_graph, height="446px", key="25")
        # st_echarts(options=voltage_therm_graph, height="446px", key="26")
        # st_echarts(options=voltage_therm_graph, height="446px", key="27")
        # st_echarts(options=voltage_therm_graph, height="446px", key="28")
        # st_echarts(options=voltage_therm_graph, height="446px", key="29")
        # st_echarts(options=voltage_therm_graph, height="446px", key="30")
        # st_echarts(options=voltage_therm_graph, height="446px", key="41")
        # st_echarts(options=voltage_therm_graph, height="446px", key="42")
        # st_echarts(options=voltage_therm_graph, height="446px", key="43")
        # st_echarts(options=voltage_therm_graph, height="446px", key="44")
        # st_echarts(options=voltage_therm_graph, height="446px", key="45")
        # st_echarts(options=voltage_therm_graph, height="446px", key="46")
        # st_echarts(options=voltage_therm_graph, height="446px", key="47")
        # st_echarts(options=voltage_therm_graph, height="446px", key="48")
        # st_echarts(options=voltage_therm_graph, height="446px", key="49")
        # st_echarts(options=voltage_therm_graph, height="446px", key="50")
        # st_echarts(options=voltage_therm_graph, height="446px", key="61")
        # st_echarts(options=voltage_therm_graph, height="446px", key="62")
        # st_echarts(options=voltage_therm_graph, height="446px", key="63")
        # st_echarts(options=voltage_therm_graph, height="446px", key="64")
        # st_echarts(options=voltage_therm_graph, height="446px", key="65")
        # st_echarts(options=voltage_therm_graph, height="446px", key="66")
        # st_echarts(options=voltage_therm_graph, height="446px", key="67")
        # st_echarts(options=voltage_therm_graph, height="446px", key="68")
        # st_echarts(options=voltage_therm_graph, height="446px", key="69")
        # st_echarts(options=voltage_therm_graph, height="446px", key="70")
        # st_echarts(options=voltage_therm_graph, height="446px", key="81")
        # st_echarts(options=voltage_therm_graph, height="446px", key="82")
        # st_echarts(options=voltage_therm_graph, height="446px", key="83")
        # st_echarts(options=voltage_therm_graph, height="446px", key="84")
        # st_echarts(options=voltage_therm_graph, height="446px", key="85")
        # st_echarts(options=voltage_therm_graph, height="446px", key="86")
        # st_echarts(options=voltage_therm_graph, height="446px", key="87")
        # st_echarts(options=voltage_therm_graph, height="446px", key="88")
        # st_echarts(options=voltage_therm_graph, height="446px", key="89")
        # st_echarts(options=voltage_therm_graph, height="446px", key="90")
        # st_echarts(options=voltage_therm_graph, height="446px", key="91")
        # st_echarts(options=voltage_therm_graph, height="446px", key="92")
        # st_echarts(options=voltage_therm_graph, height="446px", key="93")
        # st_echarts(options=voltage_therm_graph, height="446px", key="94")
        # st_echarts(options=voltage_therm_graph, height="446px", key="95")
        # st_echarts(options=voltage_therm_graph, height="446px", key="96")
        # st_echarts(options=voltage_therm_graph, height="446px", key="97")
        # st_echarts(options=voltage_therm_graph, height="446px", key="98")
        # st_echarts(options=voltage_therm_graph, height="446px", key="99")
        # st_echarts(options=voltage_therm_graph, height="446px", key="100")
        # st_echarts(options=voltage_therm_graph, height="446px", key="101")
        # st_echarts(options=voltage_therm_graph, height="446px", key="102")
        # st_echarts(options=voltage_therm_graph, height="446px", key="103")
        # st_echarts(options=voltage_therm_graph, height="446px", key="104")
        # st_echarts(options=voltage_therm_graph, height="446px", key="105")
        # st_echarts(options=voltage_therm_graph, height="446px", key="106")
        # st_echarts(options=voltage_therm_graph, height="446px", key="107")
        # st_echarts(options=voltage_therm_graph, height="446px", key="108")
        # st_echarts(options=voltage_therm_graph, height="446px", key="109")
        # st_echarts(options=voltage_therm_graph, height="446px", key="110")
        # st_echarts(options=voltage_therm_graph, height="446px", key="111")
        # st_echarts(options=voltage_therm_graph, height="446px", key="112")
        # st_echarts(options=voltage_therm_graph, height="446px", key="113")
        # st_echarts(options=voltage_therm_graph, height="446px", key="114")
        # st_echarts(options=voltage_therm_graph, height="446px", key="115")
        # st_echarts(options=voltage_therm_graph, height="446px", key="116")
        # st_echarts(options=voltage_therm_graph, height="446px", key="117")
        # st_echarts(options=voltage_therm_graph, height="446px", key="118")
        # st_echarts(options=voltage_therm_graph, height="446px", key="119")
        # st_echarts(options=voltage_therm_graph, height="446px", key="120")
        # st_echarts(options=voltage_therm_graph, height="446px", key="121")
        # st_echarts(options=voltage_therm_graph, height="446px", key="122")
        # st_echarts(options=voltage_therm_graph, height="446px", key="123")
        # st_echarts(options=voltage_therm_graph, height="446px", key="124")
        # st_echarts(options=voltage_therm_graph, height="446px", key="125")
        # st_echarts(options=voltage_therm_graph, height="446px", key="126")
        # st_echarts(options=voltage_therm_graph, height="446px", key="127")
        # st_echarts(options=voltage_therm_graph, height="446px", key="128")
        # st_echarts(options=voltage_therm_graph, height="446px", key="129")
        # st_echarts(options=voltage_therm_graph, height="446px", key="130")
        # st_echarts(options=voltage_therm_graph, height="446px", key="141")
        # st_echarts(options=voltage_therm_graph, height="446px", key="142")
        # st_echarts(options=voltage_therm_graph, height="446px", key="143")
        # st_echarts(options=voltage_therm_graph, height="446px", key="144")
        # st_echarts(options=voltage_therm_graph, height="446px", key="145")
        # st_echarts(options=voltage_therm_graph, height="446px", key="146")
        # st_echarts(options=voltage_therm_graph, height="446px", key="147")
        # st_echarts(options=voltage_therm_graph, height="446px", key="148")
        # st_echarts(options=voltage_therm_graph, height="446px", key="149")
        # st_echarts(options=voltage_therm_graph, height="446px", key="150")
        # st_echarts(options=voltage_therm_graph, height="446px", key="161")
        # st_echarts(options=voltage_therm_graph, height="446px", key="162")
        # st_echarts(options=voltage_therm_graph, height="446px", key="163")
        # st_echarts(options=voltage_therm_graph, height="446px", key="164")
        # st_echarts(options=voltage_therm_graph, height="446px", key="165")
        # st_echarts(options=voltage_therm_graph, height="446px", key="166")
        # st_echarts(options=voltage_therm_graph, height="446px", key="167")
        # st_echarts(options=voltage_therm_graph, height="446px", key="168")
        # st_echarts(options=voltage_therm_graph, height="446px", key="169")
        # st_echarts(options=voltage_therm_graph, height="446px", key="170")
        # st_echarts(options=voltage_therm_graph, height="446px", key="181")
        # st_echarts(options=voltage_therm_graph, height="446px", key="182")
        # st_echarts(options=voltage_therm_graph, height="446px", key="183")
        # st_echarts(options=voltage_therm_graph, height="446px", key="184")
        # st_echarts(options=voltage_therm_graph, height="446px", key="185")
        # st_echarts(options=voltage_therm_graph, height="446px", key="186")
        # st_echarts(options=voltage_therm_graph, height="446px", key="187")
        # st_echarts(options=voltage_therm_graph, height="446px", key="188")
        # st_echarts(options=voltage_therm_graph, height="446px", key="189")
        # st_echarts(options=voltage_therm_graph, height="446px", key="190")
        # st_echarts(options=voltage_therm_graph, height="446px", key="191")
        # st_echarts(options=voltage_therm_graph, height="446px", key="192")
        # st_echarts(options=voltage_therm_graph, height="446px", key="193")
        # st_echarts(options=voltage_therm_graph, height="446px", key="194")
        # st_echarts(options=voltage_therm_graph, height="446px", key="195")
        # st_echarts(options=voltage_therm_graph, height="446px", key="196")
        # st_echarts(options=voltage_therm_graph, height="446px", key="197")
        # st_echarts(options=voltage_therm_graph, height="446px", key="198")
        # st_echarts(options=voltage_therm_graph, height="446px", key="199")
        # st_echarts(options=voltage_therm_graph, height="446px", key="200")
        # st_echarts(options=voltage_therm_graph, height="446px", key="301")
        # st_echarts(options=voltage_therm_graph, height="446px", key="302")
        # st_echarts(options=voltage_therm_graph, height="446px", key="303")
        # st_echarts(options=voltage_therm_graph, height="446px", key="304")
        # st_echarts(options=voltage_therm_graph, height="446px", key="305")
        # st_echarts(options=voltage_therm_graph, height="446px", key="306")
        # st_echarts(options=voltage_therm_graph, height="446px", key="307")
        # st_echarts(options=voltage_therm_graph, height="446px", key="308")
        # st_echarts(options=voltage_therm_graph, height="446px", key="309")
        # st_echarts(options=voltage_therm_graph, height="446px", key="310")
        # st_echarts(options=voltage_therm_graph, height="446px", key="311")
        # st_echarts(options=voltage_therm_graph, height="446px", key="312")
        # st_echarts(options=voltage_therm_graph, height="446px", key="313")
        # st_echarts(options=voltage_therm_graph, height="446px", key="314")
        # st_echarts(options=voltage_therm_graph, height="446px", key="315")
        # st_echarts(options=voltage_therm_graph, height="446px", key="316")
        # st_echarts(options=voltage_therm_graph, height="446px", key="317")
        # st_echarts(options=voltage_therm_graph, height="446px", key="318")
        # st_echarts(options=voltage_therm_graph, height="446px", key="319")
        # st_echarts(options=voltage_therm_graph, height="446px", key="320")
        # st_echarts(options=voltage_therm_graph, height="446px", key="321")
        # st_echarts(options=voltage_therm_graph, height="446px", key="322")
        # st_echarts(options=voltage_therm_graph, height="446px", key="323")
        # st_echarts(options=voltage_therm_graph, height="446px", key="324")
        # st_echarts(options=voltage_therm_graph, height="446px", key="325")
        # st_echarts(options=voltage_therm_graph, height="446px", key="326")
        # st_echarts(options=voltage_therm_graph, height="446px", key="327")
        # st_echarts(options=voltage_therm_graph, height="446px", key="328")
        # st_echarts(options=voltage_therm_graph, height="446px", key="329")
        # st_echarts(options=voltage_therm_graph, height="446px", key="330")
        # st_echarts(options=voltage_therm_graph, height="446px", key="341")
        # st_echarts(options=voltage_therm_graph, height="446px", key="342")
        # st_echarts(options=voltage_therm_graph, height="446px", key="343")
        # st_echarts(options=voltage_therm_graph, height="446px", key="344")
        # st_echarts(options=voltage_therm_graph, height="446px", key="345")
        # st_echarts(options=voltage_therm_graph, height="446px", key="346")
        # st_echarts(options=voltage_therm_graph, height="446px", key="347")
        # st_echarts(options=voltage_therm_graph, height="446px", key="348")
        # st_echarts(options=voltage_therm_graph, height="446px", key="349")
        # st_echarts(options=voltage_therm_graph, height="446px", key="350")
        # st_echarts(options=voltage_therm_graph, height="446px", key="361")
        # st_echarts(options=voltage_therm_graph, height="446px", key="362")
        # st_echarts(options=voltage_therm_graph, height="446px", key="363")
        # st_echarts(options=voltage_therm_graph, height="446px", key="364")
        # st_echarts(options=voltage_therm_graph, height="446px", key="365")
        # st_echarts(options=voltage_therm_graph, height="446px", key="366")
        # st_echarts(options=voltage_therm_graph, height="446px", key="367")
        # st_echarts(options=voltage_therm_graph, height="446px", key="368")
        # st_echarts(options=voltage_therm_graph, height="446px", key="369")
        # st_echarts(options=voltage_therm_graph, height="446px", key="370")
        # st_echarts(options=voltage_therm_graph, height="446px", key="381")
        # st_echarts(options=voltage_therm_graph, height="446px", key="382")
        # st_echarts(options=voltage_therm_graph, height="446px", key="383")
        # st_echarts(options=voltage_therm_graph, height="446px", key="384")
        # st_echarts(options=voltage_therm_graph, height="446px", key="385")
        # st_echarts(options=voltage_therm_graph, height="446px", key="386")
        # st_echarts(options=voltage_therm_graph, height="446px", key="387")
        # st_echarts(options=voltage_therm_graph, height="446px", key="388")
        # st_echarts(options=voltage_therm_graph, height="446px", key="389")
        # st_echarts(options=voltage_therm_graph, height="446px", key="390")
        # st_echarts(options=voltage_therm_graph, height="446px", key="391")
        # st_echarts(options=voltage_therm_graph, height="446px", key="392")
        # st_echarts(options=voltage_therm_graph, height="446px", key="393")
        # st_echarts(options=voltage_therm_graph, height="446px", key="394")
        # st_echarts(options=voltage_therm_graph, height="446px", key="395")
        # st_echarts(options=voltage_therm_graph, height="446px", key="396")
        # st_echarts(options=voltage_therm_graph, height="446px", key="397")
        # st_echarts(options=voltage_therm_graph, height="446px", key="398")
        # st_echarts(options=voltage_therm_graph, height="446px", key="399")
        # st_echarts(options=voltage_therm_graph, height="446px", key="400")
        # st_echarts(options=voltage_therm_graph, height="446px", key="401")
        # st_echarts(options=voltage_therm_graph, height="446px", key="402")
        # st_echarts(options=voltage_therm_graph, height="446px", key="403")
        # st_echarts(options=voltage_therm_graph, height="446px", key="404")
        # st_echarts(options=voltage_therm_graph, height="446px", key="405")
        # st_echarts(options=voltage_therm_graph, height="446px", key="406")
        # st_echarts(options=voltage_therm_graph, height="446px", key="407")
        # st_echarts(options=voltage_therm_graph, height="446px", key="408")
        # st_echarts(options=voltage_therm_graph, height="446px", key="409")
        # st_echarts(options=voltage_therm_graph, height="446px", key="410")
        # st_echarts(options=voltage_therm_graph, height="446px", key="411")
        # st_echarts(options=voltage_therm_graph, height="446px", key="412")
        # st_echarts(options=voltage_therm_graph, height="446px", key="413")
        # st_echarts(options=voltage_therm_graph, height="446px", key="414")
        # st_echarts(options=voltage_therm_graph, height="446px", key="415")
        # st_echarts(options=voltage_therm_graph, height="446px", key="416")
        # st_echarts(options=voltage_therm_graph, height="446px", key="417")
        # st_echarts(options=voltage_therm_graph, height="446px", key="418")
        # st_echarts(options=voltage_therm_graph, height="446px", key="419")
        # st_echarts(options=voltage_therm_graph, height="446px", key="420")
        # st_echarts(options=voltage_therm_graph, height="446px", key="421")
        # st_echarts(options=voltage_therm_graph, height="446px", key="422")
        # st_echarts(options=voltage_therm_graph, height="446px", key="423")
        # st_echarts(options=voltage_therm_graph, height="446px", key="424")
        # st_echarts(options=voltage_therm_graph, height="446px", key="425")
        # st_echarts(options=voltage_therm_graph, height="446px", key="426")
        # st_echarts(options=voltage_therm_graph, height="446px", key="427")
        # st_echarts(options=voltage_therm_graph, height="446px", key="428")
        # st_echarts(options=voltage_therm_graph, height="446px", key="429")
        # st_echarts(options=voltage_therm_graph, height="446px", key="430")
        # st_echarts(options=voltage_therm_graph, height="446px", key="441")
        # st_echarts(options=voltage_therm_graph, height="446px", key="442")
        # st_echarts(options=voltage_therm_graph, height="446px", key="443")
        # st_echarts(options=voltage_therm_graph, height="446px", key="444")
        # st_echarts(options=voltage_therm_graph, height="446px", key="445")
        # st_echarts(options=voltage_therm_graph, height="446px", key="446")
        # st_echarts(options=voltage_therm_graph, height="446px", key="447")
        # st_echarts(options=voltage_therm_graph, height="446px", key="448")
        # st_echarts(options=voltage_therm_graph, height="446px", key="449")
        # st_echarts(options=voltage_therm_graph, height="446px", key="450")
        # st_echarts(options=voltage_therm_graph, height="446px", key="461")
        # st_echarts(options=voltage_therm_graph, height="446px", key="462")
        # st_echarts(options=voltage_therm_graph, height="446px", key="463")
        # st_echarts(options=voltage_therm_graph, height="446px", key="464")
        # st_echarts(options=voltage_therm_graph, height="446px", key="465")
        # st_echarts(options=voltage_therm_graph, height="446px", key="466")
        # st_echarts(options=voltage_therm_graph, height="446px", key="467")
        # st_echarts(options=voltage_therm_graph, height="446px", key="468")
        # st_echarts(options=voltage_therm_graph, height="446px", key="469")
        # st_echarts(options=voltage_therm_graph, height="446px", key="470")
        # st_echarts(options=voltage_therm_graph, height="446px", key="481")
        # st_echarts(options=voltage_therm_graph, height="446px", key="482")
        # st_echarts(options=voltage_therm_graph, height="446px", key="483")
        # st_echarts(options=voltage_therm_graph, height="446px", key="484")
        # st_echarts(options=voltage_therm_graph, height="446px", key="485")
        # st_echarts(options=voltage_therm_graph, height="446px", key="486")
        # st_echarts(options=voltage_therm_graph, height="446px", key="487")
        # st_echarts(options=voltage_therm_graph, height="446px", key="488")
        # st_echarts(options=voltage_therm_graph, height="446px", key="489")
        # st_echarts(options=voltage_therm_graph, height="446px", key="490")
        # st_echarts(options=voltage_therm_graph, height="446px", key="491")
        # st_echarts(options=voltage_therm_graph, height="446px", key="492")
        # st_echarts(options=voltage_therm_graph, height="446px", key="493")
        # st_echarts(options=voltage_therm_graph, height="446px", key="494")
        # st_echarts(options=voltage_therm_graph, height="446px", key="495")
        # st_echarts(options=voltage_therm_graph, height="446px", key="496")
        # st_echarts(options=voltage_therm_graph, height="446px", key="497")
        # st_echarts(options=voltage_therm_graph, height="446px", key="498")
        # st_echarts(options=voltage_therm_graph, height="446px", key="499")
        # st_echarts(options=voltage_therm_graph, height="446px", key="500")
        # st_echarts(options=voltage_therm_graph, height="446px", key="501")
        # st_echarts(options=voltage_therm_graph, height="446px", key="502")
        # st_echarts(options=voltage_therm_graph, height="446px", key="503")
        # st_echarts(options=voltage_therm_graph, height="446px", key="504")
        # st_echarts(options=voltage_therm_graph, height="446px", key="505")
        # st_echarts(options=voltage_therm_graph, height="446px", key="506")
        # st_echarts(options=voltage_therm_graph, height="446px", key="507")
        # st_echarts(options=voltage_therm_graph, height="446px", key="508")
        # st_echarts(options=voltage_therm_graph, height="446px", key="509")
        # st_echarts(options=voltage_therm_graph, height="446px", key="510")
        # st_echarts(options=voltage_therm_graph, height="446px", key="511")
        # st_echarts(options=voltage_therm_graph, height="446px", key="512")
        # st_echarts(options=voltage_therm_graph, height="446px", key="513")
        # st_echarts(options=voltage_therm_graph, height="446px", key="514")
        # st_echarts(options=voltage_therm_graph, height="446px", key="515")
        # st_echarts(options=voltage_therm_graph, height="446px", key="516")
        # st_echarts(options=voltage_therm_graph, height="446px", key="517")
        # st_echarts(options=voltage_therm_graph, height="446px", key="518")
        # st_echarts(options=voltage_therm_graph, height="446px", key="519")
        # st_echarts(options=voltage_therm_graph, height="446px", key="520")
        # st_echarts(options=voltage_therm_graph, height="446px", key="521")
        # st_echarts(options=voltage_therm_graph, height="446px", key="522")
        # st_echarts(options=voltage_therm_graph, height="446px", key="523")
        # st_echarts(options=voltage_therm_graph, height="446px", key="524")
        # st_echarts(options=voltage_therm_graph, height="446px", key="525")
        # st_echarts(options=voltage_therm_graph, height="446px", key="526")
        # st_echarts(options=voltage_therm_graph, height="446px", key="527")
        # st_echarts(options=voltage_therm_graph, height="446px", key="528")
        # st_echarts(options=voltage_therm_graph, height="446px", key="529")
        # st_echarts(options=voltage_therm_graph, height="446px", key="530")
        # st_echarts(options=voltage_therm_graph, height="446px", key="541")
        # st_echarts(options=voltage_therm_graph, height="446px", key="542")
        # st_echarts(options=voltage_therm_graph, height="446px", key="543")
        # st_echarts(options=voltage_therm_graph, height="446px", key="544")
        # st_echarts(options=voltage_therm_graph, height="446px", key="545")
        # st_echarts(options=voltage_therm_graph, height="446px", key="546")
        # st_echarts(options=voltage_therm_graph, height="446px", key="547")
        # st_echarts(options=voltage_therm_graph, height="446px", key="548")
        # st_echarts(options=voltage_therm_graph, height="446px", key="549")
        # st_echarts(options=voltage_therm_graph, height="446px", key="550")
        # st_echarts(options=voltage_therm_graph, height="446px", key="561")
        # st_echarts(options=voltage_therm_graph, height="446px", key="562")
        # st_echarts(options=voltage_therm_graph, height="446px", key="563")
        # st_echarts(options=voltage_therm_graph, height="446px", key="564")
        # st_echarts(options=voltage_therm_graph, height="446px", key="565")
        # st_echarts(options=voltage_therm_graph, height="446px", key="566")
        # st_echarts(options=voltage_therm_graph, height="446px", key="567")
        # st_echarts(options=voltage_therm_graph, height="446px", key="568")
        # st_echarts(options=voltage_therm_graph, height="446px", key="569")
        # st_echarts(options=voltage_therm_graph, height="446px", key="570")
        # st_echarts(options=voltage_therm_graph, height="446px", key="581")
        # st_echarts(options=voltage_therm_graph, height="446px", key="582")
        # st_echarts(options=voltage_therm_graph, height="446px", key="583")
        # st_echarts(options=voltage_therm_graph, height="446px", key="584")
        # st_echarts(options=voltage_therm_graph, height="446px", key="585")
        # st_echarts(options=voltage_therm_graph, height="446px", key="586")
        # st_echarts(options=voltage_therm_graph, height="446px", key="587")
        # st_echarts(options=voltage_therm_graph, height="446px", key="588")
        # st_echarts(options=voltage_therm_graph, height="446px", key="589")
        # st_echarts(options=voltage_therm_graph, height="446px", key="590")
        # st_echarts(options=voltage_therm_graph, height="446px", key="591")
        # st_echarts(options=voltage_therm_graph, height="446px", key="592")
        # st_echarts(options=voltage_therm_graph, height="446px", key="593")
        # st_echarts(options=voltage_therm_graph, height="446px", key="594")
        # st_echarts(options=voltage_therm_graph, height="446px", key="595")
        # st_echarts(options=voltage_therm_graph, height="446px", key="596")
        # st_echarts(options=voltage_therm_graph, height="446px", key="597")
        # st_echarts(options=voltage_therm_graph, height="446px", key="598")
        # st_echarts(options=voltage_therm_graph, height="446px", key="599")
        # st_echarts(options=voltage_therm_graph, height="446px", key="600")
        # st_echarts(options=voltage_therm_graph, height="446px", key="601")
        # st_echarts(options=voltage_therm_graph, height="446px", key="602")
        # st_echarts(options=voltage_therm_graph, height="446px", key="603")
        # st_echarts(options=voltage_therm_graph, height="446px", key="604")
        # st_echarts(options=voltage_therm_graph, height="446px", key="605")
        # st_echarts(options=voltage_therm_graph, height="446px", key="606")
        # st_echarts(options=voltage_therm_graph, height="446px", key="607")
        # st_echarts(options=voltage_therm_graph, height="446px", key="608")
        # st_echarts(options=voltage_therm_graph, height="446px", key="609")
        # st_echarts(options=voltage_therm_graph, height="446px", key="610")
        # st_echarts(options=voltage_therm_graph, height="446px", key="611")
        # st_echarts(options=voltage_therm_graph, height="446px", key="612")
        # st_echarts(options=voltage_therm_graph, height="446px", key="613")
        # st_echarts(options=voltage_therm_graph, height="446px", key="614")
        # st_echarts(options=voltage_therm_graph, height="446px", key="615")
        # st_echarts(options=voltage_therm_graph, height="446px", key="616")
        # st_echarts(options=voltage_therm_graph, height="446px", key="617")
        # st_echarts(options=voltage_therm_graph, height="446px", key="618")
        # st_echarts(options=voltage_therm_graph, height="446px", key="619")
        # st_echarts(options=voltage_therm_graph, height="446px", key="620")
        # st_echarts(options=voltage_therm_graph, height="446px", key="621")
        # st_echarts(options=voltage_therm_graph, height="446px", key="622")
        # st_echarts(options=voltage_therm_graph, height="446px", key="623")
        # st_echarts(options=voltage_therm_graph, height="446px", key="624")
        # st_echarts(options=voltage_therm_graph, height="446px", key="625")
        # st_echarts(options=voltage_therm_graph, height="446px", key="626")
        # st_echarts(options=voltage_therm_graph, height="446px", key="627")
        # st_echarts(options=voltage_therm_graph, height="446px", key="628")
        # st_echarts(options=voltage_therm_graph, height="446px", key="629")
        # st_echarts(options=voltage_therm_graph, height="446px", key="630")
        # st_echarts(options=voltage_therm_graph, height="446px", key="641")
        # st_echarts(options=voltage_therm_graph, height="446px", key="642")
        # st_echarts(options=voltage_therm_graph, height="446px", key="643")
        # st_echarts(options=voltage_therm_graph, height="446px", key="644")
        # st_echarts(options=voltage_therm_graph, height="446px", key="645")
        # st_echarts(options=voltage_therm_graph, height="446px", key="646")
        # st_echarts(options=voltage_therm_graph, height="446px", key="647")
        # st_echarts(options=voltage_therm_graph, height="446px", key="648")
        # st_echarts(options=voltage_therm_graph, height="446px", key="649")
        # st_echarts(options=voltage_therm_graph, height="446px", key="650")
        # st_echarts(options=voltage_therm_graph, height="446px", key="661")
        # st_echarts(options=voltage_therm_graph, height="446px", key="662")
        # st_echarts(options=voltage_therm_graph, height="446px", key="663")
        # st_echarts(options=voltage_therm_graph, height="446px", key="664")
        # st_echarts(options=voltage_therm_graph, height="446px", key="665")
        # st_echarts(options=voltage_therm_graph, height="446px", key="666")
        # st_echarts(options=voltage_therm_graph, height="446px", key="667")
        # st_echarts(options=voltage_therm_graph, height="446px", key="668")
        # st_echarts(options=voltage_therm_graph, height="446px", key="669")
        # st_echarts(options=voltage_therm_graph, height="446px", key="670")
        # st_echarts(options=voltage_therm_graph, height="446px", key="681")
        # st_echarts(options=voltage_therm_graph, height="446px", key="682")
        # st_echarts(options=voltage_therm_graph, height="446px", key="683")
        # st_echarts(options=voltage_therm_graph, height="446px", key="684")
        # st_echarts(options=voltage_therm_graph, height="446px", key="685")
        # st_echarts(options=voltage_therm_graph, height="446px", key="686")
        # st_echarts(options=voltage_therm_graph, height="446px", key="687")
        # st_echarts(options=voltage_therm_graph, height="446px", key="688")
        # st_echarts(options=voltage_therm_graph, height="446px", key="689")
        # st_echarts(options=voltage_therm_graph, height="446px", key="690")
        # st_echarts(options=voltage_therm_graph, height="446px", key="691")
        # st_echarts(options=voltage_therm_graph, height="446px", key="692")
        # st_echarts(options=voltage_therm_graph, height="446px", key="693")
        # st_echarts(options=voltage_therm_graph, height="446px", key="694")
        # st_echarts(options=voltage_therm_graph, height="446px", key="695")
        # st_echarts(options=voltage_therm_graph, height="446px", key="696")
        # st_echarts(options=voltage_therm_graph, height="446px", key="697")
        # st_echarts(options=voltage_therm_graph, height="446px", key="698")
        # st_echarts(options=voltage_therm_graph, height="446px", key="699")
        # st_echarts(options=voltage_therm_graph, height="446px", key="700")
        # st_echarts(options=voltage_therm_graph, height="446px", key="701")
        # st_echarts(options=voltage_therm_graph, height="446px", key="702")
        # st_echarts(options=voltage_therm_graph, height="446px", key="703")
        # st_echarts(options=voltage_therm_graph, height="446px", key="704")
        # st_echarts(options=voltage_therm_graph, height="446px", key="705")
        # st_echarts(options=voltage_therm_graph, height="446px", key="706")
        # st_echarts(options=voltage_therm_graph, height="446px", key="707")
        # st_echarts(options=voltage_therm_graph, height="446px", key="708")
        # st_echarts(options=voltage_therm_graph, height="446px", key="709")
        # st_echarts(options=voltage_therm_graph, height="446px", key="710")
        # st_echarts(options=voltage_therm_graph, height="446px", key="711")
        # st_echarts(options=voltage_therm_graph, height="446px", key="712")
        # st_echarts(options=voltage_therm_graph, height="446px", key="713")
        # st_echarts(options=voltage_therm_graph, height="446px", key="714")
        # st_echarts(options=voltage_therm_graph, height="446px", key="715")
        # st_echarts(options=voltage_therm_graph, height="446px", key="716")
        # st_echarts(options=voltage_therm_graph, height="446px", key="717")
        # st_echarts(options=voltage_therm_graph, height="446px", key="718")
        # st_echarts(options=voltage_therm_graph, height="446px", key="719")
        # st_echarts(options=voltage_therm_graph, height="446px", key="720")
        # st_echarts(options=voltage_therm_graph, height="446px", key="721")
        # st_echarts(options=voltage_therm_graph, height="446px", key="722")
        # st_echarts(options=voltage_therm_graph, height="446px", key="723")
        # st_echarts(options=voltage_therm_graph, height="446px", key="724")
        # st_echarts(options=voltage_therm_graph, height="446px", key="725")
        # st_echarts(options=voltage_therm_graph, height="446px", key="726")
        # st_echarts(options=voltage_therm_graph, height="446px", key="727")
        # st_echarts(options=voltage_therm_graph, height="446px", key="728")
        # st_echarts(options=voltage_therm_graph, height="446px", key="729")
        # st_echarts(options=voltage_therm_graph, height="446px", key="730")
        # st_echarts(options=voltage_therm_graph, height="446px", key="741")
        # st_echarts(options=voltage_therm_graph, height="446px", key="742")
        # st_echarts(options=voltage_therm_graph, height="446px", key="743")
        # st_echarts(options=voltage_therm_graph, height="446px", key="744")
        # st_echarts(options=voltage_therm_graph, height="446px", key="745")
        # st_echarts(options=voltage_therm_graph, height="446px", key="746")
        # st_echarts(options=voltage_therm_graph, height="446px", key="747")
        # st_echarts(options=voltage_therm_graph, height="446px", key="748")
        # st_echarts(options=voltage_therm_graph, height="446px", key="749")
        # st_echarts(options=voltage_therm_graph, height="446px", key="750")
        # st_echarts(options=voltage_therm_graph, height="446px", key="761")
        # st_echarts(options=voltage_therm_graph, height="446px", key="762")
        # st_echarts(options=voltage_therm_graph, height="446px", key="763")
        # st_echarts(options=voltage_therm_graph, height="446px", key="764")
        # st_echarts(options=voltage_therm_graph, height="446px", key="765")
        # st_echarts(options=voltage_therm_graph, height="446px", key="766")
        # st_echarts(options=voltage_therm_graph, height="446px", key="767")
        # st_echarts(options=voltage_therm_graph, height="446px", key="768")
        # st_echarts(options=voltage_therm_graph, height="446px", key="769")
        # st_echarts(options=voltage_therm_graph, height="446px", key="770")
        # st_echarts(options=voltage_therm_graph, height="446px", key="781")
        # st_echarts(options=voltage_therm_graph, height="446px", key="782")
        # st_echarts(options=voltage_therm_graph, height="446px", key="783")
        # st_echarts(options=voltage_therm_graph, height="446px", key="784")
        # st_echarts(options=voltage_therm_graph, height="446px", key="785")
        # st_echarts(options=voltage_therm_graph, height="446px", key="786")
        # st_echarts(options=voltage_therm_graph, height="446px", key="787")
        # st_echarts(options=voltage_therm_graph, height="446px", key="788")
        # st_echarts(options=voltage_therm_graph, height="446px", key="789")
        # st_echarts(options=voltage_therm_graph, height="446px", key="790")
        # st_echarts(options=voltage_therm_graph, height="446px", key="791")
        # st_echarts(options=voltage_therm_graph, height="446px", key="792")
        # st_echarts(options=voltage_therm_graph, height="446px", key="793")
        # st_echarts(options=voltage_therm_graph, height="446px", key="794")
        # st_echarts(options=voltage_therm_graph, height="446px", key="795")
        # st_echarts(options=voltage_therm_graph, height="446px", key="796")
        # st_echarts(options=voltage_therm_graph, height="446px", key="797")
        # st_echarts(options=voltage_therm_graph, height="446px", key="798")
        # st_echarts(options=voltage_therm_graph, height="446px", key="799")
        # st_echarts(options=voltage_therm_graph, height="446px", key="800")
        # st_echarts(options=voltage_therm_graph, height="446px", key="801")
        # st_echarts(options=voltage_therm_graph, height="446px", key="802")
        # st_echarts(options=voltage_therm_graph, height="446px", key="803")
        # st_echarts(options=voltage_therm_graph, height="446px", key="804")
        # st_echarts(options=voltage_therm_graph, height="446px", key="805")
        # st_echarts(options=voltage_therm_graph, height="446px", key="806")
        # st_echarts(options=voltage_therm_graph, height="446px", key="807")
        # st_echarts(options=voltage_therm_graph, height="446px", key="808")
        # st_echarts(options=voltage_therm_graph, height="446px", key="809")
        # st_echarts(options=voltage_therm_graph, height="446px", key="810")
        # st_echarts(options=voltage_therm_graph, height="446px", key="811")
        # st_echarts(options=voltage_therm_graph, height="446px", key="812")
        # st_echarts(options=voltage_therm_graph, height="446px", key="813")
        # st_echarts(options=voltage_therm_graph, height="446px", key="814")
        # st_echarts(options=voltage_therm_graph, height="446px", key="815")
        # st_echarts(options=voltage_therm_graph, height="446px", key="816")
        # st_echarts(options=voltage_therm_graph, height="446px", key="817")
        # st_echarts(options=voltage_therm_graph, height="446px", key="818")
        # st_echarts(options=voltage_therm_graph, height="446px", key="819")
        # st_echarts(options=voltage_therm_graph, height="446px", key="820")
        # st_echarts(options=voltage_therm_graph, height="446px", key="821")
        # st_echarts(options=voltage_therm_graph, height="446px", key="822")
        # st_echarts(options=voltage_therm_graph, height="446px", key="823")
        # st_echarts(options=voltage_therm_graph, height="446px", key="824")
        # st_echarts(options=voltage_therm_graph, height="446px", key="825")
        # st_echarts(options=voltage_therm_graph, height="446px", key="826")
        # st_echarts(options=voltage_therm_graph, height="446px", key="827")
        # st_echarts(options=voltage_therm_graph, height="446px", key="828")
        # st_echarts(options=voltage_therm_graph, height="446px", key="829")
        # st_echarts(options=voltage_therm_graph, height="446px", key="830")
        # st_echarts(options=voltage_therm_graph, height="446px", key="841")
        # st_echarts(options=voltage_therm_graph, height="446px", key="842")
        # st_echarts(options=voltage_therm_graph, height="446px", key="843")
        # st_echarts(options=voltage_therm_graph, height="446px", key="844")
        # st_echarts(options=voltage_therm_graph, height="446px", key="845")
        # st_echarts(options=voltage_therm_graph, height="446px", key="846")
        # st_echarts(options=voltage_therm_graph, height="446px", key="847")
        # st_echarts(options=voltage_therm_graph, height="446px", key="848")
        # st_echarts(options=voltage_therm_graph, height="446px", key="849")
        # st_echarts(options=voltage_therm_graph, height="446px", key="850")
        # st_echarts(options=voltage_therm_graph, height="446px", key="861")
        # st_echarts(options=voltage_therm_graph, height="446px", key="862")
        # st_echarts(options=voltage_therm_graph, height="446px", key="863")
        # st_echarts(options=voltage_therm_graph, height="446px", key="864")
        # st_echarts(options=voltage_therm_graph, height="446px", key="865")
        # st_echarts(options=voltage_therm_graph, height="446px", key="866")
        # st_echarts(options=voltage_therm_graph, height="446px", key="867")
        # st_echarts(options=voltage_therm_graph, height="446px", key="868")
        # st_echarts(options=voltage_therm_graph, height="446px", key="869")
        # st_echarts(options=voltage_therm_graph, height="446px", key="870")
        # st_echarts(options=voltage_therm_graph, height="446px", key="881")
        # st_echarts(options=voltage_therm_graph, height="446px", key="882")
        # st_echarts(options=voltage_therm_graph, height="446px", key="883")
        # st_echarts(options=voltage_therm_graph, height="446px", key="884")
        # st_echarts(options=voltage_therm_graph, height="446px", key="885")
        # st_echarts(options=voltage_therm_graph, height="446px", key="886")
        # st_echarts(options=voltage_therm_graph, height="446px", key="887")
        # st_echarts(options=voltage_therm_graph, height="446px", key="888")
        # st_echarts(options=voltage_therm_graph, height="446px", key="889")
        # st_echarts(options=voltage_therm_graph, height="446px", key="890")
        # st_echarts(options=voltage_therm_graph, height="446px", key="891")
        # st_echarts(options=voltage_therm_graph, height="446px", key="892")
        # st_echarts(options=voltage_therm_graph, height="446px", key="893")
        # st_echarts(options=voltage_therm_graph, height="446px", key="894")
        # st_echarts(options=voltage_therm_graph, height="446px", key="895")
        # st_echarts(options=voltage_therm_graph, height="446px", key="896")
        # st_echarts(options=voltage_therm_graph, height="446px", key="897")
        # st_echarts(options=voltage_therm_graph, height="446px", key="898")
        # st_echarts(options=voltage_therm_graph, height="446px", key="899")
        # st_echarts(options=voltage_therm_graph, height="446px", key="900")
        # st_echarts(options=voltage_therm_graph, height="446px", key="901")
        # st_echarts(options=voltage_therm_graph, height="446px", key="902")
        # st_echarts(options=voltage_therm_graph, height="446px", key="903")
        # st_echarts(options=voltage_therm_graph, height="446px", key="904")
        # st_echarts(options=voltage_therm_graph, height="446px", key="905")
        # st_echarts(options=voltage_therm_graph, height="446px", key="906")
        # st_echarts(options=voltage_therm_graph, height="446px", key="907")
        # st_echarts(options=voltage_therm_graph, height="446px", key="908")
        # st_echarts(options=voltage_therm_graph, height="446px", key="909")
        # st_echarts(options=voltage_therm_graph, height="446px", key="910")
        # st_echarts(options=voltage_therm_graph, height="446px", key="911")
        # st_echarts(options=voltage_therm_graph, height="446px", key="912")
        # st_echarts(options=voltage_therm_graph, height="446px", key="913")
        # st_echarts(options=voltage_therm_graph, height="446px", key="914")
        # st_echarts(options=voltage_therm_graph, height="446px", key="915")
        # st_echarts(options=voltage_therm_graph, height="446px", key="916")
        # st_echarts(options=voltage_therm_graph, height="446px", key="917")
        # st_echarts(options=voltage_therm_graph, height="446px", key="918")
        # st_echarts(options=voltage_therm_graph, height="446px", key="919")
        # st_echarts(options=voltage_therm_graph, height="446px", key="920")
        # st_echarts(options=voltage_therm_graph, height="446px", key="921")
        # st_echarts(options=voltage_therm_graph, height="446px", key="922")
        # st_echarts(options=voltage_therm_graph, height="446px", key="923")
        # st_echarts(options=voltage_therm_graph, height="446px", key="924")
        # st_echarts(options=voltage_therm_graph, height="446px", key="925")
        # st_echarts(options=voltage_therm_graph, height="446px", key="926")
        # st_echarts(options=voltage_therm_graph, height="446px", key="927")
        # st_echarts(options=voltage_therm_graph, height="446px", key="928")
        # st_echarts(options=voltage_therm_graph, height="446px", key="929")
        # st_echarts(options=voltage_therm_graph, height="446px", key="930")
        # st_echarts(options=voltage_therm_graph, height="446px", key="941")
        # st_echarts(options=voltage_therm_graph, height="446px", key="942")
        # st_echarts(options=voltage_therm_graph, height="446px", key="943")
        # st_echarts(options=voltage_therm_graph, height="446px", key="944")
        # st_echarts(options=voltage_therm_graph, height="446px", key="945")
        # st_echarts(options=voltage_therm_graph, height="446px", key="946")
        # st_echarts(options=voltage_therm_graph, height="446px", key="947")
        # st_echarts(options=voltage_therm_graph, height="446px", key="948")
        # st_echarts(options=voltage_therm_graph, height="446px", key="949")
        # st_echarts(options=voltage_therm_graph, height="446px", key="950")
        # st_echarts(options=voltage_therm_graph, height="446px", key="961")
        # st_echarts(options=voltage_therm_graph, height="446px", key="962")
        # st_echarts(options=voltage_therm_graph, height="446px", key="963")
        # st_echarts(options=voltage_therm_graph, height="446px", key="964")
        # st_echarts(options=voltage_therm_graph, height="446px", key="965")
        # st_echarts(options=voltage_therm_graph, height="446px", key="966")
        # st_echarts(options=voltage_therm_graph, height="446px", key="967")
        # st_echarts(options=voltage_therm_graph, height="446px", key="968")
        # st_echarts(options=voltage_therm_graph, height="446px", key="969")
        # st_echarts(options=voltage_therm_graph, height="446px", key="970")
        # st_echarts(options=voltage_therm_graph, height="446px", key="981")
        # st_echarts(options=voltage_therm_graph, height="446px", key="982")
        # st_echarts(options=voltage_therm_graph, height="446px", key="983")
        # st_echarts(options=voltage_therm_graph, height="446px", key="984")
        # st_echarts(options=voltage_therm_graph, height="446px", key="985")
        # st_echarts(options=voltage_therm_graph, height="446px", key="986")
        # st_echarts(options=voltage_therm_graph, height="446px", key="987")
        # st_echarts(options=voltage_therm_graph, height="446px", key="988")
        # st_echarts(options=voltage_therm_graph, height="446px", key="989")
        # st_echarts(options=voltage_therm_graph, height="446px", key="990")
        # st_echarts(options=voltage_therm_graph, height="446px", key="991")
        # st_echarts(options=voltage_therm_graph, height="446px", key="992")
        # st_echarts(options=voltage_therm_graph, height="446px", key="993")
        # st_echarts(options=voltage_therm_graph, height="446px", key="994")
        # st_echarts(options=voltage_therm_graph, height="446px", key="995")
        # st_echarts(options=voltage_therm_graph, height="446px", key="996")
        # st_echarts(options=voltage_therm_graph, height="446px", key="997")
        # st_echarts(options=voltage_therm_graph, height="446px", key="998")
        # st_echarts(options=voltage_therm_graph, height="446px", key="999")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1000")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1001")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1002")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1003")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1004")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1005")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1006")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1007")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1008")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1009")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1010")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1011")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1012")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1013")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1014")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1015")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1016")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1017")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1018")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1019")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1020")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1021")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1022")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1023")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1024")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1025")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1026")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1027")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1028")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1029")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1030")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1041")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1042")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1043")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1044")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1045")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1046")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1047")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1048")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1049")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1050")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1061")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1062")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1063")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1064")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1065")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1066")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1067")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1068")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1069")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1070")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1081")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1082")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1083")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1084")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1085")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1086")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1087")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1088")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1089")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1090")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1091")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1092")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1093")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1094")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1095")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1096")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1097")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1098")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1099")
        # st_echarts(options=voltage_therm_graph, height="446px", key="1100")
        
       

    # Logging Settings section in right column
    with st.container(border=True):
        st.header("Logging Settings")
        logging_left_column, logging_right_column = st.columns(2)
        with logging_left_column:
            enum_selectbox(
                panel,
                label="Logging Mode",
                value=LoggingMode.OFF,
                disabled=panel.get_value("is_running", False),
                key="logging_mode",
            )
        with logging_right_column:
            left_sub_column, right_sub_column = st.columns([3, 1])
            with left_sub_column:
                tdms_file_path = st.text_input(
                    label="TDMS File Path",
                    disabled=panel.get_value("is_running", False),
                    value="data.tdms",
                    key="tdms_file_path",
                )
