"""Data acquisition script that continuously acquires analog output data."""

import time
from pathlib import Path

import nidaqmx
import nidaqmx.stream_writers
import nidaqmx.system
import numpy as np
from nidaqmx.constants import AcquisitionType, Edge, Slope

import nipanel

panel_script_path = Path(__file__).with_name("nidaqmx_analog_output_voltage_panel.py")
panel = nipanel.create_streamlit_panel(panel_script_path)

system = nidaqmx.system.System.local()

available_channel_names = []
for dev in system.devices:
    for chan in dev.ao_physical_chans:
        available_channel_names.append(chan.name)
panel.set_value("available_channel_names", available_channel_names)

available_trigger_sources = []
for dev in system.devices:
    if hasattr(dev, "terminals"):
        for term in dev.terminals:
            available_trigger_sources.append(term)
panel.set_value("available_trigger_sources", available_trigger_sources)
try:
    print(f"Panel URL: {panel.panel_url}")
    print(f"Waiting for the 'Run' button to be pressed...")
    print(f"(Press Ctrl + C to quit)")
    while True:
        while not panel.get_value("run_button", False):
            panel.set_value("is_running", False)
            time.sleep(0.1)
        panel.set_value("is_running", True)
        panel.set_value("stop_button", False)

        # How to use nidaqmx: https://nidaqmx-python.readthedocs.io/en/stable/
        with nidaqmx.Task() as task:
            chan = task.ao_channels.add_ao_voltage_chan(
                panel.get_value("physical_channel", ""),
                max_val=panel.get_value("max_value_voltage", 5.0),
                min_val=panel.get_value("min_value_voltage", -5.0),
            )

            sample_rate = panel.get_value("rate", 1000.0)
            num_samples = panel.get_value("total_samples", 1000)
            frequency = panel.get_value("frequency", 10.0)
            amplitude = panel.get_value("amplitude", 1.0)

            task.timing.cfg_samp_clk_timing(
                rate=sample_rate,
                sample_mode=AcquisitionType.CONTINUOUS,
            )
            # Not all hardware supports all trigger types.
            # Refer to your device documentation for more information.
            trigger_type = panel.get_value("trigger_type")
            if trigger_type == "5":
                task.triggers.start_trigger.cfg_anlg_edge_start_trig(
                    trigger_source=panel.get_value("analog_source", ""),
                    trigger_slope=panel.get_value("slope", Slope.FALLING),
                    trigger_level=panel.get_value("level", 0.0),
                )
            if trigger_type == "2":
                task.triggers.start_trigger.cfg_dig_edge_start_trig(
                    trigger_source=panel.get_value("digital_source", ""),
                    trigger_edge=panel.get_value("edge", Edge.FALLING),
                )
                task.triggers.start_trigger.anlg_edge_hyst = hysteresis = panel.get_value(
                    "hysteresis", 0.0
                )

            panel.set_value("sample_rate", task.timing.samp_clk_rate)
            t = np.arange(num_samples) / sample_rate

            wave_type = panel.get_value("wave_type", "Sine Wave")

            if wave_type == "Sine Wave":
                waveform = amplitude * np.sin(2 * np.pi * frequency * t)
            elif wave_type == "Square Wave":
                waveform = amplitude * np.sign(np.sin(2 * np.pi * frequency * t))
            else:
                waveform = amplitude * (2 * np.abs(2 * (t * frequency % 1) - 1) - 1)

            writer = nidaqmx.stream_writers.AnalogSingleChannelWriter(
                task.out_stream, auto_start=False  # pyright: ignore[reportArgumentType]
            )
            writer.write_many_sample(waveform)
            panel.set_value("data", waveform.tolist())
            try:
                task.start()
                while not panel.get_value("stop_button", False):
                    time.sleep(0.1)

            except KeyboardInterrupt:
                break
            finally:
                task.stop()
                panel.set_value("is_running", False)
                panel.set_value("run_button", False)


except KeyboardInterrupt:
    pass
