"""Continuously acquires waveforms from NI-SCOPE, processes/scales them."""

import argparse
import niscope
import numpy as np
import sys
import nipanel
from pathlib import Path
import time
import hightime

panel_script_path = Path(__file__).with_name("niscope_panel.py")
panel = nipanel.create_panel(panel_script_path)

print(f"Panel URL: {panel.panel_url}")

def example(resource_name, channels, options, length, samples_per_fetch,):
    with niscope.Session(resource_name=resource_name, options=options) as session:
        session.configure_vertical(range=2, coupling=niscope.VerticalCoupling.DC, enabled=True)
        session.configure_horizontal_timing(min_sample_rate=100000000, min_num_pts=1000, ref_position=50.0, num_records=1000, enforce_realtime=True)
        session.configure_trigger_software()
        
        with session.initiate():
            wfm = np.ndarray(length * samples_per_fetch, dtype=np.int8)
            waveforms = session.channels[channels].fetch_into(relative_to=niscope.FetchRelativeTo.READ_POINTER,
                                                             offset=0, timeout=hightime.timedelta(seconds=5.0), waveform=wfm)
            try:
                print(f"\nPress Ctrl + C to stop")
                while True:
                        offset = session._fetch_offset
                        gain = session.meas_array_gain
                        for i in range(len(waveforms)):
                            time.sleep(0.5)
                            amplitude_list = []
                            total_data = waveforms[i].samples.tolist()
                            for amplitude in total_data:
                                amplitude = (amplitude * 10) * gain + offset 
                                amplitude_list.append(amplitude)
                            panel.set_value("Waveform", amplitude_list)

            except KeyboardInterrupt:
                 pass
            
def _main(argsv):
    parser = argparse.ArgumentParser(description='Fetches data directly into a preallocated numpy array.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-n', '--resource-name', default='Dev2', help='Resource name of an NI digitizer.')
    parser.add_argument('-c', '--channels', default='0', help='Channel(s) to use')
    parser.add_argument('-op', '--option-string', default='', type=str, help='Option string')
    parser.add_argument('-l', '--length', default=1000, type=int, help='Measure record length')
    parser.add_argument(
        "-s", "--samples-per-fetch", default=1000, type=int, help="Samples per fetch"
    )
    args = parser.parse_args(argsv)
    example(args.resource_name, 
        args.channels, 
        args.option_string, 
        args.length, 
        args.samples_per_fetch)

def main():
    _main(sys.argv[1:])

def test_example():
    options = {'simulate': True, 'driver_setup': {'Model': '5124', 'BoardType': 'PXI', }, }
    example("Dev2", options, 1, 1.0, 1000)

def test_main():
    cmd_line = ['--option-string', 'Simulate=1, DriverSetup=Model:5124; BoardType:PXI', ]
    _main(cmd_line)

if __name__ == '__main__':
    main()

