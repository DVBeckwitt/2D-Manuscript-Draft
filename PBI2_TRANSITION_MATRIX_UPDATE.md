# PbI2 transition-matrix manuscript update

This revision replaces the superseded scalar slip/flip model with the
six-state, direction-resolved transition-matrix model supplied on 2026-06-23.

## Main manuscript

- Preserved the experimental PbI2 detector-image and disorder-series narrative.
- Replaced the scalar `p_flip`, `z/f/psi`, and `R_N` formulation with six
  registry/orientation states and five allowed interface events.
- Added the exact rod-dependent 6x6 to 2x2 reduction used in the calculation.
- Added 2H-, 4H-, and 6H-rich population laws with one `epsilon_j` per
  population and normalized incoherent population weights.
- Corrected the interpretation of the m=0 rod: stacking faults are
  contrast-matched on this channel rather than physically absent.
- Replaced the abstract parent-cycle schematic with projected 2H, 4H, and 6H
  I--Pb--I stacks labeled directly as $rF_\sigma$ states, and expanded the
  Figure 11 caption to connect the atomic geometry to the transition events.
- Removed the previous `p=0.18`, `N=32`, and `2H:6H=0.76:0.24` report because
  those values do not transform uniquely into the new parameterization.

## Supporting information

- Replaced the entire no-correlation scalar derivation with the full six-state
  transition matrix, exact Fourier reduction, finite-stack intensity,
  deterministic parent checks, fault templates, population mixture, and m=0
  Laue-factor limit.
- Added calculation-only validation figures from the supplied derivation and
  marked them explicitly as non-experimental examples.
- Updated the detector-derived disorder objective to call the new finite-stack
  transition-matrix intensity.

## References

- Completed the existing Hendricks--Teller and Treacy entries with titles,
  complete page ranges, and DOIs.
- Added Kakinoki--Komura (1954, 1965) and Hart--Hansen--Kuhs (2018) for the
  general transition-matrix/Markov derivation.
- Retained Minagawa (1975) and Palosz (1990) for PbI2 polytype structures.

## Remaining numerical task

The supplied method package contains illustrative calculations but not an
unambiguous experimental set of `epsilon_2H`, `epsilon_4H`, `epsilon_6H`,
`w_2H`, `w_4H`, and `w_6H`.  The manuscript therefore leaves those numerical
values pending a refit rather than inventing or converting values from the old
scalar model.
