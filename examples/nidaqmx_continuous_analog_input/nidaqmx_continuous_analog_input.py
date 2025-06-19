"""Streamlit application script for displaying values from nidaqmx_continuous_analog_input.py"""

import pathlib

import nidaqmx
from nidaqmx.constants import AcquisitionType


import nipanel

script_path = pathlib.Path(__file__)
panel_script_path = str(script_path.with_name("nidaqmx_continuous_analog_input_panel.py"))

panel = nipanel.StreamlitPanel(
    panel_id="nidaqmx_continuous_analog_input_panel",
    streamlit_script_path=panel_script_path,

)

with nidaqmx.Task() as task:
    # User needs simulated hardware to run script, and user should use NI MAX to setup cDAQ1 Model NI 9201
    task.ai_channels.add_ai_voltage_chan("Mod1/ai2")
    task.ai_channels.add_ai_thrmcpl_chan("Mod1/ai3")
    task.timing.cfg_samp_clk_timing(
        rate=1000.0,  # Sample rate in Hz
        sample_mode=AcquisitionType.CONTINUOUS,
        samps_per_chan=3000  # Buffer size per channel
    )
    task.start()
    try:
        total_read = 0
        while True:
            print(f"\nPress Ctrl + C to stop")
            data = task.read(number_of_samples_per_channel=1000)
            panel.set_value("voltage_data", data[0])
            panel.set_value("thermocouple_data", data[1])
    except KeyboardInterrupt:
        pass
    finally:
        task.stop()
