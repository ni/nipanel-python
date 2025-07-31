"""A Streamlit visualization panel for the all_types.py example script."""

import datetime as dt
from enum import Enum, Flag

import streamlit as st
from define_types import all_types_with_values

import nipanel
from nipanel.controls import enum_selectbox, flag_checkboxes


st.set_page_config(page_title="All Types Example", page_icon="📊", layout="wide")
st.title("All Types Example")

panel = nipanel.get_streamlit_panel_accessor()

col1, col2, col3 = st.columns([0.2, 0.2, 0.6])
with col1:
    st.header("Control or Type")
with col2:
    st.header("Input")
with col3:
    st.header("Output")

st.markdown("---")
col1, col2, col3 = st.columns([0.2, 0.2, 0.6])
with col1:
    st.write("st.selectbox")
with col2:
    st.selectbox(
        label="string",
        options=["Option 1", "Option 2", "Option 3", "Option 4"],
        key="example_selectbox",
    )
with col3:
    st.write(panel.get_value("example_selectbox", ""))

st.markdown("---")
col1, col2, col3 = st.columns([0.2, 0.2, 0.6])
with col1:
    st.write("st.slider & st.progress")
with col2:
    st.slider(
        label="int",
        min_value=0,
        max_value=100,
        value=50,
        key="example_slider",
    )
with col3:
    progress = panel.get_value("example_slider", 50)
    st.progress(progress / 100, text=f"{progress}%")


st.markdown("---")
col1, col2, col3 = st.columns([0.2, 0.2, 0.6])
with col1:
    st.write("st.color_picker")
with col2:
    st.color_picker(
        label="color",
        value="#000000",
        key="example_color_picker",
    )
with col3:
    color = panel.get_value("example_color_picker", "#000000")
    st.write(color)
    st.markdown(
        f"<div style='width:40px; height:20px; background:{color}; border:1px solid #888;'></div>",
        unsafe_allow_html=True,
    )

st.markdown("---")
col1, col2, col3 = st.columns([0.2, 0.2, 0.6])
with col1:
    st.write("st.multiselect")
with col2:
    st.multiselect(
        label="list of strings",
        options=["Option A", "Option B", "Option C", "Option D"],
        default=["Option A"],
        key="example_multiselect",
    )
with col3:
    st.write(panel.get_value("example_multiselect", ["Option A"]))

st.markdown("---")
col1, col2, col3 = st.columns([0.2, 0.2, 0.6])
with col1:
    st.write("st.radio")
with col2:
    st.radio(
        label="string",
        options=["Choice 1", "Choice 2", "Choice 3"],
        index=0,
        key="example_radio",
    )
with col3:
    st.write(panel.get_value("example_radio", "Choice 1"))

for name in all_types_with_values.keys():
    st.markdown("---")

    default_value = all_types_with_values[name]

    col1, col2, col3 = st.columns([0.2, 0.2, 0.6])
    with col1:
        st.write(name)

    with col2:
        if isinstance(default_value, bool):
            st.checkbox(label=name, value=default_value, key=name)
        elif isinstance(default_value, Flag):
            flag_checkboxes(panel, label=name, value=default_value, key=name)
        elif isinstance(default_value, Enum) and not isinstance(default_value, Flag):
            enum_selectbox(panel, label=name, value=default_value, key=name)
        elif isinstance(default_value, int) and not isinstance(default_value, Flag):
            st.number_input(label=name, value=default_value, key=name)
        elif isinstance(default_value, float):
            st.number_input(label=name, value=default_value, key=name, format="%.2f")
        elif isinstance(default_value, str):
            st.text_input(label=name, value=default_value, key=name)
        elif isinstance(default_value, dt.datetime):
            date = st.date_input(label="date", value=default_value)
            time = st.time_input(label="time", value=default_value)
            datetime = dt.datetime.combine(date, time)
            panel.set_value(name, datetime)

    with col3:
        st.write(panel.get_value(name, default_value=default_value))
