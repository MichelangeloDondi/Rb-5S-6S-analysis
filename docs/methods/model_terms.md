# The model-terms registry

Generated from `rb5s6s/model_registry.py` by `scripts/make_model_terms.py`. Do not edit this page by hand: `tests/test_model_registry.py` refuses a committed copy that disagrees with the module.

One row per physical term of the forward model, naming which of the three computation paths carries it: the fitter (`rb5s6s/fullmodel.py`'s `full_profile` and the ultra-joint `Cell` of `scripts/run_ultra_joint.py`, `rb5s6s/beta.py`'s `fit_beta_self`, `rb5s6s/linefit.py`'s `fit_condition`), the joint twin of record (`rb5s6s/volume_line.py` through `rb5s6s/twin_volume.py`), and the kernel Monte Carlo (`scripts/run_kernel_mc.py`), at the archive's own 2025 conditions and at the proposed campaign's. A status of `carried` names its own code site in the `impl` column beside it. `owed`, `neglected`, `absorbed` and `n/a` are read in full in `rb5s6s/model_registry.py`'s own module docstring, and the six-status detail, the physics, the parameter names, the thesis anchor and the evidence for every row live in `results/model_terms.csv`, not repeated here. Registry digest (the joint twin's own 2025 carried set): `9d2de0da6f05ce4c`.

| term | fitter 2025 | fitter campaign | twin 2025 | twin campaign | mc 2025 | mc campaign | impl (fitter) | impl (twin) | impl (mc) |
|---|---|---|---|---|---|---|---|---|---|
| natural_width | carried | carried | carried | carried | carried | carried | rb5s6s.lineshape:model_profile | rb5s6s.volume_line:joint_spectrum | scripts.run_kernel_mc:run_node |
| transit | carried | carried | carried | carried | carried | carried | rb5s6s.lineshape:model_profile | rb5s6s.volume_line:sample_atoms | scripts.run_kernel_mc:run_node |
| transit_chirp | owed:odd-channel-chirp | owed:odd-channel-chirp | carried | carried | owed:odd-channel-chirp | owed:odd-channel-chirp | rb5s6s.fullmodel:full_profile | rb5s6s.volume_line:joint_spectrum | - |
| laser_kernel | carried | carried | carried | carried | n/a | n/a | rb5s6s.lineshape:model_profile | rb5s6s.volume_line:joint_spectrum | - |
| self_broadening_vdw | carried | carried | carried | carried | n/a | n/a | rb5s6s.beta:fit_beta_self | rb5s6s.volume_line:joint_spectrum | - |
| self_broadening_T03 | owed:beta-self-temperature-law | owed:beta-self-temperature-law | owed:beta-self-temperature-law | owed:beta-self-temperature-law | n/a | n/a | - | - | - |
| foreign_gas | absorbed:gamma_l | absorbed:gamma_l | absorbed:gamma_hom_mhz | absorbed:gamma_hom_mhz | n/a | n/a | rb5s6s.lineshape:permeated_gas_width_mhz | - | - |
| ac_stark_ramp | carried | carried | carried | carried | carried | carried | rb5s6s.fullmodel:full_profile | rb5s6s.volume_line:joint_spectrum | scripts.run_kernel_mc:run_node |
| doppler_pedestal | absorbed:baseline | absorbed:baseline | owed:doppler-pedestal-in-twin | owed:doppler-pedestal-in-twin | n/a | n/a | rb5s6s.fullmodel:doppler_pedestal_fwhm_mhz | rb5s6s.forecast:build_world_trace | - |
| saturation | carried | carried | owed:saturated-arm | owed:saturated-arm | carried | carried | rb5s6s.fullmodel:saturation_companion_mhz | - | rb5s6s.platforms:excitation_rate_per_atom |
| hyperfine_pumping | carried | carried | owed:saturated-arm | owed:saturated-arm | carried | carried | rb5s6s.fullmodel:saturation_companion_mhz | - | rb5s6s.cascade:BRANCHING_F |
| companion_pull_reduction | owed:companion-pull-reduction | owed:companion-pull-reduction | owed:companion-pull-reduction | owed:companion-pull-reduction | carried | carried | - | - | scripts.run_kernel_mc:run_node |
| axial_collection_window | owed:collection-window-in-fitter | owed:collection-window-in-fitter | carried | carried | carried | carried | scripts.run_ultra_joint:window_profile | rb5s6s.volume_line:sample_atoms | scripts.run_kernel_mc:run_node |
| bore_clipping | owed:bore-limited-recompute | owed:bore-limited-recompute | owed:bore-limited-recompute | owed:bore-limited-recompute | carried | carried | rb5s6s.lineshape:aperture_onaxis_factor_actual | - | rb5s6s.beam_field:ClippedBeam |
| retro_mismatch | owed:retro-waist | owed:retro-waist | owed:retro-waist | owed:retro-waist | n/a | n/a | rb5s6s.fullmodel:fringe_survival_mc | - | - |
| retro_offset | owed:retro-waist | owed:retro-waist | owed:retro-waist | owed:retro-waist | n/a | n/a | rb5s6s.fullmodel:fringe_survival_mc | - | - |
| fringe_tail | owed:fringe-resolved-skew | owed:fringe-resolved-skew | owed:fringe-resolved-skew | owed:fringe-resolved-skew | n/a | n/a | rb5s6s.fullmodel:fringe_survival_mc | - | - |
| retro_tilt | absorbed:sigma_laser_fwhm | absorbed:sigma_laser_fwhm | owed:retro-tilt-in-twin | owed:retro-tilt-in-twin | n/a | n/a | rb5s6s.fullmodel:residual_doppler_fwhm_mhz | - | - |
| beam_quality_m2 | owed:collection-window-in-fitter | owed:collection-window-in-fitter | carried | carried | carried | carried | scripts.run_ultra_joint:window_profile | rb5s6s.volume_line:GaussianBeam | scripts.run_kernel_mc:run_node |
| collisional_shift | absorbed:centre_mhz | absorbed:centre_mhz | absorbed:centre_mhz | absorbed:centre_mhz | n/a | n/a | rb5s6s.linefit:fit_condition | rb5s6s.twin_volume:synthetic_traces | - |
| second_order_doppler | neglected:4e-4-MHz | neglected:4e-4-MHz | owed:second-order-doppler | owed:second-order-doppler | n/a | n/a | - | - | - |
| blackbody | absorbed:centre_mhz | absorbed:centre_mhz | owed:blackbody-in-twin | owed:blackbody-in-twin | n/a | n/a | rb5s6s.fullmodel:full_profile | rb5s6s.forecast:build_world_trace | - |
| two_photon_absorption | owed:drive-depletion | owed:drive-depletion | owed:drive-depletion | owed:drive-depletion | n/a | n/a | - | - | - |
| kerr_lens | owed:kerr-lens-moments | owed:kerr-lens-moments | owed:kerr-lens-moments | owed:kerr-lens-moments | n/a | n/a | - | - | - |
| radiation_trapping | absorbed:amplitude | absorbed:amplitude | absorbed:amplitude | absorbed:amplitude | n/a | n/a | - | rb5s6s.forecast:build_world_trace | - |
| photoionisation | owed:photoionisation-channel | owed:photoionisation-channel | owed:photoionisation-channel | owed:photoionisation-channel | n/a | n/a | - | - | - |
| depletion_cascade | owed:saturated-arm | owed:saturated-arm | owed:saturated-arm | owed:saturated-arm | carried | owed:kernel-gate-node-coverage | rb5s6s.kernel_gate:depletion_factor | - | scripts.run_kernel_mc:run_node |
| hyperfine_shares | owed:hyperfine-shares-untied | owed:hyperfine-shares-untied | owed:hyperfine-shares-untied | owed:hyperfine-shares-untied | carried | carried | - | rb5s6s.forecast:build_world_trace | rb5s6s.amplitudes:predicted_shares |
| quench_4D | owed:beta-envelope | owed:beta-envelope | owed:beta-envelope | owed:beta-envelope | owed:beta-envelope | owed:beta-envelope | - | - | - |
| speed_dependent_collisional_shift | owed:speed-dependent-collisions | owed:speed-dependent-collisions | owed:speed-dependent-collisions | owed:speed-dependent-collisions | owed:speed-dependent-collisions | owed:speed-dependent-collisions | - | - | - |
| speed_dependent_collisional_width | owed:speed-dependent-collisions | owed:speed-dependent-collisions | owed:speed-dependent-collisions | owed:speed-dependent-collisions | owed:speed-dependent-collisions | owed:speed-dependent-collisions | - | - | - |
| resonant_exchange_by_line_share | owed:resonant-exchange-by-line | owed:resonant-exchange-by-line | owed:resonant-exchange-by-line | owed:resonant-exchange-by-line | owed:resonant-exchange-by-line | owed:resonant-exchange-by-line | - | - | - |
| pump_depletion | owed:pump-depletion-lineshape | owed:pump-depletion-lineshape | owed:pump-depletion-lineshape | owed:pump-depletion-lineshape | owed:pump-depletion-lineshape | owed:pump-depletion-lineshape | - | - | - |
| population_lens | owed:population-lens | owed:population-lens | owed:population-lens | owed:population-lens | owed:population-lens | owed:population-lens | - | - | - |
