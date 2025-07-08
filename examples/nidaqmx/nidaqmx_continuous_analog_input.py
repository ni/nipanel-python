"""Data acquisition script that continuously acquires analog input data."""

from pathlib import Path

import nidaqmx
from nidaqmx.constants import AcquisitionType

import nipanel

panel_script_path = Path(__file__).with_name("nidaqmx_continuous_analog_input_panel.py")
panel = nipanel.create_panel(panel_script_path)

with nidaqmx.Task() as task:
    task.ai_channels.add_ai_voltage_chan("Mod1/ai0")
    task.ai_channels.add_ai_thrmcpl_chan("Mod1/ai1")
    task.timing.cfg_samp_clk_timing(
        rate=1000.0, sample_mode=AcquisitionType.CONTINUOUS, samps_per_chan=3000
    )
    panel.set_value("sample_rate", task._timing.samp_clk_rate)
    task.start()
    try:
        print(f"\nPress Ctrl + C to stop")
        while True:
            data = task.read(number_of_samples_per_channel=1000)
            panel.set_value("voltage_data", data[0])
            panel.set_value("thermocouple_data", data[1])
    except KeyboardInterrupt:
        pass
    finally:
        task.stop()
