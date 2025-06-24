"""Example of using nipanel to display a sine wave graph using st_echarts."""

import math
import time
from pathlib import Path

import numpy as np

import nipanel


panel_script_path = Path(__file__).with_name("simple_graph_panel.py")
panel = nipanel.create_panel(panel_script_path)

amplitude = 1.0
frequency = 1.0
num_points = 100

try:
    print(f"Panel URL: {panel.panel_url}")
    print("Press Ctrl+C to exit")

    # Generate and update the sine wave data periodically
    while True:
        time_points = np.linspace(0, num_points, num_points)
        sine_values = amplitude * np.sin(frequency * time_points)

        panel.set_values(
            {
                "time_points": time_points.tolist(),
                "sine_values": sine_values.tolist(),
                "amplitude": amplitude,
                "frequency": frequency,
            }
        )

        # panel.set_value("time_points", time_points.tolist())
        # panel.set_value("sine_values", sine_values.tolist())
        # panel.set_value("amplitude", amplitude)
        # panel.set_value("frequency", frequency)

        # Slowly vary the frequency for a more dynamic visualization
        frequency = 1.0 + 0.5 * math.sin(time.time() / 5.0)
        time.sleep(1)

except KeyboardInterrupt:
    print("Exiting...")
