"""This example demonstrates how to open/update a Streamlit application using nipanel package."""

import itertools
import math
import pathlib

import nipanel

script_path = pathlib.Path(__file__)
panel_script_path = str(script_path.with_name("sample_panel.py"))

panel = nipanel.StreamlitPanel(
    panel_id="sample_panel",
    streamlit_script_uri=panel_script_path,
)
panel.open_panel()
panel.set_value("sample_string", "Hello, World!")
panel.set_value("sample_int", 42)
panel.set_value("sample_float", 3.14)
panel.set_value("sample_bool", True)

x_values = [
    float(x) for x in itertools.takewhile(lambda p: p < 2 * math.pi, itertools.count(0, 0.05))
]
y_values = [math.sin(x) for x in x_values]
panel.set_value("x_values", x_values)
panel.set_value("y_values", y_values)

input("Press Enter to close the panel...")

panel.close_panel(reset=True)
