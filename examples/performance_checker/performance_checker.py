"""Example of using nipanel to display a sine wave graph using st_echarts."""

import math
import time
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

start_time = time.time()
for i in range(100):
    panel.set_value("time_points", time_points.tolist())
stop_time = time.time()
print(f"Average time to set 'time_points': {(stop_time - start_time) * 10:.2f} ms")

start_time = time.time()
for i in range(100):
    panel.set_value("amplitude", 1.0)
stop_time = time.time()
print(f"Average time to set 'amplitude': {(stop_time - start_time) * 10:.2f} ms")

start_time = time.time()
for i in range(100):
    panel.get_value("time_points", [0.0])
stop_time = time.time()
print(f"Average time to get 'time_points': {(stop_time - start_time) * 10:.2f} ms")

start_time = time.time()
for i in range(100):
    panel.get_value("amplitude", 1.0)
stop_time = time.time()
print(f"Average time to get 'amplitude': {(stop_time - start_time) * 10:.2f} ms")

start_time = time.time()
for i in range(100):
    panel.get_value("unset_value", 1.0)
stop_time = time.time()
print(f"Average time to get 'unset_value': {(stop_time - start_time) * 10:.2f} ms")

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
