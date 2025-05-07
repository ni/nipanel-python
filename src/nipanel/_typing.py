"""Version-specific compatibility shims for the standard `typing` module.

For `typing` symbols that require Python 3.10 or later, this submodule redirects to the standard
`typing` module (when appropriate), the `typing_extensions` package, or provides a minimial stub
implementation for run time. This allows us to use new typing features without littering the rest of
our code with conditionals or making our Python packages depend on `typing_extenions` at run time.

For `typing` symbols that are supported in Python 3.9, you do not need this submodule. Import these
symbols directly from the standard `typing` module.

This submodule is vendored in multiple packages (nitypes, nipanel, etc.) to avoid compatibility
breakage when upgrading these packages.

Do not add project-specific types to this submodule.

Many of these symbols are references to `None` at run time. Clients of this submodule should use
`from __future__ import annotations` to avoid parsing type hints at run time.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

if sys.version_info >= (3, 10):
    from typing import (
        Concatenate,
        ParamSpec,
        ParamSpecArgs,
        ParamSpecKwargs,
        TypeAlias,
        TypeGuard,
    )
elif TYPE_CHECKING:
    from typing_extensions import (
        Concatenate,
        ParamSpec,
        ParamSpecArgs,
        ParamSpecKwargs,
        TypeAlias,
        TypeGuard,
    )
else:
    Concatenate = ParamSpecArgs = ParamSpecKwargs = TypeAlias = TypeGuard = None

    def ParamSpec(  # noqa: D103, N802 - Missing docstring, wrong case
        name, *, bound=None, covariant=False, contravariant=False
    ):
        return None


if sys.version_info >= (3, 11):
    from typing import (
        LiteralString,
        Never,
        NotRequired,
        Required,
        Self,
        TypeVarTuple,
        Unpack,
        assert_never,
        assert_type,
        reveal_type,
    )
elif TYPE_CHECKING:
    from typing_extensions import (
        LiteralString,
        Never,
        NotRequired,
        Required,
        Self,
        TypeVarTuple,
        Unpack,
        assert_never,
        assert_type,
        reveal_type,
    )
else:
    LiteralString = Never = NotRequired = Required = Self = Unpack = None

    def assert_never(arg, /):  # noqa: D103 - Missing docstring in public function
        pass

    def assert_type(val, typ, /):  # noqa: D103 - Missing docstring in public function
        pass

    def reveal_type(obj, /):  # noqa: D103 - Missing docstring in public function
        pass

    def TypeVarTuple(name):  # noqa: D103, N802 - Missing docstring, wrong case
        return None


if sys.version_info >= (3, 12):
    from typing import TypeAliasType, override
elif TYPE_CHECKING:
    from typing_extensions import TypeAliasType, override
else:
    TypeAliasType = None

    def override(arg, /):  # noqa: D103 - Missing docstring in public function
        return arg


if sys.version_info >= (3, 13):
    from typing import ReadOnly, TypeIs
elif TYPE_CHECKING:
    from typing_extensions import ReadOnly, TypeIs
else:
    ReadOnly = TypeIs = None

__all__ = [
    "assert_never",
    "assert_type",
    "Concatenate",
    "LiteralString",
    "Never",
    "NotRequired",
    "override",
    "ParamSpec",
    "ParamSpecArgs",
    "ParamSpecKwargs",
    "ReadOnly",
    "Required",
    "reveal_type",
    "Self",
    "TypeAlias",
    "TypeAliasType",
    "TypeGuard",
    "TypeIs",
    "TypeVarTuple",
    "Unpack",
]
