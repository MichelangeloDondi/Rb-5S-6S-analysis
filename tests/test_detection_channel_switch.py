"""The detection channel switch, thrown.

`detection_channel` and `halo_fraction` entered `twin.acquire` on 2026-09-05
and nothing in the suite called either. A parameter that selects a model form
and has only ever been called with its default is an untested assumption
wearing the costume of a tested one: `laser_kind` sat at its default for the
life of this project and moved the collisional coefficient by a median 45 per
cent when it was finally turned (the switch audit of 2026-08-20).

Both halves are pinned, because each fails in its own direction: a default that
drifts silently rewrites every committed CSV the twin feeds, and a thrown
branch nobody runs is an untested assumption wearing a tested costume.
"""
import numpy as np
import pytest

from rb5s6s import twin
from rb5s6s.amplitudes import predicted_shares

TRUTH = dict(gamma_coll_mhz=0.580779, sigma_laser_mhz=1.560691,
             transit_fwhm_mhz=0.957477)
SEED = 20260905


def _trace(**kw):
    cell = twin.vapour_cell(130.0, **TRUTH)
    acq = twin.Acquisition(instrument="lecroy_ws3104z", n_traces=1)
    f, v, meta = twin.acquire(cell, acq, kind="four_peak",
                              rng=np.random.default_rng(SEED), **kw)
    return f, v, meta


def test_the_default_path_is_untouched_by_the_channel():
    """Passing the switch OFF explicitly must equal not passing it at all.

    Fails if the default ever stops meaning equal shares, which would move
    every committed CSV produced through the twin without a producer changing.
    """
    _, a, _ = _trace()
    _, b, _ = _trace(detection_channel=None, halo_fraction=0.0)
    assert np.array_equal(a, b)


def test_the_thrown_channel_puts_the_peaks_at_their_predicted_shares():
    """With the channel on, the tallest peak carries the largest share.

    Fails if the branch raises (its key space and `predicted_shares`' must
    agree) or if the shares stop reaching the trace at all.
    """
    _, off, _ = _trace()
    _, on, _ = _trace(detection_channel=True, halo_fraction=0.0)
    strongest = max(predicted_shares().values())
    ratio = on[0].max() / off[0].max()
    # equal shares put every peak at 1.0; the channel scales the tallest to its
    # own share. The tolerance is the instrument's 8-bit quantisation.
    assert ratio == pytest.approx(strongest, abs=0.01), (
        f"tallest peak fell to {ratio:.4f} of the equal-share default, "
        f"expected the strongest predicted share {strongest:.4f}")


def test_the_halo_scales_the_collected_amplitude():
    """The trapped-light halo re-excites, so it RAISES the collected signal.

    Fails if the halo is ever wired as an attenuation: the first draft of this
    wiring used exp(-tau) with tau reaching 319, which would have generated
    blank traces.
    """
    # THE PEAK IS QUANTISATION-BLIND AND THE INTEGRAL IS NOT. Measured: a halo
    # 1.7x too strong gives an identical quantised peak (1.01053 either way) at
    # this seed, so the first version of this test passed against a
    # seventy-per-cent error. The trace SUM carries the signal without that
    # rounding, and the quantity that scales with the halo is the EXCESS over
    # the unhaloed trace, which measures 0.00106 at nominal and 0.00184 at
    # 1.7x -- a ratio of 1.74 against the 1.7 injected.
    _, plain, _ = _trace(detection_channel=True, halo_fraction=0.0)
    _, haloed, _ = _trace(detection_channel=True, halo_fraction=0.0107)
    base = float(plain[0].sum())
    excess = float(haloed[0].sum()) / base - 1.0
    assert excess > 0, (
        "the halo must RAISE the collected signal; wired as an attenuation it "
        "would lower it, and exp(-tau) with tau reaching 319 would zero it")

    # MAGNITUDE NEEDS BOTH AN ABSOLUTE AND A RELATIVE CHECK, and the first
    # version of this had only the ratio. A UNIFORM gain error cancels in a
    # ratio, so scaling the wiring by 1.7, by 0.5, or to zero all passed a
    # scaling-only test -- exactly the class it was written to catch. Planted
    # and confirmed on 2026-09-05.
    assert excess == pytest.approx(0.00106, rel=0.25), (
        f"excess of {excess:.5f} against the 0.00106 this configuration "
        "measures; a uniform error in the halo wiring shows here and nowhere "
        "else")
    # and the SCALING, which catches a wiring that is right at one magnitude
    # and wrong at another.
    _, strong, _ = _trace(detection_channel=True, halo_fraction=0.0107 * 1.7)
    strong_excess = float(strong[0].sum()) / base - 1.0
    assert strong_excess / excess == pytest.approx(1.7, rel=0.15), (
        f"excess scaled by {strong_excess / excess:.2f} for a halo scaled by "
        "1.7, so the channel does not carry the halo's magnitude")
