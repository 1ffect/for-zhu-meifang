from __future__ import annotations

from math import cos, radians, sin
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parent
QR_PATH = ROOT / "for-zhu-meifang-qr.png"
OUT_PATH = ROOT / "wechat-share-card.png"

WIDTH = 1200
HEIGHT = 1600

BG_TOP = (49, 23, 36)
BG_BOTTOM = (245, 236, 226)
ROSE = (210, 132, 154, 255)
BLUSH = (240, 202, 212, 245)
GOLD = (240, 201, 120, 255)
GOLD_SOFT = (228, 184, 118, 210)
SAGE = (117, 146, 110, 220)
INK = (77, 52, 47, 255)
INK_SOFT = (123, 91, 82, 255)
IVORY = (255, 250, 244, 255)
LINE = (217, 182, 142, 170)
SHADOW = (37, 18, 27, 70)

TITLE = "母亲节快乐"
OVERLINE = "送给朱美芳"
SUBTITLE = "扫一扫，慢慢打开这份小礼物"
SIGNATURE = "彭诗琪 敬上"
URL = "1ffect.github.io/for-zhu-meifang"

FONT_SERIF = "/System/Library/Fonts/Hiragino Sans GB.ttc"
FONT_SANS = "/System/Library/Fonts/STHeiti Light.ttc"


def load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size)


def lerp(a: int, b: int, t: float) -> int:
    return round(a + (b - a) * t)


def make_vertical_gradient(size: tuple[int, int], top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    width, height = size
    image = Image.new("RGBA", size)
    pixels = image.load()
    for y in range(height):
        t = y / max(height - 1, 1)
        color = tuple(lerp(top[i], bottom[i], t) for i in range(3)) + (255,)
        for x in range(width):
            pixels[x, y] = color
    return image


def add_glow(base: Image.Image, center: tuple[int, int], radius: int, color: tuple[int, int, int, int], blur: int) -> None:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    cx, cy = center
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=color)
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(layer)


def draw_rotated_ellipse(
    base: Image.Image,
    center: tuple[float, float],
    size: tuple[int, int],
    angle: float,
    fill: tuple[int, int, int, int],
) -> None:
    width, height = max(size[0], 1), max(size[1], 1)
    patch = Image.new("RGBA", (width * 2, height * 2), (0, 0, 0, 0))
    draw = ImageDraw.Draw(patch)
    draw.ellipse((width * 0.35, height * 0.1, width * 1.65, height * 1.9), fill=fill)
    rotated = patch.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    left = int(center[0] - rotated.width / 2)
    top = int(center[1] - rotated.height / 2)
    base.alpha_composite(rotated, (left, top))


def draw_blossom(
    base: Image.Image,
    center: tuple[int, int],
    radius: int,
    petal_color: tuple[int, int, int, int],
    core_color: tuple[int, int, int, int],
    petals: int = 6,
    rotation: float = 0.0,
) -> None:
    cx, cy = center
    for idx in range(petals):
        angle = rotation + idx * (360 / petals)
        dx = cos(radians(angle)) * radius * 0.62
        dy = sin(radians(angle)) * radius * 0.62
        draw_rotated_ellipse(
            base,
            (cx + dx, cy + dy),
            (int(radius * 1.15), int(radius * 1.75)),
            angle,
            petal_color,
        )

    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.ellipse((cx - radius * 0.34, cy - radius * 0.34, cx + radius * 0.34, cy + radius * 0.34), fill=core_color)
    base.alpha_composite(layer)


def draw_leaf(base: Image.Image, center: tuple[int, int], size: tuple[int, int], angle: float, color: tuple[int, int, int, int]) -> None:
    draw_rotated_ellipse(base, center, size, angle, color)


def draw_stem(draw: ImageDraw.ImageDraw, points: list[tuple[int, int]], color: tuple[int, int, int, int], width: int) -> None:
    draw.line(points, fill=color, width=width, joint="curve")


def draw_flower_cluster(base: Image.Image, origin: tuple[int, int], mirrored: bool = False) -> None:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    ox, oy = origin
    direction = -1 if mirrored else 1

    stem_a = [(ox, oy), (ox + 40 * direction, oy - 120), (ox + 25 * direction, oy - 230)]
    stem_b = [(ox + 50 * direction, oy + 10), (ox + 110 * direction, oy - 120), (ox + 85 * direction, oy - 260)]
    stem_c = [(ox - 20 * direction, oy + 20), (ox - 80 * direction, oy - 110), (ox - 125 * direction, oy - 220)]

    draw_stem(draw, stem_a, SAGE, 10)
    draw_stem(draw, stem_b, SAGE, 9)
    draw_stem(draw, stem_c, SAGE, 8)

    base.alpha_composite(layer)
    draw_leaf(base, (ox + 10 * direction, oy - 95), (70, 130), 40 * direction, (142, 176, 134, 180))
    draw_leaf(base, (ox + 70 * direction, oy - 175), (60, 115), -18 * direction, (126, 160, 119, 165))
    draw_leaf(base, (ox - 70 * direction, oy - 120), (62, 118), -42 * direction, (131, 166, 124, 165))

    draw_blossom(base, (ox + 28 * direction, oy - 262), 44, ROSE, GOLD_SOFT, petals=7, rotation=12)
    draw_blossom(base, (ox + 92 * direction, oy - 290), 32, BLUSH, GOLD_SOFT, petals=6, rotation=28)
    draw_blossom(base, (ox - 135 * direction, oy - 248), 34, (245, 219, 169, 238), GOLD_SOFT, petals=6, rotation=10)


def text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    left, _, right, _ = draw.textbbox((0, 0), text, font=font)
    return right - left


def centered_text(draw: ImageDraw.ImageDraw, y: int, text: str, font: ImageFont.FreeTypeFont, fill: tuple[int, int, int, int]) -> None:
    bbox = draw.textbbox((0, 0), text, font=font)
    x = (WIDTH - (bbox[2] - bbox[0])) / 2
    draw.text((x, y), text, font=font, fill=fill)


def main() -> None:
    if not QR_PATH.exists():
        raise FileNotFoundError(f"QR code not found: {QR_PATH}")

    poster = make_vertical_gradient((WIDTH, HEIGHT), BG_TOP, BG_BOTTOM)
    add_glow(poster, (220, 260), 260, (224, 170, 145, 80), blur=60)
    add_glow(poster, (960, 220), 250, (208, 129, 154, 72), blur=65)
    add_glow(poster, (920, 1360), 290, (246, 210, 137, 80), blur=88)
    add_glow(poster, (220, 1320), 240, (236, 207, 196, 84), blur=70)

    draw_flower_cluster(poster, (190, 1485), mirrored=False)
    draw_flower_cluster(poster, (1010, 480), mirrored=True)

    shadow = Image.new("RGBA", poster.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((110, 96, 1090, 1508), radius=46, fill=SHADOW)
    shadow = shadow.filter(ImageFilter.GaussianBlur(24))
    poster.alpha_composite(shadow)

    panel = Image.new("RGBA", poster.size, (0, 0, 0, 0))
    panel_draw = ImageDraw.Draw(panel)
    panel_draw.rounded_rectangle((95, 82, 1105, 1492), radius=42, fill=(255, 249, 243, 226), outline=(255, 255, 255, 84), width=2)
    panel_draw.rounded_rectangle((130, 118, 1070, 1458), radius=36, outline=(229, 195, 158, 80), width=2)
    poster.alpha_composite(panel)

    overlay = Image.new("RGBA", poster.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.arc((150, 142, 330, 322), start=220, end=342, fill=LINE, width=4)
    overlay_draw.arc((870, 1270, 1050, 1450), start=40, end=162, fill=LINE, width=4)
    overlay_draw.line((340, 238, 860, 238), fill=(221, 189, 153, 82), width=2)
    poster.alpha_composite(overlay)

    qr = Image.open(QR_PATH).convert("RGBA").resize((390, 390), Image.Resampling.NEAREST)
    qr_frame = Image.new("RGBA", poster.size, (0, 0, 0, 0))
    qr_draw = ImageDraw.Draw(qr_frame)
    qr_draw.rounded_rectangle((405, 850, 795, 1240), radius=36, fill=IVORY, outline=(213, 173, 133, 255), width=4)
    qr_shadow = Image.new("RGBA", poster.size, (0, 0, 0, 0))
    qr_shadow_draw = ImageDraw.Draw(qr_shadow)
    qr_shadow_draw.rounded_rectangle((394, 840, 806, 1250), radius=40, fill=(82, 43, 51, 28))
    qr_shadow = qr_shadow.filter(ImageFilter.GaussianBlur(18))
    poster.alpha_composite(qr_shadow)
    poster.alpha_composite(qr_frame)
    poster.alpha_composite(qr, (405, 850))

    draw = ImageDraw.Draw(poster)
    font_overline = load_font(FONT_SANS, 46)
    font_title = load_font(FONT_SERIF, 120)
    font_subtitle = load_font(FONT_SANS, 48)
    font_hint = load_font(FONT_SANS, 34)
    font_signature = load_font(FONT_SERIF, 42)
    font_url = load_font(FONT_SANS, 28)

    centered_text(draw, 220, OVERLINE, font_overline, INK_SOFT)
    centered_text(draw, 320, TITLE, font_title, INK)
    centered_text(draw, 500, SUBTITLE, font_subtitle, INK_SOFT)

    hint = "扫一扫，慢慢看"
    centered_text(draw, 1278, hint, font_hint, INK)
    centered_text(draw, 1342, URL, font_url, (116, 88, 80, 235))
    centered_text(draw, 1414, SIGNATURE, font_signature, INK_SOFT)

    line_width = text_width(draw, OVERLINE, font_overline)
    draw.line(
        (
            (WIDTH - line_width) / 2 - 80,
            244,
            (WIDTH - line_width) / 2 - 26,
            244,
        ),
        fill=LINE,
        width=3,
    )
    draw.line(
        (
            (WIDTH + line_width) / 2 + 26,
            244,
            (WIDTH + line_width) / 2 + 80,
            244,
        ),
        fill=LINE,
        width=3,
    )

    poster = poster.convert("RGB")
    poster.save(OUT_PATH, quality=95)
    print(OUT_PATH)


if __name__ == "__main__":
    main()
