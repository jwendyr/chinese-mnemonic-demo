#!/usr/bin/env python3
"""ScriptPedia: Automated Omniglot-inspired AI Writing Systems Encyclopedia (Grokipedia style)
integrated with all prepared mnemonic scripts, templates, stroke data, TTS audits, and MP4 exemplars.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
PLANS_DIR = ROOT / "plans"
OMNIGLOT_CACHE = PLANS_DIR / "omniglot_sources"
DOCS_DIR = ROOT / "docs"


class OmniglotHTMLParser(HTMLParser):
    """Lightweight HTML parser extracting headings, paragraphs, and first sample/feature blocks from Omniglot."""

    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self.in_title = False
        self.current_tag: str | None = None
        self.current_heading = ""
        self.sections: list[tuple[str, list[str]]] = []
        self._buf: list[str] = []
        self._active_heading = "Overview"
        self._active_paras: list[str] = []
        self.skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("script", "style", "noscript"):
            self.skip_depth += 1
            return
        if self.skip_depth:
            return
        if tag == "title":
            self.in_title = True
        elif tag in ("h1", "h2", "h3", "p", "li"):
            self.current_tag = tag
            self._buf = []

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style", "noscript"):
            self.skip_depth = max(0, self.skip_depth - 1)
            return
        if self.skip_depth:
            return
        if tag == "title":
            self.in_title = False
        elif tag == self.current_tag:
            text = re.sub(r"\s+", " ", html.unescape("".join(self._buf))).strip()
            if text:
                if tag in ("h1", "h2", "h3"):
                    if self._active_paras:
                        self.sections.append((self._active_heading, self._active_paras))
                    self._active_heading = text
                    self._active_paras = []
                else:
                    self._active_paras.append(text)
            self.current_tag = None
            self._buf = []

    def handle_data(self, data: str) -> None:
        if self.skip_depth:
            return
        if self.in_title:
            self.title += data
        elif self.current_tag:
            self._buf.append(data)

    def close(self) -> None:
        super().close()
        if self._active_paras:
            self.sections.append((self._active_heading, self._active_paras))


def fetch_omniglot(url: str, slug: str, refresh: bool = False) -> dict[str, Any]:
    OMNIGLOT_CACHE.mkdir(parents=True, exist_ok=True)
    cache_file = OMNIGLOT_CACHE / f"{slug}.json"
    if cache_file.exists() and not refresh:
        return json.loads(cache_file.read_text(encoding="utf-8"))

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "ScriptPedia-Bot/1.0 (Educational Writing Systems Encyclopedia)"},
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        parser = OmniglotHTMLParser()
        parser.feed(raw)
        parser.close()
        sec_map: dict[str, list[str]] = {}
        for h, paras in parser.sections:
            sec_map[h] = paras[:5]

        def find_sec(keywords: tuple[str, ...]) -> list[str]:
            for h, paras in parser.sections:
                hl = h.lower()
                if any(k in hl for k in keywords):
                    return paras[:4]
            return []

        data = {
            "slug": slug,
            "omniglot_url": url,
            "title": re.sub(r"\s+", " ", parser.title).strip(),
            "at_a_glance": find_sec(("at a glance",)),
            "history": find_sec(("history", "origin")),
            "notable_features": find_sec(("notable features",)),
            "sample_text": find_sec(("sample text",)),
        }
    except Exception as exc:
        data = {
            "slug": slug,
            "omniglot_url": url,
            "title": slug.title(),
            "at_a_glance": [],
            "history": [],
            "notable_features": [],
            "sample_text": [],
            "fetch_note": str(exc),
        }
    cache_file.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return data


SCRIPTS: list[dict[str, Any]] = [
    {
        "slug": "mandarin-hsk1",
        "name_id": "Mandarin Sederhana (HSK 3.0 Level 1)",
        "name_en": "Simplified Chinese (HSK 3.0 Level 1)",
        "native_name": "简体中文 · 汉字",
        "type_key": "logographic",
        "type_id": "Logografis / Semanto-Fonetik",
        "type_en": "Logographic / Semanto-phonetic",
        "direction": "Kiri ke kanan (horizontal) / Atas ke bawah (klasik)",
        "origin": "Tiongkok Kuno (aksara tulang orakel ~1200 SM; penyederhanaan RRT 1956)",
        "tts_voice": "zh-CN-XiaoxiaoNeural",
        "omniglot_url": "https://omniglot.com/chinese/mandarin.htm",
        "prompt_file": "plans/hsk1_full_ready_prompts.json",
        "summary_id": "277 karakter inti HSK 3.0 Level 1 dengan komponen mnemonik visual bergaya kuas Kaiti, urutan guratan terverifikasi, serta 11 video eksemplar ID & EN yang sudah terender.",
        "summary_en": "277 core HSK 3.0 Level 1 characters with Kaiti brush visual mnemonic components, verified stroke data, and 11 rendered bilingual ID & EN exemplar videos.",
    },
    {
        "slug": "taiwan-tbcl1",
        "name_id": "Mandarin Tradisional Taiwan (TBCL Level 1)",
        "name_en": "Traditional Chinese — Taiwan (TBCL Level 1)",
        "native_name": "正體中文 · 繁體字",
        "type_key": "logographic",
        "type_id": "Logografis / Semanto-Fonetik",
        "type_en": "Logographic / Semanto-phonetic",
        "direction": "Kiri ke kanan atau atas ke bawah",
        "origin": "Aksara Han Klasik (Dinasti Han; standar resmi Taiwan)",
        "tts_voice": "zh-TW-HsiaoChenNeural",
        "omniglot_url": "https://omniglot.com/writing/chinese.htm",
        "prompt_file": "plans/tbcl1_full_ready_prompts.json",
        "summary_id": "246 aksara tradisional standar TBCL Level 1 lengkap dengan Pinyin, Zhuyin (Bopomofo), serta glos Indonesia & Inggris.",
        "summary_en": "246 Taiwan TBCL Level 1 traditional characters complete with Pinyin, Zhuyin (Bopomofo), and Indonesian & English glosses.",
    },
    {
        "slug": "cantonese",
        "name_id": "Kanton Hong Kong (Pemula)",
        "name_en": "Hong Kong Cantonese (Beginner)",
        "native_name": "廣東話 · 粵語",
        "type_key": "logographic",
        "type_id": "Logografis + Karakter Vernakular Kanton",
        "type_en": "Logographic + Cantonese Vernacular Characters",
        "direction": "Kiri ke kanan",
        "origin": "Tiongkok Selatan (Guangdong & Hong Kong; standar Jyutping)",
        "tts_voice": "zh-HK-HiuMaanNeural",
        "omniglot_url": "https://omniglot.com/chinese/cantonese.htm",
        "prompt_file": "plans/kanton_full_ready_prompts.json",
        "summary_id": "184 kosakata & aksara Kanton pemula termasuk karakter khusus lisan seperti 佢, 係, 喺, 唔, 冇, 嘅, 咗, 緊 dengan romanisasi Jyutping.",
        "summary_en": "184 beginner Cantonese words & characters including vernacular glyphs like 佢, 係, 喺, 唔, 冇, 嘅, 咗, 緊 with Jyutping romanization.",
    },
    {
        "slug": "bopomofo",
        "name_id": "Bopomofo / Zhuyin Fuhao",
        "name_en": "Bopomofo (Zhuyin Fuhao)",
        "native_name": "注音符號 · ㄅㄆㄇㄈ",
        "type_key": "featural",
        "type_id": "Sistem Fonetik Semi-Silabik",
        "type_en": "Semi-syllabic Phonetic Script",
        "direction": "Kiri ke kanan atau vertikal (anotasi Ruby)",
        "origin": "Tiongkok 1913 (dipertahankan sebagai standar fonetik di Taiwan)",
        "tts_voice": "zh-TW-HsiaoChenNeural",
        "omniglot_url": "https://omniglot.com/writing/zhuyin.htm",
        "prompt_file": "plans/bopomofo_ready_prompts.json",
        "summary_id": "37 simbol fonetik Bopomofo (21 konsonan awal, 3 medial, 13 vokal/akhir) beserta aturan 5 nada Taiwan.",
        "summary_en": "37 Bopomofo phonetic symbols (21 initials, 3 medials, 13 finals) with Taiwan's 5-tone system.",
    },
    {
        "slug": "hiragana",
        "name_id": "Jepang Hiragana",
        "name_en": "Japanese Hiragana",
        "native_name": "平仮名 · ひらがな",
        "type_key": "syllabary",
        "type_id": "Silabarium (Moraik)",
        "type_en": "Syllabary (Moraic)",
        "direction": "Kiri ke kanan atau vertikal",
        "origin": "Jepang Abad ke-9 (berkembang dari gaya kursif Man'yōgana)",
        "tts_voice": "ja-JP-NanamiNeural",
        "omniglot_url": "https://omniglot.com/writing/hiragana.htm",
        "prompt_file": "plans/kana_ready_prompts.json",
        "filter_field": ("script", "hiragana"),
        "summary_id": "46 kana dasar Hiragana dengan data vektor guratan KanjiVG, template kuas membulat, dan narasi mnemonik ID/EN.",
        "summary_en": "46 core Hiragana syllabograms with KanjiVG vector strokes, rounded brush templates, and bilingual ID/EN mnemonics.",
    },
    {
        "slug": "katakana",
        "name_id": "Jepang Katakana",
        "name_en": "Japanese Katakana",
        "native_name": "片仮名 · カタカナ",
        "type_key": "syllabary",
        "type_id": "Silabarium (Moraik)",
        "type_en": "Syllabary (Moraic)",
        "direction": "Kiri ke kanan atau vertikal",
        "origin": "Jepang Abad ke-9 (fragmen guratan Kanji oleh biksu Buddha)",
        "tts_voice": "ja-JP-NanamiNeural",
        "omniglot_url": "https://omniglot.com/writing/katakana.htm",
        "prompt_file": "plans/kana_ready_prompts.json",
        "filter_field": ("script", "katakana"),
        "summary_id": "46 kana dasar Katakana untuk kata serapan, onomatope, dan penekanan visual dengan data guratan KanjiVG.",
        "summary_en": "46 core Katakana syllabograms for loanwords, onomatopoeia, and emphasis with KanjiVG stroke data.",
    },
    {
        "slug": "devanagari",
        "name_id": "Aksara Devanagari",
        "name_en": "Devanagari Script",
        "native_name": "देवनागरी",
        "type_key": "abugida",
        "type_id": "Abugida / Alfasilabarium",
        "type_en": "Abugida / Alphasyllabary",
        "direction": "Kiri ke kanan (disatukan garis atap shirorekha)",
        "origin": "India (turunan aksara Brahmi & Gupta ~Abad ke-10 M)",
        "tts_voice": "hi-IN-SwaraNeural",
        "omniglot_url": "https://omniglot.com/writing/devanagari.htm",
        "prompt_file": "plans/devanagari_ready_prompts.json",
        "summary_id": "46 aksara inti Devanagari (13 vokal Swara + 33 konsonan Vyanjana) dipakai untuk bahasa Hindi, Sanskerta, Marathi, dan Nepali.",
        "summary_en": "46 core Devanagari characters (13 Swara vowels + 33 Vyanjana consonants) used for Hindi, Sanskrit, Marathi, and Nepali.",
    },
    {
        "slug": "greek",
        "name_id": "Alfabet Yunani",
        "name_en": "Greek Alphabet",
        "native_name": "Ελληνικό αλφάβητο",
        "type_key": "alphabet",
        "type_id": "Alfabet Sejati (Vokal & Konsonan)",
        "type_en": "True Alphabet (Vowels & Consonants)",
        "direction": "Kiri ke kanan",
        "origin": "Yunani Kuno (~Abad ke-8 SM dari aksara Fenisia)",
        "tts_voice": "el-GR-AthinaNeural",
        "omniglot_url": "https://omniglot.com/writing/greek.htm",
        "prompt_file": "plans/yunani_ready_prompts.json",
        "summary_id": "24 huruf Yunani berpasangan besar & kecil (Α α sampai Ω ω) lengkap dengan bunyi modern, catatan sains, dan mnemonik bentuk.",
        "summary_en": "24 paired uppercase & lowercase Greek letters (Α α through Ω ω) with modern pronunciation, science usage, and shape mnemonics.",
    },
    {
        "slug": "particles",
        "name_id": "Partikel Tata Bahasa Mandarin & Jepang",
        "name_en": "Mandarin & Japanese Grammar Particles",
        "native_name": "的 · 了 · は · が · を",
        "type_key": "grammar",
        "type_id": "Partikel Struktural & Wacana",
        "type_en": "Structural & Discourse Particles",
        "direction": "Kiri ke kanan",
        "origin": "Mandarin Modern (HSK 3.0 L1) & Bahasa Jepang",
        "tts_voice": "zh-CN-XiaoxiaoNeural / ja-JP-NanamiNeural",
        "omniglot_url": "https://omniglot.com/writing/japanese.htm",
        "prompt_file": "plans/partikel_ready_prompts.json",
        "summary_id": "18 pelajaran partikel dua-tahap (8 partikel Mandarin HSK 3.0 Level 1 + 10 partikel Jepang) untuk visualisasi peran gramatikal.",
        "summary_en": "18 two-beat particle lessons (8 HSK 3.0 Level 1 Mandarin particles + 10 Japanese particles) visualizing grammatical roles.",
    },
]


def load_entries(spec: dict[str, Any]) -> list[dict[str, Any]]:
    raw = json.loads((ROOT / spec["prompt_file"]).read_text(encoding="utf-8"))
    if "filter_field" in spec:
        fk, fv = spec["filter_field"]
        raw = [x for x in raw if x.get(fk) == fv]
    return raw


def normalize_entry(spec: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    glyph = (
        row.get("char")
        or row.get("glyph")
        or row.get("kana")
        or row.get("symbol")
        or row.get("traditional")
        or (f"{row['upper']} {row['lower']}" if "upper" in row else "")
        or row.get("particle", "?")
    )
    reading = (
        row.get("reading")
        or row.get("pinyin")
        or row.get("jyutping")
        or row.get("romaji")
        or row.get("sound")
        or row.get("zhuyin")
        or row.get("name", "")
    )
    meaning_id = row.get("meaning_id") or row.get("stage_1_id") or row.get("stage_desc_id") or row.get("meaning_id_en") or row.get("name", "")
    meaning_en = row.get("meaning_en") or row.get("stage_1_en") or row.get("stage_desc_en") or row.get("meaning_id_en") or row.get("name", "")
    tpl = row.get("template_path", "")
    tpl_rel = f"../../{tpl}" if tpl and (ROOT / tpl).exists() else ""

    # Check if rendered MP4 exemplar exists
    char_key = row.get("char", "")
    vid_id = ""
    vid_en = ""
    if char_key:
        for rel_id in (f"char_videos/{char_key}.mp4", f"videos/{char_key}.mp4"):
            if (ROOT / rel_id).exists():
                vid_id = f"../../{rel_id}"
                break
        for rel_en in (f"char_videos_en/{char_key}.mp4", f"videos_en/{char_key}.mp4"):
            if (ROOT / rel_en).exists():
                vid_en = f"../../{rel_en}"
                break

    return {
        "glyph": glyph,
        "reading": reading,
        "meaning_id": meaning_id,
        "meaning_en": meaning_en,
        "tts_id": " ".join((row.get("tts_id") or {}).values()),
        "tts_en": " ".join((row.get("tts_en") or {}).values()),
        "image_prompt": row.get("image_prompt", ""),
        "template_rel": tpl_rel,
        "video_id": vid_id,
        "video_en": vid_en,
        "status": row.get("status", "ready"),
    }


CSS_TEXT = """
:root {
  --bg: #F9F5EC;
  --surface: #FFFDF8;
  --ink: #1E2D4A;
  --muted: #5B677D;
  --accent: #C85A32;
  --border: #E2D9C8;
  --pill-bg: #EFE7D6;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
  background: var(--bg);
  color: var(--ink);
  line-height: 1.55;
}
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
header.topbar {
  position: sticky; top: 0; z-index: 20;
  background: rgba(249, 245, 236, 0.94);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--border);
  padding: 0.8rem 1.5rem;
  display: flex; align-items: center; justify-content: space-between; gap: 1rem; flex-wrap: wrap;
}
.brand { font-weight: 800; font-size: 1.15rem; letter-spacing: -0.02em; color: var(--ink); }
.brand span { color: var(--accent); }
.lang-toggle {
  display: inline-flex; border: 1px solid var(--border); border-radius: 999px; overflow: hidden; background: var(--surface);
}
.lang-toggle button {
  border: 0; background: transparent; padding: 0.35rem 0.85rem; font-weight: 600; cursor: pointer; color: var(--muted);
}
.lang-toggle button.active { background: var(--ink); color: #fff; }
main { max-width: 1180px; margin: 0 auto; padding: 1.8rem 1.4rem 4rem; }
.hero {
  background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 1.8rem; margin-bottom: 1.6rem;
}
.hero h1 { margin: 0 0 0.5rem; font-size: clamp(1.6rem, 3vw, 2.3rem); line-height: 1.2; }
.stats-row { display: flex; gap: 1rem; flex-wrap: wrap; margin-top: 1rem; }
.stat-pill {
  background: var(--pill-bg); padding: 0.45rem 0.9rem; border-radius: 999px; font-size: 0.9rem; font-weight: 600;
}
.controls { display: flex; gap: 0.8rem; flex-wrap: wrap; margin-bottom: 1.4rem; align-items: center; }
.controls input[type="search"] {
  flex: 1 1 260px; padding: 0.65rem 1rem; border-radius: 10px; border: 1px solid var(--border);
  background: var(--surface); color: var(--ink); font-size: 0.95rem;
}
.filter-pills { display: flex; gap: 0.45rem; flex-wrap: wrap; }
.filter-pills button {
  border: 1px solid var(--border); background: var(--surface); color: var(--ink);
  padding: 0.45rem 0.85rem; border-radius: 999px; cursor: pointer; font-size: 0.85rem; font-weight: 600;
}
.filter-pills button.active { background: var(--accent); color: #fff; border-color: var(--accent); }
.script-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(310px, 1fr)); gap: 1rem; }
.script-card {
  background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 1.25rem;
  display: flex; flex-direction: column; justify-content: space-between; transition: transform 0.12s ease, border-color 0.12s ease;
}
.script-card:hover { transform: translateY(-2px); border-color: var(--accent); }
.script-native { font-size: 1.45rem; font-weight: 700; color: var(--accent); margin-bottom: 0.25rem; }
.script-meta { font-size: 0.82rem; color: var(--muted); margin-bottom: 0.6rem; }
.infobox {
  background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 1.2rem; margin-bottom: 1.5rem;
  display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 0.9rem;
}
.infobox dt { font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--muted); font-weight: 700; }
.infobox dd { margin: 0.15rem 0 0; font-weight: 600; }
.omni-box {
  background: var(--surface); border-left: 4px solid var(--accent); border-radius: 10px;
  padding: 1rem 1.2rem; margin-bottom: 1.5rem; border-top: 1px solid var(--border); border-right: 1px solid var(--border); border-bottom: 1px solid var(--border);
}
.glyph-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(175px, 1fr)); gap: 0.85rem; }
.glyph-card {
  background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 0.95rem;
  cursor: pointer; text-align: left; transition: border-color 0.12s ease, transform 0.12s ease;
}
.glyph-card:hover { border-color: var(--accent); transform: translateY(-2px); }
.glyph-big { font-size: 2.3rem; font-weight: 700; color: var(--ink); line-height: 1.15; }
.glyph-reading { font-size: 0.88rem; font-weight: 700; color: var(--accent); margin-top: 0.25rem; }
.glyph-meaning { font-size: 0.84rem; color: var(--muted); margin-top: 0.2rem; }
.badge-video {
  display: inline-block; margin-top: 0.4rem; font-size: 0.72rem; font-weight: 700;
  background: #1E2D4A; color: #fff; padding: 0.15rem 0.5rem; border-radius: 999px;
}
dialog#entryModal {
  max-width: 760px; width: 92vw; border: 1px solid var(--border); border-radius: 16px;
  background: var(--surface); color: var(--ink); padding: 1.4rem;
}
dialog#entryModal::backdrop { background: rgba(30, 45, 74, 0.5); }
.modal-layout { display: grid; grid-template-columns: 1fr 1.4fr; gap: 1.2rem; align-items: start; }
@media (max-width: 680px) { .modal-layout { grid-template-columns: 1fr; } }
.modal-media img, .modal-media video { width: 100%; border-radius: 10px; border: 1px solid var(--border); background: var(--bg); }
.prompt-box {
  background: var(--bg); border: 1px solid var(--border); border-radius: 8px; padding: 0.75rem; font-size: 0.82rem; white-space: pre-wrap;
}
"""

JS_TEXT = """
(function() {
  const saved = localStorage.getItem('scriptpedia_lang') || 'id';
  function applyLang(lang) {
    localStorage.setItem('scriptpedia_lang', lang);
    document.querySelectorAll('[data-id][data-en]').forEach(el => {
      el.textContent = lang === 'en' ? el.dataset.en : el.dataset.id;
    });
    document.querySelectorAll('.lang-toggle button').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.lang === lang);
    });
  }
  document.querySelectorAll('.lang-toggle button').forEach(btn => {
    btn.addEventListener('click', () => applyLang(btn.dataset.lang));
  });
  applyLang(saved);

  const searchInput = document.getElementById('searchInput');
  const filterButtons = document.querySelectorAll('.filter-pills button');
  let activeType = 'all';
  function runFilter() {
    const q = (searchInput ? searchInput.value : '').trim().toLowerCase();
    document.querySelectorAll('[data-searchable]').forEach(card => {
      const hay = card.dataset.searchable.toLowerCase();
      const t = card.dataset.type || 'all';
      const okType = activeType === 'all' || t === activeType;
      const okQ = !q || hay.includes(q);
      card.style.display = (okType && okQ) ? '' : 'none';
    });
  }
  if (searchInput) searchInput.addEventListener('input', runFilter);
  filterButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      activeType = btn.dataset.filter;
      filterButtons.forEach(b => b.classList.toggle('active', b === btn));
      runFilter();
    });
  });

  const modal = document.getElementById('entryModal');
  if (modal) {
    document.querySelectorAll('.glyph-card').forEach(card => {
      card.addEventListener('click', () => {
        const d = JSON.parse(card.dataset.entry);
        const lang = localStorage.getItem('scriptpedia_lang') || 'id';
        document.getElementById('mGlyph').textContent = d.glyph;
        document.getElementById('mReading').textContent = d.reading;
        document.getElementById('mMeaning').textContent = lang === 'en' ? d.meaning_en : d.meaning_id;
        document.getElementById('mTts').textContent = lang === 'en' ? d.tts_en : d.tts_id;
        document.getElementById('mPrompt').textContent = d.image_prompt || '-';
        const media = document.getElementById('mMedia');
        media.innerHTML = '';
        const vid = lang === 'en' ? (d.video_en || d.video_id) : (d.video_id || d.video_en);
        if (vid) {
          media.innerHTML = `<video controls playsinline preload="metadata" src="${vid}"></video>`;
        } else if (d.template_rel) {
          media.innerHTML = `<img alt="${d.glyph}" src="${d.template_rel}" loading="lazy">`;
        }
        modal.showModal();
      });
    });
    document.getElementById('mClose').addEventListener('click', () => modal.close());
  }
})();
"""


def build_site(refresh_omniglot: bool = False) -> None:
    (DOCS_DIR / "assets").mkdir(parents=True, exist_ok=True)
    (DOCS_DIR / "scripts").mkdir(parents=True, exist_ok=True)
    (DOCS_DIR / "assets" / "style.css").write_text(CSS_TEXT.strip() + "\n", encoding="utf-8")
    (DOCS_DIR / "assets" / "app.js").write_text(JS_TEXT.strip() + "\n", encoding="utf-8")

    total_entries = 0
    total_videos = 0
    script_cards_html = []

    for spec in SCRIPTS:
        omni = fetch_omniglot(spec["omniglot_url"], spec["slug"], refresh=refresh_omniglot)
        raw_rows = load_entries(spec)
        entries = [normalize_entry(spec, r) for r in raw_rows]
        vid_count = sum(1 for e in entries if e["video_id"] or e["video_en"])
        total_entries += len(entries)
        total_videos += vid_count

        # Build individual encyclopedia page
        omni_history = " ".join(omni.get("history", [])[:2])
        omni_features = omni.get("notable_features", [])[:3]
        omni_sample = " ".join(omni.get("sample_text", [])[:2])

        cards_html = []
        for e in entries:
            entry_json = html.escape(json.dumps(e, ensure_ascii=False))
            search_blob = html.escape(f"{e['glyph']} {e['reading']} {e['meaning_id']} {e['meaning_en']}")
            badge = '<span class="badge-video">▶ MP4 Ready</span>' if (e["video_id"] or e["video_en"]) else ""
            cards_html.append(
                f'<button class="glyph-card" data-searchable="{search_blob}" data-entry="{entry_json}">'
                f'<div class="glyph-big">{html.escape(e["glyph"])}</div>'
                f'<div class="glyph-reading">{html.escape(e["reading"])}</div>'
                f'<div class="glyph-meaning" data-id="{html.escape(e["meaning_id"])}" data-en="{html.escape(e["meaning_en"])}">{html.escape(e["meaning_id"])}</div>'
                f"{badge}</button>"
            )

        omni_block = ""
        if omni_history or omni_features or omni_sample:
            feat_lis = "".join(f"<li>{html.escape(f)}</li>" for f in omni_features)
            omni_block = f"""
            <section class="omni-box">
              <strong data-id="Ringkasan Ensiklopedia (Sumber Omniglot)" data-en="Encyclopedia Summary (Omniglot Reference)">Ringkasan Ensiklopedia (Sumber Omniglot)</strong>
              {f'<p>{html.escape(omni_history)}</p>' if omni_history else ''}
              {f'<ul>{feat_lis}</ul>' if feat_lis else ''}
              {f'<p><em>Sample:</em> {html.escape(omni_sample)}</p>' if omni_sample else ''}
              <p><a href="{html.escape(spec['omniglot_url'])}" target="_blank" rel="noopener">Omniglot Reference ↗</a></p>
            </section>
            """

        page_html = f"""<!doctype html>
<html lang="id">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(spec['name_en'])} — ScriptPedia</title>
  <link rel="stylesheet" href="../assets/style.css">
</head>
<body>
  <header class="topbar">
    <a class="brand" href="../index.html">Script<span>Pedia</span></a>
    <div class="lang-toggle" role="group" aria-label="Language">
      <button type="button" data-lang="id">ID</button>
      <button type="button" data-lang="en">EN</button>
    </div>
  </header>
  <main>
    <p><a href="../index.html" data-id="← Semua Sistem Tulisan" data-en="← All Writing Systems">← Semua Sistem Tulisan</a></p>
    <section class="hero">
      <div class="script-native">{html.escape(spec['native_name'])}</div>
      <h1 data-id="{html.escape(spec['name_id'])}" data-en="{html.escape(spec['name_en'])}">{html.escape(spec['name_id'])}</h1>
      <p data-id="{html.escape(spec['summary_id'])}" data-en="{html.escape(spec['summary_en'])}">{html.escape(spec['summary_id'])}</p>
    </section>
    <dl class="infobox">
      <div><dt data-id="Jenis Aksara" data-en="Script Type">Jenis Aksara</dt><dd data-id="{html.escape(spec['type_id'])}" data-en="{html.escape(spec['type_en'])}">{html.escape(spec['type_id'])}</dd></div>
      <div><dt data-id="Arah Penulisan" data-en="Direction">Arah Penulisan</dt><dd>{html.escape(spec['direction'])}</dd></div>
      <div><dt data-id="Asal & Sejarah" data-en="Origin">Asal & Sejarah</dt><dd>{html.escape(spec['origin'])}</dd></div>
      <div><dt data-id="Suara TTS Native" data-en="Native TTS Voice">Suara TTS Native</dt><dd><code>{html.escape(spec['tts_voice'])}</code></dd></div>
      <div><dt data-id="Entri Siap" data-en="Prepared Entries">Entri Siap</dt><dd>{len(entries)}</dd></div>
    </dl>
    {omni_block}
    <div class="controls">
      <input id="searchInput" type="search" placeholder="Cari huruf, bunyi, atau arti / Search glyph, sound, or meaning...">
    </div>
    <section class="glyph-grid">
      {"".join(cards_html)}
    </section>
  </main>
  <dialog id="entryModal">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.8rem;">
      <strong id="mGlyph" style="font-size:1.8rem;"></strong>
      <button id="mClose" type="button" style="border:1px solid var(--border);background:var(--bg);border-radius:8px;padding:0.35rem 0.75rem;cursor:pointer;font-weight:700;">✕</button>
    </div>
    <div class="modal-layout">
      <div class="modal-media" id="mMedia"></div>
      <div>
        <p><strong id="mReading" style="color:var(--accent);"></strong> — <span id="mMeaning"></span></p>
        <p><strong data-id="Naskah TTS" data-en="TTS Script">Naskah TTS</strong></p>
        <div class="prompt-box" id="mTts"></div>
        <p style="margin-top:0.8rem;"><strong data-id="Prompt Ilustrasi" data-en="Illustration Prompt">Prompt Ilustrasi</strong></p>
        <div class="prompt-box" id="mPrompt"></div>
      </div>
    </div>
  </dialog>
  <script src="../assets/app.js"></script>
</body>
</html>
"""
        (DOCS_DIR / "scripts" / f"{spec['slug']}.html").write_text(page_html, encoding="utf-8")

        search_meta = html.escape(f"{spec['name_id']} {spec['name_en']} {spec['native_name']} {spec['type_id']} {spec['type_en']}")
        script_cards_html.append(
            f'<a class="script-card" href="scripts/{spec["slug"]}.html" data-searchable="{search_meta}" data-type="{spec["type_key"]}">'
            f'<div><div class="script-native">{html.escape(spec["native_name"])}</div>'
            f'<h2 style="margin:0 0 0.25rem;font-size:1.15rem;color:var(--ink);" data-id="{html.escape(spec["name_id"])}" data-en="{html.escape(spec["name_en"])}">{html.escape(spec["name_id"])}</h2>'
            f'<div class="script-meta" data-id="{html.escape(spec["type_id"])} · {len(entries)} entri" data-en="{html.escape(spec["type_en"])} · {len(entries)} entries">{html.escape(spec["type_id"])} · {len(entries)} entri</div>'
            f'<p style="margin:0;color:var(--muted);font-size:0.9rem;" data-id="{html.escape(spec["summary_id"])}" data-en="{html.escape(spec["summary_en"])}">{html.escape(spec["summary_id"])}</p></div>'
            f'<div style="margin-top:0.9rem;font-weight:700;font-size:0.85rem;color:var(--accent);">Buka Ensiklopedia →</div>'
            f"</a>"
        )

    index_html = f"""<!doctype html>
<html lang="id">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ScriptPedia — Automated Writing Systems & Mnemonic Encyclopedia</title>
  <link rel="stylesheet" href="assets/style.css">
</head>
<body>
  <header class="topbar">
    <span class="brand">Script<span>Pedia</span> · Omniglot-Style AI Encyclopedia</span>
    <div class="lang-toggle" role="group" aria-label="Language">
      <button type="button" data-lang="id">ID</button>
      <button type="button" data-lang="en">EN</button>
    </div>
  </header>
  <main>
    <section class="hero">
      <h1 data-id="Ensiklopedia Sistem Tulisan & Mnemonik Visual" data-en="Writing Systems & Visual Mnemonic Encyclopedia">Ensiklopedia Sistem Tulisan & Mnemonik Visual</h1>
      <p data-id="Dibangun otomatis dengan struktur taksonomi ala Omniglot dan penyajian ringkas ala Grokipedia — menggabungkan data sejarah aksara, fonetik IPA/TTS, guratan vektor, template 9:16, dan video mnemonik." data-en="Automatically generated with Omniglot-style script taxonomy and Grokipedia-style structured synthesis — uniting script history, IPA/TTS phonetics, vector strokes, 9:16 templates, and mnemonic videos.">Dibangun otomatis dengan struktur taksonomi ala Omniglot dan penyajian ringkas ala Grokipedia — menggabungkan data sejarah aksara, fonetik IPA/TTS, guratan vektor, template 9:16, dan video mnemonik.</p>
      <div class="stats-row">
        <span class="stat-pill">{len(SCRIPTS)} Sistem Tulisan / Tracks</span>
        <span class="stat-pill">{total_entries} Huruf & Pelajaran Siap</span>
        <span class="stat-pill">{total_videos} Eksemplar Video Terender</span>
      </div>
    </section>
    <div class="controls">
      <input id="searchInput" type="search" placeholder="Cari bahasa, aksara, atau tipe tulisan / Search script or family...">
      <div class="filter-pills">
        <button type="button" class="active" data-filter="all">All</button>
        <button type="button" data-filter="logographic">Logographic</button>
        <button type="button" data-filter="syllabary">Syllabary</button>
        <button type="button" data-filter="abugida">Abugida</button>
        <button type="button" data-filter="alphabet">Alphabet</button>
        <button type="button" data-filter="featural">Featural</button>
        <button type="button" data-filter="grammar">Grammar</button>
      </div>
    </div>
    <section class="script-grid">
      {"".join(script_cards_html)}
    </section>
  </main>
  <script src="assets/app.js"></script>
</body>
</html>
"""
    (DOCS_DIR / "index.html").write_text(index_html, encoding="utf-8")
    print(f"Built ScriptPedia in {DOCS_DIR}: {len(SCRIPTS)} scripts, {total_entries} entries, {total_videos} video links.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build ScriptPedia encyclopedia from Omniglot + local ready prompts")
    parser.add_argument("--refresh-omniglot", action="store_true", help="Force re-fetch Omniglot pages")
    parser.add_argument("--omniglot-url", help="Optional extra Omniglot URL to ingest & cache")
    parser.add_argument("--slug", help="Slug for --omniglot-url")
    args = parser.parse_args()

    if args.omniglot_url and args.slug:
        res = fetch_omniglot(args.omniglot_url, args.slug, refresh=True)
        print(f"Ingested {args.omniglot_url} -> plans/omniglot_sources/{args.slug}.json ({len(res.get('history', []))} history paras)")
    build_site(refresh_omniglot=args.refresh_omniglot)


if __name__ == "__main__":
    main()
