"""This example demonstrates how to open/update a Streamlit application using nipanel package."""

from pathlib import Path

import nipanel

panel_script_path = Path(__file__).with_name("hello_panel.py")
panel = nipanel.create_streamlit_panel(panel_script_path)

panel.set_value("hello_string", "Hello, World!")

print(f"Panel URL: {panel.panel_url}")
