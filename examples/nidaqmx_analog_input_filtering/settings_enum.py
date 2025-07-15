"""Enumeration for amplitude values used in the simple graph example."""

import enum


class PauseWhen(enum.StrEnum):
    HIGH = "High"
    LOW = "Low"


class AnalogPause(enum.StrEnum):
    ABOVE = "ABOVE"
    BELOW = "BELOW"
