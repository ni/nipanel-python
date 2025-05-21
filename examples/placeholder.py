"""Placeholder example for the package."""

import enum

import nipanel


class MyIntFlags(enum.IntFlag):
    """Example of an IntFlag enum."""

    VALUE1 = 1
    VALUE2 = 2
    VALUE4 = 4


class MyIntEnum(enum.IntEnum):
    """Example of an IntEnum enum."""

    VALUE10 = 10
    VALUE20 = 20
    VALUE30 = 30


class MyStrEnum(str, enum.Enum):
    """Example of a mixin string enum."""

    VALUE1 = "value1"
    VALUE2 = "value2"
    VALUE3 = "value3"


if __name__ == "__main__":
    my_panel = nipanel.StreamlitPanel(
        panel_id="placeholder",
        streamlit_script_uri=__file__,
    )

    my_types = {
        "my_str": "im justa smol str",
        "my_int": 42,
        "my_float": 13.12,
        "my_bool": True,
        "my_bytes": b"robotext",
        "my_intflags": MyIntFlags.VALUE1 | MyIntFlags.VALUE4,
        "my_intenum": MyIntEnum.VALUE20,
        "my_strenum": MyStrEnum.VALUE3,
    }

    print("Setting values")
    for name, value in my_types.items():
        print(f"{name:>15}   {value}")
        my_panel.set_value(name, value)

    print()
    print("Getting values")
    for name in my_types.keys():
        the_value = my_panel.get_value(name)
        print(f"{name:>15}   {the_value}")
