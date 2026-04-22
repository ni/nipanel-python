"""Example of analog input voltage acquisition with a Fast Fourier Transform.

This example demonstrates how to acquire a continuous amount of data using the
DAQ device's internal clock. The settings are configured from the Streamlit
panel, and the acquired data is displayed on a graph. An FFT is computed from
the acquired data and displayed on a separate graph. Refer to the panel script
for details: nidaqmx_analog_input_fft_panel.py
"""

import time
from pathlib import Path
from typing import cast

import nidaqmx
import nidaqmx.system
import numpy as np
from nidaqmx.constants import (
    AcquisitionType,
    TerminalConfiguration,
    UsageTypeAI,
)
from nidaqmx.errors import DaqError
from nitypes.waveform import AnalogWaveform

import nipanel

panel_script_path = Path(__file__).with_name("nidaqmx_analog_input_fft_panel.py")
panel = nipanel.create_streamlit_panel(panel_script_path)
panel.set_value("is_running", False)

system = nidaqmx.system.System.local()

available_voltage_channels = []
for dev in system.devices:
    for chan in dev.ai_physical_chans:
        if UsageTypeAI.VOLTAGE in chan.ai_meas_types:
            available_voltage_channels.append(chan.name)
panel.set_value("available_voltage_channels", available_voltage_channels)

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
                task.timing.cfg_samp_clk_timing(
                    rate=panel.get_value("sample_rate_input", 1000.0),
                    sample_mode=AcquisitionType.CONTINUOUS,
                    samps_per_chan=panel.get_value("samples_per_channel", 100),
                )
                panel.set_value("sample_rate", task.timing.samp_clk_rate)
                try:
                    print(f"Starting data acquisition...")
                    samples_per_channel = panel.get_value("samples_per_channel", 100)
                    task.start()

                    while panel.get_value("is_running", False):
                        waveform = cast(
                            AnalogWaveform[np.float64],
                            task.read_waveform(number_of_samples_per_channel=samples_per_channel),
                        )
                        panel.set_value("voltage_waveform", waveform)

                        # calculate the Discrete Fourier Transform
                        fft = np.fft.fft(waveform.scaled_data)
                        dft_sample_freqs = np.fft.fftfreq(
                            waveform.sample_count, d=waveform.timing.sample_interval.total_seconds()
                        )

                        # convert to decibels
                        magnitudes = np.abs(fft)
                        normalized_magnitudes = magnitudes / np.max(magnitudes)
                        dbs = 20 * np.log10(normalized_magnitudes)

                        # only graph up to Nyquist
                        num_freqs_to_graph = samples_per_channel // 2
                        panel.set_value("fft_freqs", dft_sample_freqs[0:num_freqs_to_graph])
                        panel.set_value("fft_mags", dbs[0:num_freqs_to_graph])
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
