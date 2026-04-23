# NI-DAQmx Analog Input with FFT Example

### Overview

This is a nipanel example that acquires a continuous amount of data using the DAQ device's internal clock and graphs the acquired data in both the time domain and frequency domain in an interactive Streamlit panel.

### Features

- NI-DAQmx Python configuration and acquisition
- Displays data in an interactive chart using ECharts
- Updates automatically as new data is acquired

### Prerequisites

- Python 3.10 or later
- InstrumentStudio 2026 Q1 or later
- A physical or simulated device, refer to the [NI-DAQmx Python README (Getting Started section)](https://github.com/ni/nidaqmx-python/blob/master/README.rst#getting-started)

### Usage

```pwsh
poetry install --with examples
poetry run python examples\nidaqmx\nidaqmx_analog_input_fft\nidaqmx_analog_input_fft.py
```
