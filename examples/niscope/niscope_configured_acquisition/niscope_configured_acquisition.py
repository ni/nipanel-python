"""Continuously acquires waveforms from NI-SCOPE, processes/scales them."""

import time
from pathlib import Path
from typing import Any

import hightime
import niscope
import numpy as np
from niscope.errors import Error

import nipanel

panel_script_path = Path(__file__).with_name("niscope_configured_acquisition_panel.py")
panel = nipanel.create_streamlit_panel(panel_script_path)


panel.set_value("is_running", False)
panel.set_value("run_button", False)

try:
    panel.set_value("scope_error", "")
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
            session.configure_chan_characteristics(
                input_impedance=panel.get_value("input_impedance", 1.0e6),
                max_input_frequency=panel.get_value("max_input_frequency", 100.0e6),
            )
            session.configure_horizontal_timing(
                min_sample_rate=panel.get_value("min_sample_rate", 10.0e6),
                min_num_pts=panel.get_value("min_record_length", 1000),
                ref_position=panel.get_value("ref_position", 0.0),
                num_records=1000,
                enforce_realtime=panel.get_value("enforce_realtime", True),
            )
            trigger_type = int(panel.get_value("trigger_type", "1"))
            if trigger_type == 1:
                immediate = session.configure_trigger_immediate()
            elif trigger_type == 2:
                edge = session.configure_trigger_edge(
                    trigger_source=str(panel.get_value("edge_source", 0)),
                    level=panel.get_value("edge_level", 0.0),
                    slope=panel.get_value("edge_slope", niscope.TriggerSlope.POSITIVE),
                    trigger_coupling=panel.get_value("edge_coupling", niscope.TriggerCoupling.DC),
                    delay=hightime.timedelta(seconds=panel.get_value("digital_delay", 0.0)),
                )
            elif trigger_type == 3:
                digital = session.configure_trigger_digital(
                    trigger_source=panel.get_value("digital_source", "PFI 1"),
                    slope=panel.get_value("digital_slope", niscope.TriggerSlope.POSITIVE),
                    delay=hightime.timedelta(seconds=panel.get_value("digital_delay", 0.0)),
                )
            elif trigger_type == 4:
                window = session.configure_trigger_window(
                    trigger_source=str(panel.get_value("window_source", 0)),
                    window_mode=panel.get_value("window_mode", niscope.TriggerWindowMode.ENTERING),
                    low_level=panel.get_value("window_low_level", -0.1),
                    high_level=panel.get_value("window_high_level", 0.1),
                    trigger_coupling=panel.get_value("window_coupling", niscope.TriggerCoupling.DC),
                    delay=hightime.timedelta(seconds=panel.get_value("digital_delay", 0.0)),
                )
            else:
                hysteresis = session.configure_trigger_hysteresis(
                    trigger_source=str(panel.get_value("hysteresis_source", 0)),
                    level=panel.get_value("hysteresis_level", 0.0),
                    hysteresis=panel.get_value("hysteresis", 0.05),
                    slope=panel.get_value("hysteresis_slope", niscope.TriggerSlope.POSITIVE),
                    trigger_coupling=panel.get_value(
                        "hysteresis_coupling", niscope.TriggerCoupling.DC
                    ),
                    delay=hightime.timedelta(seconds=panel.get_value("digital_delay", 0.0)),
                )

            with session.initiate():
                wfm = np.array(
                    session.channels[panel.get_value("channel_number", 0)].fetch(
                        num_samples=1000,
                        num_records=1000,
                        relative_to=niscope.FetchRelativeTo.READ_POINTER,
                        offset=0,
                        timeout=hightime.timedelta(seconds=panel.get_value("timeout", 5.0)),
                    )
                )
                try:
                    panel.set_value("is_running", True)

                    panel.set_value("stop_button", False)
                    while not panel.get_value("stop_button", False):

                        for i in range(len(wfm)):
                            if panel.get_value("stop_button", True):
                                break
                            else:
                                data = wfm[i].samples.tolist()
                                panel.set_value("waveform_data", data)
                    panel.set_value("actual_record_length", session.horz_record_length)
                    panel.set_value("actual_sample_rate", session.samp_clk_timebase_rate)
                    panel.set_value("auto_triggered", session.trigger_auto_triggered)
                except KeyboardInterrupt:
                    pass
                finally:
                    panel.set_value("is_running", False)

except Error as e:
    scope_error = str(e)
    print(scope_error)
    panel.set_value("scope_error", scope_error)

except KeyboardInterrupt:
    pass
