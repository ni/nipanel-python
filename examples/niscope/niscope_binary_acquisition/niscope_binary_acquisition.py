"""Continuously acquires waveforms from NI-SCOPE, processes/scales them."""

import time
from pathlib import Path
from typing import Any

import hightime
import niscope
import numpy as np
from niscope.enums import ArrayMeasurement
from niscope.errors import Error

import nipanel

panel_script_path = Path(__file__).with_name("niscope_binary_acquisition_panel.py")
panel = nipanel.create_streamlit_panel(panel_script_path)


"""Example fetch data from device (Dev1)."""
panel.set_value("is_running", False)
panel.set_value("run_button", False)

try:
    panel.set_value("daq_error", "")
    print(f"Panel URL: {panel.panel_url}")
    print(f"Waiting for the 'Run' button to be pressed...")
    print(f"(Press Ctrl + C to quit)")
    while True:
        panel.set_value("run_button", False)
        while not panel.get_value("run_button", False):
            time.sleep(0.1)
        with niscope.Session(resource_name=panel.get_value("resource_name", "Dev1")) as session:
            session.configure_vertical(
                range=panel.get_value("vertical_range", 5.0),
                coupling=niscope.VerticalCoupling.DC,
                offset=panel.get_value("vertical_offset", 0.0),
            )
            session.configure_horizontal_timing(
                min_sample_rate=panel.get_value("min_sample_rate", 200000000.0),
                min_num_pts=1000,
                ref_position=50.0,
                num_records=1000,
                enforce_realtime=True,
            )

            session.configure_trigger_immediate()

            with session.initiate():
                data_size = panel.get_value("data_size", 8)
                if data_size == 8:
                    wfm: np.ndarray[Any, np.dtype[np.int8]] = np.ndarray(  # type: ignore
                        1000 * 1000, dtype=np.int8
                    )
                elif data_size == 16:
                    wfm: np.ndarray[Any, np.dtype[np.int16]] = np.ndarray(  # type: ignore
                        1000 * 1000, dtype=np.int16
                    )
                else:
                    wfm: np.ndarray[Any, np.dtype[np.int32]] = np.ndarray(
                        1000 * 1000, dtype=np.int32
                    )

                waveforms = session.channels[panel.get_value("channel", 0)].fetch_into(
                    relative_to=niscope.FetchRelativeTo.READ_POINTER,
                    offset=0,
                    timeout=hightime.timedelta(seconds=5.0),
                    waveform=wfm,
                )

                try:
                    panel.set_value("is_running", True)

                    panel.set_value("stop_button", False)
                    while not panel.get_value("stop_button", False):
                        wfm_info = session.channels[0].fetch_array_measurement(
                            array_meas_function=ArrayMeasurement.ADD_CHANNELS,
                            num_records=1000,
                            meas_num_samples=1000,
                        )
                        gain = 0
                        offset = 0
                        for waveform in waveforms:
                            gain = waveform.gain
                            offset = waveform.offset
                            panel.set_value("gain_factor", gain)
                            panel.set_value("offset", offset)

                        for i in range(len(waveforms)):
                            if panel.get_value("stop_button", True):
                                break
                            else:
                                time.sleep(0.1)
                                binary_data = waveforms[i].samples.tolist()
                                panel.set_value("binary_data", waveforms[i].samples.tolist())

                                samples_array = np.array(binary_data)

                                voltage_values = samples_array * gain + offset
                                panel.set_value("scaled_voltage_data", voltage_values.tolist())

                    actual_binary_data_size = session.binary_sample_width
                    panel.set_value("actual_binary_data_size", actual_binary_data_size)
                except KeyboardInterrupt:
                    pass
                finally:
                    panel.set_value("is_running", False)

except Error as e:
    daq_error = str(e)
    print(daq_error)
    panel.set_value("daq_error", daq_error)

except KeyboardInterrupt:
    pass
