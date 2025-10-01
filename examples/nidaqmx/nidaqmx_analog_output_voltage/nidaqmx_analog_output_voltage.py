"""Data acquisition script that continuously generates analog output data."""

import os
import time
from pathlib import Path

os.environ["NIDAQMX_ENABLE_WAVEFORM_SUPPORT"] = "1"
import hightime as ht  # noqa: E402
import nidaqmx  # noqa: E402 # Must import after setting os environment variable
import nidaqmx.stream_writers  # noqa: E402
import nidaqmx.system  # noqa: E402
import numpy as np  # noqa: E402
from nidaqmx.constants import AcquisitionType, Edge, UsageTypeAO  # noqa: E402
from nidaqmx.errors import DaqError  # noqa: E402
from nitypes.waveform import AnalogWaveform, SampleIntervalMode, Timing  # noqa: E402

import nipanel  # noqa: E402

panel_script_path = Path(__file__).with_name("nidaqmx_analog_output_voltage_panel.py")
panel = nipanel.create_streamlit_panel(panel_script_path)
panel.set_value("is_running", False)

system = nidaqmx.system.System.local()

available_channel_names = []
for dev in system.devices:
    for chan in dev.ao_physical_chans:
        if UsageTypeAO.VOLTAGE in chan.ao_output_types:
            available_channel_names.append(chan.name)
panel.set_value("available_channel_names", available_channel_names)

available_trigger_sources = [""]
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
        while not panel.get_value("is_running", False):
            time.sleep(0.1)

        print(f"Running...")
        try:
            # How to use nidaqmx: https://nidaqmx-python.readthedocs.io/en/stable/
            panel.set_value("daq_error", "")
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
                    source=panel.get_value("source", ""),  # "" - OnboardClock
                    rate=sample_rate,
                    sample_mode=AcquisitionType.CONTINUOUS,
                )
                # Not all hardware supports all trigger types.
                # Refer to your device documentation for more information.
                trigger_type = panel.get_value("trigger_type")

                if trigger_type == 2:
                    task.triggers.start_trigger.cfg_dig_edge_start_trig(
                        trigger_source=panel.get_value("digital_source", ""),
                        trigger_edge=panel.get_value("edge", Edge.FALLING),
                    )
                else:
                    pass

                panel.set_value("sample_rate", task.timing.samp_clk_rate)
                t = np.arange(num_samples) / sample_rate
                wave_type = panel.get_value("wave_type", "Sine Wave")

                if wave_type == "Sine Wave":
                    waveform = AnalogWaveform.from_array_1d(
                        amplitude * np.sin(2 * np.pi * frequency * t)
                    )
                elif wave_type == "Square Wave":
                    waveform = AnalogWaveform.from_array_1d(
                        amplitude * np.sign(np.sin(2 * np.pi * frequency * t))
                    )
                else:
                    waveform = AnalogWaveform.from_array_1d(
                        amplitude * (2 * np.abs(2 * (t * frequency % 1) - 1) - 1)
                    )
                waveform.timing = Timing(
                    sample_interval_mode=SampleIntervalMode.REGULAR,
                    sample_interval=ht.timedelta(seconds=1.0 / sample_rate),
                )
                waveform.units = chan.ao_voltage_units.name

                writer = nidaqmx.stream_writers.AnalogSingleChannelWriter(
                    task.out_stream, auto_start=False  # pyright: ignore[reportArgumentType]
                )
                writer.write_waveform(waveform)
                panel.set_value("waveform", waveform)
                try:
                    task.start()
                    while panel.get_value("is_running", False):
                        time.sleep(0.1)

                except KeyboardInterrupt:
                    break
                finally:
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
