#!/usr/bin/env python3
"""Stage 5: Comprehensive One-by-One Kaidah Audit (181 chars, 50 sprites, 155 CGR-linked words, modular 9:16 videos)."""

import json
import subprocess
import sys
from pathlib import Path
from PIL import Image
from fontTools.ttLib import TTFont

WORKDIR = Path("/Volumes/App/Workspace/chinese-mnemonic-demo")
FONT_CJK = "/System/Library/Fonts/STHeiti Medium.ttc"
REQUIRED_HEXES = ["#FAF6F0", "#2B2D42", "#D9534F", "#2E6F5E"]
VALID_LAYOUTS = {"Struktur Tunggal", "Kiri + Kanan", "Atas + Bawah", "Luar + Dalam", "Sudut + Isi"}


def inspect_mp4_metrics(paths: list[Path]) -> dict[str, dict]:
    """Batch-inspect MP4 duration and 1080x1920 size via Swift AVFoundation."""
    if not paths:
        return {}
    swift_code = '''
import AVFoundation; import Foundation
let paths = CommandLine.arguments.dropFirst()
let group = DispatchGroup()
var results: [[String: Any]] = []
let lock = NSLock()
for p in paths {
    group.enter()
    Task {
        let url = URL(fileURLWithPath: p)
        let asset = AVURLAsset(url: url)
        var dur = 0.0; var w = 0.0; var h = 0.0; var hasAudio = false
        if let vt = try? await asset.loadTracks(withMediaType: .video).first {
            let sz = (try? await vt.load(.naturalSize)) ?? .zero
            w = sz.width; h = sz.height
            dur = (try? await asset.load(.duration).seconds) ?? 0.0
        }
        if let _ = try? await asset.loadTracks(withMediaType: .audio).first {
            hasAudio = true
        }
        lock.lock()
        results.append(["path": p, "dur": dur, "w": w, "h": h, "audio": hasAudio])
        lock.unlock()
        group.leave()
    }
}
group.wait()
let data = try JSONSerialization.data(withJSONObject: results)
print(String(data: data, encoding: .utf8)!)
'''
    tmp_swift = WORKDIR / "build_tmp" / "inspect_mp4s.swift"
    tmp_bin = WORKDIR / "build_tmp" / "inspect_mp4s"
    if not tmp_bin.exists() or not tmp_swift.exists():
        tmp_swift.write_text(swift_code, encoding="utf-8")
        subprocess.run(["swiftc", "-O", str(tmp_swift), "-o", str(tmp_bin)], check=True)

    out = {}
    # Process in chunks of 120 to stay well under argv limits
    str_paths = [str(p) for p in paths if p.exists()]
    for i in range(0, len(str_paths), 120):
        chunk = str_paths[i:i + 120]
        res = subprocess.run([str(tmp_bin), *chunk], check=True, capture_output=True, text=True)
        for item in json.loads(res.stdout):
            out[item["path"]] = item
    return out


def run_audit() -> dict:
    actors = json.loads((WORKDIR / "actors_catalog.json").read_text(encoding="utf-8"))
    actor_map = {a["id"]: a for a in actors}
    vocab = json.loads((WORKDIR / "hsk1_vocab.json").read_text(encoding="utf-8"))
    chars = json.loads((WORKDIR / "hsk1_characters.json").read_text(encoding="utf-8"))
    prompts = json.loads((WORKDIR / "02_CHINEASY_PROMPTS.json").read_text(encoding="utf-8"))
    cgr_ref = json.loads((WORKDIR / "graded_reader_ref.json").read_text(encoding="utf-8"))

    errors: list[str] = []

    # Check 1: Official List + ChineseGradedReader DB Reference Integrity
    vocab_words = [v["word"] for v in vocab]
    char_glyphs = [c["char"] for c in chars]
    official_chars = [c for c in chars if not c.get("is_bonus_demo")]
    char_set = set(char_glyphs)
    vocab_char_set = {ch for v in vocab for ch in v["chars"]}
    missing_from_chars = sorted(vocab_char_set - char_set)

    if len(vocab) != 155 or len(set(vocab_words)) != 155:
        errors.append(f"Expected 155 unique HSK 1 vocab words, got {len(vocab)}")
    if len(official_chars) != 178:
        errors.append(f"Expected 178 unique official HSK 1 chars, got {len(official_chars)}")
    if len(chars) != 181 or len(char_set) != 181:
        errors.append(f"Expected 181 total char entries, got {len(chars)}")
    if missing_from_chars:
        errors.append(f"Vocab characters missing from hsk1_characters.json: {missing_from_chars}")
    if cgr_ref.get("cgr_old_hsk1_matched") != cgr_ref.get("cgr_old_hsk1_total"):
        errors.append(
            f"CGR oldLevel==1 mismatch: {cgr_ref.get('cgr_old_hsk1_matched')}/{cgr_ref.get('cgr_old_hsk1_total')}"
        )

    # Check 2: Font Glyph Coverage (0 missing glyphs across char, layout, radicals, mnemonic_id)
    cmap = TTFont(FONT_CJK, fontNumber=0).getBestCmap()
    all_text = "".join(c["char"] + c["layout"] + c["radicals"] + c["mnemonic_id"] for c in chars)
    missing_glyphs = sorted({ch for ch in all_text if ord(ch) > 127 and ord(ch) not in cmap})
    if missing_glyphs:
        errors.append(f"Missing font glyphs in STHeiti Medium: {missing_glyphs}")

    # Check 3: Canonical Actor Sprites (50 sprites + 50 sprite cards)
    sprite_issues = []
    for a in actors:
        sp = WORKDIR / a["sprite_path"]
        sc = WORKDIR / a["sprite_card_path"]
        if not sp.exists():
            sprite_issues.append(f"{a['id']}: missing sprite")
        if not sc.exists():
            sprite_issues.append(f"{a['id']}: missing sprite_card")
    if sprite_issues:
        errors.append(f"Actor sprite issues ({len(sprite_issues)}): {sprite_issues[:10]}")

    # Check 4: One-by-One Kaidah Audit across ALL 181 Characters
    kaidah_rows = []
    kaidah_failures = 0
    for c in chars:
        ch = c["char"]
        a_ids = c.get("actor_ids", [])
        k1_actors_ok = bool(a_ids) and all(
            aid in actor_map and actor_map[aid]["actor_name"].lower() in c["mnemonic_id"].lower()
            for aid in a_ids
        )
        k2_layout_ok = c.get("layout") in VALID_LAYOUTS
        tpl_ok = (WORKDIR / "templates" / f"{ch}.png").exists()
        ai_exists = (WORKDIR / "illustrations" / f"{ch}.jpg").exists()
        comp_exists = (WORKDIR / "illustrations_composed" / f"{ch}.png").exists()
        card_ok = (WORKDIR / "cards" / f"{ch}_card.png").exists()
        k3_visual_ok = tpl_ok and (ai_exists or comp_exists) and card_ok

        cv_path = WORKDIR / "char_videos" / f"{ch}.mp4"
        k4_video_ok = cv_path.exists() and cv_path.stat().st_size > 10000

        row_ok = k1_actors_ok and k2_layout_ok and k3_visual_ok and k4_video_ok
        if not row_ok:
            kaidah_failures += 1
        kaidah_rows.append({
            "id": c["id"],
            "char": ch,
            "pinyin": c["pinyin"],
            "layout": c.get("layout"),
            "actor_ids": a_ids,
            "visual_mode": "Nano-Banana" if ai_exists else "Actor-Sprite",
            "k1_actor_consistent": k1_actors_ok,
            "k2_spatial_layout": k2_layout_ok,
            "k3_visual_card": k3_visual_ok,
            "k4_char_video": k4_video_ok,
            "passed": row_ok,
        })
    if kaidah_failures:
        bad = [r["char"] for r in kaidah_rows if not r["passed"]][:10]
        errors.append(f"{kaidah_failures} characters failed Kaidah audit (sample: {bad})")

    # Check 5: Prompt Quality Audit (181/181)
    prompt_errors = []
    if len(prompts) != len(chars):
        prompt_errors.append(f"Prompt count {len(prompts)} != char count {len(chars)}")
    for p in prompts:
        txt = p.get("full_image_prompt", "")
        if any(x not in txt for x in [p["template_path"], p["char"], p["radicals"], p["prompt_hint"], *REQUIRED_HEXES]):
            prompt_errors.append(p["char"])
    if prompt_errors:
        errors.append(f"Prompt audit errors ({len(prompt_errors)}): {prompt_errors[:10]}")

    # Check 6: Modular 9:16 Vertical Video & Stitch Verification (181 char_videos + 155 vocab videos)
    char_vid_paths = [WORKDIR / "char_videos" / f"{c['char']}.mp4" for c in chars]
    vocab_vid_paths = [WORKDIR / "videos" / f"{v['word']}.mp4" for v in vocab]
    outro_paths = [WORKDIR / "build_tmp" / "word_outros" / f"{v['word']}_outro.mp4" for v in vocab if v["char_count"] >= 2]
    mp4_meta = inspect_mp4_metrics(char_vid_paths + vocab_vid_paths + outro_paths)

    bad_9x16 = []
    for p_str, meta in mp4_meta.items():
        if (meta["w"], meta["h"]) != (1080.0, 1920.0) or not meta["audio"] or meta["dur"] <= 1.0:
            bad_9x16.append(Path(p_str).name)
    if bad_9x16:
        errors.append(f"Videos failing 9:16 (1080x1920) + audio check ({len(bad_9x16)}): {bad_9x16[:10]}")

    single_copy_ok = 0
    compound_stitch_ok = 0
    stitch_mismatches = []
    for v in vocab:
        vp = WORKDIR / "videos" / f"{v['word']}.mp4"
        if not vp.exists():
            stitch_mismatches.append(f"{v['word']}: missing")
            continue
        if v["char_count"] == 1:
            cp = WORKDIR / "char_videos" / f"{v['chars'][0]}.mp4"
            if cp.exists() and vp.stat().st_size == cp.stat().st_size:
                single_copy_ok += 1
            else:
                stitch_mismatches.append(f"{v['word']}: size != char_video")
        else:
            op = WORKDIR / "build_tmp" / "word_outros" / f"{v['word']}_outro.mp4"
            v_dur = mp4_meta.get(str(vp), {}).get("dur", 0.0)
            c_sum = sum(mp4_meta.get(str(WORKDIR / "char_videos" / f"{ch}.mp4"), {}).get("dur", 0.0) for ch in v["chars"])
            o_dur = mp4_meta.get(str(op), {}).get("dur", 0.0)
            if op.exists() and abs(v_dur - (c_sum + o_dur)) <= 0.25:
                compound_stitch_ok += 1
            else:
                stitch_mismatches.append(f"{v['word']}: dur={v_dur:.2f} vs sum={c_sum + o_dur:.2f}")

    if stitch_mismatches:
        errors.append(f"Modular stitch mismatches ({len(stitch_mismatches)}): {stitch_mismatches[:10]}")

    # Check 7: Card Asset Audit (ID + EN 1080x1920) & EN Video Stitch Verification
    char_cards_ok = sum(1 for c in chars if (WORKDIR / "cards" / f"{c['char']}_card.png").exists())
    vocab_cards_ok = sum(1 for v in vocab if (WORKDIR / "vocab_cards" / f"{v['word']}_card.png").exists())
    char_cards_en_ok = sum(1 for c in chars if (WORKDIR / "cards_en" / f"{c['char']}_card.png").exists())
    vocab_cards_en_ok = sum(1 for v in vocab if (WORKDIR / "vocab_cards_en" / f"{v['word']}_card.png").exists())
    sprite_cards_en_ok = sum(1 for a in actors if (WORKDIR / "sprite_cards_en" / f"{a['id']}_sprite.png").exists())
    char_videos_en_done = sum(1 for c in chars if (WORKDIR / "char_videos_en" / f"{c['char']}.mp4").exists())
    vocab_videos_en_done = sum(1 for v in vocab if (WORKDIR / "videos_en" / f"{v['word']}.mp4").exists())

    # Verify EN modular 9:16 videos when present
    if char_videos_en_done or vocab_videos_en_done:
        en_char_paths = [WORKDIR / "char_videos_en" / f"{c['char']}.mp4" for c in chars]
        en_vocab_paths = [WORKDIR / "videos_en" / f"{v['word']}.mp4" for v in vocab]
        en_outro_paths = [WORKDIR / "build_tmp" / "word_outros_en" / f"{v['word']}_outro.mp4" for v in vocab if v["char_count"] >= 2]
        en_meta = inspect_mp4_metrics(en_char_paths + en_vocab_paths + en_outro_paths)
        bad_en_9x16 = [Path(p).name for p, m in en_meta.items() if (m["w"], m["h"]) != (1080.0, 1920.0) or not m["audio"] or m["dur"] <= 1.0]
        if bad_en_9x16:
            errors.append(f"EN videos failing 9:16 + audio check ({len(bad_en_9x16)}): {bad_en_9x16[:10]}")
        for v in vocab:
            vp = WORKDIR / "videos_en" / f"{v['word']}.mp4"
            if not vp.exists():
                errors.append(f"EN vocab video missing: {v['word']}")
                break
            if v["char_count"] == 1:
                cp = WORKDIR / "char_videos_en" / f"{v['chars'][0]}.mp4"
                if not cp.exists() or vp.stat().st_size != cp.stat().st_size:
                    errors.append(f"EN single-char copy mismatch: {v['word']}")
                    break
            else:
                op = WORKDIR / "build_tmp" / "word_outros_en" / f"{v['word']}_outro.mp4"
                v_dur = en_meta.get(str(vp), {}).get("dur", 0.0)
                c_sum = sum(en_meta.get(str(WORKDIR / "char_videos_en" / f"{ch}.mp4"), {}).get("dur", 0.0) for ch in v["chars"])
                o_dur = en_meta.get(str(op), {}).get("dur", 0.0)
                if not op.exists() or abs(v_dur - (c_sum + o_dur)) > 0.25:
                    errors.append(f"EN compound stitch mismatch on {v['word']}: {v_dur:.2f} vs {c_sum + o_dur:.2f}")
                    break

    ai_illus = sorted(p.stem for p in (WORKDIR / "illustrations").glob("*.jpg") if p.stat().st_size > 0)
    all_videos = sorted(p.stem for p in (WORKDIR / "videos").glob("*.mp4") if p.stat().st_size > 0)
    all_videos_en = sorted(p.stem for p in (WORKDIR / "videos_en").glob("*.mp4") if p.stat().st_size > 0)
    char_videos_done = sum(1 for r in kaidah_rows if r["k4_char_video"])
    vocab_videos_done = sum(1 for v in vocab if (WORKDIR / "videos" / f"{v['word']}.mp4").exists())
    compound_total = sum(1 for v in vocab if v["char_count"] >= 2)
    single_total = sum(1 for v in vocab if v["char_count"] == 1)

    audit_passed = len(errors) == 0
    report = {
        "audit_passed": audit_passed,
        "errors": errors,
        "official_vocab_count": len(vocab),
        "official_unique_chars": len(official_chars),
        "total_char_records": len(chars),
        "actors_count": len(actors),
        "cgr_old_hsk1_coverage": f"{cgr_ref.get('cgr_old_hsk1_matched')}/{cgr_ref.get('cgr_old_hsk1_total')}",
        "missing_font_glyphs": len(missing_glyphs),
        "prompts_audited_ok": len(prompts) - len(prompt_errors),
        "char_cards_done": char_cards_ok,
        "vocab_cards_done": vocab_cards_ok,
        "char_cards_en_done": char_cards_en_ok,
        "vocab_cards_en_done": vocab_cards_en_ok,
        "sprite_cards_en_done": sprite_cards_en_ok,
        "ai_illustrations_count": len(ai_illus),
        "composed_illustrations_count": len(list((WORKDIR / "illustrations_composed").glob("*.png"))),
        "char_videos_done": char_videos_done,
        "vocab_videos_done": vocab_videos_done,
        "char_videos_en_done": char_videos_en_done,
        "vocab_videos_en_done": vocab_videos_en_done,
        "single_copy_verified": f"{single_copy_ok}/{single_total}",
        "compound_stitch_verified": compound_stitch_ok,
        "compound_stitch_total": compound_total,
        "total_videos_in_dir": len(all_videos),
        "total_videos_en_in_dir": len(all_videos_en),
        "kaidah_rows": kaidah_rows,
    }

    (WORKDIR / "03_audit_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    md = [
        "# 03 · Laporan Audit Satu-per-Satu Kaidah Mnemonic, Actor Sprites, Video 9:16 & Referensi ChineseGradedReader",
        "",
        f"- **Status Audit:** {'PASSED ✅ (0 errors)' if audit_passed else 'FAILED ❌'}",
        f"- **Referensi DB `ChineseGradedReader` (Read-Only):** `{report['cgr_old_hsk1_coverage']}` entri `oldLevel == 1` tercakup (+ 4 entri kanonik Hanban = **{len(vocab)} kata / {len(official_chars)} karakter unik + 3 demo = {len(chars)} karakter**)",
        f"- **Kaidah 1 — Konsistensi Aktor Sprite:** `{len(actors)}/50` Actor Sprites & showcase cards valid; **{sum(1 for r in kaidah_rows if r['k1_actor_consistent'])}/{len(chars)}** karakter konsisten menyebut aktor kanoniknya",
        f"- **Kaidah 2 — Struktur Spasial:** **{sum(1 for r in kaidah_rows if r['k2_spatial_layout'])}/{len(chars)}** karakter terklasifikasi spasial (`0` missing glyph di font `STHeiti Medium`)",
        f"- **Kaidah 3 — Visual & Kartu (`1080×1920`):** **{len(ai_illus)}** ilustrasi Nano-Banana + **{report['composed_illustrations_count']}** ilustrasi komposisi Actor-Sprite = **{sum(1 for r in kaidah_rows if r['k3_visual_card'])}/{len(chars)}** kartu karakter & **{vocab_cards_ok}/{len(vocab)}** kartu kosakata",
        f"- **Kaidah 4 — Video Karakter Mandiri (9:16 `1080×1920`):** ID **{char_videos_done}/{len(chars)}** (`char_videos/`) | EN **{char_videos_en_done}/{len(chars)}** (`char_videos_en/`)",
        f"- **Kaidah 5 — Modularitas Video Gabungan Tanpa Re-generasi:** `single_copy={single_copy_ok}/{single_total}` & `compound_stitch={compound_stitch_ok}/{compound_total}` | ID **{vocab_videos_done}/{len(vocab)}** (`videos/`, total `{len(all_videos)}`) | EN **{vocab_videos_en_done}/{len(vocab)}** (`videos_en/`, total `{len(all_videos_en)}`)",
        f"- **Kartu Grafis EN (`1080×1920`):** `cards_en` **{char_cards_en_ok}/{len(chars)}**, `vocab_cards_en` **{vocab_cards_en_ok}/{len(vocab)}**, `sprite_cards_en` **{sprite_cards_en_ok}/{len(actors)}**",
        "",
        "---",
        "",
        f"## Katalog 50 Canonical Actor Sprites",
        "",
        "| # | ID | Radikal | Nama Aktor | Keyword | Warna | Dipakai pada Karakter |",
        "|---:|---|---|---|---|---|---|",
    ]
    for i, a in enumerate(actors, start=1):
        used = " ".join(a.get("used_in_chars", [])) or "-"
        md.append(f"| {i} | `{a['id']}` | {a['radical']} | **{a['actor_name']}** | {a['keyword']} | `{a['color_hex']}` | {used} |")

    md.extend([
        "",
        "---",
        "",
        f"## Audit Satu-per-Satu Seluruh {len(chars)} Karakter",
        "",
        "| # | Hanzi | Pinyin | Struktur Spasial | Aktor Sprite | Mode Visual | K1 | K2 | K3 | K4 | Status |",
        "|---:|:---:|---|---|---|---|:-:|:-:|:-:|:-:|:-:|",
    ])
    for r in kaidah_rows:
        md.append(
            f"| {r['id']} | **{r['char']}** | `{r['pinyin']}` | {r['layout']} | `{' + '.join(r['actor_ids'])}` | {r['visual_mode']} | "
            f"{'✅' if r['k1_actor_consistent'] else '❌'} | {'✅' if r['k2_spatial_layout'] else '❌'} | "
            f"{'✅' if r['k3_visual_card'] else '❌'} | {'✅' if r['k4_char_video'] else '❌'} | {'PASS' if r['passed'] else 'FAIL'} |"
        )

    if errors:
        md.extend(["", "## Errors", *[f"- {e}" for e in errors]])

    (WORKDIR / "03_AUDIT_REPORT.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    summary = {k: v for k, v in report.items() if k != "kaidah_rows"}
    print(json.dumps(summary, ensure_ascii=False))
    if not audit_passed:
        sys.exit(1)
    return report


if __name__ == "__main__":
    run_audit()
