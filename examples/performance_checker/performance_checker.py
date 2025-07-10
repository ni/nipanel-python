"""Check the performance of get_value and set_value methods in nipanel."""

import math
import time
import timeit
from pathlib import Path

import numpy as np

import nipanel


panel_script_path = Path(__file__).with_name("performance_checker_panel.py")
panel = nipanel.create_panel(panel_script_path)

amplitude = 1.0
frequency = 1.0
num_points = 1000
time_points = np.linspace(0, num_points, num_points)
sine_values = amplitude * np.sin(frequency * time_points)


def _set_time_points():
    panel.set_value("time_points", time_points.tolist())


def _set_amplitude():
    panel.set_value("amplitude", amplitude)


def _get_time_points():
    panel.get_value("time_points", [0.0])


def _get_amplitude():
    panel.get_value("amplitude", 1.0)


def _get_unset_value():
    panel.get_value("unset_value", 1.0)


iterations = 100

set_time_points_time = timeit.timeit(_set_time_points, number=iterations) * 1000 / iterations
print(f"Average time to set 'time_points': {set_time_points_time:.2f} ms")

set_amplitude_time = timeit.timeit(_set_amplitude, number=iterations) * 1000 / iterations
print(f"Average time to set 'amplitude': {set_amplitude_time:.2f} ms")

get_time_points_time = timeit.timeit(_get_time_points, number=iterations) * 1000 / iterations
print(f"Average time to get 'time_points': {get_time_points_time:.2f} ms")

get_amplitude_time = timeit.timeit(_get_amplitude, number=iterations) * 1000 / iterations
print(f"Average time to get 'amplitude': {get_amplitude_time:.2f} ms")

get_unset_value_time = timeit.timeit(_get_unset_value, number=iterations) * 1000 / iterations
print(f"Average time to get 'unset_value': {get_unset_value_time:.2f} ms")

try:
    print(f"Panel URL: {panel.panel_url}")
    print("Press Ctrl+C to exit")

    # Generate and update the sine wave data as fast as possible
    while True:
        time_points = np.linspace(0, num_points, num_points)
        sine_values = amplitude * np.sin(frequency * time_points)

        panel.set_value("time_points", time_points.tolist())
        panel.set_value("sine_values", sine_values.tolist())
        panel.set_value("amplitude", amplitude)
        panel.set_value("frequency", frequency)

        # Slowly vary the frequency for a more dynamic visualization
        frequency = 1.0 + 0.5 * math.sin(time.time() / 5.0)

except KeyboardInterrupt:
    print("Exiting...")
