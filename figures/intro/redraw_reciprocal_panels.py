from pathlib import Path
import math

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parent
SIZE = 1800
UPSCALE = 2
CANVAS = SIZE * UPSCALE


def lerp(a, b, t):
    return tuple(int(round(x + (y - x) * t)) for x, y in zip(a, b))


def alpha(color, value):
    return (*color, value)


def add_layer(base, layer):
    base.alpha_composite(layer)


def draw_gradient_disc(layer, center, radius, outer_rgb, inner_rgb, outer_alpha, inner_alpha, steps=260):
    draw = ImageDraw.Draw(layer, "RGBA")
    for step in range(steps, 0, -1):
        t = step / steps
        rr = radius * t
        rgb = lerp(inner_rgb, outer_rgb, t ** 0.9)
        aa = int(round(inner_alpha + (outer_alpha - inner_alpha) * (t ** 1.15)))
        bbox = (
            center[0] - rr,
            center[1] - rr,
            center[0] + rr,
            center[1] + rr,
        )
        draw.ellipse(bbox, fill=alpha(rgb, aa))


def draw_blur_highlight(base, bbox, fill, blur_radius):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    draw.ellipse(bbox, fill=fill)
    add_layer(base, layer.filter(ImageFilter.GaussianBlur(blur_radius)))


def draw_arrow(base, start, end, color, width, head_length, head_width):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    draw.line([start, end], fill=color, width=width)
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    norm = math.hypot(dx, dy)
    ux = dx / norm
    uy = dy / norm
    px = -uy
    py = ux
    head_base = (end[0] - ux * head_length, end[1] - uy * head_length)
    draw.polygon(
        [
            end,
            (head_base[0] + px * head_width, head_base[1] + py * head_width),
            (head_base[0] - px * head_width, head_base[1] - py * head_width),
        ],
        fill=color,
    )
    add_layer(base, layer)


def rotated_shape_layer(size, center, angle_deg, painter):
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    painter(ImageDraw.Draw(layer, "RGBA"))
    return layer.rotate(angle_deg, resample=Image.Resampling.BICUBIC, center=center)


def ellipse_bbox(center, rx, ry):
    return (center[0] - rx, center[1] - ry, center[0] + rx, center[1] + ry)


def draw_rotated_ellipse(base, center, rx, ry, angle, outline, width, fill=None):
    def painter(draw):
        draw.ellipse(ellipse_bbox(center, rx, ry), outline=outline, width=width, fill=fill)

    add_layer(base, rotated_shape_layer(base.size, center, angle, painter))


def draw_rotated_arc(base, center, rx, ry, angle, start, end, fill, width):
    def painter(draw):
        draw.arc(ellipse_bbox(center, rx, ry), start=start, end=end, fill=fill, width=width)

    add_layer(base, rotated_shape_layer(base.size, center, angle, painter))


def draw_point(base, center, radius, fill, outline=None, outline_width=0, halo=None, halo_radius=None):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    if halo and halo_radius:
        draw.ellipse(
            (
                center[0] - halo_radius,
                center[1] - halo_radius,
                center[0] + halo_radius,
                center[1] + halo_radius,
            ),
            fill=halo,
        )
    draw.ellipse(
        (
            center[0] - radius,
            center[1] - radius,
            center[0] + radius,
            center[1] + radius,
        ),
        fill=fill,
        outline=outline,
        width=outline_width,
    )
    add_layer(base, layer)


def sphere_layer(center, radius):
    layer = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    draw_gradient_disc(
        layer,
        center,
        radius,
        outer_rgb=(26, 84, 148),
        inner_rgb=(245, 250, 255),
        outer_alpha=235,
        inner_alpha=252,
        steps=320,
    )
    highlight = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    draw_blur_highlight(
        highlight,
        (
            center[0] - radius * 1.08,
            center[1] - radius * 0.18,
            center[0] + radius * 0.05,
            center[1] + radius * 0.78,
        ),
        (255, 255, 255, 78),
        blur_radius=95,
    )
    mask = Image.new("L", (CANVAS, CANVAS), 0)
    ImageDraw.Draw(mask).ellipse(
        (
            center[0] - radius,
            center[1] - radius,
            center[0] + radius,
            center[1] + radius,
        ),
        fill=255,
    )
    masked_highlight = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    masked_highlight.paste(highlight, mask=mask)
    add_layer(layer, masked_highlight)
    rim = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    rim_draw = ImageDraw.Draw(rim, "RGBA")
    rim_draw.ellipse(
        (
            center[0] - radius,
            center[1] - radius,
            center[0] + radius,
            center[1] + radius,
        ),
        outline=(48, 97, 145, 86),
        width=12,
    )
    add_layer(layer, rim)
    return layer


def save_image(image, name):
    downsampled = image.resize((SIZE, SIZE), resample=Image.Resampling.LANCZOS)
    downsampled.save(ROOT / name)


def redraw_3d_powder():
    base = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    ewald_center = (1260, 1220)
    ewald_radius = 760
    add_layer(base, sphere_layer(ewald_center, ewald_radius))

    bragg_back = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    draw_gradient_disc(
        bragg_back,
        center=(2220, 1660),
        radius=840,
        outer_rgb=(235, 92, 46),
        inner_rgb=(255, 176, 120),
        outer_alpha=232,
        inner_alpha=202,
        steps=320,
    )
    draw_blur_highlight(
        bragg_back,
        (1520, 1080, 2550, 2220),
        (255, 232, 190, 32),
        blur_radius=120,
    )
    add_layer(base, bragg_back)

    shell_glow = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    shell_draw = ImageDraw.Draw(shell_glow, "RGBA")
    shell_draw.ellipse((1510, 980, 2890, 2340), outline=(255, 114, 60, 220), width=28)
    shell_draw.ellipse((1680, 1140, 2710, 2160), fill=(214, 92, 84, 70))
    add_layer(base, shell_glow.filter(ImageFilter.GaussianBlur(1)))

    draw_rotated_ellipse(
        base,
        center=(1710, 1440),
        rx=760,
        ry=205,
        angle=-58,
        outline=(18, 28, 38, 220),
        width=22,
    )
    draw_rotated_arc(
        base,
        center=(1710, 1440),
        rx=760,
        ry=205,
        angle=-58,
        start=20,
        end=182,
        fill=(116, 126, 138, 188),
        width=18,
    )
    draw_rotated_ellipse(
        base,
        center=(1820, 1450),
        rx=520,
        ry=168,
        angle=-58,
        outline=(132, 130, 160, 185),
        width=16,
    )
    draw_rotated_arc(
        base,
        center=(1820, 1450),
        rx=520,
        ry=168,
        angle=-58,
        start=212,
        end=334,
        fill=(196, 193, 214, 190),
        width=14,
    )

    draw_arrow(
        base,
        start=(1240, 1390),
        end=(1820, 1820),
        color=(55, 95, 130, 180),
        width=12,
        head_length=98,
        head_width=42,
    )
    axis_layer = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    axis_draw = ImageDraw.Draw(axis_layer, "RGBA")
    axis_draw.line([(1580, 1200), (2010, 1680)], fill=(125, 118, 132, 122), width=8)
    axis_draw.line([(1420, 1520), (1960, 1420)], fill=(125, 118, 132, 110), width=8)
    add_layer(base, axis_layer)

    for pt in [(1280, 1610), (1530, 1000), (1850, 1710), (2020, 1260), (1940, 930)]:
        draw_point(
            base,
            center=pt,
            radius=42,
            fill=(24, 26, 32, 210),
            outline=(245, 245, 245, 130),
            outline_width=7,
            halo=(0, 0, 0, 28),
            halo_radius=64,
        )

    save_image(base, "reciprocal_3d_powder.png")


def redraw_2d_powder():
    base = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    ewald_center = (1240, 1250)
    ewald_radius = 760
    add_layer(base, sphere_layer(ewald_center, ewald_radius))

    back_rings = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    ring_draw = ImageDraw.Draw(back_rings, "RGBA")
    ring_draw.ellipse((990, 720, 3160, 1820), outline=(10, 214, 190, 204), width=16)
    ring_draw.ellipse((1090, 1280, 3100, 2360), outline=(255, 96, 72, 204), width=16)
    add_layer(base, back_rings)

    draw_rotated_arc(
        base,
        center=(1840, 1270),
        rx=1040,
        ry=520,
        angle=4,
        start=205,
        end=352,
        fill=(14, 214, 190, 235),
        width=20,
    )
    draw_rotated_arc(
        base,
        center=(1830, 1820),
        rx=1000,
        ry=505,
        angle=2,
        start=160,
        end=312,
        fill=(255, 98, 72, 235),
        width=20,
    )

    draw_rotated_arc(
        base,
        center=(1610, 1410),
        rx=635,
        ry=335,
        angle=-24,
        start=180,
        end=348,
        fill=(74, 112, 156, 168),
        width=12,
    )

    draw_arrow(
        base,
        start=(1230, 1250),
        end=(1810, 1810),
        color=(55, 95, 130, 180),
        width=12,
        head_length=98,
        head_width=42,
    )

    axis_layer = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    axis_draw = ImageDraw.Draw(axis_layer, "RGBA")
    axis_draw.line([(1830, 930), (1830, 1530)], fill=(110, 120, 132, 105), width=8)
    add_layer(base, axis_layer)

    for pt in [(970, 1520), (920, 2080), (1830, 1140), (1830, 1470), (2040, 1000)]:
        draw_point(
            base,
            center=pt,
            radius=42,
            fill=(24, 26, 32, 210),
            outline=(245, 245, 245, 120),
            outline_width=7,
            halo=(0, 0, 0, 26),
            halo_radius=64,
        )

    draw_point(
        base,
        center=(1940, 1330),
        radius=52,
        fill=(108, 126, 146, 220),
        outline=(255, 255, 255, 96),
        outline_width=7,
        halo=(255, 184, 112, 130),
        halo_radius=112,
    )
    draw_point(
        base,
        center=(1940, 1330),
        radius=26,
        fill=(181, 146, 120, 230),
    )

    save_image(base, "reciprocal_2d_powder.png")


def main():
    redraw_3d_powder()
    redraw_2d_powder()


if __name__ == "__main__":
    main()
