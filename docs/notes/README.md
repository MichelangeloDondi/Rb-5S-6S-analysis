# The working notes

Five of the eight files here are preregistrations. A preregistration is a
specification written and committed before the run whose outcome it scores. The
estimator, the thresholds, the trace census and the stop conditions are fixed in
the record while the answer is still unknown, so the run can only confirm them
or fail them. That ordering is what makes the outcome interpretable, because a
threshold chosen after seeing a fit scores nothing. The outcomes themselves are
reported in [PREREGISTRATION_RESULTS.md](../PREREGISTRATION_RESULTS.md), which
is where a prediction is marked against what happened and where the dated
addenda live, including the ones that record a failure. The remaining three
files were written after the fact rather than before: one design study of a
measurement that does not exist, and two records that close a question the
analysis had left open.

| file | what it specifies or records | kind |
|---|---|---|
| [beta_self_pooling_prereg.md](beta_self_pooling_prereg.md) | One shared self-broadening slope across the four 993 nm hyperfine lines in place of four independent fits: the physics that licenses the pooling, the pooled estimator and its variance, the scope, and the predictions the implementation then had to meet. | preregistration |
| [full_archive_fit_prereg.md](full_archive_fit_prereg.md) | The joint fit over every canonical trace, with the collisional width held under a prior and one profiled light-shift coefficient: trace census, parameter hierarchy, priors, load-time quality checks, the coefficient grid, the profile families and seeding order, and the acceptance criteria. | preregistration |
| [m28_reproducibility_prereg.md](m28_reproducibility_prereg.md) | A re-run of that same fit on bit-identical inputs, to separate a genuine response to recalibrated inputs from optimizer chain variation. The reproduction threshold, 3 per cent, is fixed before the run. | preregistration |
| [ruler_validity_and_trim_prereg.md](ruler_validity_and_trim_prereg.md) | The frequency ruler's tooth-labelling rule, the re-index ladder and its acceptance ceiling, the residual-tail trimmer and its null calibration, the outlier rule, and the eligibility conditions for two figures. Eight dated amendments follow the original text, and the opening table gives the current state of every rule. | preregistration |
| [s0_block_bootstrap_prereg.md](s0_block_bootstrap_prereg.md) | A block bootstrap of the power-lever light-shift limit, stratified by peak, as the sharper alternative to carrying block-to-block over-dispersion as one global factor. The resample count and the seed are frozen with the script that implements them. | preregistration |
| [guided_mode_two_photon_design.md](guided_mode_two_photon_design.md) | What changes if the same two-photon measurement runs in a hollow-core fibre instead of a vapour cell: how the intensity is delivered, trap shifts and vibrational structure, the signal and background budgets, a readout comparison, fibre feasibility, and what would have to be measured before any of it is a plan. Nothing in it is scheduled, agreed or costed. | design note |
| [transit_width_resolved.md](transit_width_resolved.md) | How the transit-width tension was settled: one missing crossing-flux factor in the transit Monte Carlo, the closed-form validation of the fix, and the beam-waist prior moving from 32 to about 50 µm and then to the adopted 64 µm. An earlier reading of the same evidence is retracted in place and labelled. | record |
| [vdw_difference_potential_and_4d_channel.md](vdw_difference_potential_and_4d_channel.md) | Which van der Waals coefficient enters the self-broadening anchor, the difference rather than the upper pair coefficient, with the derivation in the source, the numbers that moved, and the sites still carrying the earlier value. Its last section records the 6S to 4D interval as a candidate inelastic channel that nothing in the pipeline depends on. | record |

The notes are append-only. A correction enters as a dated addition, an
amendment or a postscript placed after the original text, and the passage that
stated the prediction is left exactly as it was written. Where an amendment
changes a rule, the amendment governs and the superseded wording stays visible,
so what was fixed in advance of the data can be told apart from what was fixed
after it. Editing a prediction into agreement with its outcome would leave a
document that reads as though it had always been right.
