from __future__ import annotations

import math
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import PowerNorm
from PIL import Image
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
FIGURES = ROOT / 'figures'

MEAN_WAVELENGTH_A = 1.540592925
K0 = 2.0 * math.pi / MEAN_WAVELENGTH_A
K_INTERNAL = 4.078341
INCIDENCE_DEG = 5.0
REF_C = 1453.12
REF_R = 1596.422
PITCH_M = 1.0e-4
DETECTOR_DISTANCE_M = 0.075


def sample_from_lab_matrix() -> np.ndarray:
    angle = math.radians(INCIDENCE_DEG)
    return np.array([
        [1.0, 0.0, 0.0],
        [0.0, math.cos(angle), math.sin(angle)],
        [0.0, -math.sin(angle), math.cos(angle)],
    ])


R_SAMPLE_FROM_LAB = sample_from_lab_matrix()
KI = np.array([
    0.0,
    K0 * math.cos(math.radians(INCIDENCE_DEG)),
    -math.sqrt(max(K_INTERNAL**2 - (K0 * math.cos(math.radians(INCIDENCE_DEG)))**2, 0.0)),
])


def detector_grid_to_q(width: int, height: int, extent: tuple[float, float, float, float]):
    cmin, cmax, rmin, rmax = extent
    c = cmin + (np.arange(width) + 0.5) * (cmax - cmin) / width
    r = rmin + (np.arange(height) + 0.5) * (rmax - rmin) / height
    C, R = np.meshgrid(c, r, indexing='xy')
    x_lab = (C - REF_C) * PITCH_M
    y_lab = np.full_like(x_lab, DETECTOR_DISTANCE_M)
    z_lab = -(R - REF_R) * PITCH_M
    ray = np.stack([x_lab, y_lab, z_lab], axis=-1)
    ray /= np.linalg.norm(ray, axis=-1, keepdims=True)
    ray_sample = np.einsum('ij,...j->...i', R_SAMPLE_FROM_LAB, ray)
    kx = K0 * ray_sample[..., 0]
    ky = K0 * ray_sample[..., 1]
    radicand = K_INTERNAL**2 - kx**2 - ky**2
    valid = radicand >= 0
    kz = np.sqrt(np.maximum(radicand, 0.0))
    kf = np.stack([kx, ky, kz], axis=-1)
    return kf - KI, valid


def sphere_wireframe(ax):
    phi = np.linspace(0.0, 2.0 * math.pi, 60)
    theta = np.linspace(0.0, math.pi, 32)
    pp, tt = np.meshgrid(phi, theta)
    x = K_INTERNAL * np.sin(tt) * np.cos(pp) - KI[0]
    y = K_INTERNAL * np.sin(tt) * np.sin(pp) - KI[1]
    z = K_INTERNAL * np.cos(tt) - KI[2]
    ax.plot_wireframe(x, y, z, rstride=2, cstride=4, color='0.58', linewidth=0.30, alpha=0.19)


def equal_3d(ax, xlim, ylim, zlim):
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_zlim(*zlim)
    ax.set_box_aspect((xlim[1]-xlim[0], ylim[1]-ylim[0], zlim[1]-zlim[0]))
    ax.set_proj_type('ortho')


def decode_magma_parameter(image: Image.Image) -> tuple[np.ndarray, np.ndarray]:
    rgb = np.asarray(image.convert('RGB'), dtype=np.float64) / 255.0
    lut_t = np.linspace(0.0, 1.0, 4096)
    lut_rgb = matplotlib.colormaps['magma'](lut_t)[:, :3]
    tree = cKDTree(lut_rgb)
    _, index = tree.query(rgb.reshape(-1, 3), k=1)
    scalar = lut_t[index].reshape(rgb.shape[:2])
    foreground = np.max(rgb, axis=-1) > 0.025
    return scalar, foreground


def add_contrast_patch(ax, image_path: Path, extent):
    image = Image.open(image_path).convert('RGB').resize((620, 720), Image.Resampling.BICUBIC)
    scalar, foreground = decode_magma_parameter(image)
    q, valid = detector_grid_to_q(scalar.shape[1], scalar.shape[0], extent)
    positive = scalar[foreground & valid]
    vmin = float(np.quantile(positive, 0.01))
    vmax = float(np.quantile(positive, 0.995))
    norm = PowerNorm(gamma=0.58, vmin=vmin, vmax=vmax, clip=True)
    cmap = matplotlib.colormaps['magma']
    mask = foreground & valid & (scalar >= vmin)
    ax.scatter(
        q[..., 0][mask], q[..., 1][mask], q[..., 2][mask],
        c=cmap(norm(scalar[mask])), s=0.78, alpha=0.96,
        linewidths=0, depthshade=False, rasterized=True,
    )
    return matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)


def main():
    detector = Image.open(ASSETS / 'specular_detector.png').convert('RGB')
    caked = Image.open(ASSETS / 'specular_caked.png').convert('RGB')
    extent = (1300.0, 1600.0, 1250.0, 1600.0)

    fig = plt.figure(figsize=(12.6, 4.35), constrained_layout=True)
    gs = fig.add_gridspec(1, 3, width_ratios=(1.40, 0.90, 1.10))

    ax = fig.add_subplot(gs[0, 0], projection='3d')
    sphere_wireframe(ax)
    mappable = add_contrast_patch(ax, ASSETS / 'specular_detector.png', extent)
    zline = np.linspace(0.0, 1.42, 120)
    ax.plot(np.zeros_like(zline), np.zeros_like(zline), zline, color='tab:blue', lw=1.25, label=r'zero-tilt $00L$ axis')
    ax.scatter([0], [0], [0], c='cyan', marker='+', s=42, linewidths=1.2, label=r'$Q=0$')
    ax.set_xlabel(r'$Q_x$ ($\AA^{-1}$)', labelpad=2)
    ax.set_ylabel(r'$Q_y$ ($\AA^{-1}$)', labelpad=2)
    ax.set_zlabel(r'$Q_z$ ($\AA^{-1}$)', labelpad=2)
    ax.set_title(r'a  Detector-visible $00L$ Ewald patch with expanded contrast', loc='left', fontsize=9, fontweight='bold')
    ax.view_init(elev=23, azim=-58)
    equal_3d(ax, (-0.55, 0.55), (-0.58, 0.52), (0.0, 1.45))
    ax.tick_params(labelsize=7, pad=0)
    ax.legend(loc='upper left', fontsize=6.8, frameon=False)
    cb = fig.colorbar(mappable, ax=ax, shrink=0.58, pad=0.025, aspect=20)
    cb.set_label('relative Ewald intensity\n(contrast-stretched display scale)', fontsize=7)
    cb.ax.tick_params(labelsize=6.5)

    ax = fig.add_subplot(gs[0, 1])
    ax.imshow(detector, extent=[1300, 1600, 1600, 1250], interpolation='bilinear')
    ax.scatter([REF_C], [REF_R], marker='+', c='cyan', s=55, linewidths=1.3)
    ax.annotate('direct beam', (REF_C, REF_R), xytext=(1515, 1575), color='cyan', fontsize=8,
                arrowprops=dict(arrowstyle='->', color='cyan', lw=0.9))
    ax.set_xlim(1300, 1600)
    ax.set_ylim(1600, 1250)
    ax.set_xlabel('detector column (px)')
    ax.set_ylabel('detector row (px)')
    ax.set_title('b  Specular detector density', loc='left', fontsize=9, fontweight='bold')

    ax = fig.add_subplot(gs[0, 2])
    ax.set_facecolor('black')
    ax.imshow(caked.transpose(Image.Transpose.FLIP_TOP_BOTTOM), extent=[4, 18, -4, 4], interpolation='bilinear', aspect='auto')
    ax.set_xlim(0, 20)
    ax.set_ylim(-10, 10)
    ax.set_xticks([0, 5, 10, 15, 20])
    ax.set_yticks([-10, -5, 0, 5, 10])
    ax.set_xlabel(r'$2\theta$ (deg)')
    ax.set_ylabel(r'$\phi$ (deg)')
    ax.set_title(r'c  Specular intensity in the full low-angle caked window', loc='left', fontsize=9, fontweight='bold')

    fig.suptitle(r'Specular ($r=0$) Ewald selection: improved intensity contrast and measurement coordinates', fontsize=12, fontweight='bold')
    FIGURES.mkdir(exist_ok=True)
    fig.savefig(FIGURES / 'fig_specular_detector_visible_round16.pdf', bbox_inches='tight')
    fig.savefig(FIGURES / 'fig_specular_detector_visible_round16.png', dpi=260, bbox_inches='tight')


if __name__ == '__main__':
    main()
