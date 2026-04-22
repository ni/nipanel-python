Prerequisites
===============
Requires a Physical or Simulated Device : https://github.com/ni/nidaqmx-python/blob/master/README.rst (Getting Started Section)

## Sample

This is a nipanel example that displays an interactive Streamlit app and updates continuous analog input samples while measuring and displaying the FFT Spectrum Magnitude.

### Feature

- Supports various data types

### Required Software

- Python 3.10 or later

### Usage

```pwsh
poetry install --with examples
poetry run python examples\nidaqmx\nidaqmx_analog_input_fft\nidaqmx_analog_input_fft.py
```
