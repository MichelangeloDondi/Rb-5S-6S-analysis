"""
Closure tests for the peak-area / degeneracy-law module (rb5s6s/amplitudes.py).
"""

from __future__ import annotations

import numpy as np

from rb5s6s import config as C
from rb5s6s.amplitudes import predicted_shares, peak_area
from rb5s6s.lineshape import model_profile
from rb5s6s.linefit import to_frequency

T_MS = np.arange(2000) * 0.5 - 500.0
NU = to_frequency(T_MS, 0.08514)


def test_predicted_shares_physics():
    s = predicted_shares()
    assert abs(sum(s.values()) - 1.0) < 1e-12
    # within-isotope ratios are PURE degeneracy: 5/3 and 7/5
    assert abs(s["4207"] / s["4121"] - 5.0 / 3.0) < 1e-12
    assert abs(s["4192"] / s["4154"] - 7.0 / 5.0) < 1e-12
    # cross-isotope carries the abundance: 4192/4207 = (.7217*7/12)/(.2783*5/8)
    assert abs(s["4192"] / s["4207"] - 2.4207) < 5e-3
    # 85Rb lines dominate (abundance): the two 85 peaks together > 70%
    assert s["4192"] + s["4154"] > 0.70


def test_peak_area_recovers_known_area():
    # Line of KNOWN area on a tilted baseline + noise: the integral must
    # recover the area within a few %, unbiased by the baseline tilt.
    rng = np.random.default_rng(C.RNG_SEED)
    true_area = 3.0  # V*MHz
    prof = model_profile(NU - 5.0, gamma_coll=1.0, sigma_laser_fwhm=2.0,
                         transit_fwhm=0.9)   # area-normalized => x true_area
    v = true_area * prof + 0.007 + 2e-4 * NU + rng.normal(0, 3e-3, len(NU))
    got = peak_area(NU, v)
    # peak_area is a TRUNCATED area: ~9% of a Lorentzian-cored line lies
    # outside +-3.5 FWHM, and the edge-baseline subtraction eats a little
    # wing too. It must UNDERCOUNT by a stable 5-15% (which cancels in
    # ratios of similar-width lines -- the next test), never overcount.
    assert 0.82 < got / true_area < 1.00, got


def test_peak_area_ratio_beats_height_ratio_under_width_change():
    # Two lines with the SAME area but different widths: the AREA ratio must
    # stay ~1 while the HEIGHT ratio deviates strongly -- the reason the
    # analysis uses integrals, not peak heights.
    rng = np.random.default_rng(3)
    pa = model_profile(NU, gamma_coll=0.5, sigma_laser_fwhm=1.0, transit_fwhm=0.9)
    pb = model_profile(NU, gamma_coll=3.0, sigma_laser_fwhm=2.5, transit_fwhm=0.9)
    va = 2.0 * pa + 0.005 + rng.normal(0, 2e-3, len(NU))
    vb = 2.0 * pb + 0.005 + rng.normal(0, 2e-3, len(NU))
    area_ratio = peak_area(NU, va) / peak_area(NU, vb)
    height_ratio = va.max() / vb.max()
    assert abs(area_ratio - 1.0) < 0.08, area_ratio
    assert height_ratio > 1.3  # heights differ a lot; areas must not
