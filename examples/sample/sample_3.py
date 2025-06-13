"""This example demonstrates how to open/update a Streamlit application using nipanel package."""

import pathlib

import nipanel

script_path = pathlib.Path(__file__)
panel_script_path = str(script_path.with_name("sample_panel_3.py"))

panel = nipanel.StreamlitPanel(
    panel_id="sample_panel_3",
    streamlit_script_path=panel_script_path,
)
panel.set_value("sample_string", "Hello, World #3!")
panel.set_value("float_values", [1.1, 2.2, 3.3])

print(f"Panel URL: {panel.panel_url}")
