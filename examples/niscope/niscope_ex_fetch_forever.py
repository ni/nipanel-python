"""Continuously acquires waveforms from NI-SCOPE, processes/scales them."""

import time
from pathlib import Path
from typing import Any

import hightime
import niscope
import numpy as np

import nipanel

panel_script_path = Path(__file__).with_name("niscope_ex_fetch_forever_panel.py")
panel = nipanel.create_streamlit_panel(panel_script_path)

print(f"Panel URL: {panel.panel_url}")

resource_name = "Dev1"
channels = 0
options = ""
length = 1000
samples_per_fetch = 1000

"""Example fetch data from device (Dev1)."""
with niscope.Session(resource_name=resource_name, options=options) as session:
    session.configure_vertical(range=2, coupling=niscope.VerticalCoupling.DC, enabled=True)
    session.configure_horizontal_timing(
        min_sample_rate=100000000,
        min_num_pts=1000,
        ref_position=50.0,
        num_records=1000,
        enforce_realtime=True,
    )
    session.configure_trigger_software()

    with session.initiate():
        wfm: np.ndarray[Any, np.dtype[np.int8]] = np.ndarray(
            length * samples_per_fetch, dtype=np.int8
        )
        waveforms = session.channels[channels].fetch_into(
            relative_to=niscope.FetchRelativeTo.READ_POINTER,
            offset=0,
            timeout=hightime.timedelta(seconds=5.0),
            waveform=wfm,
        )
        try:
            print(f"Press Ctrl + C to stop")
            while True:
                offset = session.meas_array_offset
                gain = session.meas_array_gain
                for i in range(len(waveforms)):
                    time.sleep(0.2)
                    amplitude_list = []
                    total_data = waveforms[i].samples.tolist()
                    for amplitude in total_data:
                        amplitude = (amplitude * 10) * gain + offset
                        amplitude_list.append(amplitude)
                    panel.set_value("Waveform", amplitude_list)

        except KeyboardInterrupt:
            pass
