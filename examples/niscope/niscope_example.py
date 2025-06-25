import argparse
import niscope
import numpy as np
import pprint
import sys
import nipanel
from pathlib import Path
import time
import hightime

pp = pprint.PrettyPrinter(indent=4, width=80)
panel_script_path = Path(__file__).with_name("niscope_panel.py")
panel = nipanel.create_panel(panel_script_path)

def example(resource_name, channels, options, length, total_acquisition_time_in_seconds, voltage, sample_rate_in_hz, samples_per_fetch,):
    channels = [ch.strip() for ch in channels.split(",")]
    
    num_channels = len(channels)
    
    num_records = 1000
    total_num_wfms = num_channels * num_records
    current_pos = 0   
    
    with niscope.Session(resource_name=resource_name, options=options) as session:
        session.configure_vertical(range=2, coupling=niscope.VerticalCoupling.DC, enabled=True)
        session.configure_horizontal_timing(min_sample_rate=100000000, min_num_pts=1000, ref_position=50.0, num_records=num_records, enforce_realtime=True)
        session.configure_trigger_software()
        
        with session.initiate():
            wfm = np.ndarray(length * total_num_wfms, dtype=np.int8)
            waveforms = session.channels[channels].fetch_into( relative_to=niscope.FetchRelativeTo.READ_POINTER,
                                                              offset=0, timeout=hightime.timedelta(seconds=5.0), waveform=wfm)
            while True:
                    offset = session._fetch_offset
                    gain = session.meas_array_gain
                    
                    for i in range(len(waveforms)):
                        panel.set_value("length",wfm.tolist())
                        time.sleep(0.2)
                        amplitude_list = []
                        current_pos += samples_per_fetch
                        panel.set_value("samples", sample_rate_in_hz)               
                        total_data = waveforms[i].samples.tolist()
                        for amplitude in total_data:
                            amplitude = (amplitude * 10) * gain + offset
                            amplitude_list.append(amplitude)

                        panel.set_value("Waveform", amplitude_list)

def _main(argsv):
    parser = argparse.ArgumentParser(description='Fetches data directly into a preallocated numpy array.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-n', '--resource-name', default='Dev2', help='Resource name of an NI digitizer.')
    parser.add_argument('-c', '--channels', default='0', help='Channel(s) to use')
    parser.add_argument('-l', '--length', default=1000, type=int, help='Measure record length')
    parser.add_argument('-v', '--voltage', default=1.0, type=float, help='Voltage range (V)')
    parser.add_argument('-op', '--option-string', default='', type=str, help='Option string')
    parser.add_argument("-t", "--time", default=1, type=int, help="Time to sample (s)")
    parser.add_argument("-r", "--sample-rate", default=1000.0, type=float, help="Sample Rate (Hz)")
    parser.add_argument(
        "-s", "--samples-per-fetch", default=1000, type=int, help="Samples per fetch"
    )
    args = parser.parse_args(argsv)
    example(args.resource_name, 
        args.channels, 
        args.option_string, 
        args.length, 
        args.voltage, 
        args.time,
        args.sample_rate,
        args.samples_per_fetch)



def main():
    _main(sys.argv[1:])


def test_example():
    options = {'simulate': True, 'driver_setup': {'Model': '5124', 'BoardType': 'PXI', }, }
    example("Dev2", options, 1, 1.0, 1000.0, 1000)


def test_main():
    cmd_line = ['--option-string', 'Simulate=1, DriverSetup=Model:5124; BoardType:PXI', ]
    _main(cmd_line)


if __name__ == '__main__':
    main()

