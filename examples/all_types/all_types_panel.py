"""A Streamlit visualization panel for the all_types.py example script."""

from enum import Enum
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
        if isinstance(all_types_with_values[name], Enum):
            nipanel.enum_selectbox(panel, label=name, value=cast(Enum, default_value), key=name)
        elif isinstance(all_types_with_values[name], bool):
            st.checkbox(label=name, value=cast(bool, default_value), key=name)
        elif isinstance(all_types_with_values[name], int):
            st.number_input(label=name, value=cast(int, default_value), key=name)
        elif isinstance(all_types_with_values[name], float):
            st.number_input(label=name, value=cast(float, default_value), key=name, format="%.2f")
        elif isinstance(all_types_with_values[name], str):
            st.text_input(label=name, value=cast(str, default_value), key=name)

    with col3:
        st.write(panel.get_value(name))
