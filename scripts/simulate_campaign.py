#!/usr/bin/env python
"""Generate a campaign's worth of traces, as files, from one command.

WHAT THIS IS FOR. Someone evaluating this record should be able to produce
the next campaign's data on their own machine, look at the files, and run
the analysis over them, without reading the library first. That is what a
digital twin is worth to a reader, and a twin that only prints a plot
cannot be checked.

WHAT IT WRITES. A directory of CSV traces, one file per trace, in the same
two-column shape the real instrument exports, plus a manifest describing
every setting that produced them and a README stating what they are and are
not. Plots are OFF by default, because the traces are the artefact and a
figure is a reading of them. Pass --plot to draw the overview as well, which
is the same machinery the campaign figures use.

EXAMPLES
    # the campaign as it would be run, cell platform, one-peak ladder
    python scripts/simulate_campaign.py --out /tmp/twin_cell

    # all four lines on one vertical range, on the deep instrument
    python scripts/simulate_campaign.py --kind four_peak \\
        --instrument lecroy_ws3104z --out /tmp/twin_four

    # the fibre platform, whose radiation temperature is the room and not
    # the atoms, with the overview drawn as well
    python scripts/simulate_campaign.py --platform nanofibre --plot \\
        --out /tmp/twin_onf
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rb5s6s import instruments as inst, twin                  # noqa: E402

LAW = dict(a=0.004, b=1.0e-3, c=0.0, lev_max=1.0, tau_int=1.0)
DEFAULT_POWERS_MW = (25.0, 75.0, 125.0, 175.0, 225.0)


def _platform(name: str, t_c: float, gamma_coll: float, sigma_laser: float,
              transit: float) -> twin.Platform:
    if name == "vapour_cell":
        return twin.vapour_cell(t_c, gamma_coll_mhz=gamma_coll,
                                sigma_laser_mhz=sigma_laser,
                                transit_fwhm_mhz=transit)
    if name == "nanofibre":
        # the radiation temperature is the room, fixed, and the atom
        # temperature is carried only because it sets the transit time
        return twin.nanofibre(atom_temperature_uk=30.0,
                              gamma_coll_mhz=gamma_coll,
                              sigma_laser_mhz=sigma_laser,
                              transit_fwhm_mhz=transit)
    raise SystemExit(f"unknown platform {name!r}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="write a twin campaign's traces to a directory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("EXAMPLES")[-1])
    ap.add_argument("--out", type=Path, required=True,
                    help="directory to write traces into (created if absent)")
    ap.add_argument("--platform", default="vapour_cell",
                    choices=["vapour_cell", "nanofibre"])
    ap.add_argument("--kind", default="one_peak",
                    choices=["one_peak", "four_peak"])
    ap.add_argument("--instrument", default="agilent_3054a",
                    choices=sorted(inst.INSTRUMENTS))
    ap.add_argument("--mode", default=None, help="resolution mode, instrument default if unset")
    ap.add_argument("--points", type=int, default=None, help="record length")
    ap.add_argument("--repeats", type=int, default=5, help="traces per condition")
    ap.add_argument("--powers", type=float, nargs="*", default=list(DEFAULT_POWERS_MW),
                    help="ladder rungs in mW")
    ap.add_argument("--temperature", type=float, default=130.0, help="cell temperature in C")
    ap.add_argument("--gamma-coll", type=float, default=0.580779)
    ap.add_argument("--sigma-laser", type=float, default=1.560691)
    ap.add_argument("--transit", type=float, default=0.957477)
    ap.add_argument("--tau-int", type=float, default=3.8,
                    help="sample correlation, the campaign's measured median")
    ap.add_argument("--seed", type=int, default=20260824)
    ap.add_argument("--plot", action="store_true",
                    help="also draw an overview figure of what was written")
    a = ap.parse_args(argv)

    out: Path = a.out
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(a.seed)
    platform = _platform(a.platform, a.temperature, a.gamma_coll,
                         a.sigma_laser, a.transit)

    manifest = []
    n_written = 0
    for power_mw in a.powers:
        # the line height goes as the square of the drive power, which is
        # what makes a one-range ladder a real constraint on the design
        scale = (power_mw / max(a.powers)) ** 2
        acq = twin.Acquisition(instrument=a.instrument, mode=a.mode,
                               n_points=a.points, n_traces=a.repeats,
                               tau_int_samples=a.tau_int)
        freqs, volts, meta = twin.acquire(
            platform, acq, kind=a.kind, noise_law=LAW,
            amp_v=scale * (acq.peak_fraction_of_scale * acq.full_scale_v - 0.01),
            rng=rng)
        for i, (f, v) in enumerate(zip(freqs, volts), start=1):
            name = f"{a.kind}_{a.platform}_{int(power_mw):03d}mW_{i}.csv"
            with (out / name).open("w", newline="") as fh:
                w = csv.writer(fh)
                w.writerow(["frequency_MHz_transition_axis", "volts"])
                w.writerows(zip(np.round(f, 6), np.round(v, 8)))
            manifest.append(dict(file=name, power_mW=power_mw, repeat=i,
                                 **{k: str(val) for k, val in meta.items()}))
            n_written += 1

    (out / "MANIFEST.json").write_text(json.dumps(manifest, indent=1) + "\n")
    (out / "README.md").write_text(f"""# Twin traces, {a.platform}, {a.kind}

{n_written} traces written by `scripts/simulate_campaign.py` from the digital
twin of this repository. Each file is two columns, frequency on the
two-photon transition axis in MHz and signal in volts, which is the shape
the real instrument exports.

**Instrument.** {inst.get(a.instrument).model}, mode
`{manifest[0]['mode']}` ({manifest[0]['mode_kind']}),
{manifest[0]['n_points']} points per trace, vertical step
{manifest[0]['lsb_volts']} V.

**Platform.** {a.platform}. Radiation temperature
{manifest[0]['radiation_temperature_k']} K, atom temperature
{manifest[0]['atom_temperature_k']} K. On the fibre platform these differ by
eight orders of magnitude and the blackbody shift follows the ROOM, which is
the distinction the twin exists to keep.

**What these are.** Data a known world would produce through a known
instrument. **What they are not.** A measurement. Nothing here is evidence
about rubidium: it is evidence about what an analysis recovers when the
answer is already known, which is the only thing a twin can testify to.

Regenerate with the command in `MANIFEST.json`, or fit them with
`rb5s6s.linefit.fit_condition`, which is the same estimator the campaign
uses.
""")
    print(f"wrote {n_written} traces to {out}")
    print(f"  instrument {manifest[0]['instrument']}, {manifest[0]['n_points']} points")
    print(f"  platform {a.platform}, radiation {manifest[0]['radiation_temperature_k']} K")
    print(f"  manifest {out / 'MANIFEST.json'}")

    if a.plot:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(9, 5))
        for row in manifest[::max(1, a.repeats)]:
            d = np.genfromtxt(out / row["file"], delimiter=",", skip_header=1)
            ax.plot(d[:, 0], d[:, 1], lw=0.8,
                    label=f"{row['power_mW']:g} mW")
        ax.set_xlabel("frequency, transition axis (MHz)")
        ax.set_ylabel("signal (V)")
        ax.set_title(f"twin campaign, {a.platform}, {a.kind}, "
                     f"{inst.get(a.instrument).model}")
        ax.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(out / "overview.png", dpi=150)
        print(f"  figure {out / 'overview.png'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
