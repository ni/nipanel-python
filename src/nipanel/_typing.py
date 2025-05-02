"""Single source for typing backports to avoid depending on typing_extensions at run time."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

if sys.version_info >= (3, 11):
    from typing import Self
elif TYPE_CHECKING:
    from typing_extensions import Self
else:
    Self = None

if sys.version_info >= (3, 10):
    from typing import ParamSpec
elif TYPE_CHECKING:
    from typing_extensions import ParamSpec
else:
    from typing import TypeVar as ParamSpec

__all__ = [
    "Self",
    "ParamSpec",
]
