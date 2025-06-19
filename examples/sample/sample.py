"""This example demonstrates how to open/update a Streamlit application using nipanel package."""

import pathlib

import nipanel

script_path = pathlib.Path(__file__)
panel_script_path = str(script_path.with_name("sample_panel.py"))

panel = nipanel.StreamlitPanel(
    panel_id="sample_panel",
    streamlit_script_path=panel_script_path,
)
panel.set_value("sample_string", "Hello, World!")
panel.set_value("sample_int", 6)
panel.set_value("sample_float", 3.14)
panel.set_value("sample_bool", True)
panel.set_value("float_values", [1.1, 2.2, 3.3])

print(f"Panel URL: {panel.panel_url}")
