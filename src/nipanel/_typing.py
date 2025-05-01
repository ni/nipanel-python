"""Single source for typing backports to avoid depending on typing_extensions at run time."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Callable

if sys.version_info >= (3, 11):
    from typing import Self
elif TYPE_CHECKING:
    from typing_extensions import Self
else:
    Self = None

if TYPE_CHECKING:
    from typing_extensions import ParamSpec, TypeVar

    _P = ParamSpec("_P")
    _T = TypeVar("_T")
else:
    _P = None
    _T = None

__all__ = [
    "Callable",
    "Self",
    "_P",
    "_T",
]
