"""Compose special-cause matrix PNGs from exported matrix-cell images."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from io import BytesIO
import json
import math
from pathlib import Path
import re
import sys
from typing import Any, Iterable
import zipfile

from PIL import Image, ImageDraw, ImageFont, PngImagePlugin
from plotly.colors import sample_colorscale

from mosaic_sim.detector import SPECIAL_CAUSE_MOSAIC_COLORSCALE

CELL_METADATA_KEY = "special_cause_metadata"
MATRIX_METADATA_KEY = "special_cause_matrix_metadata"
MANIFEST_NAME = "special_cause_reciprocal_matrix_cells.json"
CELL_KIND = "special-cause-matrix-cell"
BUNDLE_KIND = "special-cause-matrix-cell-bundle"

# =============================================================================
# User settings
# =============================================================================
# Change these defaults when running the script directly. Command-line arguments
# still override these values for one-off runs.

DEFAULT_INPUT_BUNDLE_NAME = "special_cause_reciprocal_matrix_cells.zip"
DEFAULT_OUTPUT_PATH = "special_cause_reciprocal_matrix_ratio_scaled.png"

OUTPUT_WIDTH_PX = 2400
OUTPUT_HEIGHT_PX: int | None = None  # None keeps the output square.

MATRIX_TITLE = "theta"
Y_AXIS_TITLE = "L"
TITLE_FONT_SIZE_PT = 90
AXIS_FONT_SIZE_PT = 90

# None uses the bundle metadata, then FALLBACK_BRAGG_FILL_FRACTION if the bundle
# does not provide a value.
BRAGG_FILL_FRACTION: float | None = None
FALLBACK_BRAGG_FILL_FRACTION = 0.82

GLOBAL_CELL_SCALE = 1.0

# Per-cell image multipliers used when no --scale values are supplied.
# Format: (L value, theta degrees, multiplier)
DEFAULT_CELL_SCALE_OVERRIDES = [
    (3, 5.0, 1.0 / 3.0),
    (3, 10.0, 1.0 / 3.0),
    (3, 15.0, 1.0 / 3.0),
    (6, 5.0, 2.0 / 3.0),
    (6, 10.0, 2.0 / 3.0),
    (6, 15.0, 2.0 / 3.0),
    (9, 5.0, 1.0),
    (9, 10.0, 1.0),
    (9, 15.0, 1.0),
]

# None uses the bundle default. True preserves relative L size; False scales each
# row locally so the Bragg footprint fills the same fraction of its grid cell.
PRESERVE_RELATIVE_L_SCALE: bool | None = None

SHOW_COLORBAR = True
CLIP_CELLS_TO_GRID = True
TRANSPARENT_BACKGROUND = False
DRAW_DEBUG_BOXES = False

LAYOUT_PX = {
    "outer_margin": 120,
    "row_label_band": 170,
    "colorbar_band": 170,
    "colorbar_band_when_hidden": 28,
    "title_band": 130,
    "column_label_band": 130,
    "bottom_margin": 80,
}


@dataclass(frozen=True)
class CellImage:
    """One cropped matrix-cell image plus the metadata needed for placement."""

    metadata: dict[str, Any]
    image: Image.Image


class _BundleReader:
    def names(self) -> list[str]:
        raise NotImplementedError

    def read_bytes(self, name: str) -> bytes:
        raise NotImplementedError

    def close(self) -> None:
        return None


class _DirectoryReader(_BundleReader):
    def __init__(self, path: Path):
        self.path = path
        self._names = [item.relative_to(path).as_posix() for item in path.rglob("*") if item.is_file()]

    def names(self) -> list[str]:
        return list(self._names)

    def read_bytes(self, name: str) -> bytes:
        return (self.path / name).read_bytes()


class _ZipReader(_BundleReader):
    def __init__(self, path: Path):
        self.archive = zipfile.ZipFile(path)
        self._names = [name for name in self.archive.namelist() if not name.endswith("/")]

    def names(self) -> list[str]:
        return list(self._names)

    def read_bytes(self, name: str) -> bytes:
        return self.archive.read(name)

    def close(self) -> None:
        self.archive.close()


def _open_reader(path: Path) -> _BundleReader:
    if path.is_dir():
        return _DirectoryReader(path)
    if path.is_file() and zipfile.is_zipfile(path):
        return _ZipReader(path)
    raise ValueError(f"Input must be an exported ZIP bundle or directory: {path}")


def _load_json_bytes(raw: bytes, *, source: str) -> dict[str, Any]:
    try:
        value = json.loads(raw.decode("utf-8"))
    except UnicodeDecodeError as exc:
        raise ValueError(f"Metadata is not UTF-8 JSON: {source}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON metadata in {source}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"Metadata must be a JSON object: {source}")
    return value


def _png_metadata_and_image(raw: bytes) -> tuple[dict[str, Any] | None, Image.Image]:
    image = Image.open(BytesIO(raw))
    metadata_text = image.info.get(CELL_METADATA_KEY)
    if metadata_text is None:
        metadata_text = getattr(image, "text", {}).get(CELL_METADATA_KEY)
    metadata = None
    if isinstance(metadata_text, str) and metadata_text.strip():
        metadata = _load_json_bytes(metadata_text.encode("utf-8"), source="embedded PNG metadata")
    return metadata, image.convert("RGBA")


def _find_manifest_name(names: Iterable[str]) -> str | None:
    for name in names:
        if Path(name).name == MANIFEST_NAME:
            return name
    return None


def _metadata_candidates(names: Iterable[str]) -> list[str]:
    return [name for name in names if name.lower().endswith(".json") and Path(name).name != MANIFEST_NAME]


def _png_candidates(names: Iterable[str]) -> list[str]:
    return [name for name in names if name.lower().endswith(".png")]


def _resolve_image_path(metadata: dict[str, Any], names: set[str]) -> str | None:
    image_path = metadata.get("image_path")
    if isinstance(image_path, str) and image_path in names:
        return image_path

    metadata_path = metadata.get("metadata_path")
    if isinstance(metadata_path, str):
        stem = Path(metadata_path).stem
        for prefix in ("cells", ""):
            candidate = f"{prefix + '/' if prefix else ''}{stem}.png"
            if candidate in names:
                return candidate

    stem = Path(str(image_path or metadata_path or "")).stem
    if stem:
        for name in names:
            path = Path(name)
            if path.suffix.lower() == ".png" and path.stem == stem:
                return name
    return None


def load_cell_bundle(input_path: str | Path) -> tuple[dict[str, Any], list[CellImage]]:
    """Load an exported special-cause cell bundle.

    ``input_path`` may be the ZIP downloaded by the GUI or an extracted directory.
    Metadata is read from the bundle manifest, JSON sidecars, or embedded PNG iTXt
    chunks, in that order.
    """

    path = Path(input_path)
    reader = _open_reader(path)
    try:
        names = reader.names()
        name_set = set(names)
        manifest_name = _find_manifest_name(names)
        manifest: dict[str, Any] = {}
        cells: list[CellImage] = []

        if manifest_name is not None:
            manifest = _load_json_bytes(reader.read_bytes(manifest_name), source=manifest_name)
            raw_cells = manifest.get("cells", [])
            if not isinstance(raw_cells, list):
                raise ValueError(f"Manifest cells must be a list: {manifest_name}")
            for index, raw_metadata in enumerate(raw_cells):
                if not isinstance(raw_metadata, dict):
                    raise ValueError(f"Manifest cell {index} is not an object")
                metadata = dict(raw_metadata)
                metadata_path = metadata.get("metadata_path")
                if isinstance(metadata_path, str) and metadata_path in name_set:
                    sidecar_metadata = _load_json_bytes(reader.read_bytes(metadata_path), source=metadata_path)
                    metadata.update(sidecar_metadata)
                image_path = _resolve_image_path(metadata, name_set)
                if image_path is None:
                    raise ValueError(f"Could not find PNG for cell metadata entry {index}")
                png_metadata, image = _png_metadata_and_image(reader.read_bytes(image_path))
                if png_metadata:
                    metadata.update(png_metadata)
                metadata.setdefault("image_path", image_path)
                cells.append(CellImage(metadata=metadata, image=image))
        else:
            for metadata_name in _metadata_candidates(names):
                metadata = _load_json_bytes(reader.read_bytes(metadata_name), source=metadata_name)
                if metadata.get("kind") != CELL_KIND:
                    continue
                metadata.setdefault("metadata_path", metadata_name)
                image_path = _resolve_image_path(metadata, name_set)
                if image_path is None:
                    continue
                png_metadata, image = _png_metadata_and_image(reader.read_bytes(image_path))
                if png_metadata:
                    metadata.update(png_metadata)
                metadata.setdefault("image_path", image_path)
                cells.append(CellImage(metadata=metadata, image=image))

            if not cells:
                for image_name in _png_candidates(names):
                    metadata, image = _png_metadata_and_image(reader.read_bytes(image_name))
                    if metadata and metadata.get("kind") == CELL_KIND:
                        metadata.setdefault("image_path", image_name)
                        cells.append(CellImage(metadata=metadata, image=image))

        if not cells:
            raise ValueError("No special-cause matrix cell images were found.")
        return manifest, cells
    finally:
        reader.close()


def _numeric_key(value: Any, *, ndigits: int = 6) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return math.nan
    return round(numeric, ndigits)


def _cell_key(L: Any, theta_deg: Any) -> tuple[int, float]:
    return int(round(float(L))), _numeric_key(theta_deg)


def _ordered_values_from_manifest_or_cells(
    manifest: dict[str, Any],
    cells: list[CellImage],
    key: str,
    metadata_key: str,
) -> list[float | int]:
    manifest_values = manifest.get(key)
    if isinstance(manifest_values, list) and manifest_values:
        return [int(value) if key == "L_values" else float(value) for value in manifest_values]

    values = []
    seen = set()
    for cell in cells:
        value = cell.metadata.get(metadata_key)
        if value is None:
            continue
        normalized = int(round(float(value))) if key == "L_values" else _numeric_key(value)
        if normalized not in seen:
            seen.add(normalized)
            values.append(normalized)
    return sorted(values)


def _bbox(metadata: dict[str, Any], image: Image.Image) -> dict[str, float]:
    raw = metadata.get("bragg_bbox_in_crop_px")
    if isinstance(raw, dict):
        try:
            return {
                "x": float(raw["x"]),
                "y": float(raw["y"]),
                "width": float(raw["width"]),
                "height": float(raw["height"]),
            }
        except (KeyError, TypeError, ValueError):
            pass
    return {"x": 0.0, "y": 0.0, "width": float(image.width), "height": float(image.height)}


def _layout_defaults(width: int, height: int, colorbar: bool) -> dict[str, int]:
    return {
        "outer_margin": LAYOUT_PX["outer_margin"],
        "row_label_band": LAYOUT_PX["row_label_band"],
        "colorbar_band": LAYOUT_PX["colorbar_band"] if colorbar else LAYOUT_PX["colorbar_band_when_hidden"],
        "title_band": LAYOUT_PX["title_band"],
        "column_label_band": LAYOUT_PX["column_label_band"],
        "bottom_margin": LAYOUT_PX["bottom_margin"],
    }


def _font(size: int, *, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def _text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def _draw_centered_text(
    image: Image.Image,
    text: str,
    x: float,
    y: float,
    *,
    font: ImageFont.ImageFont,
    fill: tuple[int, int, int, int] = (45, 67, 99, 255),
    angle: float = 0.0,
) -> None:
    draw = ImageDraw.Draw(image)
    if not angle:
        width, height = _text_size(draw, text, font)
        draw.text((x - width / 2, y - height / 2), text, font=font, fill=fill)
        return

    width, height = _text_size(draw, text, font)
    label = Image.new("RGBA", (max(1, width + 8), max(1, height + 8)), (0, 0, 0, 0))
    label_draw = ImageDraw.Draw(label)
    label_draw.text((4, 4), text, font=font, fill=fill)
    rotated = label.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
    image.alpha_composite(rotated, (int(round(x - rotated.width / 2)), int(round(y - rotated.height / 2))))


def _format_axis_value(value: float | int, *, suffix: str = "") -> str:
    numeric = float(value)
    label = str(int(numeric)) if numeric.is_integer() else f"{numeric:g}"
    return f"{label}{suffix}"


def _draw_matrix_labels(
    canvas: Image.Image,
    *,
    width: int,
    l_values: list[float | int],
    theta_values: list[float | int],
    outer_margin: int,
    row_label_band: int,
    title_band: int,
    column_label_band: int,
    grid_x: int,
    grid_y: int,
    cell_width: float,
    cell_height: float,
    title: str,
    y_axis_title: str,
    title_font_size: int,
    axis_font_size: int,
) -> None:
    title_font = _font(title_font_size)
    axis_font = _font(axis_font_size)

    _draw_centered_text(canvas, title, width / 2, outer_margin * 0.75, font=title_font)
    for col_index, theta in enumerate(theta_values):
        _draw_centered_text(
            canvas,
            _format_axis_value(theta, suffix="°"),
            grid_x + cell_width * (col_index + 0.5),
            outer_margin + title_band + column_label_band * 0.45,
            font=axis_font,
        )
    _draw_centered_text(
        canvas,
        y_axis_title,
        outer_margin * 0.45,
        grid_y + cell_height * len(l_values) / 2.0,
        font=axis_font,
        angle=90,
    )
    for row_index, L in enumerate(l_values):
        _draw_centered_text(
            canvas,
            _format_axis_value(L),
            outer_margin + row_label_band * 0.62,
            grid_y + cell_height * (row_index + 0.5),
            font=axis_font,
        )


def _plotly_color_to_rgba(color: str) -> tuple[int, int, int, int]:
    color = color.strip()
    if color.startswith("#") and len(color) == 7:
        return (int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16), 255)
    match = re.fullmatch(r"rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*[\d.]+)?\)", color)
    if match:
        return (int(match.group(1)), int(match.group(2)), int(match.group(3)), 255)
    raise ValueError(f"Unsupported Plotly color value: {color}")


def _sample_mosaic_color(value: float) -> tuple[int, int, int, int]:
    return _plotly_color_to_rgba(
        sample_colorscale(SPECIAL_CAUSE_MOSAIC_COLORSCALE, [value], colortype="rgb")[0]
    )


def _draw_colorbar(
    image: Image.Image,
    x: int,
    y: int,
    width: int,
    height: int,
) -> None:
    draw = ImageDraw.Draw(image)
    for offset in range(height):
        t = 1.0 - offset / max(1, height - 1)
        draw.line((x, y + offset, x + width - 1, y + offset), fill=_sample_mosaic_color(t))

    label_font = _font(16)
    tick_font = _font(14)
    _draw_centered_text(image, "Mosaic", x + width / 2, y - 32, font=label_font)
    _draw_centered_text(image, "Intensity", x + width / 2, y - 14, font=label_font)
    for tick in (1, 0.8, 0.6, 0.4, 0.2, 0):
        tick_y = y + (1 - tick) * height
        draw.text((x + width + 8, tick_y - 7), str(tick), font=tick_font, fill=(45, 67, 99, 255))


def _paste_clipped(
    canvas: Image.Image,
    sprite: Image.Image,
    x: float,
    y: float,
    cell_rect: tuple[float, float, float, float],
    *,
    clip: bool,
) -> None:
    paste_x = int(round(x))
    paste_y = int(round(y))
    if not clip:
        canvas.alpha_composite(sprite, (paste_x, paste_y))
        return

    cell_x, cell_y, cell_width, cell_height = cell_rect
    left = max(paste_x, int(math.floor(cell_x)), 0)
    top = max(paste_y, int(math.floor(cell_y)), 0)
    right = min(paste_x + sprite.width, int(math.ceil(cell_x + cell_width)), canvas.width)
    bottom = min(paste_y + sprite.height, int(math.ceil(cell_y + cell_height)), canvas.height)
    if right <= left or bottom <= top:
        return
    crop = sprite.crop((left - paste_x, top - paste_y, right - paste_x, bottom - paste_y))
    canvas.alpha_composite(crop, (left, top))


def _file_number_token(value: float | int, *, width: int = 3) -> str:
    numeric_value = float(value)
    if numeric_value.is_integer():
        return str(int(numeric_value)).zfill(width)
    whole, fraction = f"{numeric_value:g}".split(".", 1)
    return f"{whole.zfill(width)}p{fraction}"


def _scale_override_key(metadata: dict[str, Any]) -> str:
    L = int(round(float(metadata["L"])))
    theta = _numeric_key(metadata["theta_deg"])
    return f"L{L:03d}_theta{_file_number_token(theta)}"


def _parse_scale_override(raw: str) -> tuple[tuple[int, float] | str, float]:
    if "=" not in raw:
        raise argparse.ArgumentTypeError("Scale overrides must use KEY=SCALE.")
    key_text, scale_text = raw.split("=", 1)
    try:
        scale = float(scale_text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Invalid scale value: {scale_text}") from exc
    if scale <= 0 or not math.isfinite(scale):
        raise argparse.ArgumentTypeError("Scale must be a positive finite number.")

    compact = key_text.strip().lower().replace(" ", "")
    if "," in compact:
        left, right = compact.split(",", 1)
        try:
            return _cell_key(float(left.lstrip("l=")), float(right.lstrip("theta="))), scale
        except ValueError as exc:
            raise argparse.ArgumentTypeError(f"Invalid L,theta scale key: {key_text}") from exc

    match = re.search(r"l0*(\d+).*theta0*([0-9]+(?:p[0-9]+)?)", compact)
    if match:
        theta = float(match.group(2).replace("p", "."))
        return _cell_key(int(match.group(1)), theta), scale
    return key_text.strip(), scale


def _positive_float(raw: str) -> float:
    value = float(raw)
    if value <= 0 or not math.isfinite(value):
        raise argparse.ArgumentTypeError("Value must be a positive finite number.")
    return value


def _positive_int(raw: str) -> int:
    value = int(raw)
    if value <= 0:
        raise argparse.ArgumentTypeError("Value must be positive.")
    return value


def _default_input_candidates() -> list[Path]:
    home = Path.home()
    script_dir = Path(__file__).resolve().parent
    names = [
        Path(DEFAULT_INPUT_BUNDLE_NAME),
        script_dir / DEFAULT_INPUT_BUNDLE_NAME,
        home / "Downloads" / DEFAULT_INPUT_BUNDLE_NAME,
    ]
    unique: list[Path] = []
    seen: set[str] = set()
    for candidate in names:
        key = str(candidate.resolve()) if candidate.exists() else str(candidate)
        if key not in seen:
            seen.add(key)
            unique.append(candidate)
    return unique


def _resolve_default_input(raw_input: str | None) -> str:
    if raw_input:
        return raw_input
    for candidate in _default_input_candidates():
        if candidate.exists():
            return str(candidate)
    tried = "\n  - ".join(str(p) for p in _default_input_candidates())
    raise SystemExit(
        "No input bundle was provided, and the default bundle could not be found.\n"
        f"Looked for:\n  - {tried}"
    )


def _default_scale_overrides() -> list[tuple[tuple[int, float] | str, float]]:
    values: list[tuple[tuple[int, float] | str, float]] = []
    for L, theta, multiplier in DEFAULT_CELL_SCALE_OVERRIDES:
        values.append((_cell_key(L, theta), multiplier))
    return values


def compose_matrix_image(
    manifest: dict[str, Any],
    cells: list[CellImage],
    *,
    width: int = OUTPUT_WIDTH_PX,
    height: int | None = OUTPUT_HEIGHT_PX,
    bragg_fill_fraction: float | None = BRAGG_FILL_FRACTION,
    cell_scale: float = GLOBAL_CELL_SCALE,
    scale_overrides: dict[tuple[int, float] | str, float] | None = None,
    preserve_relative_l_scale: bool | None = PRESERVE_RELATIVE_L_SCALE,
    title: str = MATRIX_TITLE,
    y_axis_title: str = Y_AXIS_TITLE,
    colorbar: bool = SHOW_COLORBAR,
    clip_cells: bool = CLIP_CELLS_TO_GRID,
    transparent_background: bool = TRANSPARENT_BACKGROUND,
    debug_boxes: bool = DRAW_DEBUG_BOXES,
    layout: dict[str, int] | None = None,
    title_font_size: int = TITLE_FONT_SIZE_PT,
    axis_font_size: int = AXIS_FONT_SIZE_PT,
) -> tuple[Image.Image, dict[str, Any]]:
    """Return a composed 3x3 matrix image and placement metadata."""

    if height is None:
        height = width
    l_values = _ordered_values_from_manifest_or_cells(manifest, cells, "L_values", "L")
    theta_values = _ordered_values_from_manifest_or_cells(manifest, cells, "theta_values", "theta_deg")
    if len(l_values) != 3 or len(theta_values) != 3:
        raise ValueError(f"Expected a 3x3 bundle, found L={l_values} and theta={theta_values}.")

    cells_by_key = {_cell_key(cell.metadata["L"], cell.metadata["theta_deg"]): cell for cell in cells}
    defaults = manifest if manifest else (cells[0].metadata.get("matrix_defaults") or {})
    if bragg_fill_fraction is None:
        bragg_fill_fraction = float(defaults.get("bragg_cell_fill_fraction", FALLBACK_BRAGG_FILL_FRACTION))
    if preserve_relative_l_scale is None:
        preserve_relative_l_scale = bool(defaults.get("preserve_relative_l_scale", False))
    scale_overrides = scale_overrides or {}
    layout_values = _layout_defaults(width, height, colorbar)
    if layout:
        layout_values.update(layout)

    background = (0, 0, 0, 0) if transparent_background else (255, 255, 255, 255)
    canvas = Image.new("RGBA", (width, height), background)
    draw = ImageDraw.Draw(canvas)

    outer_margin = layout_values["outer_margin"]
    row_label_band = layout_values["row_label_band"]
    colorbar_band = layout_values["colorbar_band"]
    title_band = layout_values["title_band"]
    column_label_band = layout_values["column_label_band"]
    bottom_margin = layout_values["bottom_margin"]
    grid_x = outer_margin + row_label_band
    grid_y = outer_margin + title_band + column_label_band
    grid_width = width - grid_x - colorbar_band - outer_margin
    grid_height = height - grid_y - bottom_margin
    if grid_width <= 0 or grid_height <= 0:
        raise ValueError("Layout margins leave no room for the matrix grid.")
    cell_width = grid_width / len(theta_values)
    cell_height = grid_height / len(l_values)

    placements = []
    for row_index, L in enumerate(l_values):
        for col_index, theta in enumerate(theta_values):
            key = _cell_key(L, theta)
            cell = cells_by_key.get(key)
            if cell is None:
                raise ValueError(f"Missing matrix cell L={L}, theta={theta}.")
            image = cell.image.convert("RGBA")
            bragg = _bbox(cell.metadata, image)
            relative_extent = float(cell.metadata.get("relative_extent", 1.0) or 1.0)
            relative_scale = relative_extent if preserve_relative_l_scale else 1.0
            bragg_extent = max(1.0, float(bragg["width"]), float(bragg["height"]))
            override_key = _scale_override_key(cell.metadata)
            override = scale_overrides.get(key, scale_overrides.get(override_key, 1.0))
            scale = bragg_fill_fraction * min(cell_width, cell_height) * relative_scale / bragg_extent
            scale *= cell_scale * override
            draw_width = max(1, int(round(image.width * scale)))
            draw_height = max(1, int(round(image.height * scale)))
            resized = image.resize((draw_width, draw_height), Image.Resampling.LANCZOS)

            cell_x = grid_x + col_index * cell_width
            cell_y = grid_y + row_index * cell_height
            bragg_center_x = (float(bragg["x"]) + float(bragg["width"]) / 2.0) * scale
            bragg_center_y = (float(bragg["y"]) + float(bragg["height"]) / 2.0) * scale
            cell_center_x = cell_x + cell_width / 2.0
            cell_center_y = cell_y + cell_height / 2.0
            paste_x = cell_center_x - bragg_center_x
            paste_y = cell_center_y - bragg_center_y
            _paste_clipped(
                canvas,
                resized,
                paste_x,
                paste_y,
                (cell_x, cell_y, cell_width, cell_height),
                clip=clip_cells,
            )

            placement = {
                "L": int(L),
                "theta_deg": float(theta),
                "image_path": cell.metadata.get("image_path"),
                "cell_rect_px": {"x": cell_x, "y": cell_y, "width": cell_width, "height": cell_height},
                "paste_rect_px": {"x": paste_x, "y": paste_y, "width": draw_width, "height": draw_height},
                "scale": scale,
                "scale_override": override,
                "bragg_fill_fraction": max(float(bragg["width"]), float(bragg["height"])) * scale / min(cell_width, cell_height),
            }
            placements.append(placement)

            if debug_boxes:
                draw.rectangle((cell_x, cell_y, cell_x + cell_width, cell_y + cell_height), outline=(35, 35, 35, 128), width=1)
                draw.rectangle((paste_x, paste_y, paste_x + draw_width, paste_y + draw_height), outline=(214, 60, 130, 180), width=2)
                bragg_x = paste_x + float(bragg["x"]) * scale
                bragg_y = paste_y + float(bragg["y"]) * scale
                draw.rectangle(
                    (
                        bragg_x,
                        bragg_y,
                        bragg_x + float(bragg["width"]) * scale,
                        bragg_y + float(bragg["height"]) * scale,
                    ),
                    outline=(42, 126, 255, 220),
                    width=2,
                )

    if colorbar:
        colorbar_x = int(round(width - outer_margin - colorbar_band * 0.42))
        colorbar_y = int(round(grid_y + grid_height * 0.16))
        colorbar_width = 30
        colorbar_height = int(round(grid_height * 0.68))
        _draw_colorbar(canvas, colorbar_x, colorbar_y, colorbar_width, colorbar_height)

    _draw_matrix_labels(
        canvas,
        width=width,
        l_values=l_values,
        theta_values=theta_values,
        outer_margin=outer_margin,
        row_label_band=row_label_band,
        title_band=title_band,
        column_label_band=column_label_band,
        grid_x=grid_x,
        grid_y=grid_y,
        cell_width=cell_width,
        cell_height=cell_height,
        title=title,
        y_axis_title=y_axis_title,
        title_font_size=title_font_size,
        axis_font_size=axis_font_size,
    )

    metadata = {
        "kind": "special-cause-matrix-composite",
        "version": 1,
        "output_size_px": {"width": width, "height": height},
        "L_values": [int(value) for value in l_values],
        "theta_values": [float(value) for value in theta_values],
        "bragg_fill_fraction": bragg_fill_fraction,
        "cell_scale": cell_scale,
        "preserve_relative_l_scale": preserve_relative_l_scale,
        "title": title,
        "y_axis_title": y_axis_title,
        "layout": layout_values,
        "title_font_size": title_font_size,
        "axis_font_size": axis_font_size,
        "colorbar": colorbar,
        "clip_cells": clip_cells,
        "placements": placements,
    }
    return canvas, metadata


def save_matrix_image(image: Image.Image, output_path: str | Path, metadata: dict[str, Any]) -> None:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    pnginfo = PngImagePlugin.PngInfo()
    pnginfo.add_text(MATRIX_METADATA_KEY, json.dumps(metadata, indent=2, sort_keys=True))
    image.save(output, pnginfo=pnginfo)


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a 3x3 special-cause matrix PNG from exported cropped cell images.",
    )
    parser.add_argument("input", nargs="?", default=None, help="Exported special_cause_reciprocal_matrix_cells.zip or extracted directory. Defaults to special_cause_reciprocal_matrix_cells.zip in the current folder, script folder, or Downloads.")
    parser.add_argument("--output", "-o", default=DEFAULT_OUTPUT_PATH, help="Output PNG path.")
    parser.add_argument("--width", type=_positive_int, default=OUTPUT_WIDTH_PX, help="Output width in pixels.")
    parser.add_argument("--height", type=_positive_int, default=OUTPUT_HEIGHT_PX, help="Output height in pixels. Defaults to width.")
    parser.add_argument("--title", default=MATRIX_TITLE, help="Top title text.")
    parser.add_argument("--y-axis-title", default=Y_AXIS_TITLE, help="Y-axis title text.")
    parser.add_argument("--bragg-fill", type=_positive_float, default=BRAGG_FILL_FRACTION, help="Target Bragg footprint fraction in each cell.")
    parser.add_argument("--cell-scale", type=_positive_float, default=GLOBAL_CELL_SCALE, help="Global multiplier for all cropped cell images.")
    parser.add_argument(
        "--scale",
        dest="scale_overrides",
        action="append",
        type=_parse_scale_override,
        default=None,
        help="Per-cell multiplier. Use L003_theta005=1.10 or 3,5=1.10. May be repeated. If omitted, defaults to L=3 -> 1/3, L=6 -> 2/3, L=9 -> 1.0.",
    )
    parser.add_argument("--relative-l-scale", action="store_true", help="Preserve relative L size across rows.")
    parser.add_argument("--local-scale", action="store_true", help="Scale each row locally so its Bragg sphere fills the same cell fraction.")
    parser.add_argument("--colorbar", dest="colorbar", action="store_true", default=SHOW_COLORBAR, help="Draw the shared mosaic intensity colorbar.")
    parser.add_argument("--no-colorbar", dest="colorbar", action="store_false", help="Do not draw the shared mosaic intensity colorbar.")
    parser.add_argument("--clip-cells", dest="clip_cells", action="store_true", default=CLIP_CELLS_TO_GRID, help="Clip cell images to their grid cells.")
    parser.add_argument("--no-clip", dest="clip_cells", action="store_false", help="Do not clip cell images to their grid cells.")
    parser.add_argument("--transparent-background", dest="transparent_background", action="store_true", default=TRANSPARENT_BACKGROUND, help="Use a transparent background instead of white.")
    parser.add_argument("--opaque-background", dest="transparent_background", action="store_false", help="Use a white background instead of transparent.")
    parser.add_argument("--debug-boxes", dest="debug_boxes", action="store_true", default=DRAW_DEBUG_BOXES, help="Draw cell, image, and Bragg bounding boxes.")
    parser.add_argument("--no-debug-boxes", dest="debug_boxes", action="store_false", help="Do not draw debug bounding boxes.")
    parser.add_argument("--metadata-output", default=None, help="Optional JSON sidecar path for composite metadata.")
    parser.add_argument("--title-font-size", type=_positive_int, default=TITLE_FONT_SIZE_PT, help="Title font size in points.")
    parser.add_argument("--axis-font-size", type=_positive_int, default=AXIS_FONT_SIZE_PT, help="X and Y axis label font size in points.")
    parser.add_argument("--outer-margin", type=int, default=None)
    parser.add_argument("--row-label-band", type=int, default=None)
    parser.add_argument("--colorbar-band", type=int, default=None)
    parser.add_argument("--title-band", type=int, default=None)
    parser.add_argument("--column-label-band", type=int, default=None)
    parser.add_argument("--bottom-margin", type=int, default=None)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    input_path = _resolve_default_input(args.input)
    manifest, cells = load_cell_bundle(input_path)
    raw_scale_overrides = args.scale_overrides if args.scale_overrides is not None else _default_scale_overrides()
    overrides = dict(raw_scale_overrides)
    preserve_relative_l_scale = PRESERVE_RELATIVE_L_SCALE
    if args.relative_l_scale and args.local_scale:
        raise SystemExit("Use only one of --relative-l-scale or --local-scale.")
    if args.relative_l_scale:
        preserve_relative_l_scale = True
    elif args.local_scale:
        preserve_relative_l_scale = False

    layout = {
        key: value
        for key, value in {
            "outer_margin": args.outer_margin,
            "row_label_band": args.row_label_band,
            "colorbar_band": args.colorbar_band,
            "title_band": args.title_band,
            "column_label_band": args.column_label_band,
            "bottom_margin": args.bottom_margin,
        }.items()
        if value is not None
    }
    image, metadata = compose_matrix_image(
        manifest,
        cells,
        width=args.width,
        height=args.height,
        bragg_fill_fraction=args.bragg_fill,
        cell_scale=args.cell_scale,
        scale_overrides=overrides,
        preserve_relative_l_scale=preserve_relative_l_scale,
        title=args.title,
        y_axis_title=args.y_axis_title,
        colorbar=args.colorbar,
        clip_cells=args.clip_cells,
        transparent_background=args.transparent_background,
        debug_boxes=args.debug_boxes,
        layout=layout,
        title_font_size=args.title_font_size,
        axis_font_size=args.axis_font_size,
    )
    output = Path(args.output)
    save_matrix_image(image, output, metadata)
    if args.metadata_output:
        metadata_path = Path(args.metadata_output)
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Saved {output}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
