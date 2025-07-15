"""Enumeration for amplitude values used in the simple graph example."""

import enum


class PauseWhen(enum.StrEnum):
    """Pause When Trigger Setting."""

    HIGH = "High"
    LOW = "Low"


class AnalogPause(enum.StrEnum):
    """Analog Pause Trigger."""

    ABOVE = "ABOVE"
    BELOW = "BELOW"
