
"""Enumeration for amplitude values used in the simple graph example."""

import enum
from nidaqmx.constants import Edge, Slope, Timescale, TerminalConfiguration
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

class TerminalConfig(enum.StrEnum):
    DEFAULT = "DEFAULT"
    RSE = "RSE"
    NRSE = "NRSE"
    DIFF = "DIFF"
    PSEUDO_DIFF = "PSEUDO_DIFF"
