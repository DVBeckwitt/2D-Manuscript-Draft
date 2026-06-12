#!/usr/bin/env python3
"""
Interactive GIWAXS publication-figure tuner with editable Bragg peak picks.

This opens a Matplotlib window with live sliders and an editable detector-pixel
picker. You can choose new Bragg peak pixel coordinates, name each peak, tune the
Gaussian k_f cone rendering, and save a reproducible high-resolution figure.

Basic use
---------
python interactive_giwaxs_bragg_tuner_auto.py biggerB_4deg_2m.png

Use saved clicked detector pixels
---------------------------------
python interactive_giwaxs_bragg_tuner_auto.py biggerB_4deg_2m.png \
    --peaks-csv clicked_detector_pixels.csv

In the main tuner window
------------------------
s     save high-resolution PNG, optional PDF, JSON config, and mapped CSV
r     reset sliders
q     close window

In the Bragg peak picker window
-------------------------------
left click      select nearest peak or add a new peak
left drag       move selected peak
right click     delete nearest peak
Text box        rename selected Bragg peak, press Enter to apply
Snap all        move all picks to nearest local detector maxima
Close           close picker and return to tuner

Dependencies
------------
pip install numpy pillow matplotlib
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button, CheckButtons, RadioButtons, Slider, TextBox
from PIL import Image, ImageDraw, ImageFilter, ImageFont

DEFAULT_DETECTOR_SIZE = (407.0, 407.0)
DEFAULT_BASE_SIZE = (1448, 1086)

DEFAULT_PEAKS = [
    (203.33, 310.70, "B1"),
    (203.99, 214.89, "B2"),
    (204.65, 89.36, "B3"),
    (368.51, 273.04, "B4"),
    (373.13, 197.05, "B5"),
    (375.12, 101.91, "B6"),
]

DEFAULT_FACE_CORNERS = [
    (455.0, 51.0),
    (1166.0, 116.0),
    (1148.0, 810.0),
    (459.0, 694.0),
]

DEFAULT_TAIL = (620.0, 872.0)
DEFAULT_CROP_BOX = (160.0, 20.0, 1240.0, 990.0)
DEFAULT_KF_LABEL_POS = (692.0, 760.0)
DEFAULT_AREA_DETECTOR_DOT = (458.0, 330.0)
DEFAULT_AREA_DETECTOR_TEXT = (385.0, 300.0)
DEFAULT_SAMPLE_DOT = (760.0, 885.0)
DEFAULT_SAMPLE_TEXT = (880.0, 875.0)

COLOR_PRESETS = {
    "vermillion": "#D55E00",
    "orange": "#E69F00",
    "magenta": "#CC79A7",
    "purple": "#7A3E9D",
}


@dataclass
class Peak:
    x: float
    y: float
    label: str


@dataclass
class FigureConfig:
    color_name: str = "vermillion"
    max_alpha: float = 0.36
    detector_sigma: float = 7.0
    source_sigma: float = 1.0
    longitudinal_fade: float = 0.16
    detector_cap_alpha: float = 0.18
    detector_cap_sigma_scale: float = 0.90
    sample_glow_alpha: float = 0.10
    sample_glow_sigma: float = 8.0
    halo_alpha: float = 0.10
    maxima_radius: int = 14
    maxima_blur: float = 2.0
    kf_label_x: float = DEFAULT_KF_LABEL_POS[0]
    kf_label_y: float = DEFAULT_KF_LABEL_POS[1]
    bragg_label_size: float = 17.0
    bragg_label_offset: float = 30.0
    callout_font_size: float = 28.0


@dataclass
class ToggleConfig:
    snap_to_maxima: bool = True
    halo: bool = True
    detector_caps: bool = True
    sample_glow: bool = True
    setup_labels: bool = True
    bragg_labels: bool = True
    show_centers: bool = False


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Interactive tuner for GIWAXS figure with editable Bragg peaks.")
    p.add_argument("figure", help="Detector-only PNG, e.g. biggerB_4deg_2m.png, or an existing full-figure PNG")
    p.add_argument("--detector-image", default=None, help="Detector-only PNG. Optional when the positional input is already the detector image")
    p.add_argument("--input-mode", choices=["auto", "detector", "base"], default="auto",
                   help="auto: infer input type. detector: positional input is detector-only. base: positional input is an existing full figure")
    p.add_argument("--base-width", type=int, default=DEFAULT_BASE_SIZE[0], help="Generated full-figure width in pixels")
    p.add_argument("--base-height", type=int, default=DEFAULT_BASE_SIZE[1], help="Generated full-figure height in pixels")
    p.add_argument("--save-generated-base", action="store_true", help="Save the generated detector/sample/k_i base PNG when saving")
    p.add_argument("--output-prefix", default=None, help="Output prefix for saved files")
    p.add_argument("--output", default=None, help="Exact output PNG path. Overrides --output-prefix")

    p.add_argument("--peaks-csv", "--spots-csv", dest="peaks_csv", default=None,
                   help="CSV with detector pixel coordinates and optional labels")
    p.add_argument("--peaks-json", "--spots-json", dest="peaks_json", default=None,
                   help="JSON with detector pixel coordinates and optional labels")
    p.add_argument("--peaks", nargs="*", default=None,
                   help="Inline peaks as x y label x y label ... or x1 y1 x2 y2 ...")

    p.add_argument("--detector-size", nargs=2, type=float, metavar=("W", "H"), default=DEFAULT_DETECTOR_SIZE)
    p.add_argument("--tail", nargs=2, type=float, metavar=("X", "Y"), default=DEFAULT_TAIL)
    p.add_argument(
        "--face-corners",
        nargs=8,
        type=float,
        metavar=("TL_X", "TL_Y", "TR_X", "TR_Y", "BR_X", "BR_Y", "BL_X", "BL_Y"),
        default=[v for pt in DEFAULT_FACE_CORNERS for v in pt],
    )

    p.add_argument("--area-detector-dot", nargs=2, type=float, default=DEFAULT_AREA_DETECTOR_DOT)
    p.add_argument("--area-detector-text-pos", nargs=2, type=float, default=DEFAULT_AREA_DETECTOR_TEXT)
    p.add_argument("--sample-dot", nargs=2, type=float, default=DEFAULT_SAMPLE_DOT)
    p.add_argument("--sample-text-pos", nargs=2, type=float, default=DEFAULT_SAMPLE_TEXT)

    p.add_argument("--preview-scale", type=float, default=1.0, help="Interactive preview scale")
    p.add_argument("--output-scale", type=float, default=3.0, help="High-resolution save scale")
    p.add_argument("--dpi", type=int, default=600)
    p.add_argument("--pdf", action="store_true", help="Also save PDF when pressing Save")
    p.add_argument("--no-crop", action="store_true", help="Disable the default publication crop")
    p.add_argument("--crop-box", nargs=4, type=float, default=DEFAULT_CROP_BOX)
    p.add_argument("--save-only", action="store_true", help="Render once with defaults, save, and exit")
    return p.parse_args()


def default_peaks() -> List[Peak]:
    return [Peak(x, y, label) for x, y, label in DEFAULT_PEAKS]


def load_peaks(args: argparse.Namespace) -> List[Peak]:
    if args.peaks is not None:
        values = args.peaks
        peaks: List[Peak] = []
        if len(values) % 3 == 0:
            ok = True
            for i in range(0, len(values), 3):
                try:
                    x = float(values[i])
                    y = float(values[i + 1])
                except ValueError:
                    ok = False
                    break
                peaks.append(Peak(x, y, str(values[i + 2])))
            if ok:
                return peaks
        if len(values) % 2 == 0:
            peaks = []
            for i in range(0, len(values), 2):
                peaks.append(Peak(float(values[i]), float(values[i + 1]), f"B{1 + i // 2}"))
            return peaks
        raise SystemExit("--peaks requires x y label ... or x y ...")

    if args.peaks_csv:
        path = Path(args.peaks_csv)
        peaks: List[Peak] = []
        with path.open(newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                x_val = y_val = None
                for xk, yk in (
                    ("x", "y"),
                    ("x_px", "y_px"),
                    ("x_float", "y_float"),
                    ("clicked_x", "clicked_y"),
                    ("snapped_x", "snapped_y"),
                    ("detector_x", "detector_y"),
                ):
                    if xk in row and yk in row and row[xk] != "" and row[yk] != "":
                        x_val = float(row[xk])
                        y_val = float(row[yk])
                        break
                if x_val is None or y_val is None:
                    continue
                label = row.get("label") or row.get("name") or row.get("peak") or f"B{len(peaks) + 1}"
                peaks.append(Peak(x_val, y_val, str(label)))
        if not peaks:
            raise SystemExit(f"Could not read detector peaks from {path}")
        return peaks

    if args.peaks_json:
        path = Path(args.peaks_json)
        data = json.loads(path.read_text())
        if isinstance(data, dict):
            data = data.get("peaks") or data.get("points") or data.get("snapped_or_used_spots") or data
        peaks: List[Peak] = []
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    x_val = y_val = None
                    for xk, yk in (("x", "y"), ("x_px", "y_px"), ("detector_x", "detector_y"), ("snapped_x", "snapped_y")):
                        if xk in item and yk in item:
                            x_val = float(item[xk])
                            y_val = float(item[yk])
                            break
                    if x_val is None or y_val is None:
                        continue
                    label = item.get("label") or item.get("name") or item.get("peak") or f"B{len(peaks) + 1}"
                    peaks.append(Peak(x_val, y_val, str(label)))
                elif isinstance(item, (list, tuple)) and len(item) >= 2:
                    label = str(item[2]) if len(item) >= 3 else f"B{len(peaks) + 1}"
                    peaks.append(Peak(float(item[0]), float(item[1]), label))
        if not peaks:
            raise SystemExit(f"Could not read detector peaks from {path}")
        return peaks

    return default_peaks()


def compute_homography(src: np.ndarray, dst: np.ndarray) -> np.ndarray:
    A = []
    for (x, y), (u, v) in zip(src, dst):
        A.append([-x, -y, -1.0, 0.0, 0.0, 0.0, x * u, y * u, u])
        A.append([0.0, 0.0, 0.0, -x, -y, -1.0, x * v, y * v, v])
    A = np.asarray(A, dtype=float)
    _, _, vt = np.linalg.svd(A)
    H = vt[-1].reshape(3, 3)
    H /= H[2, 2]
    return H


def map_points(H: np.ndarray, pts: Sequence[Tuple[float, float]]) -> np.ndarray:
    if not pts:
        return np.zeros((0, 2), dtype=float)
    arr = np.asarray([[x, y, 1.0] for x, y in pts], dtype=float).T
    mapped = H @ arr
    mapped /= mapped[2, :]
    return mapped[:2, :].T


def detector_intensity_map(detector_image_path: Path, blur_radius: float) -> np.ndarray:
    img = Image.open(detector_image_path).convert("RGB")
    arr = np.asarray(img).astype(np.float32) / 255.0
    luminance = 0.2126 * arr[..., 0] + 0.7152 * arr[..., 1] + 0.0722 * arr[..., 2]
    lum_img = Image.fromarray(np.clip(luminance * 255.0, 0, 255).astype(np.uint8), mode="L")
    if blur_radius > 0:
        lum_img = lum_img.filter(ImageFilter.GaussianBlur(radius=float(blur_radius)))
    return np.asarray(lum_img).astype(np.float32) / 255.0


def snap_xy_to_local_maximum(x: float, y: float, intensity: np.ndarray, radius: int) -> Tuple[float, float]:
    h, w = intensity.shape
    radius = max(0, int(round(radius)))
    xi = int(round(x))
    yi = int(round(y))
    x0 = max(0, xi - radius)
    x1 = min(w, xi + radius + 1)
    y0 = max(0, yi - radius)
    y1 = min(h, yi + radius + 1)
    patch = intensity[y0:y1, x0:x1]
    max_val = float(np.max(patch))
    ys, xs = np.where(np.isclose(patch, max_val))
    best = (float(xi), float(yi))
    best_d2 = float("inf")
    for yy, xx in zip(ys, xs):
        gx = float(x0 + int(xx))
        gy = float(y0 + int(yy))
        d2 = (gx - x) ** 2 + (gy - y) ** 2
        if d2 < best_d2:
            best_d2 = d2
            best = (gx, gy)
    return best


def snap_peaks_to_local_maxima(peaks: Sequence[Peak], intensity: np.ndarray, radius: int) -> List[Peak]:
    snapped: List[Peak] = []
    for peak in peaks:
        x, y = snap_xy_to_local_maximum(peak.x, peak.y, intensity, radius)
        snapped.append(Peak(x, y, peak.label))
    return snapped


def projected_perpendicular_sigma(
    H: np.ndarray,
    spot: Tuple[float, float],
    tail: Tuple[float, float],
    sigma_x: float,
    sigma_y: float,
) -> float:
    x, y = spot
    center = map_points(H, [(x, y)])[0]
    px_plus, px_minus = map_points(H, [(x + sigma_x, y), (x - sigma_x, y)])
    py_plus, py_minus = map_points(H, [(x, y + sigma_y), (x, y - sigma_y)])
    ex = 0.5 * (px_plus - px_minus)
    ey = 0.5 * (py_plus - py_minus)
    cov = np.outer(ex, ex) + np.outer(ey, ey)
    v = center - np.asarray(tail, dtype=float)
    norm = np.linalg.norm(v)
    if norm < 1e-9:
        return max(float(np.linalg.norm(ex)), float(np.linalg.norm(ey)), 1.0)
    n = np.array([-v[1], v[0]]) / norm
    sigma = float(np.sqrt(max(n @ cov @ n, 1e-9)))
    return max(sigma, 1.0)


def cone_alpha_mask(
    shape: Tuple[int, int],
    tail: Tuple[float, float],
    head: Tuple[float, float],
    sigma_tail: float,
    sigma_head: float,
    max_alpha: float,
    truncation: float,
    longitudinal_fade: float,
) -> Tuple[slice, slice, np.ndarray]:
    h, w = shape
    tx, ty = tail
    hx, hy = head
    vx, vy = hx - tx, hy - ty
    length2 = vx * vx + vy * vy
    if length2 < 1e-9:
        return slice(0, 1), slice(0, 1), np.zeros((1, 1), dtype=np.float32)

    max_sigma = max(sigma_tail, sigma_head)
    margin = int(np.ceil(truncation * max_sigma + 4))
    x0 = max(0, int(np.floor(min(tx, hx) - margin)))
    x1 = min(w, int(np.ceil(max(tx, hx) + margin + 1)))
    y0 = max(0, int(np.floor(min(ty, hy) - margin)))
    y1 = min(h, int(np.ceil(max(ty, hy) + margin + 1)))

    yy, xx = np.mgrid[y0:y1, x0:x1]
    dx = xx - tx
    dy = yy - ty
    s = (dx * vx + dy * vy) / length2
    valid = (s >= 0.0) & (s <= 1.0)
    s_clip = np.clip(s, 0.0, 1.0)

    cx = tx + s_clip * vx
    cy = ty + s_clip * vy
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    sigma = sigma_tail + s_clip * (sigma_head - sigma_tail)
    sigma = np.maximum(sigma, 1e-6)

    gaussian = np.exp(-0.5 * (dist / sigma) ** 2)
    gaussian[dist > truncation * sigma] = 0.0
    gaussian[~valid] = 0.0

    fade = longitudinal_fade + (1.0 - longitudinal_fade) * s_clip
    alpha = np.clip(max_alpha * gaussian * fade, 0.0, 1.0).astype(np.float32)
    return slice(y0, y1), slice(x0, x1), alpha


def gaussian_spot_alpha_mask(
    shape: Tuple[int, int],
    center: Tuple[float, float],
    sigma_x: float,
    sigma_y: float,
    max_alpha: float,
    truncation: float = 3.0,
) -> Tuple[slice, slice, np.ndarray]:
    h, w = shape
    cx, cy = center
    margin_x = int(np.ceil(truncation * sigma_x + 4))
    margin_y = int(np.ceil(truncation * sigma_y + 4))
    x0 = max(0, int(np.floor(cx - margin_x)))
    x1 = min(w, int(np.ceil(cx + margin_x + 1)))
    y0 = max(0, int(np.floor(cy - margin_y)))
    y1 = min(h, int(np.ceil(cy + margin_y + 1)))
    yy, xx = np.mgrid[y0:y1, x0:x1]
    gx = (xx - cx) / max(sigma_x, 1e-6)
    gy = (yy - cy) / max(sigma_y, 1e-6)
    r2 = gx * gx + gy * gy
    alpha = max_alpha * np.exp(-0.5 * r2)
    alpha[r2 > truncation * truncation] = 0.0
    return slice(y0, y1), slice(x0, x1), alpha.astype(np.float32)


def composite_color(image: np.ndarray, color_rgb: np.ndarray, alpha: np.ndarray, ys: slice, xs: slice) -> None:
    if alpha.size == 0:
        return
    region = image[ys, xs, :]
    a = alpha[..., None]
    image[ys, xs, :] = region * (1.0 - a) + color_rgb[None, None, :] * a


def font_paths() -> Tuple[str | None, str | None, str | None]:
    italic_candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
    ]
    regular_candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    ]
    bold_candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    ]
    italic = next((p for p in italic_candidates if Path(p).exists()), None)
    regular = next((p for p in regular_candidates if Path(p).exists()), None)
    bold = next((p for p in bold_candidates if Path(p).exists()), None)
    return italic, regular, bold


def load_font(path: str | None, size: int) -> ImageFont.ImageFont:
    try:
        if path is not None:
            return ImageFont.truetype(path, size=size)
    except Exception:
        pass
    return ImageFont.load_default()


def text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, stroke_width: int = 0) -> Tuple[int, int]:
    try:
        bbox = draw.textbbox((0, 0), text, font=font, stroke_width=stroke_width)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    except Exception:
        return int(8 * len(text)), 12


def draw_kf_label(img: Image.Image, xy: Tuple[float, float], color: str, base_size: float, scale: float) -> None:
    draw = ImageDraw.Draw(img)
    italic_path, regular_path, _ = font_paths()
    size = max(12, int(round(base_size * scale)))
    sub_size = max(8, int(round(0.58 * base_size * scale)))
    font_k = load_font(italic_path or regular_path, size)
    font_f = load_font(italic_path or regular_path, sub_size)
    x = int(round(xy[0] * scale))
    y = int(round(xy[1] * scale))
    rgb = tuple(int(round(c * 255)) for c in mcolors.to_rgb(color))
    outline = (255, 255, 255)
    stroke = max(2, int(round(2.2 * scale)))
    draw.text((x, y), "k", font=font_k, fill=rgb, stroke_width=stroke, stroke_fill=outline)
    try:
        bbox_k = draw.textbbox((x, y), "k", font=font_k, stroke_width=stroke)
        k_width = bbox_k[2] - bbox_k[0]
    except Exception:
        k_width = int(0.55 * size)
    sub_x = x + int(round(0.82 * k_width))
    sub_y = y + int(round(0.58 * size))
    draw.text((sub_x, sub_y), "f", font=font_f, fill=rgb, stroke_width=stroke, stroke_fill=outline)


def draw_callout(
    img: Image.Image,
    dot_xy_base: Tuple[float, float],
    text_xy_base: Tuple[float, float],
    text: str,
    anchor: str,
    base_font_size: float,
    base_line_width: float,
    base_dot_radius: float,
    base_gap: float,
    scale: float,
) -> None:
    draw = ImageDraw.Draw(img)
    _, regular_path, _ = font_paths()
    font = load_font(regular_path, max(10, int(round(base_font_size * scale))))
    stroke_text = max(1, int(round(1.6 * scale)))
    line_width = max(1, int(round(base_line_width * scale)))
    dot_radius = max(2, int(round(base_dot_radius * scale)))
    gap = max(2, int(round(base_gap * scale)))

    dot = (float(dot_xy_base[0]) * scale, float(dot_xy_base[1]) * scale)
    tx, ty = float(text_xy_base[0]) * scale, float(text_xy_base[1]) * scale
    tw, th = text_size(draw, text, font, stroke_width=stroke_text)

    if anchor.lower() == "right":
        text_origin = (int(round(tx - tw)), int(round(ty - 0.5 * th)))
        line_end = (int(round(tx + gap)), int(round(ty)))
    else:
        text_origin = (int(round(tx)), int(round(ty - 0.5 * th)))
        line_end = (int(round(tx - gap)), int(round(ty)))

    draw.line((dot[0], dot[1], line_end[0], line_end[1]), fill=(0, 0, 0), width=line_width)
    x, y = dot
    draw.ellipse((x - dot_radius, y - dot_radius, x + dot_radius, y + dot_radius), fill=(255, 255, 255))
    inner_r = max(1, int(round(0.62 * dot_radius)))
    draw.ellipse((x - inner_r, y - inner_r, x + inner_r, y + inner_r), fill=(0, 0, 0))
    draw.text(text_origin, text, font=font, fill=(0, 0, 0), stroke_width=stroke_text, stroke_fill=(255, 255, 255))


def draw_bragg_peak_labels(
    img: Image.Image,
    peaks: Sequence[Peak],
    mapped_base: np.ndarray,
    tail_base: Tuple[float, float],
    detector_size: Tuple[float, float],
    base_font_size: float,
    base_offset: float,
    scale: float,
) -> None:
    if not peaks:
        return
    rgba = img.convert("RGBA")
    overlay = Image.new("RGBA", rgba.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    _, regular_path, _ = font_paths()
    font = load_font(regular_path, max(8, int(round(base_font_size * scale))))
    stroke = max(1, int(round(0.45 * scale)))
    pad_x = max(4, int(round(5.0 * scale)))
    pad_y = max(2, int(round(3.0 * scale)))
    radius = max(4, int(round(4.5 * scale)))
    line_width = max(1, int(round(1.2 * scale)))
    det_w, _ = detector_size

    for peak, head0 in zip(peaks, mapped_base):
        label = str(peak.label).strip()
        if not label:
            continue
        head = np.array([head0[0] * scale, head0[1] * scale], dtype=float)
        tail = np.array([tail_base[0] * scale, tail_base[1] * scale], dtype=float)
        offset = base_offset * scale

        # Put right-column peak labels to the left of the peak. Put central peaks to the right.
        if peak.x > 0.62 * det_w:
            dx = -1.45 * offset
            dy = -0.45 * offset
            anchor = "right"
        else:
            dx = 0.65 * offset
            dy = -0.60 * offset
            anchor = "left"

        label_center = head + np.array([dx, dy], dtype=float)
        tw, th = text_size(draw, label, font, stroke_width=stroke)
        box_w = tw + 2 * pad_x
        box_h = th + 2 * pad_y
        if anchor == "right":
            x0 = int(round(label_center[0] - box_w))
            y0 = int(round(label_center[1] - 0.5 * box_h))
        else:
            x0 = int(round(label_center[0]))
            y0 = int(round(label_center[1] - 0.5 * box_h))
        x1 = x0 + box_w
        y1 = y0 + box_h

        # Leader line to the nearest box edge.
        if anchor == "right":
            line_end = (x1, int(round(0.5 * (y0 + y1))))
        else:
            line_end = (x0, int(round(0.5 * (y0 + y1))))
        draw.line((head[0], head[1], line_end[0], line_end[1]), fill=(255, 255, 255, 175), width=line_width + 1)
        draw.line((head[0], head[1], line_end[0], line_end[1]), fill=(0, 0, 0, 120), width=line_width)

        draw.rounded_rectangle((x0, y0, x1, y1), radius=radius, fill=(255, 255, 255, 205), outline=(0, 0, 0, 95), width=max(1, int(round(0.6 * scale))))
        draw.text((x0 + pad_x, y0 + pad_y), label, font=font, fill=(0, 0, 0, 235), stroke_width=stroke, stroke_fill=(255, 255, 255, 200))

    composed = Image.alpha_composite(rgba, overlay).convert("RGB")
    img.paste(composed)


def draw_center_dots(img: Image.Image, mapped_base: np.ndarray, scale: float) -> None:
    draw = ImageDraw.Draw(img)
    r = max(3, int(round(4 * scale)))
    for x, y in mapped_base:
        xs = float(x) * scale
        ys = float(y) * scale
        draw.ellipse((xs - r, ys - r, xs + r, ys + r), fill=(255, 230, 0), outline=(0, 0, 0), width=max(1, int(round(scale))))


def crop_image(img: Image.Image, crop_box_base: Sequence[float], scale: float) -> Image.Image:
    left, top, right, bottom = crop_box_base
    box = tuple(int(round(v * scale)) for v in (left, top, right, bottom))
    return img.crop(box)


def save_pdf_from_png(png_path: Path, pdf_path: Path, dpi: int) -> None:
    img = Image.open(png_path).convert("RGB")
    w_px, h_px = img.size
    fig = plt.figure(figsize=(w_px / dpi, h_px / dpi), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(img)
    ax.axis("off")
    fig.savefig(pdf_path, dpi=dpi, bbox_inches="tight", pad_inches=0.0, facecolor="white")
    plt.close(fig)




def rgba_over_rgb(dst_rgb: Image.Image, src_rgba: Image.Image) -> Image.Image:
    out = dst_rgb.convert("RGBA")
    out.alpha_composite(src_rgba)
    return out.convert("RGB")


def draw_blurred_polygon(base: Image.Image, points: Sequence[Tuple[float, float]], fill: Tuple[int, int, int, int], blur: float) -> None:
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    d.polygon([(float(x), float(y)) for x, y in points], fill=fill)
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius=blur))
    base.alpha_composite(overlay)


def paste_perspective_image_to_quad(
    base_rgba: Image.Image,
    src_img: Image.Image,
    dst_quad: Sequence[Tuple[float, float]],
) -> None:
    """Warp src_img into dst_quad on base_rgba using a planar homography."""
    src = src_img.convert("RGB")
    src_arr = np.asarray(src).astype(np.float32)
    sh, sw = src_arr.shape[:2]
    dst = np.asarray(dst_quad, dtype=float)
    src_corners = np.array(
        [[0.0, 0.0], [sw - 1.0, 0.0], [sw - 1.0, sh - 1.0], [0.0, sh - 1.0]],
        dtype=float,
    )
    H = compute_homography(src_corners, dst)
    Hinv = np.linalg.inv(H)

    min_x = max(0, int(np.floor(np.min(dst[:, 0]))))
    max_x = min(base_rgba.size[0], int(np.ceil(np.max(dst[:, 0])) + 1))
    min_y = max(0, int(np.floor(np.min(dst[:, 1]))))
    max_y = min(base_rgba.size[1], int(np.ceil(np.max(dst[:, 1])) + 1))
    if max_x <= min_x or max_y <= min_y:
        return

    yy, xx = np.mgrid[min_y:max_y, min_x:max_x]
    homog = np.stack([xx.ravel(), yy.ravel(), np.ones(xx.size)], axis=0)
    uvw = Hinv @ homog
    uvw /= uvw[2:3, :]
    sx = uvw[0, :].reshape(xx.shape)
    sy = uvw[1, :].reshape(yy.shape)

    valid = (sx >= 0) & (sx <= sw - 1) & (sy >= 0) & (sy <= sh - 1)
    if not np.any(valid):
        return

    sx_clip = np.clip(sx, 0, sw - 1)
    sy_clip = np.clip(sy, 0, sh - 1)
    x0 = np.floor(sx_clip).astype(int)
    y0 = np.floor(sy_clip).astype(int)
    x1 = np.clip(x0 + 1, 0, sw - 1)
    y1 = np.clip(y0 + 1, 0, sh - 1)
    wx = sx_clip - x0
    wy = sy_clip - y0

    Ia = src_arr[y0, x0]
    Ib = src_arr[y0, x1]
    Ic = src_arr[y1, x0]
    Id = src_arr[y1, x1]
    rgb = (
        Ia * (1 - wx)[..., None] * (1 - wy)[..., None]
        + Ib * wx[..., None] * (1 - wy)[..., None]
        + Ic * (1 - wx)[..., None] * wy[..., None]
        + Id * wx[..., None] * wy[..., None]
    )

    patch = np.zeros((max_y - min_y, max_x - min_x, 4), dtype=np.uint8)
    patch[..., :3] = np.clip(rgb, 0, 255).astype(np.uint8)
    patch[..., 3] = (valid.astype(np.uint8) * 255)

    overlay = Image.new("RGBA", base_rgba.size, (0, 0, 0, 0))
    overlay.paste(Image.fromarray(patch, mode="RGBA"), (min_x, min_y))
    base_rgba.alpha_composite(overlay)


def draw_math_k_label(
    img: Image.Image,
    xy: Tuple[float, float],
    subscript: str,
    color: str,
    base_size: float,
) -> None:
    draw = ImageDraw.Draw(img)
    italic_path, regular_path, _ = font_paths()
    size = max(12, int(round(base_size)))
    sub_size = max(8, int(round(0.58 * base_size)))
    font_k = load_font(italic_path or regular_path, size)
    font_sub = load_font(italic_path or regular_path, sub_size)
    x = int(round(xy[0]))
    y = int(round(xy[1]))
    rgb = tuple(int(round(c * 255)) for c in mcolors.to_rgb(color))
    outline = (255, 255, 255)
    stroke = max(2, int(round(0.05 * base_size)))
    draw.text((x, y), "k", font=font_k, fill=rgb, stroke_width=stroke, stroke_fill=outline)
    try:
        bbox_k = draw.textbbox((x, y), "k", font=font_k, stroke_width=stroke)
        k_width = bbox_k[2] - bbox_k[0]
    except Exception:
        k_width = int(0.55 * size)
    sub_x = x + int(round(0.78 * k_width))
    sub_y = y + int(round(0.58 * size))
    draw.text((sub_x, sub_y), subscript, font=font_sub, fill=rgb, stroke_width=stroke, stroke_fill=outline)


def draw_arrow(
    img: Image.Image,
    start: Tuple[float, float],
    end: Tuple[float, float],
    color: str,
    width: float,
    head_len: float,
    head_width: float,
) -> None:
    draw = ImageDraw.Draw(img)
    rgb = tuple(int(round(c * 255)) for c in mcolors.to_rgb(color))
    p0 = np.array(start, dtype=float)
    p1 = np.array(end, dtype=float)
    v = p1 - p0
    nrm = float(np.linalg.norm(v))
    if nrm < 1e-9:
        return
    u = v / nrm
    n = np.array([-u[1], u[0]])
    base = p1 - head_len * u
    # soft shadow
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    off = np.array([10.0, 12.0])
    sd.line([tuple(p0 + off), tuple(base + off)], fill=(0, 0, 0, 55), width=int(round(width + 3)))
    head_shadow = [tuple(p1 + off), tuple(base + 0.5 * head_width * n + off), tuple(base - 0.5 * head_width * n + off)]
    sd.polygon(head_shadow, fill=(0, 0, 0, 55))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=5))
    img.alpha_composite(shadow)

    draw = ImageDraw.Draw(img)
    draw.line([tuple(p0), tuple(base)], fill=rgb + (255,), width=int(round(width)))
    head = [tuple(p1), tuple(base + 0.5 * head_width * n), tuple(base - 0.5 * head_width * n)]
    draw.polygon(head, fill=rgb + (255,))


def generate_giwaxs_base_from_detector(detector_image_path: Path, args: argparse.Namespace) -> Image.Image:
    """Generate a full detector/sample/k_i base figure from the detector-only image."""
    w = int(args.base_width)
    h = int(args.base_height)
    base = Image.new("RGBA", (w, h), (255, 255, 255, 255))

    # very subtle background vignette
    yy, xx = np.mgrid[0:h, 0:w]
    cx, cy = 0.58 * w, 0.48 * h
    rr = ((xx - cx) / w) ** 2 + ((yy - cy) / h) ** 2
    shade = np.clip(1.0 - 0.055 * np.exp(-rr / 0.20), 0.94, 1.0)
    bg = np.dstack([shade, shade, shade])
    base = Image.fromarray(np.clip(bg * 255, 0, 255).astype(np.uint8), mode="RGB").convert("RGBA")

    detector = Image.open(detector_image_path).convert("RGB")
    fc = args.face_corners
    front = [(fc[0], fc[1]), (fc[2], fc[3]), (fc[4], fc[5]), (fc[6], fc[7])]
    depth = np.array([28.0, -18.0])

    tl, tr, br, bl = [np.array(p, dtype=float) for p in front]
    top_face = [tuple(tl), tuple(tr), tuple(tr + depth), tuple(tl + depth)]
    side_face = [tuple(tr), tuple(tr + depth), tuple(br + depth), tuple(br)]

    draw_blurred_polygon(base, [tuple(tl + [14, 16]), tuple(tr + [20, 18]), tuple(br + [24, 28]), tuple(bl + [12, 22])], (0, 0, 0, 30), 16)
    d = ImageDraw.Draw(base)
    d.polygon(top_face, fill=(178, 178, 178, 255))
    d.polygon(side_face, fill=(150, 150, 150, 255))
    d.line(top_face + [top_face[0]], fill=(95, 95, 95, 255), width=2)
    d.line(side_face + [side_face[0]], fill=(95, 95, 95, 255), width=2)

    paste_perspective_image_to_quad(base, detector, front)
    d = ImageDraw.Draw(base)
    d.line([tuple(tl), tuple(tr), tuple(br), tuple(bl), tuple(tl)], fill=(65, 65, 65, 255), width=3)

    # Sample shadow and slab.
    sample_top = [(565, 815), (820, 835), (748, 925), (480, 892)]
    sample_front = [(480, 892), (748, 925), (748, 948), (480, 915)]
    sample_right = [(820, 835), (748, 925), (748, 948), (840, 858)]
    draw_blurred_polygon(base, [(510, 897), (785, 916), (745, 962), (475, 936)], (0, 0, 0, 42), 14)
    d = ImageDraw.Draw(base)
    d.polygon(sample_right, fill=(175, 175, 175, 255))
    d.polygon(sample_front, fill=(160, 160, 160, 255))
    d.polygon(sample_top, fill=(205, 205, 205, 255))
    d.line(sample_top + [sample_top[0]], fill=(120, 120, 120, 255), width=2)
    d.line(sample_front + [sample_front[0]], fill=(120, 120, 120, 255), width=2)
    d.line(sample_right + [sample_right[0]], fill=(120, 120, 120, 255), width=2)

    # Incident beam and label.
    draw_arrow(
        base,
        start=(215.0, 958.0),
        end=tuple(map(float, args.tail)),
        color="#004cff",
        width=15.0,
        head_len=52.0,
        head_width=48.0,
    )
    draw_math_k_label(base, (178.0, 850.0), "i", "#004cff", 62.0)

    return base.convert("RGB")

class GiwaxsRenderer:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.figure_path = Path(args.figure)
        if not self.figure_path.exists():
            raise SystemExit(f"Input image not found: {self.figure_path}")

        input_img = Image.open(self.figure_path).convert("RGB")
        input_w, input_h = input_img.size
        needed_w = int(max(args.crop_box[2], max(args.face_corners[0::2])) + 20)
        needed_h = int(max(args.crop_box[3], max(args.face_corners[1::2])) + 20)
        source_is_too_small_for_base = input_w < needed_w or input_h < needed_h

        if args.input_mode == "detector":
            self.generate_base = True
        elif args.input_mode == "base":
            self.generate_base = False
        else:
            self.generate_base = source_is_too_small_for_base

        if self.generate_base:
            detector_path = Path(args.detector_image) if args.detector_image else self.figure_path
            if not detector_path.exists():
                raise SystemExit(f"Detector image not found: {detector_path}")
            self.detector_image_path = detector_path
            self.base = generate_giwaxs_base_from_detector(detector_path, args)
            self.base_size = self.base.size
            print(f"Generated full GIWAXS figure from detector image: {detector_path.name}")
        else:
            detector_path = Path(args.detector_image) if args.detector_image else self.figure_path.with_name("biggerB_4deg_2m.png")
            self.detector_image_path = detector_path if detector_path.exists() else None
            if self.detector_image_path is None:
                print("Warning: detector image not found. Peak picking and maxima snapping will be unavailable.", file=sys.stderr)
            self.base = input_img
            self.base_size = self.base.size
            print(f"Using existing full figure: {self.figure_path.name}")

        self.original_peaks: List[Peak] = load_peaks(args)

        det_w, det_h = map(float, args.detector_size)
        src = np.array(
            [
                [0.0, 0.0],
                [det_w - 1.0, 0.0],
                [det_w - 1.0, det_h - 1.0],
                [0.0, det_h - 1.0],
            ],
            dtype=float,
        )
        fc = args.face_corners
        dst = np.array(
            [
                [fc[0], fc[1]],
                [fc[2], fc[3]],
                [fc[4], fc[5]],
                [fc[6], fc[7]],
            ],
            dtype=float,
        )
        self.H = compute_homography(src, dst)
        self.tail0 = tuple(map(float, args.tail))
        self.crop = not args.no_crop
        self.crop_box = args.crop_box
        self.detector_size = tuple(map(float, args.detector_size))
        self.intensity_cache: Dict[float, np.ndarray] = {}
        self.detector_image_cache: Image.Image | None = None

        self.last_config: FigureConfig | None = None
        self.last_toggles: ToggleConfig | None = None
        self.last_peaks: List[Peak] = []
        self.last_mapped: np.ndarray = np.zeros((0, 2), dtype=float)

    def detector_image(self) -> Image.Image | None:
        if self.detector_image_path is None:
            return None
        if self.detector_image_cache is None:
            self.detector_image_cache = Image.open(self.detector_image_path).convert("RGB")
        return self.detector_image_cache

    def intensity(self, blur: float) -> np.ndarray:
        if self.detector_image_path is None:
            raise RuntimeError("detector image is not available")
        key = round(float(blur), 3)
        if key not in self.intensity_cache:
            self.intensity_cache[key] = detector_intensity_map(self.detector_image_path, key)
        return self.intensity_cache[key]

    def current_peaks(self, cfg: FigureConfig, toggles: ToggleConfig) -> List[Peak]:
        if toggles.snap_to_maxima and self.detector_image_path is not None and self.original_peaks:
            return snap_peaks_to_local_maxima(self.original_peaks, self.intensity(cfg.maxima_blur), int(round(cfg.maxima_radius)))
        return [Peak(p.x, p.y, p.label) for p in self.original_peaks]

    def render(self, cfg: FigureConfig, toggles: ToggleConfig, scale: float) -> Image.Image:
        self.last_config = cfg
        self.last_toggles = toggles

        w0, h0 = self.base_size
        base_scaled = self.base.resize((int(round(w0 * scale)), int(round(h0 * scale))), Image.Resampling.LANCZOS)

        peaks = self.current_peaks(cfg, toggles)
        spots = [(p.x, p.y) for p in peaks]
        mapped = map_points(self.H, spots)
        self.last_peaks = peaks
        self.last_mapped = mapped

        rgb = np.asarray(base_scaled).astype(np.float32) / 255.0
        cone_color = COLOR_PRESETS.get(cfg.color_name, cfg.color_name)
        cone_rgb = np.array(mcolors.to_rgb(cone_color), dtype=np.float32)
        light_cone_rgb = 0.55 * cone_rgb + 0.45 * np.array([1.0, 1.0, 1.0], dtype=np.float32)
        white_rgb = np.array([1.0, 1.0, 1.0], dtype=np.float32)

        tail = (self.tail0[0] * scale, self.tail0[1] * scale)

        if toggles.halo:
            for peak, head0 in zip(peaks, mapped):
                sigma_head0 = projected_perpendicular_sigma(self.H, (peak.x, peak.y), self.tail0, cfg.detector_sigma, cfg.detector_sigma)
                ys, xs, alpha = cone_alpha_mask(
                    rgb.shape[:2],
                    tail,
                    (head0[0] * scale, head0[1] * scale),
                    cfg.source_sigma * scale * 1.55,
                    sigma_head0 * scale * 1.55,
                    cfg.halo_alpha,
                    2.7,
                    cfg.longitudinal_fade,
                )
                composite_color(rgb, white_rgb, alpha, ys, xs)

        for peak, head0 in zip(peaks, mapped):
            sigma_head0 = projected_perpendicular_sigma(self.H, (peak.x, peak.y), self.tail0, cfg.detector_sigma, cfg.detector_sigma)
            head = (head0[0] * scale, head0[1] * scale)
            ys, xs, alpha = cone_alpha_mask(
                rgb.shape[:2],
                tail,
                head,
                cfg.source_sigma * scale,
                sigma_head0 * scale,
                cfg.max_alpha,
                2.7,
                cfg.longitudinal_fade,
            )
            composite_color(rgb, cone_rgb, alpha, ys, xs)

            if toggles.detector_caps:
                cap_sigma = sigma_head0 * scale * cfg.detector_cap_sigma_scale
                if toggles.halo:
                    ys, xs, alpha = gaussian_spot_alpha_mask(rgb.shape[:2], head, cap_sigma * 1.55, cap_sigma * 1.55, 0.06)
                    composite_color(rgb, white_rgb, alpha, ys, xs)
                ys, xs, alpha = gaussian_spot_alpha_mask(rgb.shape[:2], head, cap_sigma, cap_sigma, cfg.detector_cap_alpha)
                composite_color(rgb, cone_rgb, alpha, ys, xs)

        if toggles.sample_glow:
            sample_sigma = cfg.sample_glow_sigma * scale
            ys, xs, alpha = gaussian_spot_alpha_mask(rgb.shape[:2], tail, sample_sigma * 1.8, sample_sigma * 1.8, 0.06)
            composite_color(rgb, white_rgb, alpha, ys, xs)
            ys, xs, alpha = gaussian_spot_alpha_mask(rgb.shape[:2], tail, sample_sigma, sample_sigma, cfg.sample_glow_alpha)
            composite_color(rgb, light_cone_rgb, alpha, ys, xs)

        out_img = Image.fromarray(np.clip(rgb * 255.0, 0, 255).astype(np.uint8), mode="RGB")

        if toggles.bragg_labels:
            draw_bragg_peak_labels(
                out_img,
                peaks,
                mapped,
                self.tail0,
                self.detector_size,
                cfg.bragg_label_size,
                cfg.bragg_label_offset,
                scale,
            )

        if toggles.setup_labels:
            draw_kf_label(out_img, (cfg.kf_label_x, cfg.kf_label_y), cone_color, 44.0, scale)
            draw_callout(out_img, tuple(map(float, self.args.area_detector_dot)), tuple(map(float, self.args.area_detector_text_pos)),
                         "Area detector", anchor="right", base_font_size=cfg.callout_font_size,
                         base_line_width=2.2, base_dot_radius=7.0, base_gap=12.0, scale=scale)
            draw_callout(out_img, tuple(map(float, self.args.sample_dot)), tuple(map(float, self.args.sample_text_pos)),
                         "Sample", anchor="left", base_font_size=cfg.callout_font_size,
                         base_line_width=2.2, base_dot_radius=7.0, base_gap=12.0, scale=scale)

        if toggles.show_centers:
            draw_center_dots(out_img, mapped, scale)

        if self.crop:
            out_img = crop_image(out_img, self.crop_box, scale=scale)
        return out_img

    def output_png_path(self) -> Path:
        if self.args.output:
            return Path(self.args.output)
        if self.args.output_prefix:
            return Path(self.args.output_prefix).with_suffix(".png")
        return self.figure_path.with_name(f"{self.figure_path.stem}_generated_giwaxs_tuned.png" if self.generate_base else f"{self.figure_path.stem}_interactive_bragg_tuned.png")

    def save(self, cfg: FigureConfig, toggles: ToggleConfig) -> None:
        out_path = self.output_png_path()
        out_img = self.render(cfg, toggles, scale=float(self.args.output_scale))
        out_img.save(out_path, dpi=(self.args.dpi, self.args.dpi))
        print(f"Saved {out_path}")

        if self.args.pdf:
            pdf_path = out_path.with_suffix(".pdf")
            save_pdf_from_png(out_path, pdf_path, dpi=int(self.args.dpi))
            print(f"Saved {pdf_path}")

        if self.args.save_generated_base and self.generate_base:
            base_path = out_path.with_name(out_path.stem + "_generated_base.png")
            self.base.save(base_path, dpi=(self.args.dpi, self.args.dpi))
            print(f"Saved {base_path}")

        config_path = out_path.with_name(out_path.stem + "_config.json")
        config_payload = {
            "config": asdict(cfg),
            "toggles": asdict(toggles),
            "input_mode": "detector-generated-base" if self.generate_base else "existing-base",
            "original_bragg_peaks": [asdict(p) for p in self.original_peaks],
            "snapped_or_used_bragg_peaks": [asdict(p) for p in self.last_peaks],
            "mapped_detector_face_points_base_px": self.last_mapped.tolist(),
            "figure": str(self.figure_path),
            "detector_image": str(self.detector_image_path) if self.detector_image_path else None,
        }
        config_path.write_text(json.dumps(config_payload, indent=2))
        print(f"Saved {config_path}")

        csv_path = out_path.with_name(out_path.stem + "_bragg_peaks.csv")
        with csv_path.open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["index", "label", "clicked_x", "clicked_y", "used_x", "used_y", "figure_x_base_px", "figure_y_base_px"])
            for i, (orig, used, mapped) in enumerate(zip(self.original_peaks, self.last_peaks, self.last_mapped), start=1):
                writer.writerow([i, used.label, f"{orig.x:.6f}", f"{orig.y:.6f}", f"{used.x:.6f}", f"{used.y:.6f}", f"{mapped[0]:.6f}", f"{mapped[1]:.6f}"])
        print(f"Saved {csv_path}")


class BraggPeakEditor:
    def __init__(self, renderer: GiwaxsRenderer, cfg_getter, toggles_getter, redraw_callback):
        self.renderer = renderer
        self.cfg_getter = cfg_getter
        self.toggles_getter = toggles_getter
        self.redraw_callback = redraw_callback
        self.selected_index: int | None = 0 if renderer.original_peaks else None
        self.dragging = False
        self.threshold_px = 12.0

        detector = renderer.detector_image()
        if detector is None:
            print("Detector image unavailable. Cannot open Bragg peak picker.", file=sys.stderr)
            return
        self.detector = detector
        self.detector_arr = np.asarray(detector)
        self.fig = plt.figure(figsize=(8.5, 8.0))
        self.fig.canvas.manager.set_window_title("Bragg peak picker")
        self.ax = self.fig.add_axes([0.06, 0.18, 0.88, 0.78])
        self.ax_name = self.fig.add_axes([0.16, 0.08, 0.36, 0.045])
        self.name_box = TextBox(self.ax_name, "Name", initial=self.current_label())
        self.name_box.on_submit(self.rename_selected)
        self.ax_snap = self.fig.add_axes([0.56, 0.08, 0.14, 0.045])
        self.btn_snap = Button(self.ax_snap, "Snap all")
        self.btn_snap.on_clicked(self.snap_all)
        self.ax_clear = self.fig.add_axes([0.72, 0.08, 0.10, 0.045])
        self.btn_clear = Button(self.ax_clear, "Clear")
        self.btn_clear.on_clicked(self.clear_all)
        self.ax_close = self.fig.add_axes([0.84, 0.08, 0.10, 0.045])
        self.btn_close = Button(self.ax_close, "Close")
        self.btn_close.on_clicked(lambda _: plt.close(self.fig))

        self.cid_press = self.fig.canvas.mpl_connect("button_press_event", self.on_press)
        self.cid_motion = self.fig.canvas.mpl_connect("motion_notify_event", self.on_motion)
        self.cid_release = self.fig.canvas.mpl_connect("button_release_event", self.on_release)
        self.cid_key = self.fig.canvas.mpl_connect("key_press_event", self.on_key)
        self.redraw()
        plt.show(block=False)

    def current_label(self) -> str:
        if self.selected_index is None or self.selected_index >= len(self.renderer.original_peaks):
            return ""
        return self.renderer.original_peaks[self.selected_index].label

    def set_name_box(self) -> None:
        try:
            self.name_box.set_val(self.current_label())
        except Exception:
            pass

    def nearest_peak(self, x: float, y: float) -> Tuple[int | None, float]:
        if not self.renderer.original_peaks:
            return None, float("inf")
        pts = np.array([[p.x, p.y] for p in self.renderer.original_peaks], dtype=float)
        d2 = np.sum((pts - np.array([x, y])) ** 2, axis=1)
        idx = int(np.argmin(d2))
        return idx, float(np.sqrt(d2[idx]))

    def redraw(self) -> None:
        self.ax.clear()
        self.ax.imshow(self.detector_arr)
        h, w = self.detector_arr.shape[:2]
        self.ax.set_xlim(0, w)
        self.ax.set_ylim(h, 0)
        self.ax.set_title("Left click add/select, drag to move, right click delete. Rename selected in the text box.")
        self.ax.set_xlabel("detector x pixel")
        self.ax.set_ylabel("detector y pixel")

        cfg = self.cfg_getter()
        toggles = self.toggles_getter()
        used_peaks = self.renderer.current_peaks(cfg, toggles)
        for i, peak in enumerate(self.renderer.original_peaks):
            selected = i == self.selected_index
            self.ax.plot(peak.x, peak.y, "o", ms=8 if selected else 6, mfc="none" if selected else "yellow", mec="white" if selected else "black", mew=2 if selected else 1.2)
            self.ax.text(peak.x + 5, peak.y - 5, peak.label, color="white", fontsize=10, weight="bold", path_effects=[])
            if toggles.snap_to_maxima and i < len(used_peaks):
                used = used_peaks[i]
                self.ax.plot(used.x, used.y, "x", ms=8, color="red", mew=1.5)
        self.fig.canvas.draw_idle()

    def notify_change(self) -> None:
        self.renderer.intensity_cache.clear()
        self.redraw()
        self.redraw_callback()

    def rename_selected(self, text: str) -> None:
        if self.selected_index is None or self.selected_index >= len(self.renderer.original_peaks):
            return
        self.renderer.original_peaks[self.selected_index].label = str(text).strip()
        self.notify_change()

    def add_peak(self, x: float, y: float) -> None:
        label = f"B{len(self.renderer.original_peaks) + 1}"
        self.renderer.original_peaks.append(Peak(float(x), float(y), label))
        self.selected_index = len(self.renderer.original_peaks) - 1
        self.set_name_box()
        self.notify_change()

    def delete_peak(self, idx: int) -> None:
        if idx < 0 or idx >= len(self.renderer.original_peaks):
            return
        del self.renderer.original_peaks[idx]
        if not self.renderer.original_peaks:
            self.selected_index = None
        else:
            self.selected_index = min(idx, len(self.renderer.original_peaks) - 1)
        self.set_name_box()
        self.notify_change()

    def on_press(self, event) -> None:
        if event.inaxes != self.ax or event.xdata is None or event.ydata is None:
            return
        x = float(event.xdata)
        y = float(event.ydata)
        idx, dist = self.nearest_peak(x, y)
        if event.button == 1:
            if idx is not None and dist <= self.threshold_px:
                self.selected_index = idx
                self.dragging = True
                self.set_name_box()
                self.redraw()
            else:
                self.add_peak(x, y)
                self.dragging = True
        elif event.button == 3:
            if idx is not None and dist <= 2 * self.threshold_px:
                self.delete_peak(idx)

    def on_motion(self, event) -> None:
        if not self.dragging or self.selected_index is None:
            return
        if event.inaxes != self.ax or event.xdata is None or event.ydata is None:
            return
        h, w = self.detector_arr.shape[:2]
        peak = self.renderer.original_peaks[self.selected_index]
        peak.x = float(np.clip(event.xdata, 0, w - 1))
        peak.y = float(np.clip(event.ydata, 0, h - 1))
        self.notify_change()

    def on_release(self, event) -> None:
        self.dragging = False

    def on_key(self, event) -> None:
        if event.key in ("delete", "backspace") and self.selected_index is not None:
            self.delete_peak(self.selected_index)
        elif event.key == "n":
            self.name_box.begin_typing(None)
        elif event.key == "escape":
            plt.close(self.fig)

    def snap_all(self, _=None) -> None:
        if self.renderer.detector_image_path is None:
            return
        cfg = self.cfg_getter()
        intensity = self.renderer.intensity(cfg.maxima_blur)
        snapped = snap_peaks_to_local_maxima(self.renderer.original_peaks, intensity, int(round(cfg.maxima_radius)))
        self.renderer.original_peaks = snapped
        self.set_name_box()
        self.notify_change()

    def clear_all(self, _=None) -> None:
        self.renderer.original_peaks = []
        self.selected_index = None
        self.set_name_box()
        self.notify_change()


def make_config_from_sliders(sliders: Dict[str, Slider], color_name: str) -> FigureConfig:
    return FigureConfig(
        color_name=color_name,
        max_alpha=float(sliders["max_alpha"].val),
        detector_sigma=float(sliders["detector_sigma"].val),
        source_sigma=float(sliders["source_sigma"].val),
        longitudinal_fade=float(sliders["longitudinal_fade"].val),
        detector_cap_alpha=float(sliders["cap_alpha"].val),
        detector_cap_sigma_scale=float(sliders["cap_sigma"].val),
        sample_glow_alpha=float(sliders["sample_glow_alpha"].val),
        sample_glow_sigma=float(sliders["sample_glow_sigma"].val),
        halo_alpha=float(sliders["halo_alpha"].val),
        maxima_radius=int(round(sliders["maxima_radius"].val)),
        maxima_blur=float(sliders["maxima_blur"].val),
        kf_label_x=float(sliders["kf_x"].val),
        kf_label_y=float(sliders["kf_y"].val),
        bragg_label_size=float(sliders["bragg_label_size"].val),
        bragg_label_offset=float(sliders["bragg_label_offset"].val),
        callout_font_size=float(sliders["callout_size"].val),
    )


def toggles_from_checkboxes(check: CheckButtons) -> ToggleConfig:
    status = check.get_status()
    return ToggleConfig(
        snap_to_maxima=bool(status[0]),
        halo=bool(status[1]),
        detector_caps=bool(status[2]),
        sample_glow=bool(status[3]),
        setup_labels=bool(status[4]),
        bragg_labels=bool(status[5]),
        show_centers=bool(status[6]),
    )


def run_interactive(renderer: GiwaxsRenderer, args: argparse.Namespace) -> None:
    defaults = FigureConfig()
    initial_toggles = ToggleConfig(snap_to_maxima=renderer.detector_image_path is not None)

    fig = plt.figure(figsize=(16, 8.8))
    ax_img = fig.add_axes([0.02, 0.04, 0.68, 0.92])
    ax_img.axis("off")
    fig.canvas.manager.set_window_title("GIWAXS Bragg-peak figure tuner")

    color_state = {"name": defaults.color_name}
    update_lock = {"busy": False}
    editors: List[BraggPeakEditor] = []

    sliders: Dict[str, Slider] = {}
    slider_specs = [
        ("max_alpha", "Cone alpha", 0.00, 0.80, defaults.max_alpha, 0.01),
        ("detector_sigma", "Detector sigma", 2.0, 20.0, defaults.detector_sigma, 0.5),
        ("source_sigma", "Source sigma", 0.2, 4.0, defaults.source_sigma, 0.1),
        ("longitudinal_fade", "Source fade", 0.00, 0.65, defaults.longitudinal_fade, 0.01),
        ("cap_alpha", "Cap alpha", 0.00, 0.45, defaults.detector_cap_alpha, 0.01),
        ("cap_sigma", "Cap sigma scale", 0.20, 2.00, defaults.detector_cap_sigma_scale, 0.05),
        ("sample_glow_alpha", "Sample glow", 0.00, 0.35, defaults.sample_glow_alpha, 0.01),
        ("sample_glow_sigma", "Glow sigma", 2.0, 20.0, defaults.sample_glow_sigma, 0.5),
        ("halo_alpha", "Halo alpha", 0.00, 0.25, defaults.halo_alpha, 0.01),
        ("maxima_radius", "Max search r", 2.0, 30.0, defaults.maxima_radius, 1.0),
        ("maxima_blur", "Max blur", 0.0, 5.0, defaults.maxima_blur, 0.25),
        ("kf_x", "k_f x", 600.0, 790.0, defaults.kf_label_x, 1.0),
        ("kf_y", "k_f y", 690.0, 840.0, defaults.kf_label_y, 1.0),
        ("bragg_label_size", "Bragg label size", 8.0, 26.0, defaults.bragg_label_size, 1.0),
        ("bragg_label_offset", "Bragg label offset", 5.0, 70.0, defaults.bragg_label_offset, 1.0),
        ("callout_size", "Setup label size", 18.0, 36.0, defaults.callout_font_size, 1.0),
    ]

    y0 = 0.935
    dy = 0.035
    for i, (key, label, vmin, vmax, val, step) in enumerate(slider_specs):
        ax = fig.add_axes([0.74, y0 - i * dy, 0.22, 0.022])
        sliders[key] = Slider(ax, label, vmin, vmax, valinit=val, valstep=step)

    ax_check = fig.add_axes([0.74, 0.205, 0.22, 0.165])
    check = CheckButtons(
        ax_check,
        ["snap maxima", "halo", "caps", "sample glow", "setup labels", "Bragg labels", "show centers"],
        [
            initial_toggles.snap_to_maxima,
            initial_toggles.halo,
            initial_toggles.detector_caps,
            initial_toggles.sample_glow,
            initial_toggles.setup_labels,
            initial_toggles.bragg_labels,
            initial_toggles.show_centers,
        ],
    )

    ax_radio = fig.add_axes([0.74, 0.065, 0.10, 0.115])
    radio = RadioButtons(ax_radio, list(COLOR_PRESETS.keys()), active=list(COLOR_PRESETS.keys()).index(defaults.color_name))

    ax_save = fig.add_axes([0.87, 0.145, 0.09, 0.04])
    btn_save = Button(ax_save, "Save")
    ax_edit = fig.add_axes([0.87, 0.095, 0.09, 0.04])
    btn_edit = Button(ax_edit, "Edit peaks")
    ax_reset = fig.add_axes([0.87, 0.045, 0.09, 0.04])
    btn_reset = Button(ax_reset, "Reset")

    preview_img = renderer.render(defaults, initial_toggles, scale=float(args.preview_scale))
    im_artist = ax_img.imshow(preview_img)
    title = ax_img.set_title("Live preview. Edit peaks to choose and name Bragg peaks. Press s to save, q to quit.", fontsize=10)

    def current_config() -> FigureConfig:
        return make_config_from_sliders(sliders, color_state["name"])

    def current_toggles() -> ToggleConfig:
        return toggles_from_checkboxes(check)

    def redraw(_=None) -> None:
        if update_lock["busy"]:
            return
        update_lock["busy"] = True
        try:
            cfg = current_config()
            toggles = current_toggles()
            img = renderer.render(cfg, toggles, scale=float(args.preview_scale))
            im_artist.set_data(np.asarray(img))
            ax_img.set_xlim(0, img.size[0])
            ax_img.set_ylim(img.size[1], 0)
            if renderer.last_peaks:
                labels = ", ".join(p.label for p in renderer.last_peaks[:4])
                if len(renderer.last_peaks) > 4:
                    labels += ", ..."
                title.set_text(f"{len(renderer.last_peaks)} Bragg peak(s): {labels}. Press s to save, q to quit.")
            else:
                title.set_text("No Bragg peaks selected. Click Edit peaks to add them.")
            fig.canvas.draw_idle()
            for editor in editors[:]:
                if plt.fignum_exists(editor.fig.number):
                    editor.redraw()
                else:
                    editors.remove(editor)
        finally:
            update_lock["busy"] = False

    for slider in sliders.values():
        slider.on_changed(redraw)

    check.on_clicked(lambda _label: redraw())

    def on_color(label: str) -> None:
        color_state["name"] = label
        redraw()

    radio.on_clicked(on_color)

    def save_current(_=None) -> None:
        renderer.save(current_config(), current_toggles())

    btn_save.on_clicked(save_current)

    def open_editor(_=None) -> None:
        editor = BraggPeakEditor(renderer, current_config, current_toggles, redraw)
        if hasattr(editor, "fig"):
            editors.append(editor)

    btn_edit.on_clicked(open_editor)

    def reset(_=None) -> None:
        color_state["name"] = defaults.color_name
        radio.set_active(list(COLOR_PRESETS.keys()).index(defaults.color_name))
        defaults_map = {
            "max_alpha": defaults.max_alpha,
            "detector_sigma": defaults.detector_sigma,
            "source_sigma": defaults.source_sigma,
            "longitudinal_fade": defaults.longitudinal_fade,
            "cap_alpha": defaults.detector_cap_alpha,
            "cap_sigma": defaults.detector_cap_sigma_scale,
            "sample_glow_alpha": defaults.sample_glow_alpha,
            "sample_glow_sigma": defaults.sample_glow_sigma,
            "halo_alpha": defaults.halo_alpha,
            "maxima_radius": defaults.maxima_radius,
            "maxima_blur": defaults.maxima_blur,
            "kf_x": defaults.kf_label_x,
            "kf_y": defaults.kf_label_y,
            "bragg_label_size": defaults.bragg_label_size,
            "bragg_label_offset": defaults.bragg_label_offset,
            "callout_size": defaults.callout_font_size,
        }
        for key, val in defaults_map.items():
            sliders[key].set_val(val)
        redraw()

    btn_reset.on_clicked(reset)

    def on_key(event) -> None:
        if event.key == "s":
            save_current()
        elif event.key == "r":
            reset()
        elif event.key == "q":
            plt.close(fig)

    fig.canvas.mpl_connect("key_press_event", on_key)
    plt.show()


def main() -> None:
    args = parse_args()
    renderer = GiwaxsRenderer(args)
    defaults = FigureConfig()
    toggles = ToggleConfig(snap_to_maxima=renderer.detector_image_path is not None)
    if args.save_only:
        renderer.save(defaults, toggles)
        return
    run_interactive(renderer, args)


if __name__ == "__main__":
    main()
