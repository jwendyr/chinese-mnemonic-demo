#!/usr/bin/env python3
"""Stage 4: Modular 9:16 Vertical YouTube Shorts Video Pipeline.

Phase A: Render each unique character once into char_videos/<char>.mp4 (1080x1920).
Phase B: Build vocab videos in videos/<word>.mp4 by copying single-char videos or
stitching existing char_videos/<ch>.mp4 + short word_outros/<word>_outro.mp4 via concat_mp4.
"""

import argparse
import asyncio
import json
import shutil
import subprocess
import sys
import wave
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

from generate_all_hsk1_assets import (
    CHARCOAL,
    FOREST,
    TERRACOTTA,
    FONT_CJK,
    FONT_LATIN,
    W,
    H,
    draw_bottom_card,
    draw_mixed_centered,
    draw_pill,
    load_font,
    wrap_mixed_text,
)

WORKDIR = Path("/Volumes/App/Workspace/chinese-mnemonic-demo")
ILLUS_DIR = WORKDIR / "illustrations"
COMPOSED_DIR = WORKDIR / "illustrations_composed"
CARDS_DIR = WORKDIR / "cards"
VOCAB_CARDS_DIR = WORKDIR / "vocab_cards"
CHAR_VIDEOS_DIR = WORKDIR / "char_videos"
VIDEOS_DIR = WORKDIR / "videos"
TMP_DIR = WORKDIR / "build_tmp"
CHAR_AUDIO_DIR = TMP_DIR / "char_audio"
WORD_AUDIO_DIR = TMP_DIR / "word_audio"
WORD_OUTROS_DIR = TMP_DIR / "word_outros"
INTRO_FRAME_DIR = TMP_DIR / "char_intro_frames"

for d in (CHAR_VIDEOS_DIR, VIDEOS_DIR, TMP_DIR, CHAR_AUDIO_DIR, WORD_AUDIO_DIR, WORD_OUTROS_DIR, INTRO_FRAME_DIR):
    d.mkdir(parents=True, exist_ok=True)

EDGE_TTS = "/Volumes/App/Caches-And-Env/bin/edge-tts"
VOICE_ID = "id-ID-GadisNeural"
VOICE_ZH = "zh-CN-XiaoxiaoNeural"


def ensure_swift_tools() -> tuple[Path, Path]:
    render_bin = TMP_DIR / "render_mp4"
    render_src = WORKDIR / "render_mp4.swift"
    if not render_bin.exists() or render_src.stat().st_mtime > render_bin.stat().st_mtime:
        subprocess.run(["swiftc", "-O", str(render_src), "-o", str(render_bin)], check=True)

    concat_bin = TMP_DIR / "concat_mp4"
    concat_src = WORKDIR / "concat_mp4.swift"
    if not concat_bin.exists() or concat_src.stat().st_mtime > concat_bin.stat().st_mtime:
        subprocess.run(["swiftc", "-O", str(concat_src), "-o", str(concat_bin)], check=True)

    return render_bin, concat_bin


def ensure_sil_lead() -> Path:
    sil_lead = TMP_DIR / "sil_lead_028.wav"
    if not sil_lead.exists():
        with wave.open(str(sil_lead), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(48000)
            wf.writeframes(b"\x00" * int(0.28 * 48000 * 2))
    return sil_lead


async def synth_edge_async(
    sem: asyncio.Semaphore, text: str, voice: str, out_wav: Path, rate: str = "+4%", overwrite: bool = False
) -> None:
    if not overwrite and out_wav.exists() and out_wav.stat().st_size > 1000:
        return
    mp3_path = out_wav.with_suffix(".mp3")
    async with sem:
        for attempt in range(3):
            try:
                proc = await asyncio.create_subprocess_exec(
                    EDGE_TTS,
                    "--voice", voice,
                    "--rate", rate,
                    "--text", text,
                    "--write-media", str(mp3_path),
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.PIPE,
                )
                _, stderr = await proc.communicate()
                if proc.returncode != 0:
                    raise RuntimeError(stderr.decode("utf-8", errors="ignore"))
                conv = await asyncio.create_subprocess_exec(
                    "afconvert", "-f", "WAVE", "-d", "LEI16@48000", "-c", "1",
                    str(mp3_path), str(out_wav),
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.PIPE,
                )
                _, c_err = await conv.communicate()
                if conv.returncode != 0:
                    raise RuntimeError(c_err.decode("utf-8", errors="ignore"))
                mp3_path.unlink(missing_ok=True)
                return
            except Exception as exc:
                if attempt == 2:
                    raise RuntimeError(f"edge-tts failed for '{text}': {exc}") from exc
                await asyncio.sleep(1.0 * (attempt + 1))


async def prewarm_audio(chars_to_warm: list[dict], compound_words: list[tuple[str, str]], overwrite: bool = False) -> None:
    sem = asyncio.Semaphore(6)
    tasks = []
    for c in chars_to_warm:
        ch = c["char"]
        tasks.append(
            synth_edge_async(
                sem,
                f"{c['radicals']}. {c['mnemonic_id']}",
                VOICE_ID,
                CHAR_AUDIO_DIR / f"{ch}_intro.wav",
                rate="+4%",
                overwrite=overwrite,
            )
        )
        tasks.append(
            synth_edge_async(
                sem,
                f"Karakter ini artinya {c['meaning_id']}.",
                VOICE_ID,
                CHAR_AUDIO_DIR / f"{ch}_mean.wav",
                rate="+4%",
                overwrite=False,
            )
        )
        tasks.append(
            synth_edge_async(
                sem,
                f"{ch}。{ch}。",
                VOICE_ZH,
                CHAR_AUDIO_DIR / f"{ch}_zh.wav",
                rate="-10%",
                overwrite=False,
            )
        )

    if compound_words:
        tasks.append(
            synth_edge_async(
                sem, "Saat digabung menjadi:", VOICE_ID, WORD_AUDIO_DIR / "comb_prefix.wav", rate="+4%", overwrite=False
            )
        )
        for word, meaning_id in compound_words:
            tasks.append(
                synth_edge_async(sem, f"{word}。", VOICE_ZH, WORD_AUDIO_DIR / f"{word}_zh.wav", rate="-10%", overwrite=False)
            )
            tasks.append(
                synth_edge_async(
                    sem, f"Artinya {meaning_id}.", VOICE_ID, WORD_AUDIO_DIR / f"{word}_meaning.wav", rate="+4%", overwrite=False
                )
            )

    if tasks:
        print(f"Pre-warming/verifying {len(tasks)} neural TTS audio clips (concurrency=6)...", flush=True)
        await asyncio.gather(*tasks)


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


def build_char_intro_frame(c: dict, out_path: Path, overwrite: bool = False) -> Path:
    if out_path.exists() and not overwrite:
        return out_path
    f_pill = load_font(FONT_LATIN, 26, index=6)
    f_pill_cjk = load_font(FONT_CJK, 26, index=0)
    f_rad = load_font(FONT_LATIN, 36, index=6)
    f_rad_cjk = load_font(FONT_CJK, 44, index=0)
    f_sub = load_font(FONT_LATIN, 32, index=0)
    f_sub_cjk = load_font(FONT_CJK, 32, index=0)
    f_sub_bold = load_font(FONT_LATIN, 36, index=6)
    f_sub_bold_cjk = load_font(FONT_CJK, 36, index=0)

    ch = c["char"]
    ai_path = ILLUS_DIR / f"{ch}.jpg"
    comp_path = COMPOSED_DIR / f"{ch}.png"
    src_path = ai_path if ai_path.exists() else comp_path
    frame = Image.open(src_path).convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
    if ai_path.exists():
        frame = frame.filter(ImageFilter.UnsharpMask(radius=1.2, percent=110, threshold=3))

    d = ImageDraw.Draw(frame)
    badge = f"DEMO · #{c['id']} AKTOR SPRITE" if c.get("is_bonus_demo") else f"HSK 1 · #{c['id']} AKTOR SPRITE"
    draw_pill(d, 100, badge, f_pill, f_pill_cjk, FOREST, (255, 255, 255))

    actor_names = " + ".join(a["actor_name"] for a in c.get("actors", []))
    draw_mixed_centered(d, 180, f"{c.get('layout', '')} · {c['radicals']}", f_rad, f_rad_cjk, CHARCOAL)
    draw_mixed_centered(d, 250, actor_names, f_sub_bold, f_sub_bold_cjk, TERRACOTTA)

    wrapped_story = wrap_mixed_text(d, c["mnemonic_id"], f_sub, f_sub_cjk, 890)
    lines = [(f"Komponen: {c['radicals']}", f_sub_bold, f_sub_bold_cjk, FOREST)]
    for ln in wrapped_story[:4]:
        lines.append((ln, f_sub, f_sub_cjk, CHARCOAL))
    draw_bottom_card(d, 1415, lines, bottom_margin=75)
    frame.save(out_path)
    return out_path


def render_single_char_video(c: dict, render_bin: Path, overwrite: bool = False) -> Path:
    ch = c["char"]
    out_mp4 = CHAR_VIDEOS_DIR / f"{ch}.mp4"
    if out_mp4.exists() and out_mp4.stat().st_size > 10000 and not overwrite:
        return out_mp4

    sil_lead = ensure_sil_lead()
    job_dir = TMP_DIR / f"char_job_{ch}"
    job_dir.mkdir(parents=True, exist_ok=True)

    intro_img = build_char_intro_frame(c, INTRO_FRAME_DIR / f"{ch}.png", overwrite=overwrite)
    card_img = CARDS_DIR / f"{ch}_card.png"

    s_intro = job_dir / "s_intro.wav"
    d_intro = concat_wavs([(sil_lead, 0.0), (CHAR_AUDIO_DIR / f"{ch}_intro.wav", 0.45)], s_intro)

    s_mean = job_dir / "s_mean.wav"
    d_mean = concat_wavs(
        [(sil_lead, 0.0), (CHAR_AUDIO_DIR / f"{ch}_mean.wav", 0.20), (CHAR_AUDIO_DIR / f"{ch}_zh.wav", 0.50)],
        s_mean,
    )

    full_wav = job_dir / "full_audio.wav"
    concat_wavs([(s_intro, 0.0), (s_mean, 0.0)], full_wav)

    subprocess.run(
        [str(render_bin), str(out_mp4), str(full_wav), f"{intro_img}:{d_intro:.4f}", f"{card_img}:{d_mean:.4f}"],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    return out_mp4


def assemble_vocab_video(
    word: str,
    chars: list[str],
    render_bin: Path,
    concat_bin: Path,
    overwrite: bool = False,
) -> Path:
    out_mp4 = VIDEOS_DIR / f"{word}.mp4"
    if len(chars) == 1:
        src = CHAR_VIDEOS_DIR / f"{chars[0]}.mp4"
        if overwrite or not out_mp4.exists() or out_mp4.stat().st_size != src.stat().st_size:
            shutil.copy2(src, out_mp4)
        return out_mp4

    # Compound word (2+ chars): render ONLY short word outro, then stitch char_videos + outro
    outro_mp4 = WORD_OUTROS_DIR / f"{word}_outro.mp4"
    if overwrite or not outro_mp4.exists() or outro_mp4.stat().st_size <= 5000:
        sil_lead = ensure_sil_lead()
        vocab_card = (WORKDIR / "xiuxi_card.png") if word == "休息" else (VOCAB_CARDS_DIR / f"{word}_card.png")
        outro_wav = WORD_OUTROS_DIR / f"{word}_outro.wav"
        dur = concat_wavs(
            [
                (sil_lead, 0.0),
                (WORD_AUDIO_DIR / "comb_prefix.wav", 0.15),
                (WORD_AUDIO_DIR / f"{word}_zh.wav", 0.25),
                (WORD_AUDIO_DIR / f"{word}_meaning.wav", 0.65),
            ],
            outro_wav,
        )
        subprocess.run(
            [str(render_bin), str(outro_mp4), str(outro_wav), f"{vocab_card}:{dur:.4f}"],
            check=True,
            stdout=subprocess.DEVNULL,
        )

    seg_inputs = [str(CHAR_VIDEOS_DIR / f"{ch}.mp4") for ch in chars] + [str(outro_mp4)]
    subprocess.run(
        [str(concat_bin), str(out_mp4), *seg_inputs],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    return out_mp4


def main() -> None:
    parser = argparse.ArgumentParser(description="Modular 9:16 HSK 1 video pipeline (char_videos -> stitched videos).")
    parser.add_argument("--words", nargs="*", help="Specific HSK 1 words or characters to render.")
    parser.add_argument("--all", action="store_true", help="Render all 181 char videos and all 155+ vocab videos.")
    parser.add_argument("--chars-only", action="store_true", help="Render only standalone char_videos/.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing cached frames and MP4s.")
    args = parser.parse_args()

    chars_data = json.loads((WORKDIR / "hsk1_characters.json").read_text(encoding="utf-8"))
    vocab_data = json.loads((WORKDIR / "hsk1_vocab.json").read_text(encoding="utf-8"))
    char_map = {c["char"]: c for c in chars_data}
    vocab_map = {v["word"]: v for v in vocab_data}

    render_bin, concat_bin = ensure_swift_tools()

    if args.all:
        target_chars = chars_data
        target_vocab = [] if args.chars_only else [(v["word"], v["meaning_id"], v["chars"]) for v in vocab_data]
        if not args.chars_only:
            target_vocab.append(("休息", "beristirahat / bersantai", ["休", "息"]))
    elif args.words:
        req_chars = {}
        target_vocab = []
        for w in args.words:
            if w in vocab_map and not args.chars_only:
                v = vocab_map[w]
                target_vocab.append((v["word"], v["meaning_id"], v["chars"]))
                for ch in v["chars"]:
                    req_chars[ch] = char_map[ch]
            elif w in char_map:
                req_chars[w] = char_map[w]
                if not args.chars_only:
                    target_vocab.append((w, char_map[w]["meaning_id"], [w]))
            elif all(ch in char_map for ch in w) and w:
                chs = list(w)
                target_vocab.append((w, "gabungan kosakata", chs))
                for ch in chs:
                    req_chars[ch] = char_map[ch]
            else:
                print(f"Skipping unknown target: {w}", file=sys.stderr)
        target_chars = list(req_chars.values())
    else:
        print("Pass --words ... or --all")
        return

    chars_to_render = [
        c for c in target_chars
        if args.overwrite or not (CHAR_VIDEOS_DIR / f"{c['char']}.mp4").exists() or (CHAR_VIDEOS_DIR / f"{c['char']}.mp4").stat().st_size <= 10000
    ]
    compound_to_warm = [
        (w, m) for w, m, chs in target_vocab
        if len(chs) >= 2 and (args.overwrite or not (WORD_OUTROS_DIR / f"{w}_outro.mp4").exists())
    ]

    if chars_to_render or compound_to_warm:
        asyncio.run(prewarm_audio(chars_to_render, compound_to_warm, overwrite=args.overwrite))

    # Phase A: Render standalone character videos once
    for idx, c in enumerate(target_chars, start=1):
        out_c = render_single_char_video(c, render_bin, overwrite=args.overwrite)
        if args.overwrite or c in chars_to_render:
            print(f"[Char {idx}/{len(target_chars)}] {out_c.name} ({out_c.stat().st_size // 1024} KB)", flush=True)

    # Phase B: Assemble vocab videos from char_videos without re-generating characters
    for idx, (w, _m, chs) in enumerate(target_vocab, start=1):
        out_v = assemble_vocab_video(w, chs, render_bin, concat_bin, overwrite=args.overwrite)
        mode = "copy" if len(chs) == 1 else f"stitch({len(chs)}c+outro)"
        print(f"[Vocab {idx}/{len(target_vocab)}] {out_v.name} [{mode}] ({out_v.stat().st_size // 1024} KB)", flush=True)


if __name__ == "__main__":
    main()
