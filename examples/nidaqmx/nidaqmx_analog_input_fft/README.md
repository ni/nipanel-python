## Overview

This is a nipanel example that displays an interactive Streamlit app and updates continuous analog input samples while measuring and displaying the FFT Spectrum Magnitude.

### Features

- NI-DAQmx Python configuration and acquisition
- Displays data in an interactive chart using ECharts
- Updates automatically as new data is acquired

### Prerequisites

- Python 3.10 or later
- InstrumentStudio 2026 Q1 or later
- A Physical or Simulated Device : https://github.com/ni/nidaqmx-python/blob/master/README.rst (Getting Started Section)

### Usage

```pwsh
poetry install --with examples
poetry run python examples\nidaqmx\nidaqmx_continuous_analog_input\nidaqmx_continuous_analog_input.py
```
