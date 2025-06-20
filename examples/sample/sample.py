"""This example demonstrates how to open/update a Streamlit application using nipanel package."""

from pathlib import Path

import nipanel

panel_script_path = Path(__file__).with_name("sample_panel.py")
panel = nipanel.create_panel(panel_script_path)

panel.set_value("sample_string", "Hello, World!")
panel.set_value("sample_int", 42)
panel.set_value("sample_float", 3.14)
panel.set_value("sample_bool", True)
panel.set_value("float_values", [1.1, 2.2, 3.3])

print(f"Panel URL: {panel.panel_url}")
