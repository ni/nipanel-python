"""Data acquisition script that continuously acquires analog input data."""

import time
from pathlib import Path

import nidaqmx
import nidaqmx.system
from nidaqmx.constants import (
    AcquisitionType,
    CurrentShuntResistorLocation,
    CurrentUnits,
    Edge,
    ExcitationSource,
    FilterResponse,
    Slope,
    StrainGageBridgeType,
    TerminalConfiguration,
)
from nidaqmx.errors import DaqError

import nipanel

panel_script_path = Path(__file__).with_name("nidaqmx_analog_input_filtering_panel.py")
panel = nipanel.create_streamlit_panel(panel_script_path)
panel.set_value("is_running", False)

system = nidaqmx.system.System.local()

available_channel_names = []
for dev in system.devices:
    for chan in dev.ai_physical_chans:
        available_channel_names.append(chan.name)
panel.set_value("available_channel_names", available_channel_names)

available_trigger_sources = [""]
for dev in system.devices:
    if hasattr(dev, "terminals"):
        for term in dev.terminals:
            available_trigger_sources.append(term)
panel.set_value("available_trigger_sources", available_trigger_sources)
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

            chan_type = panel.get_value("chan_type", "1")

            if chan_type == "2":
                chan = task.ai_channels.add_ai_current_chan(
                    panel.get_value("physical_channel", ""),
                    max_val=panel.get_value("max_value_current", 0.01),
                    min_val=panel.get_value("min_value_current", -0.01),
                    ext_shunt_resistor_val=panel.get_value("shunt_resistor_value", 249.0),
                    shunt_resistor_loc=panel.get_value(
                        "shunt_location", CurrentShuntResistorLocation.EXTERNAL
                    ),
                    units=panel.get_value("units", CurrentUnits.AMPS),
                )

            elif chan_type == "3":
                chan = task.ai_channels.add_ai_strain_gage_chan(
                    panel.get_value("physical_channel", ""),
                    nominal_gage_resistance=panel.get_value("gage_resistance", 350.0),
                    voltage_excit_source=ExcitationSource.EXTERNAL,  # Only mode that works
                    max_val=panel.get_value("max_value_strain", 0.001),
                    min_val=panel.get_value("min_value_strain", -0.001),
                    poisson_ratio=panel.get_value("poisson_ratio", 0.3),
                    lead_wire_resistance=panel.get_value("wire_resistance", 0.0),
                    initial_bridge_voltage=panel.get_value("initial_voltage", 0.0),
                    gage_factor=panel.get_value("gage_factor", 2.0),
                    voltage_excit_val=panel.get_value("voltage_excitation_value", 0.0),
                    strain_config=panel.get_value(
                        "strain_configuration", StrainGageBridgeType.FULL_BRIDGE_I
                    ),
                )
            else:
                chan = task.ai_channels.add_ai_voltage_chan(
                    panel.get_value("physical_channel", ""),
                    terminal_config=panel.get_value(
                        "terminal_configuration", TerminalConfiguration.DEFAULT
                    ),
                    max_val=panel.get_value("max_value_voltage", 5.0),
                    min_val=panel.get_value("min_value_voltage", -5.0),
                )
            task.timing.cfg_samp_clk_timing(
                source=panel.get_value("source", ""),  # "" - means Onboard Clock (default value)
                rate=panel.get_value("rate", 1000.0),
                sample_mode=AcquisitionType.CONTINUOUS,
                samps_per_chan=panel.get_value("total_samples", 100),
            )
            panel.set_value("sample_rate", task.timing.samp_clk_rate)
            # Not all hardware supports all filter types.
            # Refer to your device documentation for more information.
            if panel.get_value("filter", "Filter") == "Filter":
                chan.ai_filter_enable = True
                chan.ai_filter_freq = panel.get_value("filter_freq", 0.0)
                chan.ai_filter_response = panel.get_value("filter_response", FilterResponse.COMB)
                chan.ai_filter_order = panel.get_value("filter_order", 1)
                panel.set_value("actual_filter_freq", chan.ai_filter_freq)
                panel.set_value("actual_filter_response", chan.ai_filter_response)
                panel.set_value("actual_filter_order", chan.ai_filter_order)
            else:
                panel.set_value("actual_filter_freq", 0.0)
                panel.set_value("actual_filter_response", FilterResponse.COMB)
                panel.set_value("actual_filter_order", 0)
            # Not all hardware supports all filter types.
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

            try:
                task.start()
                panel.set_value("is_running", True)

                panel.set_value("stop_button", False)
                while not panel.get_value("stop_button", False):
                    data = task.read(
                        number_of_samples_per_channel=100  # pyright: ignore[reportArgumentType]
                    )
                    panel.set_value("acquired_data", data)
            except KeyboardInterrupt:
                pass
            finally:
                task.stop()
                panel.set_value("is_running", False)

except DaqError as e:
    daq_error = str(e)
    print(daq_error)
    panel.set_value("daq_error", daq_error)

except KeyboardInterrupt:
    pass
