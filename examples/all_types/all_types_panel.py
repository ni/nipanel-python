"""A Streamlit visualization panel for the all_types.py example script."""

import streamlit as st
from define_types import all_types_with_values

import nipanel


st.set_page_config(page_title="All Types Example", page_icon="📊", layout="wide")
st.title("All Types Example")

panel = nipanel.get_panel_accessor()
for name in all_types_with_values.keys():
    col1, col2 = st.columns([0.4, 0.6])

    with col1:
        st.write(name)

    with col2:
        st.write(panel.get_value(name))
