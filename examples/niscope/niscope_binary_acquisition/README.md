Prerequisites
===============
Requires a Physical or Simulated Device. Refer to the [Getting Started Section](https://github.com/ni/nidaqmx-python/blob/master/README.rst) to learn how to create a simulated device. This example uses NI oscilloscopes and digitizers like the NI PXIe-5114

## Sample

This is an nipanel example that displays an interactive Streamlit app and updates and fetches data from an NI device.

### Feature

Script demonstrates waveform data getting continuously acquired and being converted to binary data.
- Supports various data types

### Required Software

- Python 3.9 or later

### Usage

```pwsh
poetry install --with examples
poetry run examples\niscope\niscope_binary_acquisition\niscope_binary_acquisition.py
```
