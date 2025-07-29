"""Core package for the CC Diagnostics tool."""

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "diagnostics",
    "output_parser",
    "report_renderer",
]

from . import diagnostics, output_parser, report_renderer  # noqa: E402
