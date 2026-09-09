#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.textpath import TextPath
import numpy as np
import vtk
from vtk.util import numpy_support

FAMILY_ORDER = [1, 3, 4, 7, 9, 12, 13, 16, 19, 21]


def make_lookup_table(vmin: float, vmax: float, cmap_name: str = 'magma'):
    cmap = matplotlib.colormaps[cmap_name]
    lut = vtk.vtkLookupTable()
    lut.SetNumberOfTableValues(256)
    lut.SetRange(vmin, vmax)
    lut.SetScaleToLog10()
    lut.Build()
    for i in range(256):
        r, g, b, a = cmap(i / 255.0)
        lut.SetTableValue(i, r, g, b, a)
    return lut


def build_cylinder_polydata(radius: float, qz: np.ndarray, scalars_1d: np.ndarray,
                            theta_start_deg: float, theta_span_deg: float, n_theta: int,
                            qz_top: float | None = None) -> vtk.vtkPolyData:
    if qz_top is not None:
        mask = qz <= qz_top + 1e-12
        qz_use = qz[mask]
        scalars_use = scalars_1d[mask]
        if qz_use.size < 2:
            qz_use = qz[:2]
            scalars_use = scalars_1d[:2]
    else:
        qz_use = qz
        scalars_use = scalars_1d

    theta = np.linspace(math.radians(theta_start_deg), math.radians(theta_start_deg + theta_span_deg), n_theta)
    points = vtk.vtkPoints()
    quads = vtk.vtkCellArray()
    values = []
    nz = len(qz_use)

    for th in theta:
        x = radius * math.cos(th)
        y = radius * math.sin(th)
        for z, val in zip(qz_use, scalars_use):
            points.InsertNextPoint(float(x), float(y), float(z))
            values.append(float(val))

    for i in range(n_theta - 1):
        for j in range(nz - 1):
            p0 = i * nz + j
            p1 = (i + 1) * nz + j
            p2 = (i + 1) * nz + (j + 1)
            p3 = i * nz + (j + 1)
            quad = vtk.vtkQuad()
            quad.GetPointIds().SetId(0, p0)
            quad.GetPointIds().SetId(1, p1)
            quad.GetPointIds().SetId(2, p2)
            quad.GetPointIds().SetId(3, p3)
            quads.InsertNextCell(quad)

    poly = vtk.vtkPolyData()
    poly.SetPoints(points)
    poly.SetPolys(quads)
    arr = numpy_support.numpy_to_vtk(np.asarray(values, dtype=np.float64), deep=True)
    arr.SetName('rho_cyl')
    poly.GetPointData().SetScalars(arr)
    return poly


def make_top_edge(radius: float, z_top: float, theta_start_deg: float, theta_span_deg: float, n_theta: int) -> vtk.vtkActor:
    theta = np.linspace(math.radians(theta_start_deg), math.radians(theta_start_deg + theta_span_deg), n_theta)
    points = vtk.vtkPoints()
    polyline = vtk.vtkPolyLine()
    polyline.GetPointIds().SetNumberOfIds(len(theta))
    for i, th in enumerate(theta):
        pid = points.InsertNextPoint(float(radius * math.cos(th)), float(radius * math.sin(th)), float(z_top))
        polyline.GetPointIds().SetId(i, pid)
    lines = vtk.vtkCellArray()
    lines.InsertNextCell(polyline)
    pd = vtk.vtkPolyData()
    pd.SetPoints(points)
    pd.SetLines(lines)
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(pd)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(0.10, 0.10, 0.10)
    actor.GetProperty().SetLineWidth(1.6)
    return actor


def render_figure(npz_path: Path, out_png: Path, out_pdf: Path | None,
                  theta_start_deg: float, theta_span_deg: float, n_theta: int,
                  width: int, height: int):
    d = np.load(npz_path)
    families = d['families'].astype(int)
    radii = d['radii'].astype(float)
    qz = d['qz'].astype(float)
    rho = d['rho'].astype(float)
    staircase_top_qz = d['staircase_top_qz'].astype(float)

    pos = rho[rho > 0]
    vmax = max(float(np.quantile(pos, 0.9995)), float(np.max(pos)) / 1000.0)
    vmin = max(float(np.min(pos)), vmax / 1e7)
    lut = make_lookup_table(vmin, vmax)

    ren = vtk.vtkRenderer()
    ren.SetBackground(1.0, 1.0, 1.0)
    win = vtk.vtkRenderWindow()
    win.SetOffScreenRendering(1)
    win.SetSize(width, height)
    win.SetMultiSamples(0)
    win.AddRenderer(ren)

    fam_to_idx = {int(f): i for i, f in enumerate(families)}
    label_specs = []
    for f in sorted(families, key=lambda ff: radii[fam_to_idx[int(ff)]], reverse=True):
        idx = fam_to_idx[int(f)]
        radius = float(radii[idx])
        qz_top = float(staircase_top_qz[idx])
        poly = build_cylinder_polydata(radius, qz, rho[idx], theta_start_deg, theta_span_deg, n_theta, qz_top=qz_top)
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(poly)
        mapper.SetLookupTable(lut)
        mapper.SetColorModeToMapScalars()
        mapper.SetScalarModeToUsePointData()
        mapper.SetScalarRange(vmin, vmax)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetOpacity(1.0)
        actor.GetProperty().SetInterpolationToPhong()
        actor.GetProperty().SetAmbient(0.28)
        actor.GetProperty().SetDiffuse(0.72)
        actor.GetProperty().SetSpecular(0.04)
        ren.AddActor(actor)
        ren.AddActor(make_top_edge(radius, qz_top, theta_start_deg, theta_span_deg, n_theta))
        label_specs.append((radius, qz_top, int(f)))

    zmax = float(np.max(qz))
    cam = ren.GetActiveCamera()
    cam.SetPosition(-21.5, -18.0, 11.0)
    cam.SetFocalPoint(0.0, 0.0, zmax * 0.30)
    cam.SetViewUp(0.0, 0.0, 1.0)
    ren.ResetCameraClippingRange()

    win.Render()
    w2i = vtk.vtkWindowToImageFilter()
    w2i.SetInput(win)
    w2i.SetScale(2)
    w2i.ReadFrontBufferOff()
    w2i.Update()
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(out_png))
    writer.SetInputConnection(w2i.GetOutputPort())
    writer.Write()

    img = plt.imread(out_png)
    rgb = img[..., :3]
    nonwhite = np.any(rgb < 0.985, axis=2)
    ys, xs = np.where(nonwhite)
    margin = 70
    x0 = max(int(xs.min()) - margin, 0)
    x1 = min(int(xs.max()) + margin, img.shape[1] - 1)
    y0 = max(int(ys.min()) - margin, 0)
    y1 = min(int(ys.max()) + margin, img.shape[0] - 1)
    crop = img[y0:y1 + 1, x0:x1 + 1]

    side_margin = 80
    extra_top = 260
    canvas_h = crop.shape[0] + extra_top
    canvas_w = crop.shape[1] + 2 * side_margin

    fig = plt.figure(figsize=(canvas_w / 180.0, canvas_h / 180.0), dpi=180)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(np.ones((canvas_h, canvas_w, 4), dtype=crop.dtype))
    ax.imshow(crop, extent=(side_margin, side_margin + crop.shape[1], canvas_h, extra_top))
    ax.set_xlim(0, canvas_w)
    ax.set_ylim(canvas_h, 0)
    ax.axis('off')

    # Arrow tips are the exact top corners of the visible cut face of each shell.
    # This makes the target position follow the physical radius Q_R(r), not a manual drift in r.
    render_scale = 2.0
    theta_tip = math.radians(theta_start_deg)
    spec_map = {int(f): (float(radius), float(qz_top)) for radius, qz_top, f in label_specs}
    anchor_map = {}
    for family_r in FAMILY_ORDER:
        radius, qz_top = spec_map[family_r]
        x3 = radius * math.cos(theta_tip)
        y3 = radius * math.sin(theta_tip)
        z3 = qz_top
        coord = vtk.vtkCoordinate()
        coord.SetCoordinateSystemToWorld()
        coord.SetValue(x3, y3, z3)
        xd, yd = coord.GetComputedDoubleDisplayValue(ren)
        xp = xd * render_scale - x0 + side_margin
        yp = (img.shape[0] - yd * render_scale) - y0 + extra_top
        anchor_map[family_r] = (xp, yp)

    # The projected cut-face positions should increase monotonically with Q_R.
    anchor_x = np.array([anchor_map[r][0] for r in FAMILY_ORDER], dtype=float)
    if not np.all(np.diff(anchor_x) > 0.0):
        raise RuntimeError('Projected cylinder targets are not ordered by radius.')

    # Keep every label centered above its own cylinder and solve the label layout
    # against the actual label-box dimensions.  Arrow lengths vary only when a
    # nearby label would otherwise overlap.
    font_size = 13
    font_prop = FontProperties(size=font_size, weight='bold')
    layout_dpi = 180.0
    box_pad_x = 13.0
    box_pad_y = 8.0
    collision_pad = 7.0
    base_offset = 34.0
    offset_step = 36.0
    candidate_offsets = [base_offset + offset_step * level for level in range(8)]

    def label_box_size(text_value: str) -> tuple[float, float]:
        path = TextPath((0, 0), text_value, prop=font_prop, usetex=False)
        ext = path.get_extents()
        # Convert points to canvas data units.  The figure is rendered at 180 dpi,
        # so one canvas unit is one layout pixel before final export scaling.
        scale = layout_dpi / 72.0
        width_box = ext.width * scale + 2.0 * box_pad_x
        height_box = max(ext.height, font_size) * scale + 2.0 * box_pad_y
        return width_box, height_box

    def rectangles_overlap(a, b) -> bool:
        return not (
            a[1] + collision_pad <= b[0]
            or b[1] + collision_pad <= a[0]
            or a[3] + collision_pad <= b[2]
            or b[3] + collision_pad <= a[2]
        )

    placed_rectangles = []
    label_pos = []
    for family_r in FAMILY_ORDER:
        xp, yp = anchor_map[family_r]
        label_text = f'r = {family_r}'
        box_width, box_height = label_box_size(label_text)
        chosen_y = None
        chosen_rect = None
        for offset in candidate_offsets:
            candidate_y = yp - offset
            if candidate_y - 0.5 * box_height < 12.0:
                continue
            rect = (
                xp - 0.5 * box_width,
                xp + 0.5 * box_width,
                candidate_y - 0.5 * box_height,
                candidate_y + 0.5 * box_height,
            )
            if all(not rectangles_overlap(rect, previous) for previous in placed_rectangles):
                chosen_y = candidate_y
                chosen_rect = rect
                break
        if chosen_y is None:
            # This should be rare with the reserved top band.  Use the highest
            # available position and preserve the correct arrow target.
            chosen_y = max(12.0 + 0.5 * box_height, yp - candidate_offsets[-1])
            chosen_rect = (
                xp - 0.5 * box_width,
                xp + 0.5 * box_width,
                chosen_y - 0.5 * box_height,
                chosen_y + 0.5 * box_height,
            )
        placed_rectangles.append(chosen_rect)
        label_pos.append((family_r, xp, yp, chosen_y))

    # The r=12 and r=13 targets are close in projection. Put r=12 on the
    # upper label level and r=13 below it, so the r=13 leader is entirely
    # beneath the r=12 label rather than passing alongside or through it.
    label_y_by_family = {family_r: label_y for family_r, _, _, label_y in label_pos}
    label_y_by_family[12], label_y_by_family[13] = (
        min(label_y_by_family[12], label_y_by_family[13]),
        max(label_y_by_family[12], label_y_by_family[13]),
    )
    label_pos = [
        (family_r, xp, yp, label_y_by_family[family_r])
        for family_r, xp, yp, _ in label_pos
    ]

    # Draw all leaders before any label boxes. This guarantees that the r=13
    # leader passes underneath the opaque r=12 label box.
    for family_r, xp, yp, label_y in label_pos:
        ax.annotate(
            '',
            xy=(xp, yp),
            xytext=(xp, label_y),
            arrowprops=dict(
                arrowstyle='-|>',
                lw=1.5,
                color='black',
                shrinkA=0,
                shrinkB=4,
                connectionstyle='arc3,rad=0.0',
            ),
            annotation_clip=False,
            zorder=6,
        )
        ax.scatter([xp], [yp], s=25, facecolor='white', edgecolor='black', linewidth=1.0, zorder=7)

    # Draw the opaque labels after the leaders so every leader is visually behind
    # any label box it crosses.
    for family_r, xp, yp, label_y in label_pos:
        ax.text(
            xp,
            label_y,
            f'r = {family_r}',
            fontsize=font_size,
            fontweight='bold',
            ha='center',
            va='center',
            color='black',
            bbox=dict(
                boxstyle='round,pad=0.24,rounding_size=0.12',
                facecolor='white',
                edgecolor='black',
                linewidth=1.1,
                alpha=1.0,
            ),
            clip_on=False,
            zorder=10,
        )

    # Compact reciprocal-space direction key in the lower-left corner.
    # G_r points radially outward and G_z points along the cylinder axis.
    origin = (0.058, 0.078)
    ax.annotate(
        '', xy=(0.135, 0.078), xytext=origin,
        xycoords='axes fraction', textcoords='axes fraction',
        arrowprops=dict(arrowstyle='-|>', lw=2.4, color='black', shrinkA=0, shrinkB=0),
        zorder=22,
    )
    ax.annotate(
        '', xy=(0.058, 0.185), xytext=origin,
        xycoords='axes fraction', textcoords='axes fraction',
        arrowprops=dict(arrowstyle='-|>', lw=2.4, color='black', shrinkA=0, shrinkB=0),
        zorder=22,
    )
    ax.scatter([origin[0]], [origin[1]], s=18, color='black',
               transform=ax.transAxes, zorder=23)
    ax.text(0.143, 0.078, r'$G_r$', transform=ax.transAxes,
            fontsize=17, fontweight='bold', ha='left', va='center', zorder=23)
    ax.text(0.058, 0.198, r'$G_z$', transform=ax.transAxes,
            fontsize=17, fontweight='bold', ha='center', va='bottom', zorder=23)

    fig.savefig(out_png, dpi=240, bbox_inches='tight', pad_inches=0)
    if out_pdf is not None:
        fig.savefig(out_pdf, dpi=300, bbox_inches='tight', pad_inches=0)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--npz', type=Path, default=Path('/mnt/data/fig3a_actual_sf_cylinders_labels_spaced2.npz'))
    ap.add_argument('--out-png', type=Path, default=Path('/mnt/data/fig3a_actual_sf_cylinders_toplabels_verified_v9.png'))
    ap.add_argument('--out-pdf', type=Path, default=Path('/mnt/data/fig3a_actual_sf_cylinders_toplabels_verified_v9.pdf'))
    ap.add_argument('--theta-start-deg', type=float, default=-35.0)
    ap.add_argument('--theta-span-deg', type=float, default=300.0)
    ap.add_argument('--n-theta', type=int, default=360)
    ap.add_argument('--width', type=int, default=1800)
    ap.add_argument('--height', type=int, default=1400)
    args = ap.parse_args()
    render_figure(args.npz, args.out_png, args.out_pdf, args.theta_start_deg, args.theta_span_deg, args.n_theta, args.width, args.height)


if __name__ == '__main__':
    main()
