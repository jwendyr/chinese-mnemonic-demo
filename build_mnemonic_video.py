#!/usr/bin/env python3
"""Build stroke-faithful Chineasy mnemonic cards and 9:16 video for 休息 (xiūxi) using neural edge-tts."""

import subprocess
import wave
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

WORKDIR = Path("/Volumes/App/Workspace/chinese-mnemonic-demo")
IMG_XIU = WORKDIR / "xiu_illustration.jpg"
IMG_XI = WORKDIR / "xi_illustration.jpg"
TMP_DIR = WORKDIR / "build_tmp"
TMP_DIR.mkdir(parents=True, exist_ok=True)

EDGE_TTS = "/Volumes/App/Caches-And-Env/bin/edge-tts"
VOICE_ID = "id-ID-GadisNeural"
VOICE_ZH = "zh-CN-XiaoxiaoNeural"

W, H = 1080, 1920
BG_COLOR = (250, 246, 240)       # #FAF6F0
CHARCOAL = (43, 45, 66)          # #2B2D42
TERRACOTTA = (217, 83, 79)       # #D9534F
FOREST = (46, 111, 94)           # #2E6F5E
MUTED = (110, 108, 104)
CARD_BG = (255, 253, 249)
CARD_BORDER = (228, 221, 210)

FONT_CJK = "/System/Library/Fonts/STHeiti Medium.ttc"
FONT_LATIN = "/System/Library/Fonts/Avenir Next.ttc"


def load_font(path: str, size: int, index: int = 0) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size, index=index)


def prepare_base_image(path: Path) -> Image.Image:
    """Upscale illustration cleanly to 1080x1920 with LANCZOS + unsharp mask."""
    im = Image.open(path).convert("RGB")
    im = im.resize((W, H), Image.Resampling.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=110, threshold=3))
    return im


def is_cjk(ch: str) -> bool:
    cp = ord(ch)
    return (0x4E00 <= cp <= 0x9FFF) or (0x2E80 <= cp <= 0x2FDF) or (0x3400 <= cp <= 0x4DBF)


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


def draw_centered_text(
    draw: ImageDraw.ImageDraw,
    y: int,
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int],
    cjk_font: ImageFont.FreeTypeFont | None = None,
) -> int:
    runs = split_runs(text)
    if cjk_font is None or all(not flag for _, flag in runs):
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        x = (W - tw) // 2 - bbox[0]
        draw.text((x, y - bbox[1]), text, font=font, fill=fill)
        return th

    total_w = 0
    max_h = 0
    run_metrics = []
    for sub, flag in runs:
        f = cjk_font if flag else font
        bb = draw.textbbox((0, 0), sub, font=f)
        w_sub = bb[2] - bb[0]
        h_sub = bb[3] - bb[1]
        total_w += w_sub
        max_h = max(max_h, h_sub)
        run_metrics.append((sub, f, bb, w_sub, h_sub))

    cx = (W - total_w) // 2
    for sub, f, bb, w_sub, h_sub in run_metrics:
        draw.text((cx - bb[0], y + (max_h - h_sub) // 2 - bb[1]), sub, font=f, fill=fill)
        cx += w_sub + 2
    return max_h


def draw_pill(
    draw: ImageDraw.ImageDraw,
    cy: int,
    text: str,
    font: ImageFont.FreeTypeFont,
    bg_color: tuple[int, int, int],
    fg_color: tuple[int, int, int],
    pad_x: int = 34,
    pad_y: int = 14,
) -> None:
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    pw = tw + pad_x * 2
    ph = th + pad_y * 2
    x0 = (W - pw) // 2
    y0 = cy - ph // 2
    draw.rounded_rectangle([x0, y0, x0 + pw, y0 + ph], radius=ph // 2, fill=bg_color)
    tx = (W - tw) // 2 - bbox[0]
    ty = cy - th // 2 - bbox[1]
    draw.text((tx, ty), text, font=font, fill=fg_color)


def draw_bottom_card(
    draw: ImageDraw.ImageDraw,
    top_y: int,
    lines: list[tuple[str, ImageFont.FreeTypeFont, tuple[int, int, int]]],
    bottom_margin: int = 110,
    cjk_font_map: dict[int, ImageFont.FreeTypeFont] | None = None,
) -> None:
    x0, x1 = 76, W - 76
    y1 = H - bottom_margin
    draw.rounded_rectangle(
        [x0, top_y, x1, y1],
        radius=36,
        fill=CARD_BG,
        outline=CARD_BORDER,
        width=3,
    )
    heights = []
    for txt, fnt, _ in lines:
        bb = draw.textbbox((0, 0), txt, font=fnt)
        heights.append(bb[3] - bb[1])
    gap = 24
    total_h = sum(heights) + gap * (len(lines) - 1)
    cur_y = top_y + ((y1 - top_y) - total_h) // 2
    for (txt, fnt, col), lh in zip(lines, heights):
        cjk_f = cjk_font_map.get(id(fnt)) if cjk_font_map else None
        draw_centered_text(draw, cur_y, txt, fnt, col, cjk_font=cjk_f)
        cur_y += lh + gap


def draw_formula_row(
    draw: ImageDraw.ImageDraw,
    cy: int,
    left_cjk: str,
    left_col: tuple[int, int, int],
    right_cjk: str,
    right_col: tuple[int, int, int],
    f_cjk: ImageFont.FreeTypeFont,
    f_plus: ImageFont.FreeTypeFont,
) -> None:
    parts = [
        (left_cjk, f_cjk, left_col),
        ("  +  ", f_plus, MUTED),
        (right_cjk, f_cjk, right_col),
    ]
    widths = [draw.textbbox((0, 0), t, font=f)[2] - draw.textbbox((0, 0), t, font=f)[0] for t, f, _ in parts]
    cx = (W - sum(widths)) // 2
    for (t, f, col), wp in zip(parts, widths):
        bb = draw.textbbox((0, 0), t, font=f)
        th = bb[3] - bb[1]
        draw.text((cx - bb[0], cy - th // 2 - bb[1]), t, font=f, fill=col)
        cx += wp


def render_scenes(base_xiu: Image.Image, base_xi: Image.Image) -> list[Path]:
    f_pill = load_font(FONT_LATIN, 28, index=6)
    f_hanzi_big = load_font(FONT_CJK, 180, index=0)
    f_hanzi_med = load_font(FONT_CJK, 116, index=0)
    f_pinyin = load_font(FONT_LATIN, 62, index=6)
    f_title = load_font(FONT_LATIN, 48, index=6)
    f_sub = load_font(FONT_LATIN, 36, index=0)
    f_sub_bold = load_font(FONT_LATIN, 38, index=6)
    f_ex_cjk = load_font(FONT_CJK, 80, index=0)
    f_cjk_38 = load_font(FONT_CJK, 38, index=0)
    f_cjk_28 = load_font(FONT_CJK, 28, index=0)
    cjk_map = {id(f_sub_bold): f_cjk_38, id(f_pill): f_cjk_28}

    paths: list[Path] = []

    # Scene 1: Character 1 (休) — Radical Breakdown
    s1 = base_xiu.copy()
    d1 = ImageDraw.Draw(s1)
    draw_pill(d1, 115, "KARAKTER 1  ·  RADIKAL", f_pill, FOREST, (255, 255, 255))
    draw_formula_row(d1, 245, "亻", TERRACOTTA, "木", CHARCOAL, f_hanzi_med, f_title)
    draw_bottom_card(
        d1, 1465,
        [
            ("亻 (Orang)  +  木 (Pohon)", f_sub_bold, TERRACOTTA),
            ("Seseorang bersandar santai di pohon.", f_sub, CHARCOAL),
        ],
        cjk_font_map=cjk_map,
    )
    p1 = TMP_DIR / "scene_1.png"
    s1.save(p1)
    paths.append(p1)

    # Scene 2: Character 1 (休) — Meaning & Card
    s2 = base_xiu.copy()
    d2 = ImageDraw.Draw(s2)
    draw_centered_text(d2, 90, "休", f_hanzi_big, CHARCOAL)
    draw_centered_text(d2, 290, "xiū", f_pinyin, TERRACOTTA)
    draw_bottom_card(
        d2, 1465,
        [
            ("Arti: Beristirahat / Berhenti", f_sub_bold, FOREST),
            ("Orang bersandar di pohon = istirahat.", f_sub, CHARCOAL),
            ("(Catatan: 'menunggu' = 等 děng)", f_pill, MUTED),
        ],
        cjk_font_map=cjk_map,
    )
    s2.save(WORKDIR / "xiu_card.png")
    p2 = TMP_DIR / "scene_2.png"
    s2.save(p2)
    paths.append(p2)

    # Scene 3: Character 2 (息) — Radical Breakdown
    s3 = base_xi.copy()
    d3 = ImageDraw.Draw(s3)
    draw_pill(d3, 115, "KARAKTER 2  ·  RADIKAL", f_pill, CHARCOAL, (255, 255, 255))
    draw_formula_row(d3, 245, "自", CHARCOAL, "心", TERRACOTTA, f_hanzi_med, f_title)
    draw_bottom_card(
        d3, 1465,
        [
            ("自 (Hidung / Napas)  +  心 (Hati)", f_sub_bold, TERRACOTTA),
            ("Hembuskan napas hingga hati tenang.", f_sub, CHARCOAL),
        ],
        cjk_font_map=cjk_map,
    )
    p3 = TMP_DIR / "scene_3.png"
    s3.save(p3)
    paths.append(p3)

    # Scene 4: Character 2 (息) — Meaning & Card
    s4 = base_xi.copy()
    d4 = ImageDraw.Draw(s4)
    draw_centered_text(d4, 90, "息", f_hanzi_big, CHARCOAL)
    draw_centered_text(d4, 290, "xī", f_pinyin, TERRACOTTA)
    draw_bottom_card(
        d4, 1465,
        [
            ("Arti: Napas / Istirahat", f_sub_bold, FOREST),
            ("Menarik napas menenangkan hati.", f_sub, CHARCOAL),
        ],
        cjk_font_map=cjk_map,
    )
    s4.save(WORKDIR / "xi_card.png")
    p4 = TMP_DIR / "scene_4.png"
    s4.save(p4)
    paths.append(p4)

    # Scene 5: Combined Word (休息 xiūxi) — Both mnemonics side-by-side
    s5 = Image.new("RGB", (W, H), BG_COLOR)
    d5 = ImageDraw.Draw(s5)
    draw_pill(d5, 115, "GABUNGAN KATA", f_pill, TERRACOTTA, (255, 255, 255))
    draw_centered_text(d5, 195, "休息", f_hanzi_big, CHARCOAL)
    draw_centered_text(d5, 395, "xiūxi", f_pinyin, FOREST)

    # Crop center illustrations of 休 and 息 and place side-by-side
    crop_xiu = base_xiu.crop((80, 440, 1000, 1360)).resize((460, 460), Image.Resampling.LANCZOS)
    crop_xi = base_xi.crop((80, 440, 1000, 1360)).resize((460, 460), Image.Resampling.LANCZOS)
    s5.paste(crop_xiu, (60, 630))
    s5.paste(crop_xi, (560, 630))

    draw_centered_text(d5, 1120, "休 (orang + pohon)   +   息 (napas + hati)", f_sub, MUTED, cjk_font=f_cjk_38)
    draw_bottom_card(
        d5, 1450,
        [
            ("休息  (xiūxi)", f_ex_cjk, CHARCOAL),
            ("Arti: Beristirahat / Bersantai", f_sub_bold, FOREST),
            ("Bersandar di pohon + menenangkan napas.", f_sub, MUTED),
        ],
        cjk_font_map=cjk_map,
    )
    s5.save(WORKDIR / "xiuxi_card.png")
    p5 = TMP_DIR / "scene_5.png"
    s5.save(p5)
    paths.append(p5)

    return paths


def synth_edge(text: str, voice: str, out_wav: Path, rate: str = "+0%") -> float:
    """Synthesize speech with neural edge-tts and convert to 48kHz mono WAV via afconvert."""
    mp3_path = out_wav.with_suffix(".mp3")
    subprocess.run(
        [
            EDGE_TTS,
            "--voice", voice,
            "--rate", rate,
            "--text", text,
            "--write-media", str(mp3_path),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    subprocess.run(
        [
            "afconvert", "-f", "WAVE", "-d", "LEI16@48000", "-c", "1",
            str(mp3_path), str(out_wav),
        ],
        check=True,
    )
    with wave.open(str(out_wav), "rb") as wf:
        return wf.getnframes() / float(wf.getframerate())


def concat_wavs(parts: list[tuple[Path, float]], out_wav: Path) -> float:
    rate, sampwidth, nchannels = 48000, 2, 1
    total_frames = 0
    with wave.open(str(out_wav), "wb") as out_wf:
        out_wf.setnchannels(nchannels)
        out_wf.setsampwidth(sampwidth)
        out_wf.setframerate(rate)
        for wav_path, pad_sec in parts:
            with wave.open(str(wav_path), "rb") as in_wf:
                out_wf.writeframes(in_wf.readframes(in_wf.getnframes()))
                total_frames += in_wf.getnframes()
            if pad_sec > 0:
                sil_frames = int(round(pad_sec * rate))
                out_wf.writeframes(b"\x00" * (sil_frames * sampwidth * nchannels))
                total_frames += sil_frames
    return total_frames / float(rate)


def build_scene_audio() -> tuple[Path, list[float]]:
    sil_lead = TMP_DIR / "sil_lead.wav"
    with wave.open(str(sil_lead), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(48000)
        wf.writeframes(b"\x00" * int(0.30 * 48000 * 2))

    # Scene 1
    w1 = TMP_DIR / "e1.wav"
    synth_edge(
        "Karakter pertama: lihat radikal orang di kiri yang bersandar pada pohon di kanan.",
        VOICE_ID, w1, rate="+4%",
    )
    s1_wav = TMP_DIR / "s1.wav"
    d1 = concat_wavs([(sil_lead, 0.0), (w1, 0.45)], s1_wav)

    # Scene 2
    w2a = TMP_DIR / "e2a.wav"
    w2b = TMP_DIR / "e2b.wav"
    synth_edge("Ini karakter Syu, yang artinya beristirahat.", VOICE_ID, w2a, rate="+4%")
    synth_edge("休。休。", VOICE_ZH, w2b, rate="-10%")
    s2_wav = TMP_DIR / "s2.wav"
    d2 = concat_wavs([(sil_lead, 0.0), (w2a, 0.20), (w2b, 0.50)], s2_wav)

    # Scene 3
    w3 = TMP_DIR / "e3.wav"
    synth_edge(
        "Karakter kedua: di atas ada hidung untuk bernapas, dan di bawah ada hati.",
        VOICE_ID, w3, rate="+4%",
    )
    s3_wav = TMP_DIR / "s3.wav"
    d3 = concat_wavs([(sil_lead, 0.0), (w3, 0.45)], s3_wav)

    # Scene 4
    w4a = TMP_DIR / "e4a.wav"
    w4b = TMP_DIR / "e4b.wav"
    synth_edge("Ini karakter Si, yang artinya napas atau menenangkan diri.", VOICE_ID, w4a, rate="+4%")
    synth_edge("息。息。", VOICE_ZH, w4b, rate="-10%")
    s4_wav = TMP_DIR / "s4.wav"
    d4 = concat_wavs([(sil_lead, 0.0), (w4a, 0.20), (w4b, 0.50)], s4_wav)

    # Scene 5
    w5a = TMP_DIR / "e5a.wav"
    w5b = TMP_DIR / "e5b.wav"
    w5c = TMP_DIR / "e5c.wav"
    synth_edge("Saat digabung menjadi:", VOICE_ID, w5a, rate="+4%")
    synth_edge("休息。", VOICE_ZH, w5b, rate="-10%")
    synth_edge("Artinya beristirahat atau bersantai dengan tenang.", VOICE_ID, w5c, rate="+4%")
    s5_wav = TMP_DIR / "s5.wav"
    d5 = concat_wavs([(sil_lead, 0.0), (w5a, 0.15), (w5b, 0.25), (w5c, 0.65)], s5_wav)

    full_wav = TMP_DIR / "full_audio.wav"
    concat_wavs([(s1_wav, 0.0), (s2_wav, 0.0), (s3_wav, 0.0), (s4_wav, 0.0), (s5_wav, 0.0)], full_wav)
    return full_wav, [d1, d2, d3, d4, d5]


def build_video(scene_imgs: list[Path], full_wav: Path, durs: list[float]) -> Path:
    bin_path = TMP_DIR / "render_mp4"
    swift_src = WORKDIR / "render_mp4.swift"
    if not bin_path.exists() or swift_src.stat().st_mtime > bin_path.stat().st_mtime:
        subprocess.run(["swiftc", "-O", str(swift_src), "-o", str(bin_path)], check=True)

    out_mp4 = WORKDIR / "xiuxi_mnemonic.mp4"
    seg_args = [f"{img}:{dur:.4f}" for img, dur in zip(scene_imgs, durs)]
    subprocess.run([str(bin_path), str(out_mp4), str(full_wav), *seg_args], check=True)
    return out_mp4


def main() -> None:
    base_xiu = prepare_base_image(IMG_XIU)
    base_xi = prepare_base_image(IMG_XI)
    scene_imgs = render_scenes(base_xiu, base_xi)
    full_wav, durs = build_scene_audio()
    out_mp4 = build_video(scene_imgs, full_wav, durs)
    print(f"Created {out_mp4} ({sum(durs):.2f}s)")


if __name__ == "__main__":
    main()
