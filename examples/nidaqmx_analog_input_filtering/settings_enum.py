"""Enumeration for amplitude values used in the simple graph example."""

import enum

class DigitalEdge(enum.StrEnum):
    FALLING = "FALLING"
    RISING = "RISING"

class PauseWhen(enum.StrEnum):
    HIGH = "High"
    LOW = "Low"

class Slopes(enum.StrEnum):
    FALLING = "Falling"
    RISING = "Rising"

class AnalogPause(enum.StrEnum):
    ABOVE = "ABOVE"
    BELOW = "BELOW"