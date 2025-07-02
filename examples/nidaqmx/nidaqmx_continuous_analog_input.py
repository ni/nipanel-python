"""Data acquisition script that continuously acquires analog input data."""

import time
from pathlib import Path

import nidaqmx
from nidaqmx.constants import AcquisitionType, TerminalConfiguration

import nipanel

panel_script_path = Path(__file__).with_name("nidaqmx_continuous_analog_input_panel.py")
panel = nipanel.create_panel(panel_script_path)

try:
    print(f"Panel URL: {panel.panel_url}")
    print(f"Press Ctrl + C to quit")
    while True:
        print(f"Waiting for the 'Run' button to be pressed...")
        while not panel.get_value("run_button", False):
            time.sleep(0.1)

        panel.set_value("is_running", True)

        # How to use nidaqmx: https://nidaqmx-python.readthedocs.io/en/stable/
        with nidaqmx.Task() as task:
            task.ai_channels.add_ai_voltage_chan(
                physical_channel="Dev1/ai0",
                min_val=panel.get_value("voltage_min_value", -5.0),
                max_val=panel.get_value("voltage_max_value", 5.0),
                terminal_config=panel.get_value(
                    "terminal_configuration", TerminalConfiguration.DEFAULT
                ),
            )
            task.ai_channels.add_ai_thrmcpl_chan("Dev1/ai1")
            task.timing.cfg_samp_clk_timing(
                rate=1000.0, sample_mode=AcquisitionType.CONTINUOUS, samps_per_chan=3000
            )
            panel.set_value("sample_rate", task._timing.samp_clk_rate)
            try:
                print(f"Starting data acquisition...")
                task.start()
                while not panel.get_value("stop_button", False):
                    data = task.read(
                        number_of_samples_per_channel=1000  # pyright: ignore[reportArgumentType]
                    )
                    panel.set_value("voltage_data", data[0])
                    panel.set_value("thermocouple_data", data[1])
            except KeyboardInterrupt:
                raise
            finally:
                print(f"Stopping data acquisition...")
                task.stop()
                panel.set_value("is_running", False)

except KeyboardInterrupt:
    pass
