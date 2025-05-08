"""Sphinx Configuration File."""

import datetime
import pathlib

import autoapi.extension
import toml

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "autoapi.extension",
    "m2r2",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

root_path = pathlib.Path(__file__).parent.parent
pyproj_file = root_path / "pyproject.toml"
proj_config = toml.loads(pyproj_file.read_text())


project = proj_config["tool"]["poetry"]["name"]
company = "National Instruments"
copyright = f"2025-%Y, {company}"
if datetime.datetime.now().year == 2025:
    copyright = f"%Y, {company}"


# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
version = proj_config["tool"]["poetry"]["version"]
release = ".".join(version.split(".")[:2])
description = proj_config["tool"]["poetry"]["description"]


htmlhelp_basename = f"{project}doc"


# tell autoapi to doc the public options
autoapi_options = list(autoapi.extension._DEFAULT_OPTIONS)
autoapi_options.remove("private-members")  # note: remove this to include "_" members in docs
autoapi_dirs = [root_path / "src" / "nipanel"]
autoapi_type = "python"
autodoc_typehints = "description"


# TODO: https://github.com/ni/nitypes-python/issues/16 - Update nitypes-python docs to use
# :canonical: to resolve aliases (once supported by sphinx-autoapi)
def skip_aliases(app, what, name, obj, skip, options):
    """Skip documentation for classes that are exported from multiple modules."""
    # For names that are defined in a private sub-module and aliased into a
    # public package, hide the definition.
    if name.startswith("nipanel._"):
        skip = True

    return skip


def setup(sphinx):
    """Sphinx setup callback."""
    sphinx.connect("autoapi-skip-member", skip_aliases)


# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# TODO: AB#3120159 - Update nipanel intersphinx mapping for nitypes
intersphinx_mapping = {
    "grpc": ("https://grpc.github.io/grpc/python/", None),
    "measurement-plugin-python": (
        "https://measurement-plugin-python.readthedocs.io/en/latest/",
        None,
    ),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "protobuf": ("https://googleapis.dev/python/protobuf/latest/", None),
    "python": ("https://docs.python.org/3", None),
}


# -- Options for HTML output ----------------------------------------------


# The theme to use for HTML and HTML Help pages. See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "navigation_depth": -1,
}

# Napoleon settings
napoleon_numpy_docstring = False
