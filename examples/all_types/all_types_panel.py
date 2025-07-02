"""A Streamlit visualization panel for the all_types.py example script."""

from enum import Enum, Flag
from typing import cast

import streamlit as st
from define_types import all_types_with_values

import nipanel


st.set_page_config(page_title="All Types Example", page_icon="📊", layout="wide")
st.title("All Types Example")

panel = nipanel.get_panel_accessor()
for name in all_types_with_values.keys():
    st.markdown("---")

    default_value = all_types_with_values[name]
    col1, col2, col3 = st.columns([0.2, 0.2, 0.6])

    with col1:
        st.write(name)

    with col2:
        if isinstance(default_value, bool):
            st.checkbox(label=name, value=cast(bool, default_value), key=name)
        elif isinstance(default_value, Enum) and not isinstance(default_value, Flag):
            nipanel.enum_selectbox(panel, label=name, value=cast(Enum, default_value), key=name)
        elif isinstance(default_value, int) and not isinstance(default_value, Flag):
            st.number_input(label=name, value=cast(int, default_value), key=name)
        elif isinstance(default_value, float):
            st.number_input(label=name, value=cast(float, default_value), key=name, format="%.2f")
        elif isinstance(default_value, str):
            st.text_input(label=name, value=cast(str, default_value), key=name)

    with col3:
        value = panel.get_value(name)
        value_with_default = panel.get_value(name, default_value=default_value)
        st.write(value_with_default)
        if str(value) != str(value_with_default):
            st.write("(", value, ")")
