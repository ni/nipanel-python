"""Data acquisition script that continuously acquires analog input data."""

import time
from pathlib import Path

import nidaqmx
from nidaqmx.constants import (
    AcquisitionType,
    CJCSource,
    LoggingMode,
    LoggingOperation,
    TemperatureUnits,
    TerminalConfiguration,
    ThermocoupleType,
)
from nidaqmx.errors import DaqError

import nipanel

panel_script_path = Path(__file__).with_name("nidaqmx_continuous_analog_input_panel.py")
panel = nipanel.create_streamlit_panel(panel_script_path)

try:
    panel.set_value("daq_error", "")

    print(f"Panel URL: {panel.panel_url}")
    print(f"Waiting for the 'Run' button to be pressed...")
    print(f"(Press Ctrl + C to quit)")
    while True:
        panel.set_value("run_button", False)
        while not panel.get_value("run_button", False):
            time.sleep(0.1)

        # How to use nidaqmx: https://nidaqmx-python.readthedocs.io/en/stable/
        with nidaqmx.Task() as task:
            task.ai_channels.add_ai_voltage_chan(
                physical_channel="Dev4/ai0",
                min_val=panel.get_value("voltage_min_value", -5.0),
                max_val=panel.get_value("voltage_max_value", 5.0),
                terminal_config=panel.get_value(
                    "terminal_configuration", TerminalConfiguration.DEFAULT
                ),
            )
            task.ai_channels.add_ai_thrmcpl_chan(
                "Dev4/ai1",
                min_val=panel.get_value("thermocouple_min_value", 0.0),
                max_val=panel.get_value("thermocouple_max_value", 100.0),
                units=panel.get_value("thermocouple_units", TemperatureUnits.DEG_C),
                thermocouple_type=panel.get_value("thermocouple_type", ThermocoupleType.K),
                cjc_source=panel.get_value(
                    "thermocouple_cjc_source", CJCSource.CONSTANT_USER_VALUE
                ),
                cjc_val=panel.get_value("thermocouple_cjc_val", 25.0),
            )
            task.timing.cfg_samp_clk_timing(
                rate=panel.get_value("sample_rate_input", 1000.0),
                sample_mode=AcquisitionType.CONTINUOUS,
                samps_per_chan=panel.get_value("samples_per_channel", 3000),
            )
            task.in_stream.configure_logging(
                file_path=panel.get_value("tdms_file_path", "data.tdms"),
                logging_mode=panel.get_value("logging_mode", LoggingMode.OFF),
                operation=LoggingOperation.OPEN_OR_CREATE,
            )
            panel.set_value("sample_rate", task.timing.samp_clk_rate)
            try:
                print(f"Starting data acquisition...")
                task.start()
                panel.set_value("is_running", True)

                panel.set_value("stop_button", False)
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

except DaqError as e:
    daq_error = str(e)
    print(daq_error)
    panel.set_value("daq_error", daq_error)
except KeyboardInterrupt:
    pass
