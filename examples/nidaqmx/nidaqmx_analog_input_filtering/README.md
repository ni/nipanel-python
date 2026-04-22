## Overview

This is a nipanel example that acquires a continuous amount of data with filters enabled using the DAQ device's internal clock and displays it in an interactive Streamlit app.

### Features

- NI-DAQmx Python configuration and acquisition
- Displays data in an interactive chart using ECharts
- Updates automatically as new data is acquired

### Prerequisites

- Python 3.10 or later
- A Physical or Simulated Device : https://github.com/ni/nidaqmx-python/blob/master/README.rst (Getting Started Section)

### Usage

```pwsh
poetry install --with examples
poetry run python examples\nidaqmx\nidaqmx_analog_input_filtering\nidaqmx_analog_input_filtering.py
```
