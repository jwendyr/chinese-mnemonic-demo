#!/usr/bin/env python3
"""Build 3-scene audio-synced exemplars with 1:1 unified brush-calligraphy (Kaiti) strokes & AI illustrations."""

import array
import hashlib
import json
import math
import re
import subprocess
import wave
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageFilter

WORKDIR = Path("/Volumes/App/Workspace/chinese-mnemonic-demo")
ILLUS_DIR = WORKDIR / "illustrations"
TEMPLATES_DIR = WORKDIR / "templates"
STROKE_DATA_DIR = WORKDIR / "stroke_data"
EXEMPLARS_DIR = WORKDIR / "exemplars"
TMP_DIR = WORKDIR / "build_tmp"
AUDIO_CACHE_DIR = TMP_DIR / "exemplar_audio_v8"
ANIM_FRAMES_DIR = TMP_DIR / "stroke_anim_v8"
INTRO_ID_DIR = TMP_DIR / "char_intro_frames"
INTRO_EN_DIR = TMP_DIR / "char_intro_frames_en"
CARDS_ID_DIR = WORKDIR / "cards"
CARDS_EN_DIR = WORKDIR / "cards_en"
VIDEOS_ID_DIR = WORKDIR / "char_videos"
VIDEOS_EN_DIR = WORKDIR / "char_videos_en"

for d in (
    TEMPLATES_DIR,
    STROKE_DATA_DIR,
    EXEMPLARS_DIR,
    AUDIO_CACHE_DIR,
    ANIM_FRAMES_DIR,
    INTRO_ID_DIR,
    INTRO_EN_DIR,
    CARDS_ID_DIR,
    CARDS_EN_DIR,
    VIDEOS_ID_DIR,
    VIDEOS_EN_DIR,
):
    d.mkdir(parents=True, exist_ok=True)

EDGE_TTS = "/Volumes/App/Caches-And-Env/bin/edge-tts"
AFCONVERT = "/usr/bin/afconvert"
RENDER_MP4 = TMP_DIR / "render_mp4"
CONCAT_MP4 = TMP_DIR / "concat_mp4"

VOICE_ZH = "zh-CN-XiaoxiaoNeural"
VOICE_ID = "id-ID-GadisNeural"
VOICE_EN = "en-US-JennyNeural"

W, H = 1080, 1920
BG_COLOR = (249, 245, 236)        # #F9F5EC matches AI illustration background
CARD_BG = (255, 253, 249)         # #FFFDF9
CARD_BORDER = (226, 219, 207)     # #E2DBCF
GRID_LINE = (218, 210, 196)       # #DAD2C4 Mi-Zi-Ge guide lines
GHOST_STROKE = (229, 223, 213)    # #E5DFD5
DIVIDER = (237, 230, 218)         # #EDE6DA
CHARCOAL = (43, 45, 66)           # #2B2D42
NAVY = (31, 46, 77)               # #1F2E4D
TERRACOTTA = (217, 83, 79)        # #D9534F
SOFT_TERRACOTTA = (252, 237, 235) # #FCEDEB
FOREST = (46, 111, 94)            # #2E6F5E
SOFT_FOREST = (234, 244, 240)     # #EAF4F0
SOFT_NAVY = (235, 240, 248)       # #EBF0F8
GOLD_ACCENT = (227, 168, 59)      # #E3A83B active brush ring
MUTED = (108, 105, 100)           # #6C6964

FONT_CJK = "/System/Library/AssetsV2/com_apple_MobileAsset_Font8/88d6cc32a907955efa1d014207889413890573be.asset/AssetData/Kaiti.ttc"  # index 3 = Kaiti SC Bold
FONT_LATIN = "/System/Library/Fonts/Avenir Next.ttc"   # 0=Bold, 2=DemiBold, 5=Medium, 7=Regular

SAMPLES_PER_SEC = 48000
FPS = 30
CROSSFADE_SEC = 1.35

# Canonical brush-calligraphy template layout on 1080x1920 canvas
TMPL_X0, TMPL_Y0, TMPL_BOX, TMPL_PAD = 190, 610, 700, 56
TMPL_SCALE = (TMPL_BOX - 2 * TMPL_PAD) / 1024.0
TMPL_OX = TMPL_X0 + TMPL_PAD
TMPL_OY = TMPL_Y0 + TMPL_PAD


def load_latin(size: int, weight: str = "regular") -> ImageFont.FreeTypeFont:
    idx_map = {"bold": 0, "demi": 2, "medium": 5, "regular": 7}
    return ImageFont.truetype(FONT_LATIN, size=size, index=idx_map[weight])


def load_cjk(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_CJK, size=size, index=3)


def is_cjk(ch: str) -> bool:
    cp = ord(ch)
    return (0x2E80 <= cp <= 0x2FDF) or (0x3400 <= cp <= 0x4DBF) or (0x4E00 <= cp <= 0x9FFF)


def split_runs(text: str) -> list[tuple[str, bool]]:
    if not text:
        return []
    runs: list[tuple[str, bool]] = []
    cur = text[0]
    cur_cjk = is_cjk(text[0])
    for ch in text[1:]:
        flag = is_cjk(ch)
        if flag == cur_cjk:
            cur += ch
        else:
            runs.append((cur, cur_cjk))
            cur = ch
            cur_cjk = flag
    runs.append((cur, cur_cjk))
    return runs


def measure_segments(
    draw: ImageDraw.ImageDraw,
    segments: list[tuple[str, ImageFont.FreeTypeFont, ImageFont.FreeTypeFont, tuple[int, int, int]]],
    gap: int = 2,
) -> tuple[int, int, list]:
    total_w = 0
    max_h = 0
    items = []
    for txt, lf, cf, col in segments:
        for sub, flag in split_runs(txt):
            f = cf if flag else lf
            bb = draw.textbbox((0, 0), sub, font=f)
            w_sub = bb[2] - bb[0]
            h_sub = bb[3] - bb[1]
            items.append((sub, f, bb, w_sub, h_sub, col))
            total_w += w_sub
            max_h = max(max_h, h_sub)
    if len(items) > 1:
        total_w += gap * (len(items) - 1)
    return total_w, max_h, items


def draw_segments_at(
    draw: ImageDraw.ImageDraw,
    cx_center: int,
    cy: int,
    segments: list[tuple[str, ImageFont.FreeTypeFont, ImageFont.FreeTypeFont, tuple[int, int, int]]],
    gap: int = 2,
    align: str = "center",
) -> int:
    total_w, max_h, items = measure_segments(draw, segments, gap=gap)
    cx = (cx_center - total_w // 2) if align == "center" else cx_center
    ty = cy - max_h // 2
    for sub, f, bb, w_sub, h_sub, col in items:
        draw.text((cx - bb[0], ty + (max_h - h_sub) // 2 - bb[1]), sub, font=f, fill=col)
        cx += w_sub + gap
    return max_h


def draw_segments_centered(
    draw: ImageDraw.ImageDraw,
    cy: int,
    segments: list[tuple[str, ImageFont.FreeTypeFont, ImageFont.FreeTypeFont, tuple[int, int, int]]],
    gap: int = 2,
) -> int:
    return draw_segments_at(draw, W // 2, cy, segments, gap=gap, align="center")


def wrap_mixed_lines(
    draw: ImageDraw.ImageDraw,
    text: str,
    lf: ImageFont.FreeTypeFont,
    cf: ImageFont.FreeTypeFont,
    max_width: int,
) -> list[str]:
    words = text.split(" ")
    lines: list[str] = []
    cur = ""
    for w in words:
        cand = f"{cur} {w}".strip() if cur else w
        tw, _, _ = measure_segments(draw, [(cand, lf, cf, CHARCOAL)])
        if tw <= max_width or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_step_badge(
    draw: ImageDraw.ImageDraw,
    cx: int,
    cy: int,
    radius: int,
    num: int,
    bg_color: tuple[int, int, int],
    fg_color: tuple[int, int, int] = (255, 255, 255),
) -> None:
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=bg_color)
    f = load_latin(max(11, int(radius * 1.24)), "bold")
    s = str(num)
    bb = draw.textbbox((0, 0), s, font=f)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    draw.text((cx - tw // 2 - bb[0], cy - th // 2 - bb[1]), s, font=f, fill=fg_color)


def draw_simple_pill(
    draw: ImageDraw.ImageDraw,
    cx_center: int,
    cy: int,
    text: str,
    font: ImageFont.FreeTypeFont,
    bg_color: tuple[int, int, int],
    fg_color: tuple[int, int, int],
    outline: tuple[int, int, int] | None = None,
    pad_x: int = 28,
    pad_y: int = 11,
    step_num: int | None = None,
) -> None:
    cjk_dummy = load_cjk(font.size)
    tw, th, _ = measure_segments(draw, [(text, font, cjk_dummy, fg_color)])
    badge_d = int(th * 1.35) if step_num is not None else 0
    badge_gap = 11 if step_num is not None else 0
    pw = badge_d + badge_gap + tw + pad_x * 2
    ph = max(th, badge_d) + pad_y * 2
    x0, y0 = cx_center - pw // 2, cy - ph // 2
    draw.rounded_rectangle(
        [x0, y0, x0 + pw, y0 + ph],
        radius=ph // 2,
        fill=bg_color,
        outline=outline,
        width=2 if outline else 0,
    )
    tx_start = x0 + pad_x
    if step_num is not None:
        r = badge_d // 2
        draw_step_badge(draw, tx_start + r, cy, r, step_num, fg_color, bg_color)
        tx_start += badge_d + badge_gap
    draw_segments_at(draw, tx_start, cy, [(text, font, cjk_dummy, fg_color)], align="left")


def draw_tone_pill(
    draw: ImageDraw.ImageDraw,
    cy: int,
    label: str,
    tone: int,
    color: tuple[int, int, int],
    bg_color: tuple[int, int, int],
    font: ImageFont.FreeTypeFont,
) -> None:
    bb = draw.textbbox((0, 0), label, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    diag_w, diag_gap = 46, 16
    pad_x, pad_y = 26, 12
    pw = tw + diag_gap + diag_w + pad_x * 2
    ph = max(th, 32) + pad_y * 2
    x0, y0 = (W - pw) // 2, cy - ph // 2
    draw.rounded_rectangle(
        [x0, y0, x0 + pw, y0 + ph],
        radius=ph // 2,
        fill=bg_color,
        outline=color,
        width=3,
    )
    draw.text((x0 + pad_x - bb[0], cy - th // 2 - bb[1]), label, font=font, fill=color)

    dx0 = x0 + pad_x + tw + diag_gap
    dx1 = dx0 + diag_w
    dy0, dy1 = cy - 14, cy + 14
    guide_col = tuple(min(255, int(c + (255 - c) * 0.65)) for c in color)
    for frac in (0.0, 0.5, 1.0):
        gy = int(dy0 + (dy1 - dy0) * frac)
        draw.line([(dx0, gy), (dx1, gy)], fill=guide_col, width=2)

    if tone == 3:
        p1 = (dx0 + 4, int(dy0 + (dy1 - dy0) * 0.58))
        p2 = (dx0 + diag_w // 2 - 2, dy1 - 2)
        p3 = (dx1 - 6, dy0 + 5)
        draw.line([p1, p2, p3], fill=color, width=4, joint="curve")
        draw.polygon(
            [(p3[0] + 4, p3[1] - 3), (p3[0] - 9, p3[1] - 1), (p3[0] - 1, p3[1] + 9)],
            fill=color,
        )
    else:
        p1 = (dx0 + 6, dy0 + 2)
        p2 = (dx1 - 6, dy1 - 2)
        draw.line([p1, p2], fill=color, width=5)
        draw.polygon(
            [(p2[0] + 3, p2[1] + 2), (p2[0] - 12, p2[1] + 1), (p2[0] - 3, p2[1] - 11)],
            fill=color,
        )


# ---------------------------------------------------------------------------
# 1:1 Aligned Crop Helper & STHeiti Template Stroke Decomposition
# ---------------------------------------------------------------------------

def _safe_square_crop(img: Image.Image, box: tuple[int, int, int, int], fill: int | tuple[int, int, int]) -> Image.Image:
    """Crop `box` from `img` safely even if `box` extends slightly outside canvas bounds."""
    x0, y0, x1, y1 = box
    sw, sh = x1 - x0, y1 - y0
    out = Image.new(img.mode, (sw, sh), fill)
    ix0 = max(0, x0)
    iy0 = max(0, y0)
    ix1 = min(img.width, x1)
    iy1 = min(img.height, y1)
    if ix1 > ix0 and iy1 > iy0:
        region = img.crop((ix0, iy0, ix1, iy1))
        out.paste(region, (ix0 - x0, iy0 - y0))
    return out


def _pt_seg_dist2(px: float, py: float, ax: float, ay: float, bx: float, by: float) -> float:
    vx, vy = bx - ax, by - ay
    wx, wy = px - ax, py - ay
    c1 = vx * wx + vy * wy
    if c1 <= 0.0:
        return wx * wx + wy * wy
    c2 = vx * vx + vy * vy
    if c2 <= c1:
        dx, dy = px - bx, py - by
        return dx * dx + dy * dy
    t = c1 / c2
    dx, dy = px - (ax + t * vx), py - (ay + t * vy)
    return dx * dx + dy * dy


def _pt_poly_dist(px: float, py: float, poly: list[tuple[int, int]]) -> float:
    return math.sqrt(min(_pt_seg_dist2(px, py, poly[i][0], poly[i][1], poly[i + 1][0], poly[i + 1][1]) for i in range(len(poly) - 1)))


def _polyline_point_at_frac(pts: list[tuple[float, float]], frac: float) -> tuple[float, float]:
    return _polyline_prefix(pts, frac)[-1]


def _polyline_prefix(pts: list[tuple[float, float]], frac: float) -> list[tuple[float, float]]:
    if len(pts) < 2 or frac <= 0.0:
        return pts[:1]
    if frac >= 1.0:
        return pts
    seg_lens = [math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1)]
    total = sum(seg_lens) or 1.0
    target = total * frac
    acc = 0.0
    out = [pts[0]]
    for i, slen in enumerate(seg_lens):
        if acc + slen <= target:
            out.append(pts[i + 1])
            acc += slen
        else:
            rem = (target - acc) / (slen or 1.0)
            out.append((
                pts[i][0] + rem * (pts[i + 1][0] - pts[i][0]),
                pts[i][1] + rem * (pts[i + 1][1] - pts[i][1]),
            ))
            break
    return out


# Unified Brush-Calligraphy (hanzi-writer-data / Kaiti) Stroke Specs & Crop Boxes
BRUSH_SPECS = {
    "好": {
        "crop_boxes": {
            "comp1": (56, 588, 706, 1238),     # 650x650 centered on 女 (including hair bun + robe)
            "comp2": (340, 608, 990, 1258),    # 650x650 centered on 子 (including outstretched arms)
            "combined": (170, 543, 910, 1283), # 740x740 centered on 好 illustration + strokes
        },
        "comp_colors": [NAVY, NAVY, NAVY, TERRACOTTA, TERRACOTTA, TERRACOTTA],
    },
    "看": {
        "crop_boxes": {
            "comp1": (129, 617, 849, 1337),    # 720x720 centered on 手 (hand shading brow)
            "comp2": (368, 882, 748, 1262),    # 380x380 centered on 目 (eye frame)
            "combined": (129, 617, 849, 1337), # 720x720 centered on 看 illustration + strokes
        },
        "comp_colors": [TERRACOTTA, TERRACOTTA, TERRACOTTA, TERRACOTTA, NAVY, NAVY, NAVY, NAVY, NAVY],
    },
}

_STROKE_JSON_CACHE: dict[str, dict] = {}


def load_stroke_json(char: str) -> dict:
    if char not in _STROKE_JSON_CACHE:
        path = STROKE_DATA_DIR / f"{char}.json"
        _STROKE_JSON_CACHE[char] = json.loads(path.read_text(encoding="utf-8"))
    return _STROKE_JSON_CACHE[char]


def parse_svg_stroke_polys(path_d: str, scale: float, ox: float, oy: float) -> list[list[tuple[float, float]]]:
    """Parse MakeMeAHanzi SVG stroke path (`M/L/Q/C/Z`) into 2D polygon rings in canvas pixels."""
    tokens = re.findall(r"[MLQCZmlqcz]|-?\d+(?:\.\d+)?", path_d)
    i = 0
    cmd: str | None = None
    cur = (0.0, 0.0)
    polys: list[list[tuple[float, float]]] = []
    pts: list[tuple[float, float]] = []

    def tx(x: float, y: float) -> tuple[float, float]:
        return (x * scale + ox, (900.0 - y) * scale + oy)

    while i < len(tokens):
        t = tokens[i]
        if t.isalpha():
            cmd = t
            i += 1
            if cmd in ("Z", "z"):
                if len(pts) >= 3:
                    polys.append(pts)
                pts = []
                continue
        if cmd == "M":
            if len(pts) >= 3:
                polys.append(pts)
                pts = []
            cur = (float(tokens[i]), float(tokens[i + 1]))
            i += 2
            pts.append(tx(*cur))
            cmd = "L"
        elif cmd == "L":
            cur = (float(tokens[i]), float(tokens[i + 1]))
            i += 2
            pts.append(tx(*cur))
        elif cmd == "Q":
            x1, y1, x2, y2 = map(float, tokens[i : i + 4])
            i += 4
            p0, p1, p2 = cur, (x1, y1), (x2, y2)
            for s in range(1, 15):
                u = s / 14.0
                v = 1.0 - u
                pts.append(tx(
                    v * v * p0[0] + 2 * v * u * p1[0] + u * u * p2[0],
                    v * v * p0[1] + 2 * v * u * p1[1] + u * u * p2[1],
                ))
            cur = p2
        elif cmd == "C":
            x1, y1, x2, y2, x3, y3 = map(float, tokens[i : i + 6])
            i += 6
            p0, p1, p2, p3 = cur, (x1, y1), (x2, y2), (x3, y3)
            for s in range(1, 15):
                u = s / 14.0
                v = 1.0 - u
                pts.append(tx(
                    v ** 3 * p0[0] + 3 * v ** 2 * u * p1[0] + 3 * v * u ** 2 * p2[0] + u ** 3 * p3[0],
                    v ** 3 * p0[1] + 3 * v ** 2 * u * p1[1] + 3 * v * u ** 2 * p2[1] + u ** 3 * p3[1],
                ))
            cur = p3
        else:
            i += 1
    if len(pts) >= 3:
        polys.append(pts)
    return polys


def render_brush_glyph_rgba(
    source_char: str,
    stroke_indices: list[int] | None,
    box_size: int,
    fill_color: tuple[int, int, int],
) -> Image.Image:
    """Render tight-cropped RGBA brush-calligraphy glyph from `stroke_data/<source_char>.json`."""
    data = load_stroke_json(source_char)
    sel = stroke_indices if stroke_indices is not None else list(range(len(data["strokes"])))

    # First measure SVG bbox across selected strokes (in 1024x1024 flipped Y space)
    raw_polys: list[list[tuple[float, float]]] = []
    xs: list[float] = []
    ys: list[float] = []
    for idx in sel:
        for poly in parse_svg_stroke_polys(data["strokes"][idx], 1.0, 0.0, 0.0):
            raw_polys.append(poly)
            for x, y in poly:
                xs.append(x)
                ys.append(y)

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    gw = max(1.0, max_x - min_x)
    gh = max(1.0, max_y - min_y)

    # Keep uniform stroke weight consistency across narrow components (女/子/目) and full chars (好/看)
    target_span = box_size * 0.90
    scale = min(target_span / gw, target_span / gh, (box_size / 1024.0) * 1.24)
    out_w = max(8, int(math.ceil(gw * scale)) + 4)
    out_h = max(8, int(math.ceil(gh * scale)) + 4)

    ss = 2
    ox = (out_w / 2.0 - ((min_x + max_x) / 2.0) * scale) * ss
    oy = (out_h / 2.0 - ((min_y + max_y) / 2.0) * scale) * ss
    mask = Image.new("L", (out_w * ss, out_h * ss), 0)
    md = ImageDraw.Draw(mask)
    for poly in raw_polys:
        scaled_poly = [(x * scale * ss + ox, y * scale * ss + oy) for (x, y) in poly]
        md.polygon(scaled_poly, fill=255)
    mask_aa = mask.resize((out_w, out_h), Image.Resampling.LANCZOS)

    rgba = Image.new("RGBA", (out_w, out_h), fill_color + (0,))
    fill_layer = Image.new("RGBA", (out_w, out_h), fill_color + (255,))
    rgba.paste(fill_layer, (0, 0), mask_aa)
    return rgba


def draw_brush_hero_with_pinyin(
    canvas: Image.Image,
    cx_center: int,
    cy: int,
    glyph_source_char: str,
    stroke_indices: list[int] | None,
    glyph_box: int,
    glyph_color: tuple[int, int, int],
    pinyin: str,
    pinyin_font: ImageFont.FreeTypeFont,
    pinyin_color: tuple[int, int, int],
    gap: int = 28,
) -> None:
    """Draw a brush-calligraphy glyph paired horizontally with its Pinyin, centered on `(cx_center, cy)`."""
    glyph = render_brush_glyph_rgba(glyph_source_char, stroke_indices, glyph_box, glyph_color)
    d = ImageDraw.Draw(canvas)
    bb = d.textbbox((0, 0), pinyin, font=pinyin_font)
    pw, ph = bb[2] - bb[0], bb[3] - bb[1]

    total_w = glyph.width + gap + pw
    gx = cx_center - total_w // 2
    gy = cy - glyph.height // 2
    canvas.paste(glyph, (gx, gy), glyph)

    d = ImageDraw.Draw(canvas)
    px = gx + glyph.width + gap
    py = cy - ph // 2 - bb[1]
    d.text((px - bb[0], py), pinyin, font=pinyin_font, fill=pinyin_color)


def _normalize_cream_bg(img: Image.Image) -> Image.Image:
    """Snap near-cream JPEG background pixels cleanly to `#F9F5EC` to avoid faint box seams."""
    out = img.copy()
    px = out.load()
    bw, bh = out.size
    for y in range(bh):
        for x in range(bw):
            r, g, b = px[x, y]
            if r > 234 and g > 230 and b > 218 and abs(r - b) < 24:
                px[x, y] = BG_COLOR
    return out


def build_aligned_ai_artworks(char: str) -> dict[str, Image.Image]:
    """Extract 1:1 aligned brush-style AI illustrations cropped identically to `BRUSH_SPECS[char]`."""
    spec = BRUSH_SPECS[char]
    src_raw = Image.open(ILLUS_DIR / f"{char}.jpg").convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
    src = _normalize_cream_bg(src_raw)
    px = src.load()

    def build_masked_canvas(keep_fn) -> Image.Image:
        out = Image.new("RGB", (W, H), BG_COLOR)
        opx = out.load()
        for y in range(H):
            for x in range(W):
                if px[x, y] != BG_COLOR and keep_fn(x, y, px[x, y]):
                    opx[x, y] = px[x, y]
        return out

    if char == "好":
        def keep_c1(x, y, rgb):
            r, g, b = rgb
            is_navy = (b > r + 8) or (r < 95 and g < 100)
            in_heart = (524 <= x <= 582) and (852 <= y <= 912)
            if in_heart:
                return False
            if y < 845:
                return x <= 555
            if y < 1030:
                return is_navy or (x < 492)
            return x <= 552

        def keep_c2(x, y, rgb):
            r, g, b = rgb
            is_navy = (b > r + 8) or (r < 95 and g < 100)
            in_heart = (524 <= x <= 582) and (852 <= y <= 912)
            if in_heart or is_navy:
                return False
            return (935 <= y <= 1005 and x >= 482) or (x >= 555)

        c1_full = build_masked_canvas(keep_c1)
        c2_full = build_masked_canvas(keep_c2)
    elif char == "看":
        def keep_c1(x, y, rgb):
            r, g, b = rgb
            is_terracotta = (r - b > 20 and r > 125)
            return is_terracotta or (y < 932)

        def keep_c2(x, y, rgb):
            r, g, b = rgb
            is_terracotta = (r - b > 20 and r > 125)
            return (y >= 932) and (x >= 440) and not is_terracotta

        c1_full = build_masked_canvas(keep_c1)
        c2_full = build_masked_canvas(keep_c2)
    else:
        raise ValueError(f"Unsupported character: {char}")

    boxes = spec["crop_boxes"]
    return {
        "comp1": _safe_square_crop(c1_full, boxes["comp1"], BG_COLOR),
        "comp2": _safe_square_crop(c2_full, boxes["comp2"], BG_COLOR),
        "combined": _safe_square_crop(src, boxes["combined"], BG_COLOR),
    }


def build_brush_stroke_masks(
    char: str,
    crop_key: str,
    size: int,
    stroke_indices: list[int] | None = None,
) -> dict:
    """Render 1:1 rounded brush-calligraphy stroke masks & medians cropped identically to `BRUSH_SPECS`."""
    spec = BRUSH_SPECS[char]
    data = load_stroke_json(char)
    all_strokes = data["strokes"]
    all_medians = data["medians"]
    sel = stroke_indices if stroke_indices is not None else list(range(len(all_strokes)))
    crop_box = spec["crop_boxes"][crop_key]
    cx0, cy0, cx1, cy1 = crop_box
    crop_w = float(cx1 - cx0)
    scale_crop = size / crop_w

    ss = 2
    masks: list[Image.Image] = []
    medians: list[list[tuple[float, float]]] = []
    badge_pts: list[tuple[int, int]] = []
    colors: list[tuple[int, int, int]] = []
    badge_r = max(12, int(size * 0.025))

    # Map SVG (0..1024) -> template 1080x1920 -> crop_box (size x size) directly for crisp vector fidelity
    tile_scale = TMPL_SCALE * scale_crop * ss
    tile_ox = (TMPL_OX - cx0) * scale_crop * ss
    tile_oy_shift = TMPL_OY - cy0

    def tx_tile_med(mx: float, my: float) -> tuple[float, float]:
        px_c = (mx * TMPL_SCALE + TMPL_OX - cx0) * scale_crop
        py_c = (((900.0 - my) * TMPL_SCALE + TMPL_OY) - cy0) * scale_crop
        return (px_c, py_c)

    for s_id in sel:
        # Render exact brush stroke polygon at 2x supersampling directly inside (size, size)
        m_hi = Image.new("L", (size * ss, size * ss), 0)
        md = ImageDraw.Draw(m_hi)
        polys = parse_svg_stroke_polys(
            all_strokes[s_id],
            tile_scale,
            tile_ox,
            tile_oy_shift * scale_crop * ss,
        )
        for poly in polys:
            md.polygon(poly, fill=255)
        masks.append(m_hi.resize((size, size), Image.Resampling.LANCZOS))
        colors.append(spec["comp_colors"][s_id])

        med_px = [tx_tile_med(mx, my) for (mx, my) in all_medians[s_id]]
        bx, by = _polyline_point_at_frac(med_px, 0.08)
        for cand_f in (0.08, 0.18, 0.28, 0.40, 0.03):
            px_c, py_c = _polyline_point_at_frac(med_px, cand_f)
            if all(math.hypot(px_c - ox, py_c - oy) >= badge_r * 2.35 for (ox, oy) in badge_pts):
                bx, by = px_c, py_c
                break
        badge_pts.append((int(bx), int(by)))

        if len(med_px) >= 2:
            dx0, dy0 = med_px[1][0] - med_px[0][0], med_px[1][1] - med_px[0][1]
            l0 = math.hypot(dx0, dy0) or 1.0
            dx1, dy1 = med_px[-1][0] - med_px[-2][0], med_px[-1][1] - med_px[-2][1]
            l1 = math.hypot(dx1, dy1) or 1.0
            ext = size * 0.045
            med_px[0] = (med_px[0][0] - ext * dx0 / l0, med_px[0][1] - ext * dy0 / l0)
            med_px[-1] = (med_px[-1][0] + ext * dx1 / l1, med_px[-1][1] + ext * dy1 / l1)
        medians.append(med_px)

    return {
        "n": len(masks),
        "masks": masks,
        "medians": medians,
        "badge_pts": badge_pts,
        "colors": colors,
        "size": size,
    }


def _draw_mizige_box(
    draw: ImageDraw.ImageDraw,
    x0: int,
    y0: int,
    size: int,
    fill: tuple[int, int, int] = BG_COLOR,
    outline: tuple[int, int, int] = CARD_BORDER,
    outline_w: int = 3,
    guide_color: tuple[int, int, int] = GRID_LINE,
) -> None:
    x1, y1 = x0 + size, y0 + size
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    draw.rounded_rectangle([x0, y0, x1, y1], radius=max(10, size // 16), fill=fill, outline=outline, width=outline_w)
    dash = max(5, size // 36)
    for pos in range(x0 + 8, x1 - 8, dash * 2):
        draw.line([(pos, cy), (min(pos + dash, x1 - 8), cy)], fill=guide_color, width=1)
    for pos in range(y0 + 8, y1 - 8, dash * 2):
        draw.line([(cx, pos), (cx, min(pos + dash, y1 - 8))], fill=guide_color, width=1)
    steps = max(7, size // 28)
    for k in range(0, steps, 2):
        t0, t1 = k / steps, min(1.0, (k + 1) / steps)
        draw.line([(x0 + 8 + t0 * (size - 16), y0 + 8 + t0 * (size - 16)), (x0 + 8 + t1 * (size - 16), y0 + 8 + t1 * (size - 16))], fill=guide_color, width=1)
        draw.line([(x1 - 8 - t0 * (size - 16), y0 + 8 + t0 * (size - 16)), (x1 - 8 - t1 * (size - 16), y0 + 8 + t1 * (size - 16))], fill=guide_color, width=1)


def _render_char_strokes_tile(
    sdata: dict,
    active_idx: int,
    frac: float,
    all_done: bool,
    box_bg: tuple[int, int, int] = BG_COLOR,
    outline: tuple[int, int, int] = CARD_BORDER,
) -> Image.Image:
    """Render `size x size` Mi-Zi-Ge practice box using the exact Kaiti brush strokes aligned to AI art."""
    size = sdata["size"]
    tile = Image.new("RGB", (size, size), BG_COLOR)
    td = ImageDraw.Draw(tile)
    _draw_mizige_box(td, 0, 0, size, fill=box_bg, outline=outline, outline_w=3)

    fg = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    masks = sdata["masks"]
    colors = sdata["colors"]
    medians = sdata["medians"]

    ghost_layer = Image.new("RGBA", (size, size), GHOST_STROKE + (255,))
    for idx in range(sdata["n"]):
        fg.paste(ghost_layer, (0, 0), masks[idx])

    done_count = sdata["n"] if all_done else active_idx
    for idx in range(done_count):
        col_layer = Image.new("RGBA", (size, size), colors[idx] + (255,))
        fg.paste(col_layer, (0, 0), masks[idx])

    tip_pt = None
    if not all_done and 0 <= active_idx < sdata["n"]:
        pref = _polyline_prefix(medians[active_idx], frac)
        brush_mask = Image.new("L", (size, size), 0)
        bd = ImageDraw.Draw(brush_mask)
        brush_r = int(size * 0.135)
        for p in pref:
            bd.ellipse([p[0] - brush_r, p[1] - brush_r, p[0] + brush_r, p[1] + brush_r], fill=255)
        if len(pref) >= 2:
            bd.line(pref, fill=255, width=brush_r * 2, joint="curve")
        clipped = ImageChops.darker(masks[active_idx], brush_mask)
        col_layer = Image.new("RGBA", (size, size), colors[active_idx] + (255,))
        fg.paste(col_layer, (0, 0), clipped)
        tip_pt = pref[-1]

    tile.paste(fg, (0, 0), fg)
    d = ImageDraw.Draw(tile)
    if tip_pt is not None:
        r_outer = max(11, int(size * 0.024))
        r_inner = max(6, int(size * 0.014))
        tx, ty = tip_pt
        d.ellipse([tx - r_outer, ty - r_outer, tx + r_outer, ty + r_outer], fill=GOLD_ACCENT, outline=(255, 255, 255), width=3)
        d.ellipse([tx - r_inner, ty - r_inner, tx + r_inner, ty + r_inner], fill=colors[active_idx])

    badge_r = max(12, int(size * 0.024))
    shown_up_to = sdata["n"] if all_done else min(active_idx + 1, sdata["n"])
    for idx in range(shown_up_to):
        bx, by = sdata["badge_pts"][idx]
        bg = colors[idx] if (idx == active_idx and not all_done) else CHARCOAL
        draw_step_badge(d, bx, by, badge_r, idx + 1, bg, (255, 255, 255))

    return tile


def _build_static_stroke_strip_tiles(
    char: str,
    crop_key: str,
    stroke_indices: list[int] | None,
    mini_size: int,
) -> list[Image.Image]:
    sdata = build_brush_stroke_masks(char, crop_key, mini_size, stroke_indices=stroke_indices)
    n = sdata["n"]
    tiles: list[Image.Image] = []
    for k in range(n):
        tile = Image.new("RGB", (mini_size, mini_size), BG_COLOR)
        td = ImageDraw.Draw(tile)
        _draw_mizige_box(td, 0, 0, mini_size, fill=BG_COLOR, outline=CARD_BORDER, outline_w=2)

        fg = Image.new("RGBA", (mini_size, mini_size), (0, 0, 0, 0))
        ghost_l = Image.new("RGBA", (mini_size, mini_size), GHOST_STROKE + (255,))
        for idx in range(n):
            fg.paste(ghost_l, (0, 0), sdata["masks"][idx])
        for idx in range(k):
            prev_l = Image.new("RGBA", (mini_size, mini_size), CHARCOAL + (255,))
            fg.paste(prev_l, (0, 0), sdata["masks"][idx])
        cur_col = sdata["colors"][k]
        cur_l = Image.new("RGBA", (mini_size, mini_size), cur_col + (255,))
        fg.paste(cur_l, (0, 0), sdata["masks"][k])

        tile.paste(fg, (0, 0), fg)
        draw_step_badge(td, max(12, mini_size // 8), max(12, mini_size // 8), max(10, mini_size // 11), k + 1, cur_col, (255, 255, 255))
        tiles.append(tile)
    return tiles


def _build_aligned_illustration_tile(artwork: Image.Image, size: int) -> Image.Image:
    """Resize 1:1 aligned artwork directly to `size x size` with ZERO extra inner padding shift."""
    scaled = artwork.resize((size, size), Image.Resampling.LANCZOS).filter(
        ImageFilter.UnsharpMask(radius=0.9, percent=90, threshold=3)
    )
    tile = Image.new("RGB", (size, size), BG_COLOR)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, size, size], radius=max(24, size // 16), fill=255)
    tile.paste(scaled, (0, 0), mask)
    ImageDraw.Draw(tile).rounded_rectangle([0, 0, size - 1, size - 1], radius=max(24, size // 16), outline=CARD_BORDER, width=3)
    return tile


def paste_thumbnail_frame(
    canvas: Image.Image,
    artwork: Image.Image,
    box: tuple[int, int, int, int],
    radius: int = 20,
) -> None:
    x0, y0, x1, y1 = box
    side = min(x1 - x0, y1 - y0)
    scaled = artwork.resize((side, side), Image.Resampling.LANCZOS).filter(
        ImageFilter.UnsharpMask(radius=0.9, percent=90, threshold=3)
    )
    mask = Image.new("L", (side, side), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, side, side], radius=radius, fill=255)
    canvas.paste(scaled, (x0, y0), mask)
    ImageDraw.Draw(canvas).rounded_rectangle([x0, y0, x1, y1], radius=radius, outline=CARD_BORDER, width=2)


# ---------------------------------------------------------------------------
# Synchronized 3-Scene Exemplar Specs (Arti -> Karakter Mandarin Word Order)
# ---------------------------------------------------------------------------

EXEMPLARS = {
    "好": {
        "target_pinyin": "hǎo",
        "target_tone": 3,
        "stroke_split": 3,
        "c1_indices": [0, 1, 2],
        "c2_indices": [3, 4, 5],
        "id": {
            "badge_final": "HSK 1  ·  ASAL-USUL & MNEMONIK",
            "tone_label": "Nada 3  ·  Turun-Naik",
            "combined_pill": "GABUNGAN:  女  +  子  =  好",
            "meaning": "Arti:  Baik / Bagus / Suka",
            "hook_pill": "MNEMONIK 3 KARAKTER",
            "hook_lines": [
                "Saat ibu (女) memeluk anak (子),",
                "rasanya baik & suka (好)!",
            ],
            "c1": {
                "step": 1,
                "hanzi": "女",
                "pinyin": "nǚ",
                "tone": 3,
                "tone_label": "Nada 3  ·  Turun-Naik",
                "color": NAVY,
                "soft_bg": SOFT_NAVY,
                "scene_badge": "LANGKAH 1 / 3  ·  ASAL KARAKTER 1",
                "card_title": "ASAL KARAKTER 1",
                "meaning_short": "Perempuan / Ibu  ·  Nada 3",
                "meaning_full": "Arti:  Perempuan / Ibu",
                "origin_pill": "DARI GAMBAR KE HURUF",
                "mini_origin": "Ibu duduk bersimpuh dengan anggun",
                "scene_origin": "Berasal dari sosok ibu yang duduk bersimpuh.",
                "audio_part_a": [
                    (VOICE_ZH, "女。", 80),
                    (VOICE_ID, "Artinya perempuan atau ibu.", 90),
                ],
                "audio_part_b": [
                    (VOICE_ID, "Berasal dari sosok ibu yang duduk bersimpuh.", 0),
                ],
            },
            "c2": {
                "step": 2,
                "hanzi": "子",
                "pinyin": "zǐ",
                "tone": 3,
                "tone_label": "Nada 3  ·  Turun-Naik",
                "color": TERRACOTTA,
                "soft_bg": SOFT_TERRACOTTA,
                "scene_badge": "LANGKAH 2 / 3  ·  ASAL KARAKTER 2",
                "card_title": "ASAL KARAKTER 2",
                "meaning_short": "Anak / Bayi  ·  Nada 3",
                "meaning_full": "Arti:  Anak / Bayi",
                "origin_pill": "DARI GAMBAR KE HURUF",
                "mini_origin": "Bayi merentangkan kedua tangannya",
                "scene_origin": "Berasal dari bayi yang merentangkan kedua tangan.",
                "audio_part_a": [
                    (VOICE_ZH, "子。", 80),
                    (VOICE_ID, "Artinya anak.", 90),
                ],
                "audio_part_b": [
                    (VOICE_ID, "Berasal dari bayi yang merentangkan kedua tangan.", 0),
                ],
            },
            "s3_phase1": [
                (VOICE_ID, "Saat ibu,", 60),
                (VOICE_ZH, "女，", 80),
            ],
            "s3_phase2": [
                (VOICE_ID, "memeluk anak,", 60),
                (VOICE_ZH, "子，", 80),
            ],
            "s3_phase3": [
                (VOICE_ID, "rasanya baik dan suka,", 70),
                (VOICE_ZH, "好。", 140),
                (VOICE_ID, "Artinya baik, bagus, atau suka.", 120),
                (VOICE_ZH, "好。", 0),
            ],
        },
        "en": {
            "badge_final": "HSK 1  ·  ORIGINS & MNEMONIC",
            "tone_label": "Tone 3  ·  Dipping",
            "combined_pill": "COMBINED:  女  +  子  =  好",
            "meaning": "Meaning:  Good / Fine / To Like",
            "hook_pill": "3-CHARACTER MNEMONIC",
            "hook_lines": [
                "When a mother (女) hugs her child (子),",
                "everything feels good (好)!",
            ],
            "c1": {
                "step": 1,
                "hanzi": "女",
                "pinyin": "nǚ",
                "tone": 3,
                "tone_label": "Tone 3  ·  Dipping",
                "color": NAVY,
                "soft_bg": SOFT_NAVY,
                "scene_badge": "STEP 1 / 3  ·  CHARACTER 1 ORIGIN",
                "card_title": "CHARACTER 1 ORIGIN",
                "meaning_short": "Woman / Mother  ·  Tone 3",
                "meaning_full": "Meaning:  Woman / Mother",
                "origin_pill": "FROM PICTURE TO CHARACTER",
                "mini_origin": "Mother sitting gracefully on knees",
                "scene_origin": "Coming from a kneeling mother.",
                "audio_part_a": [
                    (VOICE_ZH, "女。", 80),
                    (VOICE_EN, "Means woman or mother.", 90),
                ],
                "audio_part_b": [
                    (VOICE_EN, "Coming from a kneeling mother.", 0),
                ],
            },
            "c2": {
                "step": 2,
                "hanzi": "子",
                "pinyin": "zǐ",
                "tone": 3,
                "tone_label": "Tone 3  ·  Dipping",
                "color": TERRACOTTA,
                "soft_bg": SOFT_TERRACOTTA,
                "scene_badge": "STEP 2 / 3  ·  CHARACTER 2 ORIGIN",
                "card_title": "CHARACTER 2 ORIGIN",
                "meaning_short": "Child / Baby  ·  Tone 3",
                "meaning_full": "Meaning:  Child / Baby",
                "origin_pill": "FROM PICTURE TO CHARACTER",
                "mini_origin": "Swaddled baby opening both arms",
                "scene_origin": "Coming from a baby with open arms.",
                "audio_part_a": [
                    (VOICE_ZH, "子。", 80),
                    (VOICE_EN, "Means child.", 90),
                ],
                "audio_part_b": [
                    (VOICE_EN, "Coming from a baby with open arms.", 0),
                ],
            },
            "s3_phase1": [
                (VOICE_EN, "When a mother,", 60),
                (VOICE_ZH, "女，", 80),
            ],
            "s3_phase2": [
                (VOICE_EN, "hugs her child,", 60),
                (VOICE_ZH, "子，", 80),
            ],
            "s3_phase3": [
                (VOICE_EN, "everything feels good,", 70),
                (VOICE_ZH, "好。", 140),
                (VOICE_EN, "Meaning good, fine, or to like.", 120),
                (VOICE_ZH, "好。", 0),
            ],
        },
    },
    "看": {
        "target_pinyin": "kàn",
        "target_tone": 4,
        "stroke_split": 4,
        "c1_indices": [0, 1, 2, 3],
        "c2_indices": [4, 5, 6, 7, 8],
        "id": {
            "badge_final": "HSK 1  ·  ASAL-USUL & MNEMONIK",
            "tone_label": "Nada 4  ·  Turun Tegas",
            "combined_pill": "GABUNGAN:  手  +  目  =  看",
            "meaning": "Arti:  Melihat / Menonton",
            "hook_pill": "MNEMONIK 3 KARAKTER",
            "hook_lines": [
                "Taruh tangan (手) di atas mata (目),",
                "untuk melihat jauh (看)!",
            ],
            "c1": {
                "step": 1,
                "hanzi": "手",
                "pinyin": "shǒu",
                "tone": 3,
                "tone_label": "Nada 3  ·  Turun-Naik",
                "color": TERRACOTTA,
                "soft_bg": SOFT_TERRACOTTA,
                "scene_badge": "LANGKAH 1 / 3  ·  ASAL KARAKTER 1",
                "card_title": "ASAL KARAKTER 1",
                "meaning_short": "Tangan  ·  Nada 3",
                "meaning_full": "Arti:  Tangan",
                "origin_pill": "DARI GAMBAR KE HURUF",
                "mini_origin": "Lima jari tangan yang terbuka lebar",
                "scene_origin": "Berasal dari lima jari tangan yang terbuka.",
                "audio_part_a": [
                    (VOICE_ZH, "手。", 80),
                    (VOICE_ID, "Artinya tangan.", 90),
                ],
                "audio_part_b": [
                    (VOICE_ID, "Berasal dari lima jari tangan yang terbuka.", 0),
                ],
            },
            "c2": {
                "step": 2,
                "hanzi": "目",
                "pinyin": "mù",
                "tone": 4,
                "tone_label": "Nada 4  ·  Turun Tegas",
                "color": NAVY,
                "soft_bg": SOFT_NAVY,
                "scene_badge": "LANGKAH 2 / 3  ·  ASAL KARAKTER 2",
                "card_title": "ASAL KARAKTER 2",
                "meaning_short": "Mata  ·  Nada 4",
                "meaning_full": "Arti:  Mata",
                "origin_pill": "DARI GAMBAR KE HURUF",
                "mini_origin": "Mata manusia lengkap dengan bola mata",
                "scene_origin": "Berasal dari mata manusia yang diputar tegak.",
                "audio_part_a": [
                    (VOICE_ZH, "目。", 80),
                    (VOICE_ID, "Artinya mata.", 90),
                ],
                "audio_part_b": [
                    (VOICE_ID, "Berasal dari mata manusia yang diputar tegak.", 0),
                ],
            },
            "s3_phase1": [
                (VOICE_ID, "Taruh tangan,", 60),
                (VOICE_ZH, "手，", 80),
            ],
            "s3_phase2": [
                (VOICE_ID, "di atas mata,", 60),
                (VOICE_ZH, "目，", 80),
            ],
            "s3_phase3": [
                (VOICE_ID, "untuk melihat jauh,", 70),
                (VOICE_ZH, "看。", 140),
                (VOICE_ID, "Artinya melihat atau menonton.", 120),
                (VOICE_ZH, "看。", 0),
            ],
        },
        "en": {
            "badge_final": "HSK 1  ·  ORIGINS & MNEMONIC",
            "tone_label": "Tone 4  ·  Sharp Falling",
            "combined_pill": "COMBINED:  手  +  目  =  看",
            "meaning": "Meaning:  To Look / Watch",
            "hook_pill": "3-CHARACTER MNEMONIC",
            "hook_lines": [
                "Put your hand (手) above your eye (目),",
                "to look far ahead (看)!",
            ],
            "c1": {
                "step": 1,
                "hanzi": "手",
                "pinyin": "shǒu",
                "tone": 3,
                "tone_label": "Tone 3  ·  Dipping",
                "color": TERRACOTTA,
                "soft_bg": SOFT_TERRACOTTA,
                "scene_badge": "STEP 1 / 3  ·  CHARACTER 1 ORIGIN",
                "card_title": "CHARACTER 1 ORIGIN",
                "meaning_short": "Hand  ·  Tone 3",
                "meaning_full": "Meaning:  Hand",
                "origin_pill": "FROM PICTURE TO CHARACTER",
                "mini_origin": "Open hand with five fingers out",
                "scene_origin": "Coming from an open hand with five fingers.",
                "audio_part_a": [
                    (VOICE_ZH, "手。", 80),
                    (VOICE_EN, "Means hand.", 90),
                ],
                "audio_part_b": [
                    (VOICE_EN, "Coming from an open hand with five fingers.", 0),
                ],
            },
            "c2": {
                "step": 2,
                "hanzi": "目",
                "pinyin": "mù",
                "tone": 4,
                "tone_label": "Tone 4  ·  Sharp Falling",
                "color": NAVY,
                "soft_bg": SOFT_NAVY,
                "scene_badge": "STEP 2 / 3  ·  CHARACTER 2 ORIGIN",
                "card_title": "CHARACTER 2 ORIGIN",
                "meaning_short": "Eye  ·  Tone 4",
                "meaning_full": "Meaning:  Eye",
                "origin_pill": "FROM PICTURE TO CHARACTER",
                "mini_origin": "Human eye turned upright into frame",
                "scene_origin": "Coming from a human eye turned upright.",
                "audio_part_a": [
                    (VOICE_ZH, "目。", 80),
                    (VOICE_EN, "Means eye.", 90),
                ],
                "audio_part_b": [
                    (VOICE_EN, "Coming from a human eye turned upright.", 0),
                ],
            },
            "s3_phase1": [
                (VOICE_EN, "Put your hand,", 60),
                (VOICE_ZH, "手，", 80),
            ],
            "s3_phase2": [
                (VOICE_EN, "above your eye,", 60),
                (VOICE_ZH, "目，", 80),
            ],
            "s3_phase3": [
                (VOICE_EN, "to look far ahead,", 70),
                (VOICE_ZH, "看。", 140),
                (VOICE_EN, "Meaning to look or watch.", 120),
                (VOICE_ZH, "看。", 0),
            ],
        },
    },
}


# ---------------------------------------------------------------------------
# Component Mini-Card Helper
# ---------------------------------------------------------------------------

def _draw_mini_origin_card(
    canvas: Image.Image,
    box: tuple[int, int, int, int],
    comp_cfg: dict,
    art_comp: Image.Image,
    glyph_source_char: str,
    stroke_indices: list[int],
) -> None:
    x0, y0, x1, y1 = box
    w_box = x1 - x0
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle([x0, y0, x1, y1], radius=26, fill=CARD_BG, outline=CARD_BORDER, width=3)

    f_hdr = load_latin(19, "bold")
    hdr_cx = (x0 + x1) // 2
    draw_simple_pill(
        d, hdr_cx, y0 + 32, comp_cfg["card_title"], f_hdr,
        comp_cfg["soft_bg"], comp_cfg["color"], outline=comp_cfg["color"],
        pad_x=16, pad_y=5, step_num=comp_cfg["step"],
    )

    thumb_box = (x0 + 18, y0 + 70, x0 + 180, y0 + 232)
    paste_thumbnail_frame(canvas, art_comp, box=thumb_box, radius=20)

    right_cx = (x0 + 186 + x1 - 12) // 2
    f_comp_hanzi = load_cjk(60)
    f_comp_py = load_latin(34, "bold")
    f_comp_sub = load_latin(21, "demi")
    draw_brush_hero_with_pinyin(
        canvas, right_cx, y0 + 114,
        glyph_source_char, stroke_indices, 66, comp_cfg["color"],
        comp_cfg["pinyin"], f_comp_py, CHARCOAL, gap=14,
    )
    d = ImageDraw.Draw(canvas)
    parts = [p.strip() for p in comp_cfg["meaning_short"].split("·")]
    f_tone_sm = load_latin(20, "bold")
    draw_segments_at(d, right_cx, y0 + 174, [(parts[0], f_comp_sub, f_comp_hanzi, CHARCOAL)])
    if len(parts) > 1:
        draw_segments_at(d, right_cx, y0 + 204, [(parts[1], f_tone_sm, f_comp_hanzi, comp_cfg["color"])])

    d.line([(x0 + 18, y0 + 244), (x1 - 18, y0 + 244)], fill=DIVIDER, width=2)
    f_orig = load_latin(21, "medium")
    f_orig_cjk = load_cjk(21)
    orig_lines = wrap_mixed_lines(d, comp_cfg["mini_origin"], f_orig, f_orig_cjk, max_width=w_box - 32)
    start_y = y0 + (274 if len(orig_lines) > 1 else 288)
    for idx, ln in enumerate(orig_lines[:2]):
        draw_segments_at(d, hdr_cx, start_y + idx * 30, [(ln, f_orig, f_orig_cjk, MUTED)])


# ---------------------------------------------------------------------------
# Audio Helpers
# ---------------------------------------------------------------------------

def validate_tts_segment(voice: str, text: str) -> None:
    if voice in (VOICE_ID, VOICE_EN):
        assert not any(c in text for c in "/+()→↘·"), f"Forbidden symbol in non-ZH TTS ({voice}): {text!r}"
        assert not re.search(r"[\u2e80-\u9fff]", text), f"Forbidden CJK character in non-ZH TTS ({voice}): {text!r}"


def synth_segment_wav(voice: str, text: str, rate: str = "+0%") -> Path:
    validate_tts_segment(voice, text)
    key = hashlib.sha1(f"{voice}|{rate}|{text}".encode("utf-8")).hexdigest()[:16]
    out_wav = AUDIO_CACHE_DIR / f"seg_{key}.wav"
    if out_wav.exists() and out_wav.stat().st_size > 1024:
        return out_wav
    mp3_path = out_wav.with_suffix(".mp3")
    subprocess.run(
        [EDGE_TTS, "--voice", voice, "--rate", rate, "--text", text, "--write-media", str(mp3_path)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    subprocess.run(
        [AFCONVERT, "-f", "WAVE", "-d", f"LEI16@{SAMPLES_PER_SEC}", "-c", "1", str(mp3_path), str(out_wav)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    mp3_path.unlink(missing_ok=True)
    return out_wav


def trim_pcm_silence(
    raw_bytes: bytes,
    thresh: int = 180,
    pad_head_ms: int = 24,
    pad_tail_ms: int = 48,
    fade_ms: int = 5,
) -> bytes:
    samples = array.array("h")
    samples.frombytes(raw_bytes)
    n = len(samples)
    if n == 0:
        return raw_bytes
    active = [i for i, v in enumerate(samples) if abs(v) > thresh]
    if not active:
        return raw_bytes
    i0 = max(0, active[0] - (SAMPLES_PER_SEC * pad_head_ms // 1000))
    i1 = min(n, active[-1] + (SAMPLES_PER_SEC * pad_tail_ms // 1000) + 1)
    trimmed = samples[i0:i1]
    fade_n = min(SAMPLES_PER_SEC * fade_ms // 1000, len(trimmed) // 4)
    for k in range(fade_n):
        trimmed[k] = int(trimmed[k] * (k / fade_n))
        trimmed[-1 - k] = int(trimmed[-1 - k] * (k / fade_n))
    return trimmed.tobytes()


def stitch_phased_wav(
    phases: list[list[tuple[str, str, int]]],
    out_wav: Path,
    non_zh_rate: str,
    lead_ms: int = 140,
    tail_ms: int = 360,
    inter_phase_ms: int = 120,
) -> tuple[float, list[float]]:
    chunks: list[bytes] = []
    if lead_ms > 0:
        chunks.append(b"\x00\x00" * (SAMPLES_PER_SEC * lead_ms // 1000))

    byte_cursor = sum(len(c) for c in chunks)
    phase_end_times: list[float] = []

    for p_idx, lines in enumerate(phases):
        for idx, (voice, text, pause_ms) in enumerate(lines):
            rate = "+4%" if voice == VOICE_ZH else non_zh_rate
            wav_p = synth_segment_wav(voice, text, rate=rate)
            with wave.open(str(wav_p), "rb") as w:
                assert w.getnchannels() == 1 and w.getsampwidth() == 2 and w.getframerate() == SAMPLES_PER_SEC
                pcm = trim_pcm_silence(w.readframes(w.getnframes()))
            chunks.append(pcm)
            byte_cursor += len(pcm)
            if pause_ms > 0 and idx < len(lines) - 1:
                sil = b"\x00\x00" * (SAMPLES_PER_SEC * pause_ms // 1000)
                chunks.append(sil)
                byte_cursor += len(sil)
        if p_idx < len(phases) - 1 and inter_phase_ms > 0:
            sil = b"\x00\x00" * (SAMPLES_PER_SEC * inter_phase_ms // 1000)
            chunks.append(sil)
            byte_cursor += len(sil)
        phase_end_times.append(byte_cursor / (2 * SAMPLES_PER_SEC))

    if tail_ms > 0:
        sil = b"\x00\x00" * (SAMPLES_PER_SEC * tail_ms // 1000)
        chunks.append(sil)
        byte_cursor += len(sil)
        phase_end_times[-1] = byte_cursor / (2 * SAMPLES_PER_SEC)

    raw = b"".join(chunks)
    with wave.open(str(out_wav), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(SAMPLES_PER_SEC)
        out.writeframes(raw)
    return byte_cursor / (2 * SAMPLES_PER_SEC), phase_end_times


def _smoothstep(x: float) -> float:
    t = max(0.0, min(1.0, x))
    return t * t * (3.0 - 2.0 * t)


def _append_hold_segments(segments: list[tuple[Path, float]], hold_img: Path, hold_dur: float) -> None:
    if hold_dur <= 0.016:
        return
    n_frames = max(1, int(round(hold_dur * FPS)))
    chunk = 3
    while n_frames > 0:
        take = min(chunk, n_frames)
        segments.append((hold_img, take / FPS))
        n_frames -= take


# ---------------------------------------------------------------------------
# Scene 1 & Scene 2 Animator (1:1 Aligned Brush-Calligraphy Strokes -> AI Illustration)
# ---------------------------------------------------------------------------

def render_component_synced_scene(
    char: str,
    lang: str,
    tag: str,
    crop_key: str,
    stroke_indices: list[int],
    comp_cfg: dict,
    art_comp: Image.Image,
    total_dur: float,
    t_draw_end: float,
) -> tuple[list[tuple[Path, float]], dict[str, Path]]:
    center_size = 560
    mx0 = (W - center_size) // 2
    my0 = 416

    sdata = build_brush_stroke_masks(char, crop_key, center_size, stroke_indices=stroke_indices)
    n_strokes = sdata["n"]
    art_tile = _build_aligned_illustration_tile(art_comp, center_size)
    completed_strokes_tile = _render_char_strokes_tile(sdata, n_strokes - 1, 1.0, all_done=True)

    mini_size = 114
    mini_gap = 20
    mini_tiles = _build_static_stroke_strip_tiles(char, crop_key, stroke_indices, mini_size)
    strip_w = n_strokes * mini_size + (n_strokes - 1) * mini_gap
    sx0 = (W - strip_w) // 2
    sy0 = 1344

    base = Image.new("RGB", (W, H), BG_COLOR)
    d = ImageDraw.Draw(base)
    f_badge = load_latin(25, "demi")
    f_pinyin = load_latin(86, "bold")
    f_tone = load_latin(30, "demi")
    f_meaning = load_latin(42, "bold")
    f_pill = load_latin(22, "bold")
    f_origin = load_latin(33, "medium")
    f_origin_cjk = load_cjk(33)

    draw_simple_pill(
        d, W // 2, 86, comp_cfg["scene_badge"], f_badge,
        comp_cfg["color"], (255, 255, 255), step_num=comp_cfg["step"],
    )
    draw_brush_hero_with_pinyin(
        base, W // 2, 222,
        char, stroke_indices, 188, comp_cfg["color"],
        comp_cfg["pinyin"], f_pinyin, CHARCOAL, gap=36,
    )
    d = ImageDraw.Draw(base)
    draw_tone_pill(
        d, 352, comp_cfg["tone_label"], comp_cfg["tone"],
        comp_cfg["color"], comp_cfg["soft_bg"], f_tone,
    )

    x0, x1, y0, y1 = 64, W - 64, 1020, 1852
    d.rounded_rectangle([x0, y0, x1, y1], radius=36, fill=CARD_BG, outline=CARD_BORDER, width=3)
    draw_segments_centered(d, 1096, [(comp_cfg["meaning_full"], f_meaning, f_origin_cjk, comp_cfg["color"])])
    d.line([(x0 + 48, 1152), (x1 - 48, 1152)], fill=DIVIDER, width=3)
    draw_simple_pill(
        d, W // 2, 1214, comp_cfg["origin_pill"], f_pill,
        comp_cfg["soft_bg"], comp_cfg["color"], outline=comp_cfg["color"], pad_x=24, pad_y=8,
    )
    draw_segments_centered(d, 1296, [(comp_cfg["scene_badge"].split("·")[-1].strip(), load_latin(20, "bold"), f_origin_cjk, MUTED)])

    mini_boxes: list[tuple[int, int]] = []
    for k in range(n_strokes):
        bx = sx0 + k * (mini_size + mini_gap)
        base.paste(mini_tiles[k], (bx, sy0))
        mini_boxes.append((bx, sy0))

    orig_div_y = 1492
    d.line([(x0 + 48, orig_div_y), (x1 - 48, orig_div_y)], fill=DIVIDER, width=3)
    lines = wrap_mixed_lines(d, comp_cfg["scene_origin"], f_origin, f_origin_cjk, max_width=860)
    orig_top = 1602 + max(0, (2 - len(lines)) * 30)
    for idx, line in enumerate(lines[:3]):
        draw_segments_centered(d, orig_top + idx * 58, [(line, f_origin, f_origin_cjk, CHARCOAL)])

    frame_dir = ANIM_FRAMES_DIR / f"{char}_{lang}_{tag}"
    frame_dir.mkdir(parents=True, exist_ok=True)
    for old_f in frame_dir.glob("*.jpg"):
        old_f.unlink()

    n_draw_frames = max(24, int(round(t_draw_end * FPS)))
    part_b_dur = max(0.3, total_dur - t_draw_end)
    fade_dur = min(CROSSFADE_SEC, part_b_dur * 0.78)
    n_fade_frames = max(12, int(round(fade_dur * FPS)))

    segments: list[tuple[Path, float]] = []
    preview_dir = INTRO_ID_DIR if lang == "id" else INTRO_EN_DIR
    mid_draw_idx = n_draw_frames // 2
    mid_fade_idx = n_fade_frames // 2

    dt_draw = t_draw_end / n_draw_frames
    for f_idx in range(n_draw_frames):
        pos = (f_idx + 0.5) / n_draw_frames * n_strokes
        s_idx = min(n_strokes - 1, int(pos))
        frac = min(1.0, max(0.06, pos - s_idx))

        frame = base.copy()
        center_tile = _render_char_strokes_tile(sdata, s_idx, frac, all_done=False)
        frame.paste(center_tile, (mx0, my0))
        fd = ImageDraw.Draw(frame)
        bx, by = mini_boxes[s_idx]
        fd.rounded_rectangle([bx - 2, by - 2, bx + mini_size + 2, by + mini_size + 2], radius=14, outline=sdata["colors"][s_idx], width=4)

        out_p = frame_dir / f"a_{f_idx:04d}.jpg"
        frame.save(out_p, quality=93)
        segments.append((out_p, dt_draw))
        if f_idx == mid_draw_idx:
            frame.save(preview_dir / f"{char}_{tag}_write.png")
            frame.save(EXEMPLARS_DIR / f"{char}_{tag}_write_{lang}.png")

    dt_fade = fade_dur / n_fade_frames
    for f_idx in range(n_fade_frames):
        alpha = _smoothstep((f_idx + 1) / n_fade_frames)
        frame = base.copy()
        blended = Image.blend(completed_strokes_tile, art_tile, alpha)
        frame.paste(blended, (mx0, my0))
        fd = ImageDraw.Draw(frame)
        for bx, by in mini_boxes:
            fd.rounded_rectangle([bx, by, bx + mini_size, by + mini_size], radius=12, outline=comp_cfg["color"], width=2)

        out_p = frame_dir / f"b_{f_idx:04d}.jpg"
        frame.save(out_p, quality=93)
        segments.append((out_p, dt_fade))
        if f_idx == mid_fade_idx:
            frame.save(preview_dir / f"{char}_{tag}_morph.png")
            frame.save(EXEMPLARS_DIR / f"{char}_{tag}_morph_{lang}.png")

    final_frame = base.copy()
    final_frame.paste(art_tile, (mx0, my0))
    fd = ImageDraw.Draw(final_frame)
    for bx, by in mini_boxes:
        fd.rounded_rectangle([bx, by, bx + mini_size, by + mini_size], radius=12, outline=comp_cfg["color"], width=2)
    hold_p = frame_dir / "hold.jpg"
    final_frame.save(hold_p, quality=94)
    final_png = preview_dir / f"{char}_{tag}_final.png"
    final_frame.save(final_png)

    hold_dur = max(0.0, total_dur - (t_draw_end + fade_dur))
    _append_hold_segments(segments, hold_p, hold_dur)

    return segments, {
        "write": preview_dir / f"{char}_{tag}_write.png",
        "morph": preview_dir / f"{char}_{tag}_morph.png",
        "final": final_png,
    }


# ---------------------------------------------------------------------------
# Scene 3 Synced Animator (1:1 Aligned Brush Character -> AI Illustration)
# ---------------------------------------------------------------------------

def render_combined_synced_scene(
    char: str,
    lang: str,
    spec: dict,
    lcfg: dict,
    artworks: dict[str, Image.Image],
    total_dur: float,
    t_p1: float,
    t_p2: float,
) -> tuple[list[tuple[Path, float]], Path, dict[str, Path]]:
    center_size = 530
    frame_box = (275, 706, 805, 1236)
    mx0, my0 = frame_box[0], frame_box[1]

    sdata = build_brush_stroke_masks(char, "combined", center_size, stroke_indices=None)
    n_strokes = sdata["n"]
    split = spec["stroke_split"]

    art_tile = _build_aligned_illustration_tile(artworks["combined"], center_size)
    completed_strokes_tile = _render_char_strokes_tile(sdata, n_strokes - 1, 1.0, all_done=True)

    mini_size = 94 if n_strokes <= 6 else 78
    mini_gap = 20 if n_strokes <= 6 else 12
    mini_tiles = _build_static_stroke_strip_tiles(char, "combined", None, mini_size)
    strip_w = n_strokes * mini_size + (n_strokes - 1) * mini_gap
    sx0 = (W - strip_w) // 2
    sy0 = 1726 if n_strokes <= 6 else 1738

    base = Image.new("RGB", (W, H), BG_COLOR)
    d = ImageDraw.Draw(base)

    f_badge = load_latin(23, "demi")
    f_hero_py = load_latin(74, "bold")
    f_tone = load_latin(27, "demi")
    f_meaning = load_latin(38, "bold")
    f_hook_pill = load_latin(21, "bold")
    f_hook = load_latin(33, "medium")
    f_hook_cjk = load_cjk(33)

    draw_simple_pill(d, W // 2, 58, lcfg["badge_final"], f_badge, FOREST, (255, 255, 255))
    draw_brush_hero_with_pinyin(
        base, W // 2, 152,
        char, None, 126, CHARCOAL,
        spec["target_pinyin"], f_hero_py, TERRACOTTA, gap=32,
    )
    d = ImageDraw.Draw(base)
    tone_col = TERRACOTTA if spec["target_tone"] == 4 else FOREST
    tone_bg = SOFT_TERRACOTTA if spec["target_tone"] == 4 else SOFT_FOREST
    draw_tone_pill(d, 260, lcfg["tone_label"], spec["target_tone"], tone_col, tone_bg, f_tone)

    _draw_mini_origin_card(base, (54, 304, 512, 638), lcfg["c1"], artworks["comp1"], char, spec["c1_indices"])
    _draw_mini_origin_card(base, (568, 304, 1026, 638), lcfg["c2"], artworks["comp2"], char, spec["c2_indices"])
    d = ImageDraw.Draw(base)

    d.ellipse([516, 446, 564, 494], fill=CHARCOAL)
    f_plus = load_latin(36, "bold")
    bb_p = d.textbbox((0, 0), "+", font=f_plus)
    d.text((540 - (bb_p[2] - bb_p[0]) // 2 - bb_p[0], 470 - (bb_p[3] - bb_p[1]) // 2 - bb_p[1]), "+", font=f_plus, fill=(255, 255, 255))

    draw_simple_pill(
        d, W // 2, 672, lcfg["combined_pill"], load_latin(21, "bold"),
        SOFT_FOREST, FOREST, outline=FOREST, pad_x=22, pad_y=6, step_num=3,
    )

    cx0, cx1, cy0, cy1 = 54, W - 54, 1264, 1858
    d.rounded_rectangle([cx0, cy0, cx1, cy1], radius=34, fill=CARD_BG, outline=CARD_BORDER, width=3)

    draw_segments_centered(d, 1326, [(lcfg["meaning"], f_meaning, f_hook_cjk, FOREST)])
    d.line([(cx0 + 44, 1372), (cx1 - 44, 1372)], fill=DIVIDER, width=3)
    draw_simple_pill(
        d, W // 2, 1424, lcfg["hook_pill"], f_hook_pill,
        SOFT_TERRACOTTA, TERRACOTTA, outline=TERRACOTTA, pad_x=22, pad_y=7, step_num=3,
    )
    draw_segments_centered(d, 1502, [(lcfg["hook_lines"][0], f_hook, f_hook_cjk, CHARCOAL)])
    draw_segments_centered(d, 1558, [(lcfg["hook_lines"][1], f_hook, f_hook_cjk, CHARCOAL)])

    d.line([(cx0 + 44, 1626), (cx1 - 44, 1626)], fill=DIVIDER, width=2)
    draw_segments_centered(
        d, 1666,
        [("URUTAN GURATAN  (1 – " + str(n_strokes) + ")" if lang == "id" else f"STROKE ORDER  (1 – {n_strokes})", load_latin(20, "bold"), f_hook_cjk, MUTED)],
    )

    mini_boxes: list[tuple[int, int]] = []
    for k in range(n_strokes):
        bx = sx0 + k * (mini_size + mini_gap)
        base.paste(mini_tiles[k], (bx, sy0))
        mini_boxes.append((bx, sy0))

    frame_dir = ANIM_FRAMES_DIR / f"{char}_{lang}_s3"
    frame_dir.mkdir(parents=True, exist_ok=True)
    for old_f in frame_dir.glob("*.jpg"):
        old_f.unlink()

    preview_dir = INTRO_ID_DIR if lang == "id" else INTRO_EN_DIR
    segments: list[tuple[Path, float]] = []

    p1_dur = max(0.4, t_p1)
    p2_dur = max(0.4, t_p2 - t_p1)
    p3_dur = max(0.4, total_dur - t_p2)
    fade_dur = min(CROSSFADE_SEC, p3_dur * 0.65)

    n_p1 = max(12, int(round(p1_dur * FPS)))
    n_p2 = max(12, int(round(p2_dur * FPS)))
    n_fade = max(12, int(round(fade_dur * FPS)))

    def save_write_range(tag_prefix: str, n_frames: int, dur_sec: float, s_start: int, s_end: int, preview_name: str, ex_name: str) -> None:
        dt = dur_sec / n_frames
        count = s_end - s_start
        for f_idx in range(n_frames):
            pos = s_start + (f_idx + 0.5) / n_frames * count
            s_idx = min(s_end - 1, max(s_start, int(pos)))
            frac = min(1.0, max(0.06, pos - s_idx))

            frame = base.copy()
            tile = _render_char_strokes_tile(sdata, s_idx, frac, all_done=False)
            frame.paste(tile, (mx0, my0))
            fd = ImageDraw.Draw(frame)
            bx, by = mini_boxes[s_idx]
            fd.rounded_rectangle([bx - 2, by - 2, bx + mini_size + 2, by + mini_size + 2], radius=10, outline=sdata["colors"][s_idx], width=3)

            out_p = frame_dir / f"{tag_prefix}_{f_idx:04d}.jpg"
            frame.save(out_p, quality=93)
            segments.append((out_p, dt))
            if f_idx == n_frames // 2:
                frame.save(preview_dir / preview_name)
                frame.save(EXEMPLARS_DIR / ex_name)

    save_write_range("p1", n_p1, p1_dur, 0, split, f"{char}_s3_write_p1.png", f"{char}_s3_write_p1_{lang}.png")
    save_write_range("p2", n_p2, p2_dur, split, n_strokes, f"{char}_s3_write_p2.png", f"{char}_s3_write_p2_{lang}.png")

    dt_fade = fade_dur / n_fade
    for f_idx in range(n_fade):
        alpha = _smoothstep((f_idx + 1) / n_fade)
        frame = base.copy()
        blended = Image.blend(completed_strokes_tile, art_tile, alpha)
        frame.paste(blended, (mx0, my0))
        fd = ImageDraw.Draw(frame)
        for idx_b, (bx, by) in enumerate(mini_boxes):
            fd.rounded_rectangle([bx, by, bx + mini_size, by + mini_size], radius=10, outline=sdata["colors"][idx_b], width=2)

        out_p = frame_dir / f"p3_{f_idx:04d}.jpg"
        frame.save(out_p, quality=93)
        segments.append((out_p, dt_fade))
        if f_idx == n_fade // 2:
            frame.save(preview_dir / f"{char}_s3_morph.png")
            frame.save(EXEMPLARS_DIR / f"{char}_s3_morph_{lang}.png")

    final_frame = base.copy()
    final_frame.paste(art_tile, (mx0, my0))
    fd = ImageDraw.Draw(final_frame)
    for idx_b, (bx, by) in enumerate(mini_boxes):
        fd.rounded_rectangle([bx, by, bx + mini_size, by + mini_size], radius=10, outline=sdata["colors"][idx_b], width=2)

    hold_p = frame_dir / "hold.jpg"
    final_frame.save(hold_p, quality=94)

    card_dir = CARDS_ID_DIR if lang == "id" else CARDS_EN_DIR
    card_path = card_dir / f"{char}.png"
    final_frame.save(card_path, quality=95)
    final_frame.save(card_dir / f"{char}_card.png", quality=95)
    final_frame.save(EXEMPLARS_DIR / f"{char}_card_{lang}.png", quality=95)

    hold_dur = max(0.0, total_dur - (p1_dur + p2_dur + fade_dur))
    _append_hold_segments(segments, hold_p, hold_dur)

    return segments, card_path, {
        "p1": preview_dir / f"{char}_s3_write_p1.png",
        "p2": preview_dir / f"{char}_s3_write_p2.png",
        "morph": preview_dir / f"{char}_s3_morph.png",
        "card": card_path,
    }


def build_exemplar_for_char(char: str, lang: str, artworks: dict[str, Image.Image]) -> dict:
    spec = EXEMPLARS[char]
    lcfg = spec[lang]
    code = f"{spec['target_pinyin']}_{lang}_v8_brush"

    candidate_rates = ("+2%", "-4%", "-9%", "+8%") if lang == "id" else ("-4%", "-9%", "-14%", "+2%")
    chosen = None

    for non_zh_rate in candidate_rates:
        s1_wav = AUDIO_CACHE_DIR / f"{code}_{non_zh_rate}_s1.wav"
        s2_wav = AUDIO_CACHE_DIR / f"{code}_{non_zh_rate}_s2.wav"
        s3_wav = AUDIO_CACHE_DIR / f"{code}_{non_zh_rate}_s3.wav"

        s1_dur, s1_times = stitch_phased_wav(
            [lcfg["c1"]["audio_part_a"], lcfg["c1"]["audio_part_b"]],
            s1_wav, non_zh_rate, lead_ms=140, tail_ms=520, inter_phase_ms=140,
        )
        s2_dur, s2_times = stitch_phased_wav(
            [lcfg["c2"]["audio_part_a"], lcfg["c2"]["audio_part_b"]],
            s2_wav, non_zh_rate, lead_ms=140, tail_ms=520, inter_phase_ms=140,
        )
        s3_dur, s3_times = stitch_phased_wav(
            [lcfg["s3_phase1"], lcfg["s3_phase2"], lcfg["s3_phase3"]],
            s3_wav, non_zh_rate, lead_ms=140, tail_ms=820, inter_phase_ms=110,
        )
        total = s1_dur + s2_dur + s3_dur
        chosen = (non_zh_rate, s1_wav, s1_dur, s1_times, s2_wav, s2_dur, s2_times, s3_wav, s3_dur, s3_times, total)
        if 20.0 <= total <= 30.0:
            break

    assert chosen is not None
    non_zh_rate, s1_wav, s1_dur, s1_times, s2_wav, s2_dur, s2_times, s3_wav, s3_dur, s3_times, total = chosen

    if total < 20.0:
        extra_ms = int((20.8 - total) * 1000)
        p1 = extra_ms // 3
        p2 = extra_ms // 3
        p3 = extra_ms - p1 - p2
        s1_dur, s1_times = stitch_phased_wav(
            [lcfg["c1"]["audio_part_a"], lcfg["c1"]["audio_part_b"]],
            s1_wav, non_zh_rate, lead_ms=150, tail_ms=520 + p1, inter_phase_ms=140,
        )
        s2_dur, s2_times = stitch_phased_wav(
            [lcfg["c2"]["audio_part_a"], lcfg["c2"]["audio_part_b"]],
            s2_wav, non_zh_rate, lead_ms=150, tail_ms=520 + p2, inter_phase_ms=140,
        )
        s3_dur, s3_times = stitch_phased_wav(
            [lcfg["s3_phase1"], lcfg["s3_phase2"], lcfg["s3_phase3"]],
            s3_wav, non_zh_rate, lead_ms=150, tail_ms=820 + p3, inter_phase_ms=110,
        )
        total = s1_dur + s2_dur + s3_dur

    assert 20.0 <= total <= 30.0, f"3-scene duration {total:.2f}s out of 20..30s for {char} ({lang})"

    s1_segs, _ = render_component_synced_scene(
        char, lang, "s1", "comp1", spec["c1_indices"], lcfg["c1"], artworks["comp1"],
        total_dur=s1_dur, t_draw_end=s1_times[0],
    )
    s2_segs, _ = render_component_synced_scene(
        char, lang, "s2", "comp2", spec["c2_indices"], lcfg["c2"], artworks["comp2"],
        total_dur=s2_dur, t_draw_end=s2_times[0],
    )
    s3_segs, card_path, _ = render_combined_synced_scene(
        char, lang, spec, lcfg, artworks,
        total_dur=s3_dur, t_p1=s3_times[0], t_p2=s3_times[1],
    )

    scene_mp4s: list[Path] = []
    for tag, wav_p, segs in (("s1", s1_wav, s1_segs), ("s2", s2_wav, s2_segs), ("s3", s3_wav, s3_segs)):
        seg_mp4 = AUDIO_CACHE_DIR / f"{code}_{tag}.mp4"
        args = [f"{p}:{dt:.6f}" for p, dt in segs]
        subprocess.run([str(RENDER_MP4), str(seg_mp4), str(wav_p), *args], check=True)
        scene_mp4s.append(seg_mp4)

    out_dir = VIDEOS_ID_DIR if lang == "id" else VIDEOS_EN_DIR
    out_video = out_dir / f"{char}.mp4"
    subprocess.run([str(CONCAT_MP4), str(out_video), *(str(p) for p in scene_mp4s)], check=True)

    return {
        "char": char,
        "lang": lang,
        "rate": non_zh_rate,
        "card": str(card_path),
        "video": str(out_video),
        "durations": [round(s1_dur, 2), round(s2_dur, 2), round(s3_dur, 2)],
        "timestamps": {
            "s1_draw_end": round(s1_times[0], 2),
            "s2_draw_end": round(s2_times[0], 2),
            "s3_p1_end": round(s3_times[0], 2),
            "s3_p2_end": round(s3_times[1], 2),
        },
        "total": round(total, 2),
    }


def main() -> None:
    for char in ("好", "看"):
        artworks = build_aligned_ai_artworks(char)
        for lang in ("id", "en"):
            res = build_exemplar_for_char(char, lang, artworks)
            print(
                f"[{char}][{lang.upper()}] rate={res['rate']} | Card: {res['card']} | "
                f"Video: {res['video']} ({res['total']}s = {res['durations']}) | sync={res['timestamps']}"
            )


if __name__ == "__main__":
    main()
