"""Data acquisition script that continuously acquires analog input data."""

from pathlib import Path

import nidaqmx
from nidaqmx.constants import (
    AcquisitionType,
    CurrentShuntResistorLocation,
    CurrentUnits,
    Edge,
    ExcitationSource,
    FilterResponse,
    LoggingMode,
    LoggingOperation,
    Slope,
    StrainGageBridgeType,
    TerminalConfiguration,
)
from settings_enum import AnalogPause, PauseWhen

import nipanel

panel_script_path = Path(__file__).with_name("nidaqmx_analog_input_filtering_panel.py")
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
            chan_type = panel.get_value("chan_type", "1")
            if chan_type == "1":
                chan = task.ai_channels.add_ai_voltage_chan(
                    "Mod3/ai10",
                    terminal_config=panel.get_value(
                        "terminal_configuration", TerminalConfiguration.DEFAULT
                    ),
                    max_val=panel.get_value("max_value_voltage", 5.0),
                    min_val=panel.get_value("min_value_voltage", -5.0),
                )
                chan.ai_filter_freq = panel.get_value("filter_freq", 0.0)
                chan.ai_filter_response = panel.get_value("filter_response", FilterResponse.COMB)
                chan.ai_filter_order = 1

            elif chan_type == "2":
                chan = task.ai_channels.add_ai_current_chan(
                    "Mod3/ai10",
                    max_val=panel.get_value("max_value_current", 0.01),
                    min_val=panel.get_value("min_value_current", -0.01),
                    ext_shunt_resistor_val=panel.get_value("shunt_resistor_value", 249.0),
                    shunt_resistor_loc=panel.get_value(
                        "shunt_location", CurrentShuntResistorLocation.EXTERNAL
                    ),
                    units=panel.get_value("units", CurrentUnits.AMPS),
                )
                chan.ai_filter_freq = panel.get_value("filter_freq", 0.0)
                chan.ai_filter_response = panel.get_value("filter_response", FilterResponse.COMB)
                chan.ai_filter_order = 1

            elif chan_type == "3":
                chan = task.ai_channels.add_ai_strain_gage_chan(
                    "Mod3/ai10",
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

                chan.ai_filter_freq = panel.get_value("filter_freq", 0.0)
                chan.ai_filter_response = panel.get_value("filter_response", FilterResponse.COMB)
                chan.ai_filter_order = 1
            
            task.timing.cfg_samp_clk_timing(
                rate=panel.get_value("rate", 1000.0),
                sample_mode=AcquisitionType.CONTINUOUS,
                samps_per_chan=panel.get_value("total_samples", 100),
            )
            task.in_stream.configure_logging(
                file_path=panel.get_value("tdms_file_path", "data.tdms"),
                logging_mode=panel.get_value("logging_mode", LoggingMode.OFF),
                operation=LoggingOperation.OPEN_OR_CREATE,
            )

            trigger_type = panel.get_value("trigger_type")
            panel.set_value("sample_rate", task._timing.samp_clk_rate)
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
                task.triggers.start_trigger.anlg_edge_hyst =  hysteresis = panel.get_value(
                    "hysteresis", 0.0
                )

            try:

                task.start()

                while not panel.get_value("stop_button", False):
                    data = task.read(number_of_samples_per_channel=100)
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
