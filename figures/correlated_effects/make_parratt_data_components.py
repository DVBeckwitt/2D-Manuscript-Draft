#!/usr/bin/env python3
"""Create one overlaid measured/Parratt/kinematic reflectivity plot."""
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import medfilt, savgol_filter

HERE = Path(__file__).resolve().parent
OUT = HERE / "fig_reflectivity_data_parratt_kinematic.png"


def smooth_log(y, window=9):
    y = np.asarray(y, float)
    return 10 ** savgol_filter(np.log10(y), window, 2)


def interpolate_log(x, xp, fp):
    return 10 ** np.interp(x, xp, np.log10(fp))


def range_mask(values, lower, upper):
    return (values >= lower) & (values <= upper)


measured = pd.read_csv(HERE / "measured_m0_trace_from_figure9.csv")
model = pd.read_csv(HERE / "parratt_kinematic_traces_from_previous_figure8.csv")

L_data = measured["L"].to_numpy(float)
I_data = smooth_log(measured["measured_intensity_trace"].to_numpy(float))
# Remove the narrow vertical-grid-line artifact in the digitized measured trace.
gap = range_mask(L_data, 0.94, 1.08)
left = np.where(L_data < 0.94)[0][-1]
right = np.where(L_data > 1.08)[0][0]
I_data[gap] = interpolate_log(
    L_data[gap],
    [L_data[left], L_data[right]],
    [I_data[left], I_data[right]],
)
background = np.nanmin(I_data[range_mask(L_data, 0.75, 1.15)])
I_data = np.clip(I_data - background, 1e-8, None)
I_data /= np.nanmax(I_data[range_mask(L_data, 0.19, 1.05)])

L_model = model["L"].to_numpy(float)
I_parratt = model["parratt_trace"].to_numpy(float)
# Bridge only the interval hidden by the old panel label.
I_parratt[range_mask(L_model, 0.223, 0.336)] = np.nan
finite = np.isfinite(I_parratt) & (I_parratt > 0)
I_parratt = interpolate_log(L_model, L_model[finite], I_parratt[finite])
I_parratt = 10 ** medfilt(np.log10(np.clip(I_parratt, 1e-12, None)), 7)

raw_kinematic = model["kinematic_trace"].to_numpy(float)
I_kinematic = np.full_like(raw_kinematic, np.nan)
resolved = np.isfinite(raw_kinematic) & (raw_kinematic > 0) & (L_model >= 0.54)
kin_log = medfilt(np.log10(raw_kinematic[resolved]), 7)
kin_log = savgol_filter(kin_log, 15, 2)
kin_values = np.minimum.accumulate(10 ** kin_log)
I_kinematic[resolved] = kin_values
# The upper branch is clipped/obscured in the source raster; retain its visible plateau.
plateau = np.nanmax(raw_kinematic[range_mask(L_model, 0.53, 0.55)])
I_kinematic[(L_model >= 0.40) & (L_model < 0.54)] = plateau

fig, ax = plt.subplots(figsize=(10.5, 5.9), constrained_layout=True)
data_range = range_mask(L_data, 0.19, 1.05)
model_range = range_mask(L_model, 0.19, 1.05)
ax.semilogy(L_data[data_range], I_data[data_range], "k-", lw=2.4,
            label="Measured, background subtracted")
ax.semilogy(L_model[model_range], I_parratt[model_range], color="0.3",
            ls=":", lw=2.6, label="Parratt calculation")
ax.semilogy(L_model[model_range], I_kinematic[model_range], color="#56B4E9",
            ls="--", lw=2.8, label="Kinematic finite-stack calculation")
ax.set(xlim=(0.18, 1.05), ylim=(1e-4, 3.0), xlabel=r"$L$",
       ylabel="Normalized intensity")
ax.legend(frameon=False, loc="upper right")
ax.grid(True, which="both", alpha=0.25)
fig.savefig(OUT, dpi=600, facecolor="white")
print(OUT)
