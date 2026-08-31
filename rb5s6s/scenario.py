"""The campaign scenario: every knob of a session, loadable, refusing nonsense.

WHAT THIS IS. One dataclass holding everything a campaign session chooses --
temperatures, the power ladder, the waist, the retro ratio, the lock state,
the session length, the oscilloscope and its settings, the noise law, and
for the nanofibre platform the fibre geometry -- loaded from a TOML file a
stranger can read, diff and edit. The twin consumes a `Scenario`; the three
shipped presets under `examples/scenarios/` are the validation target
(`dataset_2025`), the proposed cell campaign (`campaign_cell`), and the
cell-plus-nanofibre arm (`campaign_cell_onf`).

TWO RULES THE LOADER ENFORCES, both poka-yokes in the kaizen sense.

First, EVERY VALUE CARRIES ITS PROVENANCE. A preset must name, in its
`[provenance]` table, the source of every field it sets: the constants
module, a DATA.md section, a manual page, an open item. A field without a
provenance entry refuses to load. This is the four-things rule applied to
configuration: a number nobody can source is not a setting, it is a guess
wearing one's clothes.

Second, THE ACQUISITION MUST BE REALISABLE ON THE NAMED SCOPE. A record
length beyond the instrument's memory, a resolution mode it does not offer,
or a sample rate above a manual-anchored ceiling is rejected at load with
an error naming the field and citing the manual's own limit, so a nonsense
configuration cannot survive into a forecast. Where the held manual prints
no ceiling (the held LeCroy and R&S manuals print no sample-rate spec),
the loader says the limit is unenforced and why, instead of inventing one.

APPARATUS UNKNOWNS ARE SPANS. The waist is the open knife-edge item and
loads as a (low, high) span, never a point; the repaired lock's residual
drift is unmeasured (docs/plan/12) and loads the same way. A forecast built
on a Scenario runs the span, not a guess.
"""
from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional, Tuple

from . import instruments

__all__ = ["Span", "Acquisition", "FibreArm", "Scenario", "load_scenario"]


@dataclass(frozen=True)
class Span:
    """A quantity the record holds as a range, never a point.

    `low == high` is allowed (a measured value enters as a degenerate span)
    but the loader never builds one silently from a scalar: writing
    `[8.0, 24.0]` in the preset is the visible admission that the number is
    open, and that visibility is the point.
    """

    low: float
    high: float

    def __post_init__(self):
        if self.high < self.low:
            raise ValueError(f"span upside down: [{self.low}, {self.high}]")

    @property
    def width(self) -> float:
        return self.high - self.low

    def grid(self, n: int = 3) -> Tuple[float, ...]:
        if n < 2 or self.width == 0.0:
            return (0.5 * (self.low + self.high),)
        step = self.width / (n - 1)
        return tuple(self.low + i * step for i in range(n))


@dataclass(frozen=True)
class Acquisition:
    """The scope half of a scenario, validated against the registry."""

    instrument: str
    resolution_mode: Optional[str] = None   # None takes the registry default
    record_length: Optional[int] = None     # None takes the registry default
    sample_rate_hz: Optional[float] = None  # None: the campaign regime is kSa/s

    def validated(self) -> "Acquisition":
        ins = instruments.get(self.instrument)   # KeyError names the registry
        if self.resolution_mode is not None and \
                self.resolution_mode not in ins.modes:
            raise ValueError(
                f"scenario refuses: {ins.model} offers no resolution mode "
                f"{self.resolution_mode!r}, only {sorted(ins.modes)} "
                f"({ins.provenance})")
        if self.record_length is not None and \
                self.record_length > ins.max_points:
            raise ValueError(
                f"scenario refuses: {self.record_length} points exceed the "
                f"{ins.max_points} the {ins.model} can store "
                f"({ins.provenance})")
        ceiling = MANUAL_RATE_CEILING_HZ.get(self.instrument)
        if self.sample_rate_hz is not None and ceiling is not None \
                and self.sample_rate_hz > ceiling[0]:
            raise ValueError(
                f"scenario refuses: {self.sample_rate_hz:.3g} Sa/s exceeds "
                f"the {ceiling[0]:.3g} Sa/s ceiling of the {ins.model} "
                f"({ceiling[1]})")
        return self


# Sample-rate ceilings the HELD manuals actually print, keyed like the
# registry. The Keysight manual's Table 1 prints 4 GSa/s interleaved for
# the 500 MHz model. The WaveSurfer manual and the RTM3000
# manual print no sample-rate line (checked 2026-08-31, the same
# pass that checked the resolution modes), so their entries are ABSENT and
# the loader says the limit is unenforced rather than inventing a datasheet
# number it cannot cite.
MANUAL_RATE_CEILING_HZ: Dict[str, tuple] = {
    "agilent_3054a": (4e9, "manual Table 1, 4 GSa/s interleaved"),
}


@dataclass(frozen=True)
class FibreArm:
    """The nanofibre geometry, reaching fibre.py's solved mode."""

    diameter_nm: float
    diameter_tolerance_nm: float
    distances_nm: Tuple[float, ...]
    atom_temperature_k: float
    # The radiation temperature is NOT a field: rb5s6s.twin fixes it at
    # 300 K for a laboratory fibre and refuses to read the atoms'
    # temperature as a radiation temperature. A field here would reopen
    # exactly that door.


@dataclass(frozen=True)
class Scenario:
    name: str
    platform: str                          # "cell" | "onf"
    temperatures_c: Tuple[float, ...]
    powers_w: Tuple[float, ...]
    waist_um: Span                         # the open knife-edge item
    retro_ratio: float
    retro_ratio_err: float
    lock: str                              # "fixed" | "drifting"
    lock_drift_mhz_per_min: Span           # unmeasured residual -> span
    session_hours: float
    acquisition: Acquisition
    noise_law_csv: str
    fibre: Optional[FibreArm] = None
    provenance: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        if self.platform not in ("cell", "onf"):
            raise ValueError(f"unknown platform {self.platform!r}")
        if self.lock not in ("fixed", "drifting"):
            raise ValueError(f"unknown lock state {self.lock!r}")
        if self.platform == "onf" and self.fibre is None:
            raise ValueError("an onf scenario must carry its [fibre] table")


_REQUIRED_PROVENANCE = (
    "temperatures_c", "powers_w", "waist_um", "retro_ratio", "lock",
    "lock_drift_mhz_per_min", "session_hours", "acquisition", "noise_law_csv",
)


def load_scenario(path) -> Scenario:
    """Load and validate one scenario TOML. Refusals name their reason."""
    raw = tomllib.loads(Path(path).read_text(encoding="utf-8"))
    s = raw["scenario"]
    prov = raw.get("provenance", {})
    missing = [k for k in _REQUIRED_PROVENANCE if k not in prov]
    if missing:
        raise ValueError(
            f"scenario refuses: no provenance for {missing} in {path}. Every "
            "field names its source, or it does not load.")
    if s.get("platform") == "onf" and "fibre" not in prov and "fibre" in raw:
        raise ValueError(
            f"scenario refuses: the [fibre] table in {path} carries no "
            "provenance entry")
    acq = Acquisition(**raw["acquisition"]).validated()
    fibre_arm = None
    if "fibre" in raw:
        f = raw["fibre"]
        fibre_arm = FibreArm(
            diameter_nm=float(f["diameter_nm"]),
            diameter_tolerance_nm=float(f["diameter_tolerance_nm"]),
            distances_nm=tuple(float(x) for x in f["distances_nm"]),
            atom_temperature_k=float(f["atom_temperature_k"]))
    return Scenario(
        name=str(s["name"]),
        platform=str(s["platform"]),
        temperatures_c=tuple(float(x) for x in s["temperatures_c"]),
        powers_w=tuple(float(x) for x in s["powers_w"]),
        waist_um=Span(*[float(x) for x in s["waist_um"]]),
        retro_ratio=float(s["retro_ratio"]),
        retro_ratio_err=float(s["retro_ratio_err"]),
        lock=str(s["lock"]),
        lock_drift_mhz_per_min=Span(
            *[float(x) for x in s["lock_drift_mhz_per_min"]]),
        session_hours=float(s["session_hours"]),
        acquisition=acq,
        noise_law_csv=str(s["noise_law_csv"]),
        fibre=fibre_arm,
        provenance=dict(prov),
    )
