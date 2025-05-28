import nipanel
import os

script_path = os.path.dirname(os.path.abspath(__file__))
panel_script_path = os.path.join(script_path, "sample_panel.py")

panel = nipanel.StreamlitPanel(
    panel_id="sample_panel",
    streamlit_script_uri=panel_script_path,
)
panel.set_value("sample_string", "Hello, World!")
panel.set_value("sample_int", 42)
panel.set_value("sample_float", 3.14)
panel.set_value("sample_bool", True)
panel.open_panel()

input("Press Enter to close the panel...")

panel.close_panel(reset=True)