"""Define types."""

import datetime as dt
import enum

import numpy as np
from nitypes.scalar import Scalar
from nitypes.waveform import AnalogWaveform


class MyIntFlags(enum.IntFlag):
    """Example of an IntFlag enum."""

    VALUE1 = 1
    VALUE2 = 2
    VALUE4 = 4


class MyIntableFlags(enum.Flag):
    """Example of an Flag enum with int values."""

    VALUE8 = 8
    VALUE16 = 16
    VALUE32 = 32


class MyIntEnum(enum.IntEnum):
    """Example of an IntEnum enum."""

    VALUE10 = 10
    VALUE20 = 20
    VALUE30 = 30


class MyIntableEnum(enum.Enum):
    """Example of an enum with int values."""

    VALUE100 = 100
    VALUE200 = 200
    VALUE300 = 300


class MyStrEnum(str, enum.Enum):
    """Example of a mixin string enum."""

    VALUE1 = "value1"
    VALUE2 = "value2"
    VALUE3 = "value3"


class MyStringableEnum(enum.Enum):
    """Example of an enum with string values."""

    VALUE1 = "value1"
    VALUE2 = "value2"
    VALUE3 = "value3"


class MyMixedEnum(enum.Enum):
    """Example of an enum with mixed values."""

    VALUE1 = "value1"
    VALUE2 = 2
    VALUE3 = 3.0


all_types_with_values = {
    # supported scalar types
    "bool": True,
    "bytes": b"robotext",
    "float": 13.12,
    "int": 42,
    "str": "sample string",
    "dt_datetime": dt.datetime.now(),
    "dt_timedelta": dt.timedelta(weeks=2, days=5, minutes=12, milliseconds=75),
    # supported enum and flag types
    "intflags": MyIntFlags.VALUE1 | MyIntFlags.VALUE4,
    "intenum": MyIntEnum.VALUE20,
    "strenum": MyStrEnum.VALUE3,
    "intableenum": MyIntableEnum.VALUE200,
    "intableflags": MyIntableFlags.VALUE8 | MyIntableFlags.VALUE32,
    "stringableenum": MyStringableEnum.VALUE2,
    "mixedenum": MyMixedEnum.VALUE2,
    # NI types
    "nitypes_Scalar": Scalar(42, "m"),
    "nitypes_AnalogWaveform": AnalogWaveform.from_array_1d(np.array([1.0, 2.0, 3.0])),
    # supported collection types
    "bool_collection": [True, False, True],
    "bytes_collection": [b"one", b"two", b"three"],
    "float_collection": [1.1, 2.2, 3.3],
    "int_collection": [1, 2, 3],
    "str_collection": ["one", "two", "three"],
    "intflags_collection": [MyIntFlags.VALUE1, MyIntFlags.VALUE2, MyIntFlags.VALUE4],
    "intenum_collection": [MyIntEnum.VALUE10, MyIntEnum.VALUE20, MyIntEnum.VALUE30],
    "strenum_collection": [MyStrEnum.VALUE1, MyStrEnum.VALUE2, MyStrEnum.VALUE3],
    # supported collections
    "list": [1, 2, 3],
    "tuple": (4, 5, 6),
    "set": {7, 8, 9},
    "frozenset": frozenset([10, 11, 12]),
    # supported 2D collections
    "list_list_float": [[1.0, 2.0], [3.0, 4.0]],
    "tuple_tuple_float": ((1.0, 2.0), (3.0, 4.0)),
    "set_list_float": set([(1.0, 2.0), (3.0, 4.0)]),
    "frozenset_frozenset_float": frozenset([frozenset([1.0, 2.0]), frozenset([3.0, 4.0])]),
}
