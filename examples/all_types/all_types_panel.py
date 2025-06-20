"""A Streamlit panel to demonstrate various types and their values."""

import streamlit as st
from define_types import all_types_with_values

import nipanel

panel = nipanel.initialize_panel()

st.title("All Types")

for name in all_types_with_values.keys():
    col1, col2 = st.columns([0.4, 0.6])

    with col1:
        st.write(name)

    with col2:
        st.write(panel.get_value(name))
