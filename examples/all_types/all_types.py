"""An example that demonstrates the supported data types for nipanel scripts."""

from pathlib import Path

from define_types import all_types_with_values

import nipanel

panel_script_path = Path(__file__).with_name("all_types_panel.py")
panel = nipanel.create_panel(panel_script_path)

print("Setting values")
for name, value in all_types_with_values.items():
    print(f"{name:>15}   {value}")
    panel.set_value(name, value)

print()
print("Getting values")
for name in all_types_with_values.keys():
    the_value = panel.get_value(name)
    print(f"{name:>20}   {the_value}")

print(f"Panel URL: {panel.panel_url}")
