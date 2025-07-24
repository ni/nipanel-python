"""Data acquisition script that continuously acquires analog input data."""

from pathlib import Path

import nidaqmx
from nidaqmx.constants import (
    AcquisitionType,
    CurrentShuntResistorLocation,
    CurrentUnits,
    Edge,
    LoggingMode,
    LoggingOperation,
    Slope,
)
from settings import AnalogPause, PauseWhen

import nipanel

panel_script_path = Path(__file__).with_name("nidaqmx_current_panel.py")
panel = nipanel.create_panel(panel_script_path)
panel.set_value("is_running", False)
try:
    print(f"Panel URL: {panel.panel_url}")
    print(f"Waiting for the 'Run' button to be pressed...")
    print(f"(Press Ctrl + C to quit)")
    while True:
        while not panel.get_value("run_button", False):
            panel.set_value("is_running", False)
        panel.set_value("is_running", True)
        panel.set_value("stop_button", False)

        # How to use nidaqmx: https://nidaqmx-python.readthedocs.io/en/stable/
        with nidaqmx.Task() as task:

            chan = task.ai_channels.add_ai_current_chan(
                "Mod3/ai10",
                max_val=panel.get_value("max_value_current", 0.01),
                min_val=panel.get_value("min_value_current", -0.01),
                ext_shunt_resistor_val=panel.get_value("shunt_resistor_value", 249.0),
                shunt_resistor_loc=panel.get_value(
                    "shunt_location", CurrentShuntResistorLocation.EXTERNAL
                ),
            )

            task.timing.cfg_samp_clk_timing(
                rate=panel.get_value("rate", 1000.0),
                sample_mode=AcquisitionType.CONTINUOUS,
                samps_per_chan=panel.get_value("num_of_samps", 1000),
            )
            panel.set_value("sample_rate", task._timing.samp_clk_rate)

            task.in_stream.configure_logging(
                file_path=panel.get_value("tdms_file_path", "data.tdms"),
                logging_mode=panel.get_value("logging_mode", LoggingMode.OFF),
                operation=LoggingOperation.OPEN_OR_CREATE,
            )
            trigger_type = panel.get_value("trigger_type")

            if trigger_type == "5":
                task.triggers.start_trigger.cfg_anlg_edge_start_trig(
                    trigger_source="APFI0",
                    trigger_slope=panel.get_value("slope", Slope.FALLING),
                    trigger_level=panel.get_value("level", 0.0),
                )

            if trigger_type == "2":
                task.triggers.start_trigger.cfg_dig_edge_start_trig(
                    trigger_source="/Dev2/PFI0", trigger_edge=panel.get_value("edge", Edge.FALLING)
                )
                task.triggers.start_trigger.anlg_edge_hyst = hysteresis = panel.get_value(
                    "hysteresis", 0.0
                )

            try:

                task.start()

                while not panel.get_value("stop_button", False):
                    data = task.read(
                        number_of_samples_per_channel=1000
                    )  # pyright: ignore[reportArgumentType]
                    panel.set_value("voltage_data", data)
                    panel.set_value("current_data", data)
                    panel.set_value("strain_data", data)

            except KeyboardInterrupt:
                pass
            finally:
                task.stop()
                panel.set_value("is_running", False)
                panel.set_value("run_button", False)


except KeyboardInterrupt:
    pass
