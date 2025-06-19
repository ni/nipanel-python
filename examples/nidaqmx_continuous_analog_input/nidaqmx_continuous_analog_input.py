"""This is the logic that will read/set values to panel."""

import pathlib
import time

import nidaqmx

import nipanel

script_path = pathlib.Path(__file__)
panel_script_path = str(script_path.with_name("nidaqmx_continuous_analog_input_panel.py"))

panel = nipanel.StreamlitPanel(
    panel_id="nidaqmx_continuous_analog_input_panel",
    streamlit_script_path=panel_script_path,
)

data_arr = []
with nidaqmx.Task() as task:
    task.ai_channels.add_ai_voltage_chan("Mod1/ai2")
    task.ai_channels.add_ai_thrmcpl_chan("Mod1/ai3")
    try:
        total_read = 0
        while True:
            data = task.read(number_of_samples_per_channel=3)
            read = len(data)
            total_read += read

            data_arr.append(data)
            time.sleep(1)
            panel.set_value("amplitude", data_arr[-1][-1])
            panel.set_value("Volts", data_arr[-1][0])
    except KeyboardInterrupt:
        pass
    finally:
        task.stop()
        print(f"\nAcquired {total_read} total samples.")
