"""This example demonstrates how to open/update a Streamlit application using nipanel package."""

import os

import nipanel

script_path = os.path.dirname(os.path.abspath(__file__))
panel_script_path = os.path.join(script_path, "sample_panel.py")

panel = nipanel.StreamlitPanel(
    panel_id="sample_panel",
    streamlit_script_uri=panel_script_path,
)
panel.open_panel()
panel.set_value("sample_string", "Hello, World!")
panel.set_value("sample_int", 42)
panel.set_value("sample_float", 3.14)
panel.set_value("sample_bool", True)

input("Press Enter to close the panel...")

panel.close_panel(reset=True)
