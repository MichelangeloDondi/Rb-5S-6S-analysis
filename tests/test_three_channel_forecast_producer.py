"""Guards for `scripts/run_three_channel_forecast.py` and the world builder's
`tooth_of` hook it needs: the EOM comb's teeth are the same physical line and
must look up cascade and saturation under it; the default is the identity and
byte-identical; the comb's heights follow the Bessel law the ruler carries."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_three_channel_forecast.py"


def _load():
    spec = importlib.util.spec_from_file_location("_tcf", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _kw():
    return dict(positions={"4192": 0.0}, shares={"4192": 1.0}, gamma_coll=0.55, sigma_laser_fwhm=1.6,
                transit_fwhm=0.9575, power_max_w=1.0, cycles_at_max=1.0, drift_mhz_total=0.0,
                noise_frac_bright=0.004, adc_levels=4096)


def test_tooth_of_default_is_byte_identical_and_a_comb_changes_the_trace():
    from rb5s6s.forecast import build_world_trace
    L = {"cascade": True, "saturation": True, "stark": True, "bbr": True, "drift": False, "quantise": True, "randomise": False}
    a = build_world_trace(1.0, 0.364, 130.0, 0, 1, np.random.default_rng(7), L, **_kw())[1]
    b = build_world_trace(1.0, 0.364, 130.0, 0, 1, np.random.default_rng(7), L, tooth_of=None, **_kw())[1]
    assert np.array_equal(a, b)
    kw = _kw(); kw["positions"] = {"4192": 0.0, "4192@+1": 12.5}; kw["shares"] = {"4192": 0.6, "4192@+1": 0.2}
    c = build_world_trace(1.0, 0.364, 130.0, 0, 1, np.random.default_rng(7), L, tooth_of={"4192@+1": "4192"}, **kw)[1]
    assert not np.array_equal(a, c)


def test_a_tooth_without_a_physical_peak_refuses_rather_than_guessing():
    from rb5s6s.forecast import build_world_trace
    L = {"cascade": True, "saturation": False, "stark": True, "bbr": False, "drift": False, "quantise": False, "randomise": False}
    kw = _kw(); kw["positions"] = {"4192": 0.0, "4192@+1": 12.5}; kw["shares"] = {"4192": 0.6, "4192@+1": 0.2}
    with pytest.raises((KeyError, ValueError, RuntimeError)):
        build_world_trace(1.0, 0.364, 130.0, 0, 1, np.random.default_rng(7), L, **kw)


def test_the_comb_heights_follow_the_bessel_law_and_sum_to_the_line():
    mod = _load()
    from scipy.special import jv
    pos, shares, tooth_of = mod._comb(12.5, 1.2)
    assert set(tooth_of.values()) == {"4192"}
    assert pos["4192"] == 0.0 and pos["4192@+1"] == 12.5 and pos["4192@-2"] == -25.0
    w = np.array([jv(k, 1.2) ** 2 for k in (-3, -2, -1, 0, 1, 2, 3)])
    got = np.array([shares[k] for k in ("4192@-3", "4192@-2", "4192@-1", "4192", "4192@+1", "4192@+2", "4192@+3")])
    assert np.allclose(got / got.sum(), w / w.sum())


def test_the_carrier_vanishes_at_the_first_bessel_zero():
    mod = _load()
    pos, shares, _ = mod._comb(12.5, 2.405)
    assert shares["4192"] < 1e-4 * shares["4192@+1"]


def test_every_lever_varies_one_field_from_the_base_except_the_named_depth_cells():
    """The base is the RF-off trace, so a depth cell must also switch a comb
    on: those two cells change two keys and say so in their names. Every other
    lever changes exactly one."""
    mod = _load()
    cells = mod.levers()
    names = [n for n, _ in cells]
    assert names[0] == "base" and len(set(names)) == len(names)
    assert mod.BASE["f_mod"] is None
    for name, cfg in cells[1:]:
        changed = sorted(k for k in mod.BASE if cfg[k] != mod.BASE[k] and not (k == "two_beta" and mod.BASE[k] is None and cfg[k] == mod._two_beta_default()))
        if "depth_ladder" in name:
            assert changed == ["f_mod", "ladder"], (name, changed)
        elif "depth" in name:
            assert changed == ["f_mod", "two_beta"], (name, changed)
        else:
            assert len(changed) == 1, (name, changed)


def test_the_pull_channel_reads_the_ramps_mean_from_the_fitted_centre():
    """The ramp's mean is -2 S0/3: a centre fitted with s0 = 0 shifts by that
    amount, so kappa = -(3/2) d centre / dP. Checked here on the model's own
    first moment; the producer's fitted centre on its quiet traces returns
    the same to about a per cent at 16 um and better at 40 and 64."""
    from rb5s6s.lineshape import model_profile
    nu = np.linspace(-30, 30, 12001)
    cs = []
    for s0 in (0.0, 1.0, 2.0):
        y = model_profile(nu, gamma_coll=0.55, sigma_laser_fwhm=1.6, transit_fwhm=0.9575, s0=s0, resolve_shift=True)
        y = y / y.sum()
        cs.append(float(np.sum(nu * y)))
    slope = (cs[2] - cs[0]) / 2.0
    assert slope == pytest.approx(-2.0 / 3.0, rel=0.05)


def test_the_worker_cap_and_the_flag_refusal_hold(monkeypatch):
    mod = _load()
    src = SCRIPT.read_text(encoding="utf-8")
    assert "min(8," in src
    monkeypatch.setattr("sys.argv", ["x", "--one_cell"])
    with pytest.raises(SystemExit) as e:
        mod.main()
    assert "unknown flag" in str(e.value)


def test_a_rung_is_admitted_on_two_statistics_and_a_loud_coin_flip_is_not():
    """The defect of 2026-09-06: a rung whose sign is a coin flip but whose
    magnitude is large (pure noise on a normalised window) was admitted at
    eight sets by the fraction-negative bar alone and inverted into a
    coefficient 230 times the truth. Every case is built by construction, not
    drawn, so the test cannot pass or fail on a random fraction."""
    mod = _load()
    n = 400
    i = np.arange(n)
    settled = 1.0 + 0.1 * np.sin(i)                                  # all positive, tight: admitted
    loud = 50.0 * np.where(i % 2 == 0, 1.0, -1.0) * (1 + 0.01 * i)   # half negative, huge: refused
    quarter = np.where(i % 4 == 0, -1.0, 1.0) * (0.5 + 4.5 * (i % 97) / 96)  # 25 per cent negative, median well above its SE: admitted
    k3_sets = np.column_stack([settled, loud, quarter])
    usable, frac_neg = mod.admit_rungs(k3_sets)
    assert usable[0] and not usable[1] and usable[2]
    assert frac_neg[0] == 0.0 and frac_neg[1] == 0.5 and frac_neg[2] == 0.25
    # the second statistic is what refuses the case that actually happened: at
    # EIGHT sets a symmetric noise rung with two negatives clears the fraction
    # bar by chance, and its median sits inside its own standard error
    eight = np.array([-3.0, -1.0, 0.5, 1.0, 1.5, 2.0, 2.5, 4.0])[:, None]
    one_bar, fn = mod.admit_rungs(eight, sigma_min=0.0)
    two_bars, _ = mod.admit_rungs(eight)
    assert fn[0] == 0.25 and one_bar[0], "the fraction bar alone admits it"
    assert not two_bars[0], "the significance bar refuses it, which is the whole point"

def test_the_power_ladder_is_the_campaign_twin_example_ladder():
    """Failure: the producer drifts from the campaign's own ladder while the
    prose keeps calling it the campaign's. The example is the reference the
    scenario forecast and the plan hub drive."""
    import re
    mod = _load()
    src = (ROOT / "examples" / "campaign_twin.py").read_text()
    m = re.search(r"POWERS_W\s*=\s*np\.array\(\[([^\]]+)\]\)", src)
    assert m, "examples/campaign_twin.py no longer states POWERS_W as an array literal"
    ladder = tuple(float(x) for x in m.group(1).split(","))
    assert tuple(mod.POWERS_W) == ladder


def test_the_combination_of_two_identical_channels_gains_nothing():
    """The board's finding: the single channels' spreads were the median's
    standard error scaled back by root n, 1.2533 times a standard deviation,
    while the combined spread was a plain one, so the gain read 1.25 on two
    channels that were the same. Every spread is now the same statistic and
    the degenerate case must read a gain of one."""
    rng = np.random.default_rng(11)
    a = rng.normal(25.9, 1.3, 400)
    cov = np.cov(a, a); v1, v2, c12 = cov[0, 0], cov[1, 1], cov[0, 1]
    w1 = (v2 - c12) / (v1 + v2 - 2 * c12) if (v1 + v2 - 2 * c12) > 0 else 0.5
    var_c = w1 ** 2 * v1 + (1 - w1) ** 2 * v2 + 2 * w1 * (1 - w1) * c12
    sd_comb = float(np.sqrt(max(var_c, 0.0)))
    assert sd_comb == pytest.approx(float(np.std(a, ddof=1)), rel=1e-9)
    src = (ROOT / "scripts" / "run_three_channel_forecast.py").read_text()
    assert "float(np.std(a, ddof=1))" in src and "median_standard_error(a) * math.sqrt" not in src


def test_the_modulation_depth_is_supplied_or_the_producer_refuses(monkeypatch):
    """Failure: a fallback depth that inverts the teeth's ordering against
    the carrier. The seam value comes from one place or the call refuses."""
    mod = _load()
    assert mod._two_beta_default() == pytest.approx(1.569, abs=1e-6)
    monkeypatch.delattr(mod.C, "RULER_MOD_DEPTH_2BETA", raising=False)
    monkeypatch.delattr(mod.K, "RULER_MOD_DEPTH_2BETA", raising=False)
    with pytest.raises(RuntimeError):
        mod._two_beta_default()


def test_every_cell_carries_its_seam_values_and_a_pooled_worker_builds_at_them():
    """The physics seat's finding: the seam values were set with `global` in
    main and never reached a spawned worker, which built every trace at the
    module's placeholder depth while the file was labelled with the parent's.
    Now they travel in the cell, and a pooled worker returns the values it
    used."""
    mod = _load()
    cells = mod.levers()
    for name, cfg in cells:
        assert cfg["two_beta"] == pytest.approx(mod._two_beta_default()) or "depth" in name, name
        assert 0.005 < cfg["beta_self"] < 0.05, name
    src = (ROOT / "scripts" / "run_three_channel_forecast.py").read_text()
    # no module global carries a seam value into _trace: the cfg does, and the
    # cfg is what the pool pickles into every worker
    assert "_TWO_BETA" not in src and "_BETA_SELF" not in src
    assert 'cfg["two_beta"]' in src and 'cfg["beta_self"]' in src
    # (a pooled run of _cell cannot be started from a module loaded under a
    # test name, since a spawned worker re-imports the file by that name; the
    # producer's own --plant is the pooled check and it now compares the
    # values the workers used, which travel in the cell)


def test_the_grid_span_is_opt_in_and_symmetric_under_a_comb():
    """Failure: the world builder's default grid moves (every committed twin
    file would), or a comb cell's grid still ends at +60 MHz with a tooth in
    the wing the baseline is read from."""
    from rb5s6s.forecast import build_world_trace
    L = {"cascade": True, "saturation": True, "stark": True, "bbr": True, "drift": False, "quantise": True, "randomise": False}
    args = (1.0, 0.364, 130.0, 0, 1)
    kw = _kw()
    nu0, y0, _ = build_world_trace(*args, np.random.default_rng(7), L, **kw)
    nu1, y1, _ = build_world_trace(*args, np.random.default_rng(7), L, grid_span=None, **kw)
    assert np.array_equal(nu0, nu1) and np.array_equal(y0, y1)
    assert nu0[0] == pytest.approx(-60.0) and nu0[-1] == pytest.approx(60.0) and nu0.size == 6000
    kw2 = {**kw, "positions": {"4192": 0.0, "4192@+1": 40.0, "4192@-1": -40.0},
           "shares": {"4192": 0.4, "4192@+1": 0.3, "4192@-1": 0.3}}
    nu2, y2, _ = build_world_trace(*args, np.random.default_rng(7), L, tooth_of={"4192@+1": "4192", "4192@-1": "4192"},
                                   grid_span=(-180.0, 180.0), **kw2)
    assert nu2[0] == pytest.approx(-180.0) and nu2[-1] == pytest.approx(180.0)
    assert nu2[1] - nu2[0] == pytest.approx(120.0 / 5999, rel=1e-3)


def test_a_tooth_is_depleted_at_its_own_rate_and_the_identity_map_stays_a_no_op():
    """A83, planted at three points because one plant would have passed a wrong fix.

    A phase modulation redistributes a line's excitation among its teeth as
    J_k(2 beta)^2 and leaves the intensity alone, so a dim sideband must be
    depleted less than a bright one at the same power. The builder counted the
    total power's cycles for every tooth. The three points: the injected
    amplitude equals the depletion law evaluated at the TOOTH's rate; an
    identity map over a SCALED share stays byte-identical (a fix reading the
    predicted shares rather than the caller's own would fail exactly here);
    and with depletion off the comb conserves the line's signal, which is the
    sum rule the weights obey.
    """
    from rb5s6s.forecast import build_world_trace
    from rb5s6s import cascade
    L = {"cascade": True, "saturation": False, "stark": True, "bbr": False, "drift": False,
         "quantise": False, "randomise": False}
    kw = _kw(); kw["cycles_at_max"] = 4.0
    kw["positions"] = {"4192": 0.0, "4192@+1": 25.0}
    kw["shares"] = {"4192": 0.44, "4192@+1": 0.11}
    tmap = {"4192@+1": "4192"}
    _, _, truth = build_world_trace(1.0, 0.364, 130.0, 0, 1, np.random.default_rng(7), L,
                                    tooth_of=tmap, **kw)
    own = 0.44 + 0.11
    for key, share in kw["shares"].items():
        want = share * cascade.amplitude_factor("4192", 4.0 * share / own)
        assert truth[key] == pytest.approx(want, rel=1e-12)
    assert truth["4192@+1"] / 0.11 > truth["4192"] / 0.44

    # an identity map over a scaled share changes nothing
    kw1 = _kw(); kw1["cycles_at_max"] = 4.0; kw1["shares"] = {"4192": 0.31}
    a = build_world_trace(1.0, 0.364, 130.0, 0, 1, np.random.default_rng(7), L, **kw1)[1]
    b = build_world_trace(1.0, 0.364, 130.0, 0, 1, np.random.default_rng(7), L,
                          tooth_of={"4192": "4192"}, **kw1)[1]
    assert np.array_equal(a, b)

    # with depletion off, the teeth carry exactly the line's own signal
    Loff = {**L, "cascade": False}
    _, _, one = build_world_trace(1.0, 0.364, 130.0, 0, 1, np.random.default_rng(7), Loff,
                                  **{**_kw(), "shares": {"4192": 0.55}, "cycles_at_max": 4.0})
    _, _, many = build_world_trace(1.0, 0.364, 130.0, 0, 1, np.random.default_rng(7), Loff,
                                   tooth_of=tmap, **kw)
    assert sum(many.values()) == pytest.approx(one["4192"], rel=1e-12)


def test_the_light_shift_does_not_move_with_the_modulation_depth():
    """The lever's premise, asserted on the builder rather than believed.

    A phase modulation holds the intensity constant, so the light shift and
    every width keyed on it are the same for every tooth at any depth, while
    the excitation rate per tooth follows the Bessel weights. On the builder
    that is two exact statements. A tooth's weight SCALES its profile and
    does not move or reshape it, so two depths give proportional traces to
    floating point. And a comb is the superposition of its teeth, each
    carrying the same ramp, so a two-tooth trace is the sum of the two
    one-tooth traces. Both are checked with the depletion off, because
    depletion is the one rate-keyed term and it is meant to break the first.
    """
    from rb5s6s.forecast import build_world_trace
    L = {"cascade": False, "saturation": True, "stark": True, "bbr": True, "drift": False,
         "quantise": False, "randomise": False}
    quiet = dict(noise_frac_bright=0.0, offset=0.0)

    def trace(shares, positions, tooth_of=None):
        kw = {**_kw(), **quiet, "positions": positions, "shares": shares}
        return build_world_trace(1.0, 0.364, 130.0, 0, 1, np.random.default_rng(7), L,
                                 tooth_of=tooth_of, grid_span=(-60.0, 60.0), **kw)[1]

    a = trace({"4192": 0.22}, {"4192": 0.0})
    b = trace({"4192": 0.05}, {"4192": 0.0})
    assert np.allclose(b, a * (0.05 / 0.22), rtol=0, atol=1e-12 + 1e-9 * np.max(a))

    # SUPERPOSITION NEEDS EVERY RATE-KEYED TERM OFF, and this half of the test
    # left one on. The docstring above names depletion as "the one rate-keyed
    # term" and switches it off; the companion WIDTH is a second, because power
    # broadening follows a tooth's own Rabi frequency, which is the root of its
    # share. It was inert here until 2026-09-06 only because the producer never
    # set `stark.COMPANIONS`, so the layer was declared and did nothing. With it
    # wired, a tooth built ALONE is normalised against itself and carries the
    # whole drive, while the same tooth inside a comb carries its share, so the
    # two constructions are broadened differently and cannot sum. That is the
    # physics working, not a defect, and the switch goes off to match the
    # sentence that was already written about depletion.
    Lw = {**L, "saturation": False}

    def trace_w(shares, positions, tooth_of=None):
        kw = {**_kw(), **quiet, "positions": positions, "shares": shares}
        return build_world_trace(1.0, 0.364, 130.0, 0, 1, np.random.default_rng(7), Lw,
                                 tooth_of=tooth_of, grid_span=(-60.0, 60.0), **kw)[1]

    carrier = trace_w({"4192": 0.22}, {"4192": 0.0})
    side = trace_w({"4192@+1": 0.05}, {"4192@+1": 25.0}, {"4192@+1": "4192"})
    both = trace_w({"4192": 0.22, "4192@+1": 0.05}, {"4192": 0.0, "4192@+1": 25.0},
                   {"4192@+1": "4192"})
    assert np.allclose(both, carrier + side, rtol=0, atol=1e-9 * np.max(both))


def test_a_dim_tooth_is_broadened_less_because_its_rabi_frequency_is_smaller(monkeypatch):
    """A86: the companion width is power broadening and follows the tooth.

    The two-photon amplitude into the tooth at order k is J_k(2 beta), so a
    tooth's Rabi frequency is J_k(2 beta) of the line's while its rate is the
    square of that, and the light shift is neither, being set by the whole
    spectrum. The builder keyed the companion width on the line's own shift for
    every tooth, so a dim sideband came out as broad as the carrier and a depth
    ladder would have read a constant width that is not physics.

    Measured as a width, which is what a bench sees, and each tooth compared
    with ITSELF under the companion model switched off, so the two teeth's
    different tail contamination cancels out of the comparison. At a share of
    one twentieth the tooth's Rabi frequency is under a quarter of the line's,
    so its broadening is a small fraction of the carrier's; under the defect
    the two increments are equal. `stark.COMPANIONS` is None by default and is
    switched on through monkeypatch, so pytest restores it: a plain assignment
    would leak into every later module of the session.
    """
    from rb5s6s.forecast import build_world_trace
    from rb5s6s import stark

    def fwhm(nu, y, centre, half=18.0):
        m = (nu > centre - half) & (nu < centre + half)
        x, v = nu[m], y[m] - np.min(y[m])
        above = x[v >= 0.5 * v.max()]
        return float(above.max() - above.min())

    L = {"cascade": False, "saturation": True, "stark": True, "bbr": False,
         "drift": False, "quantise": False, "randomise": False}
    kw = {**_kw(), "noise_frac_bright": 0.0, "offset": 0.0, "power_max_w": 0.225,
          "positions": {"4192": 0.0, "4192@+1": 60.0},
          "shares": {"4192": 0.40, "4192@+1": 0.02}}
    w = {}
    for label, comp in (("on", {"ratio": 1.2367, "scale": 1.0, "cycles": 1.0}), ("off", None)):
        monkeypatch.setattr(stark, "COMPANIONS", comp)
        nu, y, _ = build_world_trace(0.225, 8.0, 130.0, 0, 1, np.random.default_rng(3), L,
                                     tooth_of={"4192@+1": "4192"}, grid_span=(-90.0, 150.0), **kw)
        w[label] = (fwhm(nu, y, 0.0), fwhm(nu, y, 60.0))
    carrier = w["on"][0] - w["off"][0]
    dim = w["on"][1] - w["off"][1]
    assert carrier > 0.5, w                      # the model is doing something
    assert dim < carrier / 3.0, (carrier, dim)   # and it does far less to the dim tooth


def test_the_depth_ladder_holds_the_power_and_climbs_the_depth():
    mod = _load()
    cells = dict(mod.levers())
    cfg = cells["depth_ladder_40MHz"]
    assert cfg["ladder"] == "depth" and cfg["f_mod"] == 40.0
    for i, d in enumerate(mod.DEPTHS_2BETA):
        rcfg, p = mod._rung_cfg(cfg, i)
        assert rcfg["two_beta"] == d and p == cfg["p_top"]
    pcfg, p0 = mod._rung_cfg(cells["base"], 0)
    assert pcfg is cells["base"] and p0 == pytest.approx(mod.POWERS_W[0])


def test_the_area_sum_rule_is_flat_in_depth_and_quadratic_in_power():
    """The depth ladder's second null, on the producer's own helper.

    The tooth weights sum to one, so with the depletion off the summed area
    over a comb does not depend on the depth, while along a power ladder the
    two-photon area follows P squared. Both are checked on `_area` directly,
    which is what the producer accumulates per rung, so a change to the
    baseline or the clipping fails here.
    """
    import numpy as np
    from rb5s6s.forecast import build_world_trace
    from rb5s6s.ruler import bessel_tooth_weights
    mod = _load()
    L = {"cascade": False, "saturation": False, "stark": True, "bbr": False,
         "drift": False, "quantise": False, "randomise": False}
    kw = {**_kw(), "noise_frac_bright": 0.0, "offset": 0.0, "power_max_w": 0.225}

    def area_at(two_beta, power):
        w = bessel_tooth_weights(two_beta, slots=(0, 1, -1))
        tot = float(w[0] + w[1] + w[2])
        pos = {"4192": 0.0, "4192@+1": 40.0, "4192@-1": -40.0}
        sh = {k: 0.44 * float(w[i]) / tot for i, k in enumerate(pos)}
        kwr = {**kw, "positions": pos, "shares": sh}
        nu, y, _ = build_world_trace(power, 1.618, 130.0, 0, 1, np.random.default_rng(5), L,
                                     tooth_of={"4192@+1": "4192", "4192@-1": "4192"},
                                     grid_span=(-140.0, 140.0), **kwr)
        return mod._area(nu, y)

    flat = [area_at(tb, 0.225) for tb in (0.6, 1.2, 2.0)]
    assert max(flat) / min(flat) < 1.01, flat
    a1, a2 = area_at(1.2, 0.1125), area_at(1.2, 0.225)
    assert a2 / a1 == pytest.approx(4.0, rel=0.02)


def test_the_saturation_layer_is_wired_and_not_only_declared():
    """The layer table said saturation was on and
    `stark.COMPANIONS` was never set, so `companion_gamma_mhz` returned zero
    in every cell of the published file. A flag is not a term.

    Planted at both ends. With the parameters absent the width is exactly
    zero at a shift that should broaden the line by megahertz, which is the
    state that shipped; with them present it is large. A test asserting only
    that the module sets the attribute would pass against a value of None.
    """
    mod = _load()
    from rb5s6s import stark
    assert mod.LAYERS["saturation"] is True
    assert stark.COMPANIONS is not None, "the layer is declared and unwired"
    s0 = mod.stark_shift_S0_mhz(0.225, 16e-6, rho=0.94)
    assert s0 > 5.0, "the base cell's own shift, so the term has something to do"
    on = stark.companion_gamma_mhz(s0, "4192")
    assert on > 5.0, "power broadening at this shift is megahertz, not a rounding"
    saved = stark.COMPANIONS
    try:
        stark.COMPANIONS = None
        assert stark.companion_gamma_mhz(s0, "4192") == 0.0, (
            "the negative case: this is what the published file computed")
    finally:
        stark.COMPANIONS = saved
    assert stark.companion_gamma_mhz(0.0, "4192") == 0.0, "and zero at zero shift"


def test_a_monotone_acquisition_order_cannot_separate_the_drift_from_the_pull():
    """Eight of four hundred draws carried the
    channel's whole published scatter.

    The campaign's power ladder is equally spaced, so an acquisition order
    that ascends or descends with power is an exact affine function of it and
    the design is singular. Probed on BOTH sides of the refusal and at the
    threshold's own neighbourhood: a monotone order is far above the cut, a
    drawn one far below, and the gap is wide enough that the cut's value is
    not a tuning parameter."""
    mod = _load()
    P = np.asarray([p * 0.225 / 0.225 for p in mod.POWERS_W])
    assert np.allclose(np.diff(P), np.diff(P)[0]), "the ladder is equally spaced"

    def cond(order):
        return float(np.linalg.cond(np.column_stack([np.ones_like(P), P, np.asarray(order)])))

    up, down = cond(range(len(P))), cond(range(len(P) - 1, -1, -1))
    assert up > 1e12 and down > 1e12, "a monotone order is singular in both directions"
    drawn = cond([2, 0, 4, 1, 3])
    assert drawn < 1e3, "a genuinely drawn order is well conditioned"
    assert drawn < mod.COND_MAX < up, "the cut sits inside the empty gap"
    assert cond([0, 1, 2, 4, 3]) < mod.COND_MAX, (
        "one transposition away from monotone is already admitted")
    src = SCRIPT.read_text(encoding="utf-8")
    assert "np.linalg.cond(A)) > COND_MAX" in src, "the producer must apply it"


def test_a_skew_channel_that_falls_with_power_is_not_reported():
    """The third admission statistic. The ramp's third cumulant rises with
    power because the shift does, so a cell whose sets fit a NEGATIVE
    exponent is reading noise, however settled the sign of k3 happens to be.
    The base cell did exactly that once the saturation term was present:
    -1.0 against a quiet curve of +1.9.

    Planted either side of the refusal, since a one-sided probe would pass
    against a rule that refuses everything."""
    src = SCRIPT.read_text(encoding="utf-8")
    assert "if np.isfinite(_e) and _e <= 0.0:" in src, "the refusal must be live"
    assert "ok = np.isfinite(row) & (row != 0) & usable" in src, (
        "and taken over the ADMITTED rungs: fitted over every finite rung the "
        "slope reads about -1 in every configuration, because a windowed "
        "cumulant of pure noise is largest where the signal is smallest")

    def refuses(expo):
        e = np.asarray(expo, dtype=float)
        _e = float(np.nanmedian(e)) if np.isfinite(e).any() else float("nan")
        return bool(np.isfinite(_e) and _e <= 0.0)

    # Either side of the bar, and the two ends that decide its shape: a cell
    # with no exponent at all must NOT be refused, since fewer than three
    # admitted rungs is an absence and not a measured negative, and exactly
    # zero must be, since a channel that does not respond to power is not
    # reading the shift.
    for expo, want in (([-1.0, -0.9, -1.2], True), ([2.9, 3.1, 2.8], False),
                       ([0.4, 0.6, 0.5], False), ([-0.1, 0.0, 0.05], True),
                       ([0.0, 0.0, 0.0], True),
                       ([np.nan, np.nan, np.nan], False)):
        assert refuses(expo) is want, (expo, want)


def test_the_ladders_own_abscissa_is_what_every_slope_is_fitted_against():
    """Seven diagnostic columns on the two depth
    cells were regressed against log power, which those cells hold fixed at
    the top rung. The regressor now follows the ladder."""
    mod = _load()
    src = SCRIPT.read_text(encoding="utf-8")
    assert "lp = np.log(_x)" in src, "the abscissa follows the ladder"
    assert "P = np.asarray(powers); lp = np.log(P)" not in src, "and not the power ladder"
    for name, cfg in mod.levers():
        if cfg.get("ladder") == "depth":
            _, p_first = mod._rung_cfg(cfg, 0)
            _, p_last = mod._rung_cfg(cfg, len(mod.DEPTHS_2BETA) - 1)
            assert p_first == p_last == cfg["p_top"], (
                f"{name}: a depth cell holds the power, so log power is no axis")
            break
    else:
        raise AssertionError("no depth cell to check")
