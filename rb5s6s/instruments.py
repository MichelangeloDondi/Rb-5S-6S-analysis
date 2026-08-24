"""The oscilloscopes as objects the twin can acquire with.

WHY THIS EXISTS. The twin could generate a line and add noise, but it could
not answer the question an acquisition design actually asks: what would THIS
instrument, at THESE settings, record. Point count, vertical step, the
resolution mode's own mechanism and the record's memory all decide what
reaches the fitter, and until now they lived in prose in the plan chapters
while the twin used a bare `n_points`.

EVERY NUMBER HERE COMES FROM A MANUFACTURER MANUAL, read in the private tree
and summarised in `docs/plan/07_acquisition-settings.md`. Where a manual does
not print a quantity, the field says so instead of guessing: the RTM's native
converter depth is a datasheet item nobody has read, and it is `None`.

THE RESOLUTION MODES ARE NOT INTERCHANGEABLE, which is the fact this module
exists to make unavoidable in code. High resolution on the InfiniiVision and
the RTM is a DISJOINT boxcar: each stored point averages its own block of raw
samples and adjacent points share none, so it raises the effective bit depth
and leaves neighbouring samples uncorrelated. Enhanced resolution on the
LeCroy is a moving-average FIR ACROSS stored samples: it also raises the bit
depth, and it correlates neighbours by construction and halves the bandwidth
per half-bit. A twin that treats them alike will report an artefact class the
record spent two days removing.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np


@dataclass(frozen=True)
class ResolutionMode:
    """One vertical-resolution setting of one instrument."""

    name: str
    kind: str                    # "raw", "boxcar" or "moving_average"
    bits: float                  # effective bits at the campaign's timebase
    correlates_neighbours: bool  # the FIR does, the disjoint boxcar does not
    note: str = ""


@dataclass(frozen=True)
class Instrument:
    """An oscilloscope, as far as the twin needs to know it."""

    key: str
    model: str
    adc_bits: Optional[int]           # native converter depth, None if unprinted
    max_points: int                   # deepest record the export tolerates
    default_points: int               # what the campaign or the design uses
    channels: int
    modes: Dict[str, ResolutionMode]
    default_mode: str
    provenance: str = ""

    def mode(self, name: Optional[str] = None) -> ResolutionMode:
        return self.modes[name or self.default_mode]

    def lsb_volts(self, full_scale_v: float, mode: Optional[str] = None) -> float:
        """The vertical step at this full scale, from the mode's bit depth.

        Full scale is the whole vertical window, so the step is that window
        divided by two to the bits. A campaign that puts the line peak at
        four fifths of the window has a step of four fifths of the peak over
        two to the bits, which is the arithmetic the acquisition chapter runs
        in prose.
        """
        return float(full_scale_v) / (2.0 ** self.mode(mode).bits)


# The campaign instrument. High Resolution is a disjoint per-interval boxcar
# with a ceiling printed as a table against sweep speed: eight bits at or
# below 1 us per division, one more per step, twelve at or above 20 us. The
# 2025 campaign sat four decades past that threshold, so its measured 11.86
# effective bits ARE the ceiling and not a coincidence.
AGILENT = Instrument(
    key="agilent_3054a",
    model="Agilent dso-x 3054a (InfiniiVision)",
    adc_bits=8,
    max_points=64_000,          # the CSV export cap measured on the bench
    default_points=2_000,       # the 2025 campaign's own record
    channels=4,
    modes={
        "raw": ResolutionMode("raw", "raw", 8.0, False),
        "hires": ResolutionMode(
            "hires", "boxcar", 12.0, False,
            "ceiling from the manual's table, reached at or above 20 us/div"),
    },
    default_mode="hires",
    provenance="Keysight InfiniiVision instrument manual, private/Manuals",
)

# The deep instrument. Enhanced resolution is a moving average ACROSS stored
# samples, 0.5 to 3.0 bits in half-bit steps, each step halving bandwidth, so
# the design runs it RAW and smooths offline where the kernel is known.
LECROY = Instrument(
    key="lecroy_ws3104z",
    model="LeCroy WaveSurfer 3104z",
    adc_bits=8,
    max_points=500_001,         # measured in the rehearsal files
    default_points=500_001,
    channels=4,
    modes={
        "raw": ResolutionMode("raw", "raw", 8.0, False,
                              "the design's choice: smooth offline instead"),
        "eres_1.5": ResolutionMode(
            "eres_1.5", "moving_average", 9.5, True,
            "1.5 bits, and it halves bandwidth three times over"),
        "eres_3.0": ResolutionMode(
            "eres_3.0", "moving_average", 11.0, True,
            "the top of the range, at the cost of most of the bandwidth"),
    },
    default_mode="raw",
    provenance="WaveSurfer 3000z operator manual, private/Manuals",
)

# The borrowable instrument. High resolution is decimation, the same disjoint
# family as the Agilent, and the stored words go to sixteen bits. Sixteen-bit
# words are not sixteen effective bits and the native depth is not printed.
RTM3004 = Instrument(
    key="rtm3004",
    model="R&S RTM3004",
    adc_bits=None,              # the manual does not print it
    max_points=80_000_000,
    default_points=5_000_000,
    channels=4,
    modes={
        "raw": ResolutionMode("raw", "raw", 8.0, False),
        "hires": ResolutionMode(
            "hires", "boxcar", 16.0, False,
            "16-bit stored words, effective depth unprinted, so this is the "
            "word length and an upper bound on the resolution"),
    },
    default_mode="hires",
    provenance="RTM3000 instrument manual, private/Manuals",
)

INSTRUMENTS: Dict[str, Instrument] = {
    i.key: i for i in (AGILENT, LECROY, RTM3004)
}


def get(key: str) -> Instrument:
    if key not in INSTRUMENTS:
        raise KeyError(f"unknown instrument {key!r}, have {sorted(INSTRUMENTS)}")
    return INSTRUMENTS[key]


def quantise(v: np.ndarray, step: float) -> np.ndarray:
    """Round onto the vertical grid. A step of zero leaves the trace alone."""
    if step <= 0:
        return v
    return np.round(np.asarray(v, dtype=float) / step) * step


def apply_resolution_mode(v: np.ndarray, mode: ResolutionMode,
                          *, raw_per_point: int = 1) -> np.ndarray:
    """What the instrument's own vertical processing does to the samples.

    The disjoint boxcar is applied by the CALLER, by generating raw samples
    and averaging blocks of them, because that is what the instrument does
    and it changes the noise as well as the depth. This function carries the
    part that acts on the stored record: the moving average of the enhanced
    mode, which correlates neighbours and is the whole reason the design
    prefers raw.
    """
    if mode.kind != "moving_average":
        return v
    # half a bit per doubling of the window, which inverts to this width
    width = max(1, int(round(4.0 ** (mode.bits - 8.0))))
    if width <= 1:
        return v
    kernel = np.ones(width) / width
    return np.convolve(np.asarray(v, dtype=float), kernel, mode="same")
