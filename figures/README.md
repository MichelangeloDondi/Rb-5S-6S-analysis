# The figures

Every PNG in this directory is generated, and each one is rebuilt from the
repository rather than kept as a saved plot from an interactive session. Most
are drawn by [`scripts/make_figures.py`](../scripts/make_figures.py), which
reads the committed CSVs under [`results/`](../results/README.md) and computes
every number it prints. Two figures have their own producers.
`fig0_spectrum.png` comes from
[`scripts/make_fig0_spectrum.py`](../scripts/make_fig0_spectrum.py), which
reloads one condition's repeats from the raw archive and re-runs the joint fit
end to end. `fig9_polarizability_ladder.png` comes from
[`scripts/run_polarizability_ladder.py`](../scripts/run_polarizability_ladder.py),
which sums over states in `rb5s6s/polarizability.py` and writes nothing to
`results/`. The four fit galleries (fig16, fig18, fig21 and fig22) take their
shared parameters from `results/global_archive_fit.csv` and the traces
themselves from [`data_raw/`](../data_raw/README.md), refitting only each
trace's own amplitude, centre, background and detector saturation.

To redraw them:

```
python scripts/make_fig0_spectrum.py
python scripts/make_figures.py
python scripts/run_polarizability_ladder.py
```

The first two lines are the figure steps of
[`scripts/run_all.sh`](../scripts/run_all.sh), so a full pipeline run already
produces them. The third is run on its own.

Each figure that `make_figures.py` writes carries a fingerprint of the
results CSVs in its PNG metadata, stamped at save time.
[`tests/test_figures_fresh.py`](../tests/test_figures_fresh.py) reads that
stamp back for the data-driven figures and fails when a committed PNG was
drawn from results that have since moved, which makes the check independent
of the matplotlib version that drew the figure. The two figures with their own
producers carry no stamp, and `fig0_spectrum.png` is exempt by design because
it is drawn from the frozen raw archive. Every figure also carries a footer
line naming the sources it is drawn from and the command that regenerates it.

Ten figures are cited by no document. Their rows below name the claim they
support instead of a citing passage.

| file | what it shows | drawn by | discussed in |
|---|---|---|---|
| `fig0_spectrum.png` | one fitted spectrum, the 993.4192 nm line at 130 °C and 225 mW, with the composite model overlaid and a residual panel | `make_fig0_spectrum.py` | [README.md](../README.md) |
| `fig1_width_vs_density.png` | total line width at half maximum against vapour density, one series per hyperfine component, with cell temperature on the top axis | `make_figures.py` | [methods/07_what_we_found.md](../docs/methods/07_what_we_found.md) |
| `fig2_power_sweep.png` | width and amplitude against drive power, the amplitude following the two-photon square law and the width carrying no significant slope | `make_figures.py` | [methods/07_what_we_found.md](../docs/methods/07_what_we_found.md) |
| `fig3_transit_mc.png` | the Monte Carlo transit contribution against beam waist, with the waist at which it would account for the observed total | `make_figures.py` | [README.md](../README.md), [PLAN.md](../docs/PLAN.md) |
| `fig4_amplitude_ratios.png` | within-isotope area ratios against the parameter-free degeneracy law | `make_figures.py` | [methods/07_what_we_found.md](../docs/methods/07_what_we_found.md) |
| `fig5_pooled_width.png` | the four components pooled into one width budget against density, with the shared laser width against temperature beside it | `make_figures.py` | cited nowhere. Supports the self-broadening bound, [RESULTS.md](../docs/RESULTS.md) C1, by showing the pooled trend the individual components are too noisy to carry |
| `fig6_gamma_floor.png` | the fitted collisional width rising about 1.5-fold while the density rises 52-fold, which is why the coefficient is read as a floor | `make_figures.py` | [README.md](../README.md), [PLAN.md](../docs/PLAN.md) |
| `fig7_identifiability_profile.png` | the profile-likelihood map of the collisional-width and laser-width degeneracy, the wide topology and a zoom against the local covariance ellipse | `make_figures.py` | [methods/06_the_statistics.md](../docs/methods/06_the_statistics.md) |
| `fig8_ruler.png` | one EOM ruler trace with its constrained seven-tooth comb fit, and the free-centres nonlinearity map beside it | `make_figures.py` | [methods/05_the_frequency_ruler.md](../docs/methods/05_the_frequency_ruler.md) |
| `fig9_polarizability_ladder.png` | the polarizability difference against wavelength for the 5S to 6S and 5S to 7S ladders, each drive marked and each crossing labelled | `run_polarizability_ladder.py` | [BIG_PICTURE.md](../docs/BIG_PICTURE.md) |
| `fig10_degeneracy_vs_observable.png` | the twenty power-sweep conditions as error ellipses over contours of constant total width, and the same conditions' total width against power | `make_figures.py` | [BIG_PICTURE.md](../docs/BIG_PICTURE.md), [RESEARCH_DECISIONS.md](../docs/RESEARCH_DECISIONS.md) |
| `fig11_laser_history.png` | the campaign's laser frequency within each run of unchanged scope-window setting, with a visible break at every setting change, the one long untouched stretch, and the within-epoch step distribution | `make_figures.py` | cited nowhere. Supports the drift limitation in [DATA.md](../docs/DATA.md): an offset means nothing across a setting change, and within one setting the excursion is about 1 MHz |
| `fig12_ramp_construction.png` | how the intensity profile of a focused Gaussian beam becomes a triangular light-shift distribution, in four steps, with no data and no fitted parameters | `make_figures.py` | [THEORY_NOTE.md](../docs/THEORY_NOTE.md), [PLAN.md](../docs/PLAN.md) |
| `fig13_level_scheme.png` | which levels are driven and which arm is detected, in the term-diagram idiom, with the digitised cavity scan in side panels | `make_figures.py` | [methods/01_the_measurement.md](../docs/methods/01_the_measurement.md), [APPARATUS.md](../docs/APPARATUS.md) |
| `fig14_wavemeter_reconstruction.png` | the 2025-06-11 wavemeter record, the sawtooth model fitted to it, and the resulting floor on unmodelled laser motion | `make_figures.py` | [APPARATUS.md](../docs/APPARATUS.md), [PREREGISTRATION_RESULTS.md](../docs/PREREGISTRATION_RESULTS.md) |
| `fig15_drift_story.png` | the drift problem photographed, the campaign record reconstructed from its own traces, and what each drift regime licenses | `make_figures.py` | [README.md](../README.md), [PLAN.md](../docs/PLAN.md) |
| `fig16_fit_gallery.png` | the brightest campaign trace of each component against the committed shared model, with residuals, four panels in one frame | `make_figures.py` | [README.md](../README.md) |
| `fig17_magic_wavelengths.png` | the 5S and 6S polarizabilities and their difference, with the three zero crossings and each crossing's Monte Carlo band | `make_figures.py` | [README.md](../README.md) |
| `fig18_single_4121.png` | one full-page panel for the 993.4121 nm component: the same trace and shared model as fig16, with a parameter box naming every number as shared or per-trace | `make_figures.py` | cited nowhere. Supports the composite lineshape model of [methods/04_the_composite_model.md](../docs/methods/04_the_composite_model.md), whose shared and per-trace split the parameter box states |
| `fig18_single_4154.png` | the same panel for the 993.4154 nm component | `make_figures.py` | cited nowhere. Supports [methods/04_the_composite_model.md](../docs/methods/04_the_composite_model.md), as above |
| `fig18_single_4192.png` | the same panel for the 993.4192 nm component | `make_figures.py` | cited nowhere. Supports [methods/04_the_composite_model.md](../docs/methods/04_the_composite_model.md), as above |
| `fig18_single_4207.png` | the same panel for the 993.4207 nm component | `make_figures.py` | cited nowhere. Supports [methods/04_the_composite_model.md](../docs/methods/04_the_composite_model.md), as above |
| `fig19_width_trends.png` | the two broadening laws side by side: raw contiguous width against density for all four components, drawn as the headline self-broadening estimator itself fits it, with the pilot point outside the fit and the licensing of each candidate source stated on the panel, and beside it the same widths against drive power under the thin wedge of growth the light-shift bound still permits | `make_figures.py` | cited nowhere. Supports the self-broadening bound, [RESULTS.md](../docs/RESULTS.md) C1, and is the only figure that draws that estimator's own construction |
| `fig20_method_loop.png` | a schematic of the method: an observation, an identifiability test, then either a claim or a named limitation and the measurement that lifts it, with two worked examples from this archive beneath | `make_figures.py` | cited nowhere. Supports the framing of [BIG_PICTURE.md](../docs/BIG_PICTURE.md), that the bounds and the limitations they name are the result |
| `fig21_joint_fit_five.png` | five repeats of one condition under a single shared line shape, the shared widths in the header with the four per-repeat parameters named beside them, and each row printing its own fitted centre, peak height and reduced chi-squared | `make_figures.py` | cited nowhere. Supports the shared-shape archive fit preregistered in [notes/full_archive_fit_prereg.md](../docs/notes/full_archive_fit_prereg.md) |
| `fig22_joint_fit_twenty.png` | the same shared line shape across all twenty campaign power-sweep conditions, brightest repeat each, nothing retuned per panel | `make_figures.py` | cited nowhere. Supports the same fit as fig21, [notes/full_archive_fit_prereg.md](../docs/notes/full_archive_fit_prereg.md) |

The colour of a component is fixed across every panel here, so a colour means
the same hyperfine line wherever it appears. Absolute widths ride on the open
beam waist, and the figures that carry one say so on their face.
