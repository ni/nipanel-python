"""Data acquisition script that continuously acquires analog input data."""

from pathlib import Path


import nidaqmx
from nidaqmx.constants import AcquisitionType, ExcitationSource, Edge, Slope, Timescale, TerminalConfiguration
from settings_enum import DigitalEdge, PauseWhen, Slopes, AnalogPause, TerminalConfig
import nipanel
import time

panel_script_path = Path(__file__).with_name("nidaqmx_analog_input_filtering_panel.py")
panel = nipanel.create_panel(panel_script_path)


with nidaqmx.Task() as task:
    terminal_config = TerminalConfig(panel.get_value("terminal_config", TerminalConfig.RSE.value))
    chan_voltage = task.ai_channels.add_ai_voltage_chan("Mod3/ai10", terminal_config=TerminalConfiguration.DEFAULT)
    chan_strain_gage = task.ai_channels.add_ai_strain_gage_chan("Mod3/ai7", voltage_excit_source=ExcitationSource.EXTERNAL, max_val=0.001, min_val=-0.001)
    chan_current = task.ai_channels.add_ai_current_chan("Mod3/ai9", max_val = 0.01, min_val= -0.01, ext_shunt_resistor_val=249)
    task.timing.cfg_samp_clk_timing(
        rate = 1000.0, sample_mode = AcquisitionType.CONTINUOUS, samps_per_chan = 1000
    )

    task.timing.samp_clk_dig_fltr_min_pulse_width = 20.0e-6
    task.timing.samp_clk_dig_fltr_enable = True
    chan_voltage.ai_filter_response
    filter = panel.get_value("filter", "No Filtering")
    if filter == "No Filtering":
        chan_voltage.ai_filter_freq = 0.0
        chan_current.ai_filter_freq = 0.0
        chan_strain_gage.ai_filter_freq = 0.0

        chan_voltage.ai_filter_order = 0
        chan_current.ai_filter_order = 0
        chan_strain_gage.ai_filter_order = 0

        chan_voltage.ai_filter_response = panel.get_value("filter_response", "Comb")
        chan_current.ai_filter_response = panel.get_value("filter_response", "Comb")
        chan_strain_gage.ai_filter_response = panel.get_value("filter_response", "Comb")
    else:
        chan_voltage.ai_filter_freq = panel.get_value("filter_freq", 1000.0)
        chan_current.ai_filter_freq = panel.get_value("filter_freq", 1000.0)
        chan_strain_gage.ai_filter_freq = panel.get_value("filter_freq", 1000.0)

        chan_voltage.ai_filter_order = panel.get_value("filter_order", 1)
        chan_current.ai_filter_order = panel.get_value("filter_order", 1)
        chan_strain_gage.ai_filter_order = panel.get_value("filter_order", 1)

        chan_voltage.ai_filter_response = panel.get_value("filter_response", "Comb")
        chan_current.ai_filter_response = panel.get_value("filter_response", "Comb")
        chan_strain_gage.ai_filter_response = panel.get_value("filter_response", "Comb")
    
  

    panel.set_value("source", [task.triggers.pause_trigger.dig_lvl_src])
    panel.set_value("analog_source", [task.triggers.start_trigger.anlg_edge_src])
   
    panel.set_value("sample_rate", task._timing.samp_clk_rate)

    slope = Slopes(panel.get_value("slope",Slopes.FALLING.value))

    if slope == "Rising":
        task.triggers.start_trigger.cfg_anlg_edge_start_trig(trigger_source="APFI0", trigger_level=0, trigger_slope= Slope.RISING)
    else:
        task.triggers.start_trigger.cfg_anlg_edge_start_trig(trigger_source="APFI0", trigger_level=0, trigger_slope= Slope.FALLING)

    digital_edge = DigitalEdge(panel.get_value("edge_digital", DigitalEdge.FALLING.value))
    if digital_edge == "RISING":
        task.triggers.start_trigger.cfg_dig_edge_start_trig(trigger_source="/Dev2/PFI0", trigger_edge=Edge.RISING)
    else:
        task.triggers.start_trigger.cfg_dig_edge_start_trig(trigger_source="/Dev2/PFI0", trigger_edge=Edge.FALLING)
    task.start()

    try:
        print(f"Press Ctrl + C to stop")
        
        while True:
            date = panel.get_value("date", None)
            time_input = panel.get_value("time", None)

            hysteriresis = panel.get_value("hysteriesis", 0.0)
            task.triggers.start_trigger.cfg_time_start_trig(when = date, timescale=Timescale.USE_HOST)
            level = panel.get_value("level", 0.0)
            new_slope = Slopes(panel.get_value("slope",Slopes.FALLING.value))
            if slope != new_slope:
                task.stop()
                
                if new_slope == "Rising":
                    task.triggers.start_trigger.cfg_anlg_edge_start_trig(trigger_source="APFI0", trigger_level=level, trigger_slope= Slope.RISING)
                else:
                    task.triggers.start_trigger.cfg_anlg_edge_start_trig(trigger_source="APFI0", trigger_level=level, trigger_slope= Slope.FALLING)
                task.triggers.start_trigger.anlg_edge_hyst = hysteriresis
                task.start()
                slope = new_slope
           
            analog_pause = AnalogPause(panel.get_value("analog_pause", AnalogPause.ABOVE.value))

            if analog_pause == "ABOVE":
                task.triggers.pause_trigger.anlg_lvl_when.ABOVE
            else:
                task.triggers.pause_trigger.anlg_lvl_when.BELOW


            pause_when = PauseWhen(panel.get_value("pause_when",PauseWhen.HIGH.value))
            if pause_when == "High":
                task.triggers.pause_trigger.dig_lvl_when.HIGH
            else:
                task.triggers.pause_trigger.dig_lvl_when.LOW

            new_edge = DigitalEdge(panel.get_value("edge_digital", DigitalEdge.FALLING.value))
            if new_edge != digital_edge:
                task.stop()
                if new_edge == "RISING":
                    task.triggers.start_trigger.cfg_dig_edge_start_trig(trigger_source="/Dev2/PFI0", trigger_edge=Edge.RISING)
                else:
                    task.triggers.start_trigger.cfg_dig_edge_start_trig(trigger_source="/Dev2/PFI0", trigger_edge=Edge.FALLING)
                task.start()
                digital_edge = new_edge
            
            
            task.triggers.start_trigger.cfg_dig_edge_start_trig
   
            data = task.read(number_of_samples_per_channel=100)
            panel.set_value("voltage_data", data[0])
            panel.set_value("current_data", data[2])
            panel.set_value("strain_data", data[1])
            
    except KeyboardInterrupt:
        pass
    finally:
        task.stop()
       
