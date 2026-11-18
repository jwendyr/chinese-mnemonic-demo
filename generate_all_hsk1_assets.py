#!/usr/bin/env python3
"""Generate stroke templates, character mnemonic cards, and multi-char vocab cards for all HSK 1 items."""

import json
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

WORKDIR = Path("/Volumes/App/Workspace/chinese-mnemonic-demo")
TEMPLATES_DIR = WORKDIR / "templates"
ILLUS_DIR = WORKDIR / "illustrations"
COMPOSED_DIR = WORKDIR / "illustrations_composed"
SPRITES_DIR = WORKDIR / "sprites"
CARDS_DIR = WORKDIR / "cards"
VOCAB_CARDS_DIR = WORKDIR / "vocab_cards"
VIDEOS_DIR = WORKDIR / "videos"
CHAR_VIDEOS_DIR = WORKDIR / "char_videos"

for d in (TEMPLATES_DIR, ILLUS_DIR, COMPOSED_DIR, CARDS_DIR, VOCAB_CARDS_DIR, VIDEOS_DIR, CHAR_VIDEOS_DIR):
    d.mkdir(parents=True, exist_ok=True)

W, H = 1080, 1920
BG_COLOR = (250, 246, 240)       # #FAF6F0
SOFT_RING = (242, 234, 221)      # subtle warm disc
CHARCOAL = (43, 45, 66)          # #2B2D42
TERRACOTTA = (217, 83, 79)       # #D9534F
FOREST = (46, 111, 94)           # #2E6F5E
MUSTARD = (196, 138, 52)         # warm ochre accent
MUTED = (108, 105, 100)
CARD_BG = (255, 253, 249)
CARD_BORDER = (228, 221, 210)

FONT_CJK = "/System/Library/Fonts/STHeiti Medium.ttc"
FONT_LATIN = "/System/Library/Fonts/Avenir Next.ttc"


def load_font(path: str, size: int, index: int = 0) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size, index=index)


def is_cjk(ch: str) -> bool:
    cp = ord(ch)
    return (
        (0x2E80 <= cp <= 0x2FDF)
        or (0x31C0 <= cp <= 0x31EF)
        or (0x3400 <= cp <= 0x4DBF)
        or (0x4E00 <= cp <= 0x9FFF)
        or (0xF900 <= cp <= 0xFAFF)
        or (0x20000 <= cp <= 0x2CEAF)
    )


def split_runs(text: str) -> list[tuple[str, bool]]:
    if not text:
        return []
    runs: list[tuple[str, bool]] = []
    cur = text[0]
    cur_flag = is_cjk(text[0])
    for ch in text[1:]:
        flag = is_cjk(ch)
        if flag == cur_flag:
            cur += ch
        else:
            runs.append((cur, cur_flag))
            cur = ch
            cur_flag = flag
    runs.append((cur, cur_flag))
    return runs


def measure_mixed(
    draw: ImageDraw.ImageDraw,
    text: str,
    latin_font: ImageFont.FreeTypeFont,
    cjk_font: ImageFont.FreeTypeFont,
) -> tuple[int, int, list]:
    runs = split_runs(text)
    total_w = 0
    max_h = 0
    metrics = []
    for idx, (sub, flag) in enumerate(runs):
        f = cjk_font if flag else latin_font
        bb = draw.textbbox((0, 0), sub, font=f)
        w_sub = bb[2] - bb[0]
        h_sub = bb[3] - bb[1]
        total_w += w_sub + (2 if idx < len(runs) - 1 else 0)
        max_h = max(max_h, h_sub)
        metrics.append((sub, f, bb, w_sub, h_sub))
    return total_w, max_h, metrics


def draw_mixed_centered(
    draw: ImageDraw.ImageDraw,
    y: int,
    text: str,
    latin_font: ImageFont.FreeTypeFont,
    cjk_font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int],
) -> int:
    total_w, max_h, metrics = measure_mixed(draw, text, latin_font, cjk_font)
    cx = (W - total_w) // 2
    for sub, f, bb, w_sub, h_sub in metrics:
        draw.text((cx - bb[0], y + (max_h - h_sub) // 2 - bb[1]), sub, font=f, fill=fill)
        cx += w_sub + 2
    return max_h


def wrap_mixed_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    latin_font: ImageFont.FreeTypeFont,
    cjk_font: ImageFont.FreeTypeFont,
    max_width: int,
) -> list[str]:
    words = text.split(" ")
    lines: list[str] = []
    cur = ""
    for w in words:
        cand = f"{cur} {w}".strip() if cur else w
        tw, _, _ = measure_mixed(draw, cand, latin_font, cjk_font)
        if tw <= max_width or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_pill(
    draw: ImageDraw.ImageDraw,
    cy: int,
    text: str,
    latin_font: ImageFont.FreeTypeFont,
    cjk_font: ImageFont.FreeTypeFont,
    bg_color: tuple[int, int, int],
    fg_color: tuple[int, int, int],
    pad_x: int = 34,
    pad_y: int = 14,
) -> None:
    tw, th, metrics = measure_mixed(draw, text, latin_font, cjk_font)
    pw = tw + pad_x * 2
    ph = th + pad_y * 2
    x0 = (W - pw) // 2
    y0 = cy - ph // 2
    draw.rounded_rectangle([x0, y0, x0 + pw, y0 + ph], radius=ph // 2, fill=bg_color)
    cx = (W - tw) // 2
    ty = cy - th // 2
    for sub, f, bb, w_sub, h_sub in metrics:
        draw.text((cx - bb[0], ty + (th - h_sub) // 2 - bb[1]), sub, font=f, fill=fg_color)
        cx += w_sub + 2


def draw_bottom_card(
    draw: ImageDraw.ImageDraw,
    top_y: int,
    lines: list[tuple[str, ImageFont.FreeTypeFont, ImageFont.FreeTypeFont, tuple[int, int, int]]],
    bottom_margin: int = 90,
) -> None:
    x0, x1 = 68, W - 68
    y1 = H - bottom_margin
    draw.rounded_rectangle(
        [x0, top_y, x1, y1],
        radius=36,
        fill=CARD_BG,
        outline=CARD_BORDER,
        width=3,
    )
    heights = []
    for txt, lf, cf, _ in lines:
        _, lh, _ = measure_mixed(draw, txt, lf, cf)
        heights.append(max(lh, 28))
    gap = 20
    total_h = sum(heights) + gap * (len(lines) - 1)
    cur_y = top_y + max(24, ((y1 - top_y) - total_h) // 2)
    for (txt, lf, cf, col), lh in zip(lines, heights):
        draw_mixed_centered(draw, cur_y, txt, lf, cf, col)
        cur_y += lh + gap


def seed_existing_assets() -> None:
    pairs = [
        (WORKDIR / "xiu_illustration.jpg", ILLUS_DIR / "休.jpg"),
        (WORKDIR / "xi_illustration.jpg", ILLUS_DIR / "息.jpg"),
        (WORKDIR / "xiuxi_mnemonic.mp4", VIDEOS_DIR / "休息.mp4"),
    ]
    for src, dst in pairs:
        if src.exists() and not dst.exists():
            shutil.copy2(src, dst)


def make_template(ch: str, f_template: ImageFont.FreeTypeFont) -> Path:
    out_path = TEMPLATES_DIR / f"{ch}.png"
    if out_path.exists():
        return out_path
    im = Image.new("RGB", (W, H), BG_COLOR)
    d = ImageDraw.Draw(im)
    bb = d.textbbox((0, 0), ch, font=f_template)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    x = (W - tw) // 2 - bb[0]
    y = (H - th) // 2 - bb[1] - 20
    d.text((x, y), ch, font=f_template, fill=CHARCOAL)
    im.save(out_path)
    return out_path


def _hex_to_rgb(hx: str) -> tuple[int, int, int]:
    hx = hx.lstrip("#")
    return tuple(int(hx[i:i+2], 16) for i in (0, 2, 4))


def make_char_center_tile(
    ch: str,
    accent: tuple[int, int, int],
    f_big: ImageFont.FreeTypeFont,
    char_info: dict | None = None,
) -> Image.Image:
    """Return a 760x760 illustration tile (Nano-Banana AI crop if present, else Actor-Sprite composed tile)."""
    ai_path = ILLUS_DIR / f"{ch}.jpg"
    if ai_path.exists():
        im = Image.open(ai_path).convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
        im = im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=110, threshold=3))
        return im.crop((100, 460, 980, 1340)).resize((760, 760), Image.Resampling.LANCZOS)

    tile = Image.new("RGBA", (760, 760), BG_COLOR + (255,))
    d = ImageDraw.Draw(tile)
    actors = (char_info or {}).get("actors", [])
    layout = (char_info or {}).get("layout", "Tunggal (独体)")
    primary_col = _hex_to_rgb(actors[0]["color_hex"]) if actors else accent

    # Soft warm circular halo behind Hanzi
    d.ellipse([90, 90, 670, 670], fill=SOFT_RING + (255,))
    d.ellipse([112, 112, 648, 648], outline=primary_col + (255,), width=4)

    # Draw crisp central Hanzi (scaled cleanly so Actor Sprites frame it without overlap)
    f_hanzi = ImageFont.truetype(FONT_CJK, 370, index=0) if actors else f_big
    bb = d.textbbox((0, 0), ch, font=f_hanzi)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    hx = (760 - tw) // 2 - bb[0]
    hy = (760 - th) // 2 - bb[1] - 8
    d.text((hx, hy), ch, font=f_hanzi, fill=CHARCOAL + (255,))

    # Position 1..3 canonical Actor Sprites according to spatial layout kaidah
    sprites_imgs = []
    for a in actors[:3]:
        sp_path = WORKDIR / a["sprite_path"]
        if sp_path.exists():
            sprites_imgs.append(Image.open(sp_path).convert("RGBA"))

    if len(sprites_imgs) == 1:
        sp = sprites_imgs[0].resize((188, 188), Image.Resampling.LANCZOS)
        tile.paste(sp, (540, 28), sp)
    elif len(sprites_imgs) == 2:
        if "Kiri" in layout:
            pos = [(14, 280), (558, 280)]
        elif "Atas" in layout:
            pos = [(28, 22), (544, 548)]
        else:
            pos = [(24, 24), (544, 544)]
        for sp_raw, (px, py) in zip(sprites_imgs, pos):
            sp = sp_raw.resize((188, 188), Image.Resampling.LANCZOS)
            tile.paste(sp, (px, py), sp)
    elif len(sprites_imgs) >= 3:
        pos = [(26, 22), (554, 22), (295, 560)]
        for sp_raw, (px, py) in zip(sprites_imgs[:3], pos):
            sp = sp_raw.resize((172, 172), Image.Resampling.LANCZOS)
            tile.paste(sp, (px, py), sp)

    # Save full 1080x1920 sprite-composed illustration for audit & video reuse
    full_comp = Image.new("RGB", (W, H), BG_COLOR)
    full_comp.paste(tile.convert("RGB"), ((W - 760) // 2, 490))
    full_comp.save(COMPOSED_DIR / f"{ch}.png")

    return tile.convert("RGB")


def generate_all() -> dict:
    seed_existing_assets()

    chars_data = json.loads((WORKDIR / "hsk1_characters.json").read_text(encoding="utf-8"))
    vocab_data = json.loads((WORKDIR / "hsk1_vocab.json").read_text(encoding="utf-8"))
    actors_data = json.loads((WORKDIR / "actors_catalog.json").read_text(encoding="utf-8"))
    char_map = {c["char"]: c for c in chars_data}

    f_template = load_font(FONT_CJK, 760, index=0)
    f_tile_big = load_font(FONT_CJK, 440, index=0)
    f_hanzi_top = load_font(FONT_CJK, 170, index=0)
    f_pinyin = load_font(FONT_LATIN, 56, index=6)
    f_pill = load_font(FONT_LATIN, 26, index=6)
    f_pill_cjk = load_font(FONT_CJK, 26, index=0)
    f_sub_bold = load_font(FONT_LATIN, 36, index=6)
    f_sub_bold_cjk = load_font(FONT_CJK, 36, index=0)
    f_sub = load_font(FONT_LATIN, 32, index=0)
    f_sub_cjk = load_font(FONT_CJK, 32, index=0)
    f_small = load_font(FONT_LATIN, 26, index=0)
    f_small_cjk = load_font(FONT_CJK, 26, index=0)

    accents = [TERRACOTTA, FOREST, MUSTARD]
    ai_chars = []

    # 1. Templates + Individual Character Cards
    for idx, c in enumerate(chars_data):
        ch = c["char"]
        make_template(ch, f_template)
        accent = accents[idx % len(accents)]
        has_ai = (ILLUS_DIR / f"{ch}.jpg").exists()
        if has_ai:
            ai_chars.append(ch)
            card = Image.open(ILLUS_DIR / f"{ch}.jpg").convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
            card = card.filter(ImageFilter.UnsharpMask(radius=1.2, percent=110, threshold=3))
        else:
            card = Image.new("RGB", (W, H), BG_COLOR)
            tile = make_char_center_tile(ch, accent, f_tile_big, char_info=c)
            card.paste(tile, ((W - 760) // 2, 490))

        d = ImageDraw.Draw(card)
        badge = f"DEMO · #{c['id']}" if c.get("is_bonus_demo") else f"HSK 1 · #{c['id']}"
        draw_pill(d, 90, badge, f_pill, f_pill_cjk, accent, (255, 255, 255))
        draw_mixed_centered(d, 140, ch, f_hanzi_top, f_hanzi_top, CHARCOAL)
        draw_mixed_centered(d, 330, c["pinyin"], f_pinyin, f_pinyin, TERRACOTTA)
        draw_mixed_centered(d, 415, f"{c.get('layout', '')} · {c['radicals']}", f_small, f_small_cjk, MUTED)

        wrapped_story = wrap_mixed_text(d, c["mnemonic_id"], f_sub, f_sub_cjk, 890)
        card_lines = [
            (f"Arti: {c['meaning_id'].capitalize()}", f_sub_bold, f_sub_bold_cjk, FOREST),
        ]
        for line in wrapped_story[:4]:
            card_lines.append((line, f_sub, f_sub_cjk, CHARCOAL))
        draw_bottom_card(d, 1415, card_lines, bottom_margin=75)

        card.save(CARDS_DIR / f"{ch}_card.png")

    # 2. Multi-character & Single-character Vocab Cards (all 155 words)
    for v in vocab_data:
        word = v["word"]
        chars = v["chars"]
        if len(chars) == 1:
            src_card = CARDS_DIR / f"{chars[0]}_card.png"
            dst_card = VOCAB_CARDS_DIR / f"{word}_card.png"
            shutil.copy2(src_card, dst_card)
            continue

        card = Image.new("RGB", (W, H), BG_COLOR)
        d = ImageDraw.Draw(card)
        draw_pill(d, 90, f"HSK 1 #{v['id']} · {v['category'].upper()}", f_pill, f_pill_cjk, TERRACOTTA, (255, 255, 255))
        word_font = f_hanzi_top if len(chars) <= 2 else load_font(FONT_CJK, 138, index=0)
        draw_mixed_centered(d, 145, word, word_font, word_font, CHARCOAL)
        draw_mixed_centered(d, 340, v["pinyin"], f_pinyin, f_pinyin, FOREST)

        n = len(chars)
        if n == 2:
            tile_sz = 440
            gap = 48
            start_x = (W - (2 * tile_sz + gap)) // 2
            y_tile = 500
        else:
            tile_sz = 310
            gap = 28
            start_x = (W - (3 * tile_sz + 2 * gap)) // 2
            y_tile = 540

        for i, ch in enumerate(chars):
            c_info = char_map[ch]
            tile = make_char_center_tile(ch, accents[i % len(accents)], f_tile_big, char_info=c_info).resize(
                (tile_sz, tile_sz), Image.Resampling.LANCZOS
            )
            tx = start_x + i * (tile_sz + gap)
            card.paste(tile, (tx, y_tile))
            d.rounded_rectangle([tx, y_tile, tx + tile_sz, y_tile + tile_sz], radius=24, outline=CARD_BORDER, width=3)
            label_y = y_tile + tile_sz + 18
            lbl = f"{ch} ({c_info['pinyin']})"
            tw, _, metrics = measure_mixed(d, lbl, f_sub_bold, f_sub_bold_cjk)
            cx = tx + (tile_sz - tw) // 2
            for sub, f, bb, w_sub, _ in metrics:
                d.text((cx - bb[0], label_y - bb[1]), sub, font=f, fill=CHARCOAL)
                cx += w_sub + 2
            mean_lbl = c_info["meaning_id"]
            mw, _, m_metrics = measure_mixed(d, mean_lbl, f_small, f_small_cjk)
            if mw > tile_sz:
                mean_lbl = mean_lbl.split("/")[0].strip()
                mw, _, m_metrics = measure_mixed(d, mean_lbl, f_small, f_small_cjk)
            cx2 = tx + (tile_sz - mw) // 2
            for sub, f, bb, w_sub, _ in m_metrics:
                d.text((cx2 - bb[0], label_y + 48 - bb[1]), sub, font=f, fill=TERRACOTTA)
                cx2 += w_sub + 2

        summary_lines = [
            (f"Arti: {v['meaning_id'].capitalize()}", f_sub_bold, f_sub_bold_cjk, FOREST),
        ]
        for ch in chars:
            ci = char_map[ch]
            short_m = f"{ch}: {ci['radicals']} — {ci['mnemonic_id']}"
            wrapped = wrap_mixed_text(d, short_m, f_small, f_small_cjk, 870)
            line_txt = wrapped[0] if len(wrapped) == 1 else f"{wrapped[0].rstrip(' ,—-')}…"
            summary_lines.append((line_txt, f_small, f_small_cjk, CHARCOAL))
        draw_bottom_card(d, 1340, summary_lines[:4], bottom_margin=80)
        card.save(VOCAB_CARDS_DIR / f"{word}_card.png")

    available_videos = sorted(p.stem for p in VIDEOS_DIR.glob("*.mp4"))
    available_char_videos = sorted(p.stem for p in CHAR_VIDEOS_DIR.glob("*.mp4"))
    available_videos_en = sorted(p.stem for p in (WORKDIR / "videos_en").glob("*.mp4"))
    available_char_videos_en = sorted(p.stem for p in (WORKDIR / "char_videos_en").glob("*.mp4"))
    manifest = {
        "vocab_count": len(vocab_data),
        "hsk1_unique_chars": sum(1 for c in chars_data if not c.get("is_bonus_demo")),
        "total_char_records": len(chars_data),
        "ai_illustrated_chars": sorted(set(ai_chars)),
        "composed_chars_count": len(list(COMPOSED_DIR.glob("*.png"))),
        "available_videos": available_videos,
        "available_char_videos": available_char_videos,
        "available_videos_en": available_videos_en,
        "available_char_videos_en": available_char_videos_en,
        "actors": actors_data,
        "chars": chars_data,
        "vocab": vocab_data,
    }
    (WORKDIR / "gallery_data.js").write_text(
        "window.HSK1_GALLERY_DATA = " + json.dumps(manifest, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )

    result = {
        "templates_count": len(list(TEMPLATES_DIR.glob("*.png"))),
        "composed_count": len(list(COMPOSED_DIR.glob("*.png"))),
        "char_cards_count": len(list(CARDS_DIR.glob("*.png"))),
        "vocab_cards_count": len(list(VOCAB_CARDS_DIR.glob("*.png"))),
        "ai_illustrated_chars": sorted(set(ai_chars)),
        "available_videos_count": len(available_videos),
        "available_char_videos_count": len(available_char_videos),
    }
    print(json.dumps(result, ensure_ascii=False))
    return result


if __name__ == "__main__":
    generate_all()
