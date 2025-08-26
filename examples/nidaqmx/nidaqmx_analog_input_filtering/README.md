Prerequisites 
===============
Requires a Physical or Simulated Device. Refer to the [Getting Started Section](https://github.com/ni/nidaqmx-python/blob/master/README.rst) to learn how to create a simulated device. 
## Sample

This is an nipanel example that displays an interactive Streamlit app and updates and fetches data from device.

### Feature

Script demonstrates analog input data getting continuously acquired, and being filtered. 
- Supports various data types

### Required Software

- Python 3.9 or later

### Usage

```pwsh
poetry install --with examples
poetry run python examples\nidaqmx\nidaqmx_analog_input_filtering\nidaqmx_analog_input_filtering.py
```

