"""Data acquisition script that continuously acquires analog input data."""

import os
import time
from pathlib import Path
from typing import cast

os.environ["NIDAQMX_ENABLE_WAVEFORM_SUPPORT"] = "1"
import nidaqmx  # noqa: E402 # Must import after setting os environment variable
import nidaqmx.system  # noqa: E402
import numpy as np  # noqa: E402
from nidaqmx.constants import (  # noqa: E402
    AcquisitionType,
    CJCSource,
    LoggingMode,
    LoggingOperation,
    TemperatureUnits,
    TerminalConfiguration,
    ThermocoupleType,
    UsageTypeAI,
)
from nidaqmx.errors import DaqError  # noqa: E402
from nitypes.waveform import AnalogWaveform  # noqa: E402

import nipanel  # noqa: E402

panel_script_path = Path(__file__).with_name("nidaqmx_continuous_analog_input_panel.py")
panel = nipanel.create_streamlit_panel(panel_script_path)
panel.set_value("is_running", False)

system = nidaqmx.system.System.local()

available_voltage_channels = []
available_thermocouple_channels = []
for dev in system.devices:
    for chan in dev.ai_physical_chans:
        if UsageTypeAI.VOLTAGE in chan.ai_meas_types:
            available_voltage_channels.append(chan.name)
        if UsageTypeAI.TEMPERATURE_THERMOCOUPLE in chan.ai_meas_types:
            available_thermocouple_channels.append(chan.name)
panel.set_value("available_voltage_channels", available_voltage_channels)
panel.set_value("available_thermocouple_channels", available_thermocouple_channels)

print(f"Panel URL: {panel.panel_url}")
print(f"Waiting for the 'Run' button to be pressed...")
print(f"(Press Ctrl + C to quit)")

try:
    while True:
        while not panel.get_value("is_running", False):
            time.sleep(0.1)

        print(f"Running...")
        try:
            # How to use nidaqmx: https://nidaqmx-python.readthedocs.io/en/stable/
            panel.set_value("daq_error", "")
            with nidaqmx.Task() as task:
                task.ai_channels.add_ai_voltage_chan(
                    physical_channel=panel.get_value("voltage_channel", ""),
                    min_val=panel.get_value("voltage_min_value", -5.0),
                    max_val=panel.get_value("voltage_max_value", 5.0),
                    terminal_config=panel.get_value(
                        "terminal_configuration", TerminalConfiguration.DEFAULT
                    ),
                )
                task.ai_channels.add_ai_thrmcpl_chan(
                    physical_channel=panel.get_value("thermocouple_channel", ""),
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

                    while panel.get_value("is_running", False):
                        waveforms = cast(
                            list[AnalogWaveform[np.float64]],
                            task.read_waveform(number_of_samples_per_channel=1000),
                        )
                        panel.set_value("voltage_waveform", waveforms[0])
                        panel.set_value("thermocouple_waveform", waveforms[1])
                except KeyboardInterrupt:
                    raise
                finally:
                    print(f"Stopping data acquisition...")
                    task.stop()
                    panel.set_value("is_running", False)
                    print(f"Stopped")

        except DaqError as e:
            daq_error = str(e)
            panel.set_value("daq_error", daq_error)
            panel.set_value("is_running", False)
            print(f"ERRORED")

except KeyboardInterrupt:
    pass
