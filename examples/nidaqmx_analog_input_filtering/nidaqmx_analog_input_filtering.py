"""Data acquisition script that continuously acquires analog input data."""

from pathlib import Path


import nidaqmx
from nidaqmx.constants import AcquisitionType, ExcitationSource, Edge, Slope
from settings_enum import DigitalEdge, PauseWhen, Slopes, AnalogPause
import nipanel
import time

panel_script_path = Path(__file__).with_name("nidaqmx_analog_input_filtering_panel.py")
panel = nipanel.create_panel(panel_script_path)



with nidaqmx.Task() as task:
    chan_voltage = task.ai_channels.add_ai_voltage_chan("Mod3/ai10")
    chan_strain_gage = task.ai_channels.add_ai_strain_gage_chan("Mod3/ai7", voltage_excit_source=ExcitationSource.EXTERNAL)
    chan_current = task.ai_channels.add_ai_current_chan("Mod3/ai9")
    task.timing.cfg_samp_clk_timing(
        rate = 1000.0, sample_mode = AcquisitionType.CONTINUOUS, samps_per_chan = 3000
    )
    
    task.timing.samp_clk_dig_fltr_min_pulse_width = 20.0e-6
    task.timing.samp_clk_dig_fltr_enable = True
    chan_voltage.ai_filter_response

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

            level = panel.get_value("level", 0.0)
            new_slope = Slopes(panel.get_value("slope",Slopes.FALLING.value))
            if slope != new_slope:
                task.stop()
                
                if new_slope == "Rising":
                    task.triggers.start_trigger.cfg_anlg_edge_start_trig(trigger_source="APFI0", trigger_level=level, trigger_slope= Slope.RISING)
                else:
                    task.triggers.start_trigger.cfg_anlg_edge_start_trig(trigger_source="APFI0", trigger_level=level, trigger_slope= Slope.FALLING)
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
            # task.triggers.start_trigger.cfg_dig_edge_start_trig(trigger_source="/Dev2/te1/SampleClock")
            # task.triggers.start_trigger.cfg_time_start_trig(10)
            # task.triggers.start_trigger.cfg_anlg_edge_start_trig(trigger_source="APFI0")
            # Configure a digital pause trigger (example)
            # Replace "PFI0" with your actual trigger source if needed
            
            # task.triggers.pause_trigger.trig_type = TriggerType.DIGITAL_LEVEL
            # task.triggers.pause_trigger.dig_lvl_src = "/Dev2/PFI0"
        
            # task.triggers.pause_trigger.dig_lvl_when 
            # task.triggers.pause_trigger.trig_type = TriggerType.ANALOG_LEVEL
            # task.triggers.pause_trigger.anlg_lvl_src
            # task.triggers.pause_trigger.anlg_lvl_when

            
            data = task.read(number_of_samples_per_channel=100)
            panel.set_value("voltage_data", data[0])
            panel.set_value("current_data", data[2])
            panel.set_value("strain_data", data[1])
            
    except KeyboardInterrupt:
        pass
    finally:
        task.stop()
       
