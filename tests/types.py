"""Types that support conversion to and from protobuf."""

import enum


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


class MyStrEnum(enum.StrEnum):
    """Example of a StrEnum enum."""

    VALUE1 = "value1"
    VALUE2 = "value2"
    VALUE3 = "value3"
