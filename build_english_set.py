#!/usr/bin/env python3
"""Build the complete parallel English HSK 1 set (cards, prompts, sprites, and 9:16 videos)
by reusing all shared visuals (sprites, illustrations, composed tiles) and Mandarin TTS clips."""

import argparse
import asyncio
import json
import re
import shutil
import subprocess
import wave
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from generate_all_hsk1_assets import (
    BG_COLOR,
    CARD_BG,
    CARD_BORDER,
    CHARCOAL,
    FOREST,
    MUSTARD,
    MUTED,
    TERRACOTTA,
    FONT_CJK,
    FONT_LATIN,
    W,
    H,
    draw_bottom_card,
    draw_mixed_centered,
    draw_pill,
    load_font,
    measure_mixed,
    wrap_mixed_text,
)

WORKDIR = Path("/Volumes/App/Workspace/chinese-mnemonic-demo")
ILLUS_DIR = WORKDIR / "illustrations"
COMPOSED_DIR = WORKDIR / "illustrations_composed"
SPRITES_DIR = WORKDIR / "sprites"
SPRITE_CARDS_EN_DIR = WORKDIR / "sprite_cards_en"
CARDS_EN_DIR = WORKDIR / "cards_en"
VOCAB_CARDS_EN_DIR = WORKDIR / "vocab_cards_en"
CHAR_VIDEOS_EN_DIR = WORKDIR / "char_videos_en"
VIDEOS_EN_DIR = WORKDIR / "videos_en"
TMP_DIR = WORKDIR / "build_tmp"
CHAR_AUDIO_ZH_DIR = TMP_DIR / "char_audio"
WORD_AUDIO_ZH_DIR = TMP_DIR / "word_audio"
CHAR_AUDIO_EN_DIR = TMP_DIR / "char_audio_en"
WORD_AUDIO_EN_DIR = TMP_DIR / "word_audio_en"
WORD_OUTROS_EN_DIR = TMP_DIR / "word_outros_en"
INTRO_FRAME_EN_DIR = TMP_DIR / "char_intro_frames_en"

for d in (
    SPRITE_CARDS_EN_DIR,
    CARDS_EN_DIR,
    VOCAB_CARDS_EN_DIR,
    CHAR_VIDEOS_EN_DIR,
    VIDEOS_EN_DIR,
    CHAR_AUDIO_EN_DIR,
    WORD_AUDIO_EN_DIR,
    WORD_OUTROS_EN_DIR,
    INTRO_FRAME_EN_DIR,
):
    d.mkdir(parents=True, exist_ok=True)

EDGE_TTS = "/Volumes/App/Caches-And-Env/bin/edge-tts"
VOICE_EN = "en-US-JennyNeural"

LAYOUT_EN_MAP = {
    "Struktur Tunggal": "Single Structure",
    "Kiri + Kanan": "Left + Right",
    "Atas + Bawah": "Top + Bottom",
    "Luar + Dalam": "Outer + Inner",
    "Sudut + Isi": "Corner + Inner",
}

# 50 Canonical English Actor Metadata keyed by actor id
EN_ACTORS = {
    "ren_person": ("Person Actor", "Person", "Human", "Minimalist coral-headed walking person acting as the main human character."),
    "nv_woman": ("Mother / Woman", "Woman", "Human", "Graceful female figure with a coral hair bun representing women and mothers."),
    "zi_child": ("Little Child", "Child", "Human", "Cheerful child silhouette with open arms representing youth and learning."),
    "kou_mouth": ("Speaking Mouth", "Mouth", "Communication", "Expressive speaking mouth icon used for talking, eating, and asking."),
    "yan_speech": ("Speech Wave", "Speech", "Communication", "Dialogue speech bubble representing language, speaking, and questions."),
    "mu_eye": ("Watching Eye", "Eye", "Senses", "Rectangular eye box with forest-teal iris used for looking and sleeping."),
    "shou_hand": ("Action Hand", "Hand", "Action", "Gesturing hand with rounded fingertips performing holding and shading."),
    "xin_heart": ("Feeling Heart", "Heart", "Emotion", "Warm coral heart with gentle pulse arcs representing thoughts and feelings."),
    "zu_foot": ("Walking Step", "Step", "Motion", "Stepping feet along a winding road path for moving, coming, and going."),
    "shui_water": ("Water Drops", "Water", "Nature", "Three water drops and flowing river ripples for liquids and drinking."),
    "mu_tree": ("Timber Tree", "Tree", "Nature", "Charcoal trunk and forest-teal canopy for wood, fruit, and shade."),
    "cao_grass": ("Green Sprout", "Sprout", "Nature", "Twin fresh green leaves sprouting from soil for plants, tea, and greens."),
    "ri_sun": ("Shining Sun", "Sun", "Time & Nature", "Golden glowing sun with crisp rays marking daytime and brightness."),
    "yue_moon": ("Crescent Moon", "Moon", "Time & Nature", "Curved crescent moon with stars marking months and companionship."),
    "huo_fire": ("Blazing Fire", "Fire", "Nature & Energy", "Flickering flame tongues over crossed firewood for heat and sparks."),
    "shan_mountain": ("Mountain Peaks", "Mountain", "Nature", "Three geometric peaks with snow caps symbolizing height and mountains."),
    "tu_earth": ("Earth Mound", "Earth", "Nature & Place", "Layered ground mound and horizon bar for soil, sitting, and places."),
    "mian_roof": ("House Roof", "Roof", "Building", "Sheltering pitched roof protecting family, writing, shops, and learning."),
    "men_door": ("Gateway Door", "Door", "Building", "Double-leaf entrance door frame for entering, exiting, and opening."),
    "wei_wall": ("Border Wall", "Border Box", "Building", "Protective square enclosure frame guarding whatever rests inside."),
    "jin_metal": ("Gold Metal", "Metal", "Objects & Value", "Gleaming gold coin and chime bar representing money and clocks."),
    "shi_food": ("Rice Bowl", "Food", "Food", "Steaming warm rice bowl with chopsticks for daily nourishment."),
    "he_grain": ("Grain Stalk", "Grain", "Nature & Food", "Drooping golden grain stalk laden with harvest kernels for harmony."),
    "quan_animal": ("Agile Animal", "Animal", "Creatures", "Playful four-legged silhouette used for loyal dogs and curious cats."),
    "ma_horse": ("Swift Horse", "Horse", "Creatures", "Galloping horse silhouette also used as a classic phonetic marker."),
    "zhui_bird": ("Flying Bird", "Bird/Wing", "Creatures", "Perched bird or soaring wing representing flight and agile birds."),
    "che_vehicle": ("Rolling Wheel", "Vehicle", "Transport", "Top-down axle and rolling carriage wheels for cars, taxis, and trains."),
    "yu_rain": ("Rain Cloud", "Rain", "Weather", "Dark cloud bar with four falling raindrops for rain and weather."),
    "bing_ice": ("Ice Crystal", "Ice", "Weather", "Two sharp geometric ice crystals bringing freezing cold temperatures."),
    "tian_field": ("Rice Field", "Field", "Nature & Place", "Four-square divided green paddy grid for farmland and inner bounds."),
    "dao_knife": ("Sharp Knife", "Knife", "Tools", "Sleek cutting blade slicing objects cleanly into measured parts."),
    "gong_tool": ("Measuring Tool", "Tool", "Tools & Work", "Carpenter I-beam and inch ruler representing precise work and craft."),
    "yi_cloth": ("Robe & Cloth", "Cloth", "Objects", "Tailored collar robe and cloth banner for garments and etiquette."),
    "si_silk": ("Silk Thread", "Thread", "Objects", "Intertwined silk ribbon coils connecting elements cleanly together."),
    "shi_arrow": ("Arrow & Spear", "Arrow/Spear", "Tools", "Sharp arrow and halberd spear for precision and self-defense."),
    "li_stand": ("Standing Firm", "Stand", "Action", "Figure standing upright on the ground line waiting or stationed firmly."),
    "yi_one": ("Counting Bar", "Line", "Numbers & Space", "Clean horizontal counting bar marking numbers and upper/lower lines."),
    "shi_ten": ("Cross of Ten", "Cross", "Numbers", "Crisp geometric cross representing ten fingers and central alignment."),
    "ba_divide": ("Balanced Split", "Split", "Numbers & Form", "Two symmetrical parted strokes or small table for sharing evenly."),
    "da_big": ("Wide Stretch", "Big", "Size", "Person stretching both arms wide apart to demonstrate BIG scale."),
    "xiao_small": ("Tiny Droplet", "Small", "Size", "Minimal central drop flanked by two tiny specks showing smallness."),
    "xi_evening": ("Evening Moon", "Evening", "Time", "Tilted twilight crescent moon marking dusk and passing nights."),
    "zi_nose": ("Breathing Nose", "Nose", "Body", "Minimalist nose bridge drawing calm air in to settle oneself."),
    "qi_steam": ("Rising Steam", "Air", "Nature", "Three wispy warm vapor currents drifting upward into the sky."),
    "gui_jade": ("Precious Jade", "Jewel", "Objects", "Faceted sparkling jade gem symbolizing clarity and treasure."),
    "shi_pig": ("Home Livestock", "Livestock", "Creatures", "Friendly farm piglet or sheep figure symbolizing home prosperity."),
    "fu_father": ("Wise Elder", "Elder", "Human", "Supportive father and walking-cane elder guiding the family."),
    "gu_drum": ("Festive Drum", "Drum", "Celebration", "Celebratory drum beaten with joyful sticks for happiness."),
    "jing_tower": ("Palace Tower", "Tower", "Building", "Multi-tiered pitched pagoda tower rising high in the capital city."),
    "fu_mound": ("City Wall", "Wall", "Building", "Curved defensive wall and stepped hillside marking locations."),
}

# Concise English glosses for items where CGR meaning is verbose or missing
EN_OVERRIDE = {
    "一": "one", "二": "two", "三": "three", "四": "four", "五": "five",
    "六": "six", "七": "seven", "八": "eight", "九": "nine", "十": "ten",
    "的": "possessive particle ('s)", "了": "completed action particle", "吗": "question particle (?)",
    "呢": "follow-up question particle", "个": "general measure word", "本": "measure word for books",
    "块": "piece / yuan (currency)", "些": "some / a few", "不客气": "you're welcome",
    "没关系": "it doesn't matter", "对不起": "I'm sorry", "谢谢": "thank you",
    "再见": "goodbye", "喂": "hello (on phone)", "请": "please / invite",
    "爱": "love", "人": "person / people", "我": "I / me", "我们": "we / us",
    "你": "you", "他": "he / him", "她": "she / her", "是": "to be (is/am/are)",
    "有": "to have / there is", "在": "at / in / be located", "和": "and / with",
    "很": "very", "太": "too / extremely", "都": "all / both", "不": "not / no",
    "没": "not / have not", "没有": "do not have", "这": "this", "那": "that",
    "哪": "which", "哪儿": "where", "谁": "who", "什么": "what",
    "几": "how many (small)", "多少": "how many / how much", "怎么": "how",
    "怎么样": "how about / how is it", "大": "big / large", "小": "small / little",
    "多": "many / much", "少": "few / little", "好": "good / well",
    "冷": "cold", "热": "hot", "高兴": "happy / glad", "漂亮": "pretty / beautiful",
    "上": "up / above / go up", "下": "down / below / next", "里": "inside / in",
    "前面": "front / in front", "后面": "back / behind", "今天": "today",
    "明天": "tomorrow", "昨天": "yesterday", "上午": "morning", "中午": "noon",
    "下午": "afternoon", "年": "year", "月": "month / moon", "日": "day / sun",
    "号": "date / number", "星期": "week", "点": "o'clock / dot", "分钟": "minute",
    "现在": "now", "时候": "time / moment", "岁": "years old (age)",
    "爸爸": "dad / father", "妈妈": "mom / mother", "儿子": "son", "女儿": "daughter",
    "朋友": "friend", "老师": "teacher", "学生": "student", "同学": "classmate",
    "先生": "Mr. / sir / husband", "小姐": "Miss / young lady", "医生": "doctor",
    "名字": "name", "家": "home / family", "学校": "school", "饭店": "restaurant / hotel",
    "饭馆": "restaurant", "商店": "shop / store", "医院": "hospital", "火车站": "train station",
    "中国": "China", "北京": "Beijing", "汉语": "Chinese language", "字": "Chinese character",
    "书": "book", "桌子": "table / desk", "椅子": "chair", "杯子": "cup / glass",
    "钱": "money", "水": "water", "茶": "tea", "米饭": "cooked rice",
    "菜": "dish / vegetable", "水果": "fruit", "苹果": "apple", "衣服": "clothes",
    "飞机": "airplane", "出租车": "taxi", "电视": "television", "电脑": "computer",
    "电影": "movie / film", "天气": "weather", "猫": "cat", "狗": "dog", "东西": "thing / stuff",
    "看": "to look / watch / read", "看见": "to see", "听": "to listen / hear",
    "说": "to speak / say", "说话": "to speak / talk", "读": "to read aloud", "写": "to write",
    "叫": "to call / be named", "来": "to come", "回": "to return", "去": "to go",
    "吃": "to eat", "喝": "to drink", "睡觉": "to sleep", "打电话": "to make a phone call",
    "做": "to do / make", "买": "to buy", "开": "to open / drive", "坐": "to sit / ride",
    "住": "to live / stay", "学习": "to study / learn", "工作": "to work / job",
    "下雨": "to rain", "喜欢": "to like", "想": "to want / think / miss",
    "认识": "to know (someone)", "会": "can (learned) / will", "能": "can / be able to",
    "一点儿": "a little bit",
    "什": "what (in 什么)", "今": "now / today", "们": "plural suffix", "候": "wait / time",
    "作": "work / make", "兴": "happy / excited", "分": "minute / divide", "前": "front / before",
    "北": "north", "医": "medicine / doctor", "午": "noon", "友": "friend", "同": "same / together",
    "名": "name", "后": "back / after", "商": "commerce / shop", "喜": "happy / like",
    "国": "country", "姐": "older sister", "客": "guest", "师": "teacher / master",
    "店": "shop / inn", "影": "shadow / movie", "怎": "how", "打": "hit / call",
    "时": "time / hour", "明": "bright / tomorrow", "星": "star", "昨": "yesterday",
    "朋": "friend", "服": "clothes / serve", "期": "period / week", "机": "machine / plane",
    "果": "fruit", "校": "school", "样": "appearance / kind", "桌": "table", "椅": "chair",
    "欢": "joyous / happy", "汉": "Chinese (Han)", "漂": "pretty / float", "火": "fire",
    "爸": "dad", "现": "present / appear", "生": "life / student", "电": "electricity",
    "睡": "sleep", "租": "rent", "站": "stand / station", "米": "rice", "系": "system / relation",
    "老": "old / elder", "脑": "brain", "苹": "apple", "衣": "clothes", "西": "west",
    "视": "look / view", "见": "see / meet", "觉": "sleep / feel", "认": "recognize",
    "识": "know", "话": "speech / words", "语": "language", "谁": "who", "谢": "thank",
    "起": "rise / get up", "车": "vehicle / car", "钟": "clock / bell", "院": "courtyard / hospital",
    "雨": "rain", "面": "face / side", "飞": "fly", "饭": "rice / meal", "馆": "hall / restaurant",
    "高": "tall / high", "休": "rest", "息": "breath / rest", "山": "mountain",
    "休": "rest", "休息": "to rest / take a break",
}


def clean_en_meaning(key: str, cgr_ref: dict) -> str:
    if key in EN_OVERRIDE:
        return EN_OVERRIDE[key]
    raw = (cgr_ref or {}).get("meaning_en") or ""
    if raw:
        # Take concise first 2 semicolon clauses, strip parenthetical classifier noise
        parts = [re.sub(r"\s*\([^)]*\)", "", p).strip() for p in raw.split(";")]
        parts = [p for p in parts if p and not p.lower().startswith("cl:") and not p.lower().startswith("surname")]
        if parts:
            short = "; ".join(parts[:2])
            return short[:68].rstrip(" ;,")
    return key


def enrich_bilingual_data() -> tuple[list[dict], list[dict], list[dict]]:
    actors = json.loads((WORKDIR / "actors_catalog.json").read_text(encoding="utf-8"))
    chars = json.loads((WORKDIR / "hsk1_characters.json").read_text(encoding="utf-8"))
    vocab = json.loads((WORKDIR / "hsk1_vocab.json").read_text(encoding="utf-8"))

    actor_map = {}
    for a in actors:
        aid = a["id"]
        name_en, kw_en, grp_en, desc_en = EN_ACTORS[aid]
        a["actor_name_en"] = name_en
        a["keyword_en"] = kw_en
        a["role_group_en"] = grp_en
        a["description_en"] = desc_en
        actor_map[aid] = a

    (WORKDIR / "actors_catalog.json").write_text(
        json.dumps(actors, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    char_by_glyph = {}
    prompts_en = []
    md_list_en = [
        "# 01 · Official HSK 1 List (Alphabetical Pinyin Order + ChineseGradedReader Reference)",
        "",
        f"- **Total HSK 1 Words:** **{len(vocab)}** (covering **100% (151/151)** of `ChineseGradedReader` `oldLevel == 1` + 4 canonical Hanban words)",
        f"- **Total Unique Characters:** **{sum(1 for c in chars if not c.get('is_bonus_demo'))}** (+ 3 demo characters `休, 息, 山` = **{len(chars)}**)",
        "",
        "---",
        "",
        f"## Part A: All {len(chars)} Characters with Spatial Structure & Consistent Actors",
        "",
        "| # | Hanzi | Pinyin | English Meaning | Spatial Structure | Consistent Actors |",
        "|---:|:---:|---|---|---|---|",
    ]
    md_prompts_en = [
        f"# 02 · English Chineasy Prompts & Voiceover Scripts ({len(chars)} Characters)",
        "",
        "Palette: `#FAF6F0` (cream), `#2B2D42` (charcoal), `#D9534F` (terracotta), `#2E6F5E` (forest teal).",
        "",
        "---",
        "",
    ]

    for c in chars:
        ch = c["char"]
        m_en = clean_en_meaning(ch, c.get("cgr_ref", {}))
        l_en = LAYOUT_EN_MAP.get(c.get("layout", "Struktur Tunggal"), "Single Structure")
        actor_objs = []
        for a in c.get("actors", []):
            full_a = actor_map[a["id"]]
            a_copy = dict(a)
            a_copy["actor_name_en"] = full_a["actor_name_en"]
            a_copy["keyword_en"] = full_a["keyword_en"]
            actor_objs.append(a_copy)

        actor_phrase_en = " and ".join(f"{a['actor_name_en']} ({a['radical']})" for a in actor_objs)
        rad_en = " + ".join(f"{a['radical']} ({a['keyword_en']})" for a in actor_objs)
        story_en = f"{c['prompt_hint']}. Consistent actors: {actor_phrase_en}."

        c["meaning_en"] = m_en
        c["layout_en"] = l_en
        c["radicals_en"] = rad_en
        c["mnemonic_en"] = story_en
        c["actors"] = actor_objs
        char_by_glyph[ch] = c

        tag = " *(demo)*" if c.get("is_bonus_demo") else ""
        md_list_en.append(f"| {c['id']} | **{ch}**{tag} | `{c['pinyin']}` | {m_en} | {l_en} | {actor_phrase_en} |")

        tpl = str(WORKDIR / "templates" / f"{ch}.png")
        full_prompt = (
            f"Edit `{tpl}` into a Chineasy flat-vector visual mnemonic for {ch} ({c['pinyin']} — {m_en}) "
            f"preserving exact stroke geometry (#FAF6F0, #2B2D42, #D9534F, #2E6F5E). Story: {story_en}"
        )
        prompts_en.append({
            "id": c["id"],
            "char": ch,
            "pinyin": c["pinyin"],
            "meaning_en": m_en,
            "layout_en": l_en,
            "radicals_en": rad_en,
            "actor_ids": c["actor_ids"],
            "mnemonic_en": story_en,
            "template_path": tpl,
            "full_image_prompt": full_prompt,
            "voiceover_intro_en": f"{rad_en}. {story_en}",
            "voiceover_meaning_en": f"This character means {m_en}.",
            "voiceover_zh": f"{ch}。{ch}。",
        })
        md_prompts_en.extend([
            f"### #{c['id']} · {ch} (`{c['pinyin']}`) — {m_en}",
            f"- **Structure:** {l_en} | **Actors:** {actor_phrase_en}",
            f"- **Voiceover EN:** {rad_en}. {story_en} This character means {m_en}.",
            "",
        ])

    md_list_en.extend([
        "",
        "---",
        "",
        f"## Part B: All {len(vocab)} Official HSK 1 Vocabulary Words",
        "",
        "| # | Word | Pinyin | English Meaning | Category | Character Breakdown |",
        "|---:|:---:|---|---|---|---|",
    ])

    for v in vocab:
        m_en = clean_en_meaning(v["word"], v.get("cgr_ref", {}))
        v["meaning_en"] = m_en
        for b in v.get("breakdown", []):
            ch_b = b["char"]
            b["meaning_en"] = char_by_glyph[ch_b]["meaning_en"]
            b["layout_en"] = char_by_glyph[ch_b]["layout_en"]
            b["radicals_en"] = char_by_glyph[ch_b]["radicals_en"]
            b["mnemonic_en"] = char_by_glyph[ch_b]["mnemonic_en"]
        md_list_en.append(
            f"| {v['id']} | **{v['word']}** | `{v['pinyin']}` | {m_en} | {v['category']} | {' + '.join(v['chars'])} |"
        )

    (WORKDIR / "hsk1_characters.json").write_text(json.dumps(chars, ensure_ascii=False, indent=2), encoding="utf-8")
    (WORKDIR / "hsk1_vocab.json").write_text(json.dumps(vocab, ensure_ascii=False, indent=2), encoding="utf-8")
    (WORKDIR / "01_OFFICIAL_HSK1_LIST_EN.md").write_text("\n".join(md_list_en) + "\n", encoding="utf-8")
    (WORKDIR / "02_CHINEASY_PROMPTS_EN.json").write_text(json.dumps(prompts_en, ensure_ascii=False, indent=2), encoding="utf-8")
    (WORKDIR / "02_CHINEASY_PROMPTS_EN.md").write_text("\n".join(md_prompts_en) + "\n", encoding="utf-8")
    return actors, chars, vocab


def render_english_cards(actors: list[dict], chars: list[dict], vocab: list[dict]) -> None:
    """Render all 50 sprite_cards_en, 181 cards_en, and 155 vocab_cards_en reusing existing tiles."""
    char_map = {c["char"]: c for c in chars}
    f_cjk_big = load_font(FONT_CJK, 140, index=0)
    f_title = load_font(FONT_LATIN, 56, index=6)
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

    def hex_rgb(hx: str) -> tuple[int, int, int]:
        hx = hx.lstrip("#")
        return tuple(int(hx[i:i+2], 16) for i in (0, 2, 4))

    def get_center_tile(ch: str) -> Image.Image:
        ai_p = ILLUS_DIR / f"{ch}.jpg"
        if ai_p.exists():
            im = Image.open(ai_p).convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
            im = im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=110, threshold=3))
            return im.crop((100, 460, 980, 1340)).resize((760, 760), Image.Resampling.LANCZOS)
        comp_p = COMPOSED_DIR / f"{ch}.png"
        im = Image.open(comp_p).convert("RGB")
        return im.crop(((W - 760) // 2, 490, (W + 760) // 2, 490 + 760))

    # 1. 50 English Sprite Cards (reusing sprites/<id>.png)
    for idx, a in enumerate(actors, start=1):
        col = hex_rgb(a["color_hex"])
        card = Image.new("RGB", (W, H), BG_COLOR)
        d = ImageDraw.Draw(card)
        draw_pill(d, 115, f"ACTOR SPRITE #{idx} · {a['role_group_en'].upper()}", f_pill, f_pill_cjk, col, (255, 255, 255))
        draw_mixed_centered(d, 190, a["radical"], f_cjk_big, f_cjk_big, CHARCOAL)
        draw_mixed_centered(d, 365, f"{a['actor_name_en']} ({a['keyword_en']})", f_title, f_title, col)
        sp = Image.open(WORKDIR / a["sprite_path"]).convert("RGBA").resize((720, 720), Image.Resampling.LANCZOS)
        card.paste(sp, (180, 520), sp)

        used_chars = a.get("used_in_chars", [])
        used_str = " ".join(used_chars[:20]) + ("…" if len(used_chars) > 20 else "")
        wrapped = wrap_mixed_text(d, a["description_en"], f_sub, f_sub_cjk, 840)
        lines = [(ln, f_sub, f_sub_cjk, CHARCOAL) for ln in wrapped[:3]]
        if used_chars:
            lines.append((f"Used consistently across {len(used_chars)} characters:", f_pill, f_pill_cjk, FOREST))
            lines.append((used_str, f_sub_bold, f_sub_bold_cjk, CHARCOAL))
        draw_bottom_card(d, 1355, lines, bottom_margin=90)
        card.save(SPRITE_CARDS_EN_DIR / f"{a['id']}_sprite.png")

    # 2. 181 English Character Cards (reusing illustrations/ & illustrations_composed/)
    accents = [TERRACOTTA, FOREST, MUSTARD]
    for idx, c in enumerate(chars):
        ch = c["char"]
        accent = accents[idx % len(accents)]
        ai_p = ILLUS_DIR / f"{ch}.jpg"
        if ai_p.exists():
            card = Image.open(ai_p).convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
            card = card.filter(ImageFilter.UnsharpMask(radius=1.2, percent=110, threshold=3))
        else:
            card = Image.open(COMPOSED_DIR / f"{ch}.png").convert("RGB")

        d = ImageDraw.Draw(card)
        badge = f"DEMO · #{c['id']}" if c.get("is_bonus_demo") else f"HSK 1 · #{c['id']}"
        draw_pill(d, 90, badge, f_pill, f_pill_cjk, accent, (255, 255, 255))
        draw_mixed_centered(d, 140, ch, f_hanzi_top, f_hanzi_top, CHARCOAL)
        draw_mixed_centered(d, 330, c["pinyin"], f_pinyin, f_pinyin, TERRACOTTA)
        draw_mixed_centered(d, 415, f"{c['layout_en']} · {c['radicals']}", f_small, f_small_cjk, MUTED)

        wrapped_story = wrap_mixed_text(d, c["mnemonic_en"], f_sub, f_sub_cjk, 890)
        lines = [(f"Meaning: {c['meaning_en'].capitalize()}", f_sub_bold, f_sub_bold_cjk, FOREST)]
        for ln in wrapped_story[:4]:
            lines.append((ln, f_sub, f_sub_cjk, CHARCOAL))
        draw_bottom_card(d, 1415, lines, bottom_margin=75)
        card.save(CARDS_EN_DIR / f"{ch}_card.png")

    # 3. 155 English Vocab Cards (reusing existing tiles)
    for v in vocab:
        word = v["word"]
        chs = v["chars"]
        if len(chs) == 1:
            shutil.copy2(CARDS_EN_DIR / f"{chs[0]}_card.png", VOCAB_CARDS_EN_DIR / f"{word}_card.png")
            continue

        card = Image.new("RGB", (W, H), BG_COLOR)
        d = ImageDraw.Draw(card)
        draw_pill(d, 90, f"HSK 1 #{v['id']} · VOCABULARY", f_pill, f_pill_cjk, TERRACOTTA, (255, 255, 255))
        word_font = f_hanzi_top if len(chs) <= 2 else load_font(FONT_CJK, 138, index=0)
        draw_mixed_centered(d, 145, word, word_font, word_font, CHARCOAL)
        draw_mixed_centered(d, 340, v["pinyin"], f_pinyin, f_pinyin, FOREST)

        n = len(chs)
        if n == 2:
            tile_sz, gap, y_tile = 440, 48, 500
            start_x = (W - (2 * tile_sz + gap)) // 2
        else:
            tile_sz, gap, y_tile = 310, 28, 540
            start_x = (W - (3 * tile_sz + 2 * gap)) // 2

        for i, ch in enumerate(chs):
            ci = char_map[ch]
            tile = get_center_tile(ch).resize((tile_sz, tile_sz), Image.Resampling.LANCZOS)
            tx = start_x + i * (tile_sz + gap)
            card.paste(tile, (tx, y_tile))
            d.rounded_rectangle([tx, y_tile, tx + tile_sz, y_tile + tile_sz], radius=24, outline=CARD_BORDER, width=3)
            label_y = y_tile + tile_sz + 18
            lbl = f"{ch} ({ci['pinyin']})"
            tw, _, metrics = measure_mixed(d, lbl, f_sub_bold, f_sub_bold_cjk)
            cx = tx + (tile_sz - tw) // 2
            for sub, f, bb, w_sub, _ in metrics:
                d.text((cx - bb[0], label_y - bb[1]), sub, font=f, fill=CHARCOAL)
                cx += w_sub + 2

            mean_lbl = ci["meaning_en"].split(";")[0].split("/")[0].strip()
            mw, _, m_metrics = measure_mixed(d, mean_lbl, f_small, f_small_cjk)
            cx2 = tx + (tile_sz - mw) // 2
            for sub, f, bb, w_sub, _ in m_metrics:
                d.text((cx2 - bb[0], label_y + 48 - bb[1]), sub, font=f, fill=TERRACOTTA)
                cx2 += w_sub + 2

        summary_lines = [(f"Meaning: {v['meaning_en'].capitalize()}", f_sub_bold, f_sub_bold_cjk, FOREST)]
        for ch in chs:
            ci = char_map[ch]
            short_m = f"{ch}: {ci['radicals_en']} — {ci['mnemonic_en']}"
            wrapped = wrap_mixed_text(d, short_m, f_small, f_small_cjk, 870)
            line_txt = wrapped[0] if len(wrapped) == 1 else f"{wrapped[0].rstrip(' ,—-')}…"
            summary_lines.append((line_txt, f_small, f_small_cjk, CHARCOAL))
        draw_bottom_card(d, 1340, summary_lines[:4], bottom_margin=80)
        card.save(VOCAB_CARDS_EN_DIR / f"{word}_card.png")

    print(f"Rendered EN cards: {len(actors)} sprite_cards_en, {len(chars)} cards_en, {len(vocab)} vocab_cards_en")


async def synth_en_async(sem: asyncio.Semaphore, text: str, out_wav: Path, rate: str = "+2%", overwrite: bool = False) -> None:
    if not overwrite and out_wav.exists() and out_wav.stat().st_size > 1000:
        return
    mp3_path = out_wav.with_suffix(".mp3")
    async with sem:
        for attempt in range(3):
            try:
                proc = await asyncio.create_subprocess_exec(
                    EDGE_TTS, "--voice", VOICE_EN, "--rate", rate, "--text", text, "--write-media", str(mp3_path),
                    stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.PIPE,
                )
                _, stderr = await proc.communicate()
                if proc.returncode != 0:
                    raise RuntimeError(stderr.decode("utf-8", errors="ignore"))
                conv = await asyncio.create_subprocess_exec(
                    "afconvert", "-f", "WAVE", "-d", "LEI16@48000", "-c", "1", str(mp3_path), str(out_wav),
                    stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.PIPE,
                )
                _, c_err = await conv.communicate()
                if conv.returncode != 0:
                    raise RuntimeError(c_err.decode("utf-8", errors="ignore"))
                mp3_path.unlink(missing_ok=True)
                return
            except Exception as exc:
                if attempt == 2:
                    raise RuntimeError(f"EN TTS failed for '{text}': {exc}") from exc
                await asyncio.sleep(1.0 * (attempt + 1))


async def prewarm_en_audio(chars: list[dict], compound_words: list[tuple[str, str]], overwrite: bool = False) -> None:
    sem = asyncio.Semaphore(6)
    tasks = []
    for c in chars:
        ch = c["char"]
        tasks.append(synth_en_async(sem, f"{c['radicals_en']}. {c['mnemonic_en']}", CHAR_AUDIO_EN_DIR / f"{ch}_intro.wav", overwrite=overwrite))
        tasks.append(synth_en_async(sem, f"This character means {c['meaning_en']}.", CHAR_AUDIO_EN_DIR / f"{ch}_mean.wav", overwrite=overwrite))
    if compound_words:
        tasks.append(synth_en_async(sem, "Combined together:", WORD_AUDIO_EN_DIR / "comb_prefix.wav", overwrite=False))
        for word, m_en in compound_words:
            tasks.append(synth_en_async(sem, f"Meaning: {m_en}.", WORD_AUDIO_EN_DIR / f"{word}_meaning.wav", overwrite=overwrite))
    print(f"Pre-warming/verifying {len(tasks)} English TTS clips (reusing all Mandarin *_zh.wav)...", flush=True)
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


def build_en_intro_frame(c: dict, out_path: Path, overwrite: bool = False) -> Path:
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
    ai_p = ILLUS_DIR / f"{ch}.jpg"
    src_p = ai_p if ai_p.exists() else COMPOSED_DIR / f"{ch}.png"
    frame = Image.open(src_p).convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
    if ai_p.exists():
        frame = frame.filter(ImageFilter.UnsharpMask(radius=1.2, percent=110, threshold=3))

    d = ImageDraw.Draw(frame)
    badge = f"DEMO · #{c['id']} ACTOR SPRITE" if c.get("is_bonus_demo") else f"HSK 1 · #{c['id']} ACTOR SPRITE"
    draw_pill(d, 100, badge, f_pill, f_pill_cjk, FOREST, (255, 255, 255))
    actor_names = " + ".join(a["actor_name_en"] for a in c.get("actors", []))
    draw_mixed_centered(d, 180, f"{c['layout_en']} · {c['radicals']}", f_rad, f_rad_cjk, CHARCOAL)
    draw_mixed_centered(d, 250, actor_names, f_sub_bold, f_sub_bold_cjk, TERRACOTTA)

    wrapped = wrap_mixed_text(d, c["mnemonic_en"], f_sub, f_sub_cjk, 890)
    lines = [(f"Components: {c['radicals_en']}", f_sub_bold, f_sub_bold_cjk, FOREST)]
    for ln in wrapped[:4]:
        lines.append((ln, f_sub, f_sub_cjk, CHARCOAL))
    draw_bottom_card(d, 1415, lines, bottom_margin=75)
    frame.save(out_path)
    return out_path


def render_en_videos(chars: list[dict], vocab: list[dict], overwrite: bool = False) -> None:
    render_bin = TMP_DIR / "render_mp4"
    concat_bin = TMP_DIR / "concat_mp4"
    sil_lead = TMP_DIR / "sil_lead_028.wav"

    compound_list = [(v["word"], v["meaning_en"]) for v in vocab if v["char_count"] >= 2]
    compound_list.append(("休息", "to rest / take a break"))

    asyncio.run(prewarm_en_audio(chars, compound_list, overwrite=overwrite))

    # Phase A: 181 English 9:16 single-char videos (reusing char_audio/<ch>_zh.wav)
    for idx, c in enumerate(chars, start=1):
        ch = c["char"]
        out_mp4 = CHAR_VIDEOS_EN_DIR / f"{ch}.mp4"
        if not overwrite and out_mp4.exists() and out_mp4.stat().st_size > 10000:
            continue
        job_dir = TMP_DIR / f"char_job_en_{ch}"
        job_dir.mkdir(parents=True, exist_ok=True)
        intro_img = build_en_intro_frame(c, INTRO_FRAME_EN_DIR / f"{ch}.png", overwrite=overwrite)
        card_img = CARDS_EN_DIR / f"{ch}_card.png"

        s_intro = job_dir / "s_intro.wav"
        d_intro = concat_wavs([(sil_lead, 0.0), (CHAR_AUDIO_EN_DIR / f"{ch}_intro.wav", 0.45)], s_intro)
        s_mean = job_dir / "s_mean.wav"
        d_mean = concat_wavs(
            [(sil_lead, 0.0), (CHAR_AUDIO_EN_DIR / f"{ch}_mean.wav", 0.20), (CHAR_AUDIO_ZH_DIR / f"{ch}_zh.wav", 0.50)],
            s_mean,
        )
        full_wav = job_dir / "full_audio.wav"
        concat_wavs([(s_intro, 0.0), (s_mean, 0.0)], full_wav)
        subprocess.run(
            [str(render_bin), str(out_mp4), str(full_wav), f"{intro_img}:{d_intro:.4f}", f"{card_img}:{d_mean:.4f}"],
            check=True, stdout=subprocess.DEVNULL,
        )
        print(f"[EN Char {idx}/{len(chars)}] {out_mp4.name} ({out_mp4.stat().st_size // 1024} KB)", flush=True)

    # Phase B: 155 HSK 1 + 休息 English 9:16 vocab videos (copy 1-char or stitch char_videos_en + outro)
    all_targets = [(v["word"], v["chars"]) for v in vocab] + [("休息", ["休", "息"])]
    for idx, (word, chs) in enumerate(all_targets, start=1):
        out_mp4 = VIDEOS_EN_DIR / f"{word}.mp4"
        if len(chs) == 1:
            src = CHAR_VIDEOS_EN_DIR / f"{chs[0]}.mp4"
            if overwrite or not out_mp4.exists() or out_mp4.stat().st_size != src.stat().st_size:
                shutil.copy2(src, out_mp4)
            print(f"[EN Vocab {idx}/{len(all_targets)}] {out_mp4.name} [copy]", flush=True)
            continue

        outro_mp4 = WORD_OUTROS_EN_DIR / f"{word}_outro.mp4"
        if overwrite or not outro_mp4.exists() or outro_mp4.stat().st_size <= 5000:
            v_card = (WORKDIR / "xiuxi_card.png") if word == "休息" else (VOCAB_CARDS_EN_DIR / f"{word}_card.png")
            outro_wav = WORD_OUTROS_EN_DIR / f"{word}_outro.wav"
            dur = concat_wavs(
                [
                    (sil_lead, 0.0),
                    (WORD_AUDIO_EN_DIR / "comb_prefix.wav", 0.15),
                    (WORD_AUDIO_ZH_DIR / f"{word}_zh.wav", 0.25),
                    (WORD_AUDIO_EN_DIR / f"{word}_meaning.wav", 0.65),
                ],
                outro_wav,
            )
            subprocess.run(
                [str(render_bin), str(outro_mp4), str(outro_wav), f"{v_card}:{dur:.4f}"],
                check=True, stdout=subprocess.DEVNULL,
            )

        seg_inputs = [str(CHAR_VIDEOS_EN_DIR / f"{ch}.mp4") for ch in chs] + [str(outro_mp4)]
        subprocess.run([str(concat_bin), str(out_mp4), *seg_inputs], check=True, stdout=subprocess.DEVNULL)
        print(f"[EN Vocab {idx}/{len(all_targets)}] {out_mp4.name} [stitch({len(chs)}c+outro)] ({out_mp4.stat().st_size // 1024} KB)", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build English HSK 1 set reusing shared visuals & Mandarin audio.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing EN cards and videos.")
    args = parser.parse_args()

    actors, chars, vocab = enrich_bilingual_data()
    render_english_cards(actors, chars, vocab)
    render_en_videos(chars, vocab, overwrite=args.overwrite)


if __name__ == "__main__":
    main()
