#!/usr/bin/env python3
"""Stage 2: Prepare audited stroke-faithful Chineasy prompts & voiceover scripts for all 179 characters."""

import json
from pathlib import Path

WORKDIR = Path("/Volumes/App/Workspace/chinese-mnemonic-demo")


def build_image_prompt(c: dict) -> str:
    ch = c["char"]
    py = c["pinyin"]
    meaning = c["meaning_id"]
    radicals = c["radicals"]
    hint = c["prompt_hint"]
    story = c["mnemonic_id"]
    tpl = str(WORKDIR / "templates" / f"{ch}.png")

    return (
        f"Edit the reference image `{tpl}` into a true \"Chineasy\"-style flat-vector visual mnemonic "
        f"illustration for the Chinese character {ch} ({py} — {meaning}) where the exact strokes of {ch} "
        f"remain unmistakably recognizable as the core skeleton!\n\n"
        f"STRICT RULES:\n"
        f"1. Keep the exact 9:16 vertical composition, warm cream background (#FAF6F0), and the EXACT stroke "
        f"positions, angles, and proportions of {ch} from `{tpl}`.\n"
        f"2. Radical & Visual Integration ({radicals}): {hint}. Mnemonic story: {story}\n"
        f"3. Palette: Use warm charcoal (#2B2D42) for primary structural strokes, terracotta coral-red (#D9534F) "
        f"for human/heart/fire/focal accents, and deep forest teal-green (#2E6F5E) for nature/breath/support accents.\n"
        f"4. Clean flat-vector editorial design, crisp sharp edges, generous empty top & bottom space, zero text, "
        f"zero pinyin, zero watermarks."
    )


def main() -> None:
    chars_data = json.loads((WORKDIR / "hsk1_characters.json").read_text(encoding="utf-8"))
    prompts = []
    md_lines = [
        f"# 02 · Persiapan Prompt Chineasy & Naskah Voiceover ({len(chars_data)} Karakter)",
        "",
        f"Total karakter yang disiapkan prompt-nya: **{len(chars_data)}** (178 resmi HSK 1 + 3 demo/radikal dasar).",
        "",
        "Standar palet Chineasy: `#FAF6F0` (background), `#2B2D42` (charcoal), `#D9534F` (terracotta coral-red), `#2E6F5E` (forest teal-green).",
        "",
        "---",
        "",
    ]

    for c in chars_data:
        ch = c["char"]
        tpl = str(WORKDIR / "templates" / f"{ch}.png")
        out_img = str(WORKDIR / "illustrations" / f"{ch}.jpg")
        full_prompt = build_image_prompt(c)
        vo_intro = f"{c['radicals']}. {c['mnemonic_id']}"
        vo_meaning = f"Karakter ini artinya {c['meaning_id']}."
        vo_zh = f"{ch}。{ch}。"

        rec = {
            "id": c["id"],
            "char": ch,
            "pinyin": c["pinyin"],
            "meaning_id": c["meaning_id"],
            "radicals": c["radicals"],
            "layout": c.get("layout", ""),
            "actor_ids": c.get("actor_ids", []),
            "mnemonic_id": c["mnemonic_id"],
            "prompt_hint": c["prompt_hint"],
            "is_bonus_demo": c.get("is_bonus_demo", False),
            "template_path": tpl,
            "output_illustration_path": out_img,
            "full_image_prompt": full_prompt,
            "voiceover_intro_id": vo_intro,
            "voiceover_meaning_id": vo_meaning,
            "voiceover_zh": vo_zh,
        }
        prompts.append(rec)

        md_lines.extend([
            f"### #{c['id']} · {ch} (`{c['pinyin']}`) — {c['meaning_id']}",
            f"- **Struktur:** {c.get('layout', '-')} | **Aktor:** {', '.join(c.get('actor_ids', []))}",
            f"- **Komponen:** {c['radicals']}",
            f"- **Template:** `{tpl}`",
            f"- **Visual Hint:** {c['prompt_hint']}",
            f"- **Narasi ID:** {vo_intro} {vo_meaning}",
            f"- **Mandarin ZH:** `{vo_zh}`",
            "",
            "```text",
            full_prompt,
            "```",
            "",
        ])

    (WORKDIR / "02_CHINEASY_PROMPTS.json").write_text(
        json.dumps(prompts, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (WORKDIR / "02_CHINEASY_PROMPTS.md").write_text("\n".join(md_lines), encoding="utf-8")
    print(f"Prepared {len(prompts)} audited prompt records -> 02_CHINEASY_PROMPTS.json & 02_CHINEASY_PROMPTS.md")


if __name__ == "__main__":
    main()
