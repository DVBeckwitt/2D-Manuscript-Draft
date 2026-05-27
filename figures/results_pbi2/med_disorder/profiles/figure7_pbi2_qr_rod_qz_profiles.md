# PbI2 4° HK-rod L profiles

Source state: `C:\Users\Kenpo\.local\share\ra_sim\PbI2.json`
Active lattice: `a=4.59 A`, `c=6.78 A`, source=`state.variables`.
Rod reference policy: `allow_generated=False`, saved=`4`, generated=`0`, skipped_generated=`0`.
Tilt used for Q conversion: `4°`
Source Delta $Q_r$: `0.1529` Å^-1
Active Delta $Q_r$: `0.13` Å^-1 (`0.85` x source)
Detector-rotation calibration is Qr-driven for centerline overlay alignment: success=`False`, non-specular fitted peaks=`2`, active peaks=`2`.
Detector distance for rod Q-space: `0.075` m -> `0.075` m.
Qr RMS: `nan` -> `nan` Å^-1; Qz diagnostic RMS: `nan` -> `nan` Å^-1.
Displayed/integrated detector support is limited to `2theta <= 71.3°` and `Qz > 0`.
Phi signs: `-` and `+`.

The figure uses only the 4° background. Non-specular traces are integrated directly in detector Qr/Qz space.
Nonzero rods use detector Q maps at `theta_i = 4°`.
m = 0 ROI uses caked phi/2theta bounds `phi=[-10, 10]°`, `2theta=[5, 55]°`; its final L axis is autoscaled from the accepted ROI trace.
Before integration, each non-specular HK rod center is adjusted from fitted detector peak Qr samples; every Qz bin then uses the adjusted Qr0 +/- delta_Qr, branch, positive Qz, and the 2theta display limit before summing intensity.
The detector-region figure is a detector-space Qr overlay diagnostic: the background is linear detector intensity with robust percentile clipping, translucent ribbons show the active Delta Qr support with dashed boundary strokes, solid curves are projected fitted-geometry rod centerlines, and solid-white m labels start from the default geometry before manual adjustment; the intensity scale is saved as a separate file.
The plotted traces are acceptance-normalized detector-count densities unless BACKGROUND_SOLID_ANGLE_CORRECTION is enabled. Raw summed columns are retained for audit only.
Solid-angle correction enabled: `False`.
Background image subtraction disabled: `True`. When enabled, saved `peak_subtracted` image products are raw background images.
Qr-sideband transverse background subtraction enabled: `False`. When enabled, `background_density_raw` is the central rod-band density, `qr_sideband_background_density` is the same-Qz off-rod estimate, and `background_density` is their difference.
PbI2 no-background debug mode: `False`. When enabled, PbI2 Qr-rod transverse sideband subtraction is forced off and raw `background_density` remains the plotted data.
When caked sum fields are available, density uses sum_signal / sum_normalization. Otherwise it falls back to acceptance weights, then pixel_count.
For every Qr-rod panel, plotted `Data` is the GUI-integrated `background_density`; the dashed trace is the same data smoothed along L.
Qr-rod profile plots use log-scaled intensity only for `HK=0`; nonzero HK panels use linear intensity and display `0.5 <= L <= 3`.
Peak fitting is disabled for the final Qr-rod profile figure; the component CSV is retained as an empty compatibility artifact.
The CSV includes `smoothed_background_density`, generated from the accepted GUI trace with the final smoothing slider value.
The detector-space fit model remains in the CSV as `fit_density` for audit only.
Subplot labels show `m = H^2 + H*K + K^2`.
Nonzero-m masks still use detector-space Qr/Qz internally and extend to the projected sign endpoint.
The detector-region figure labels the specular rod as `m = 0`; the displayed support is the same phi/2theta ROI arc used for profile extraction.
Hidden Qr-rod subplot HK values: `7`.

## Rods

| HK | source | generated | saved Qr | active fit peaks | fit samples | method | marker count |
|---:|:---|:---:|---:|---:|---:|:---|---:|
| 1 | saved_q_group_rows | False | 1.5807 | 0 | 2 | saved_q_group_rows_insufficient_detector_rotation_anchors | 9 |
| 3 | saved_q_group_rows | False | 2.7378 | 0 | 0 | saved_q_group_rows_no_fit_points | 8 |
| 4 | saved_q_group_rows | False | 3.1613 | 0 | 0 | saved_q_group_rows_no_fit_points | 9 |
| 7 | saved_q_group_rows | False | 4.182 | 0 | 0 | saved_q_group_rows_no_fit_points | 7 |

Specular `(0,L)` rod uses `Qr = 0` and the dynamic specular strip.

## Fitted detector geometry

| parameter | original | fitted |
|:---|---:|---:|
| theta_i_deg | 4 | 4 |
| detector_distance_m | 0.075 | 0.075 |
| gamma_deg | 5.0643 | 5.0643 |
| Gamma_deg | 0.123 | 0.123 |
| rotation_bound_hit | False | False |

## Final profile plot policy

Peak fitting and marker placement overlays are disabled for the final Qr-rod profile figure.
Each panel plots the GUI-integrated `background_density` trace plus the same trace after Gaussian smoothing.
Gaussian smoothing sigma: `1` bins.
Curvature-adaptive smoothing strength: `0`.
