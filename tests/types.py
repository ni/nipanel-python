"""Types that exercise conversion to and from protobuf."""

import enum
import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:

    class StrEnum(str, enum.Enum):
        """Example of a mixin string enum."""

        pass


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


class MixinIntEnum(int, enum.Enum):
    """Example of an IntEnum using a mixin."""

    VALUE11 = 11
    VALUE22 = 22
    VALUE33 = 33


class MyStrEnum(StrEnum):
    """Example of a StrEnum enum."""

    VALUE1 = "value1"
    VALUE2 = "value2"
    VALUE3 = "value3"


class MixinStrEnum(str, enum.Enum):
    """Example of a StrEnum using a mixin."""

    VALUE11 = "value11"
    VALUE22 = "value22"
    VALUE33 = "value33"


class MyEnum(enum.Enum):
    """Example of a simple enum."""

    VALUE100 = 100
    VALUE200 = 200
    VALUE300 = 300


class MyFlags(enum.Flag):
    """Example of a simple flag."""

    VALUE8 = 8
    VALUE16 = 16
    VALUE32 = 32
