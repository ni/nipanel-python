"""This example demonstrates how to open/update a Streamlit application using nipanel package."""

from pathlib import Path

import nipanel

panel_script_path = Path(__file__).with_name("hello_panel.py")
panel = nipanel.create_panel(panel_script_path)

index = 0
while True:
    panel.set_value("hello_string", f"Hello, World! {index}")
    index += 1
    print(f"...{index}")

print(f"Panel URL: {panel.panel_url}")
