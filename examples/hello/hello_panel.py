"""A Streamlit visualization panel for the hello.py example script."""

import streamlit as st

import nipanel


st.set_page_config(page_title="Hello World Example", page_icon="📊", layout="wide")
st.title("Hello World Example")

panel = nipanel.get_panel_accessor()
st.write(panel.get_value("hello_string", ""))
