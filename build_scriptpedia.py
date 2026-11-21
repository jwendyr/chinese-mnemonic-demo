#!/usr/bin/env python3
"""ScriptPedia v2: Automated Omniglot-inspired + Grokipedia-style Writing Systems Encyclopedia.

Features:
- Omniglot-grade taxonomy (Alphabets, Abugidas, Syllabaries, Logographic, Featural, Grammar)
- Structured At-a-Glance infoboxes, Unicode ranges, Notable Features, UDHR/Classic Sample Texts
- Grouped orthographic views (Gojuon 5-column matrix for Kana, Place-of-Articulation for Devanagari,
  Onset/Medial/Final for Bopomofo, Vowels/Consonants for Greek, Topic groups for Cantonese, etc.)
- Interactive Modal with SVG Stroke-Order Animator (from stroke_data/*.json & kana_stroke_data/*.svg),
  Web Speech live pronunciation, MP4 video player, 9:16 template preview, TTS script, and AI prompt.
- Global cross-script search index on docs/index.html.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
PLANS_DIR = ROOT / "plans"
OMNIGLOT_CACHE = PLANS_DIR / "omniglot_sources"
DOCS_DIR = ROOT / "docs"
AUDIO_DIR = DOCS_DIR / "assets" / "audio"
EDGE_TTS = "/Volumes/App/Caches-And-Env/bin/edge-tts"


class OmniglotHTMLParser(HTMLParser):
    """Extracts headings, paragraphs, list items, and table cells from Omniglot pages."""

    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self.in_title = False
        self.current_tag: str | None = None
        self.sections: list[tuple[str, list[str]]] = []
        self._buf: list[str] = []
        self._active_heading = "Overview"
        self._active_items: list[str] = []
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
                    if self._active_items:
                        self.sections.append((self._active_heading, self._active_items))
                    self._active_heading = text
                    self._active_items = []
                else:
                    self._active_items.append(text)
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
        if self._active_items:
            self.sections.append((self._active_heading, self._active_items))


def fetch_omniglot(url: str, slug: str, refresh: bool = False) -> dict[str, Any]:
    OMNIGLOT_CACHE.mkdir(parents=True, exist_ok=True)
    cache_file = OMNIGLOT_CACHE / f"{slug}.json"
    if cache_file.exists() and not refresh:
        return json.loads(cache_file.read_text(encoding="utf-8"))

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "ScriptPedia-Bot/2.0 (Educational Writing Systems Encyclopedia)"},
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        parser = OmniglotHTMLParser()
        parser.feed(raw)
        parser.close()

        def find_sec(keywords: tuple[str, ...]) -> list[str]:
            for h, paras in parser.sections:
                if any(k in h.lower() for k in keywords):
                    return paras[:5]
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
        "unicode": "U+4E00–U+9FFF (CJK Unified Ideographs)",
        "direction": "Kiri ke kanan (horizontal) / Atas ke bawah (klasik)",
        "lineage": "Oracle Bone (~1200 SM) → Seal → Clerical → Regular (Kaiti) → Simplified (1956)",
        "languages": "Mandarin (Putonghua)",
        "speech_lang": "zh-CN",
        "tts_voice": "zh-CN-XiaoxiaoNeural",
        "omniglot_url": "https://omniglot.com/chinese/mandarin.htm",
        "prompt_file": "plans/hsk1_full_ready_prompts.json",
        "related": ["taiwan-tbcl1", "cantonese", "bopomofo", "particles"],
        "summary_id": "277 karakter inti HSK 3.0 Level 1 dengan dekomposisi radikal-fonetik kuas Kaiti, urutan guratan terverifikasi, serta video eksemplar ID & EN.",
        "summary_en": "277 core HSK 3.0 Level 1 characters with Kaiti brush radical-phonetic decomposition, verified stroke order, and bilingual ID & EN exemplar videos.",
        "features_id": [
            "Sebagian besar karakter adalah gabungan radikal makna (kiri/atas) dan komponen bunyi.",
            "Setiap karakter dibaca satu suku kata dengan 4 nada utama + 1 nada netral.",
            "Urutan guratan mengikuti aturan standar: atas ke bawah, kiri ke kanan, luar sebelum dalam.",
        ],
        "features_en": [
            "Most characters combine a semantic radical (meaning clue) with a phonetic component.",
            "Each character maps to one syllable carrying 4 main tones plus a neutral tone.",
            "Standard stroke order follows top-to-bottom, left-to-right, outside-before-inside.",
        ],
        "sample": {
            "native": "人人生而自由，在尊严和权利上一律平等。",
            "translit": "Rénrén shēng ér zìyóu, zài zūnyán hé quánlì shàng yīlǜ píngděng.",
            "id": "Semua orang dilahirkan merdeka dan mempunyai martabat serta hak yang sama.",
            "en": "All human beings are born free and equal in dignity and rights.",
        },
    },
    {
        "slug": "taiwan-tbcl1",
        "name_id": "Mandarin Tradisional Taiwan (TBCL Level 1)",
        "name_en": "Traditional Chinese — Taiwan (TBCL Level 1)",
        "native_name": "正體中文 · 繁體字",
        "type_key": "logographic",
        "type_id": "Logografis / Semanto-Fonetik",
        "type_en": "Logographic / Semanto-phonetic",
        "unicode": "U+4E00–U+9FFF (CJK Unified Ideographs)",
        "direction": "Kiri ke kanan atau vertikal (kanan ke kiri)",
        "lineage": "Clerical Script → Regular Script (Kaiti) → Standar Resmi Taiwan (MOE)",
        "languages": "Mandarin Taiwan (Guoyu), Hokkien Taiwan, Hakka",
        "speech_lang": "zh-TW",
        "tts_voice": "zh-TW-HsiaoChenNeural",
        "omniglot_url": "https://omniglot.com/writing/chinese.htm",
        "prompt_file": "plans/tbcl1_full_ready_prompts.json",
        "related": ["mandarin-hsk1", "bopomofo", "cantonese", "particles"],
        "summary_id": "246 aksara tradisional standar TBCL Level 1 lengkap dengan Pinyin, Zhuyin (Bopomofo), urutan guratan, serta glos Indonesia & Inggris.",
        "summary_en": "246 Taiwan TBCL Level 1 traditional characters with Pinyin, Zhuyin (Bopomofo), stroke order data, and Indonesian & English glosses.",
        "features_id": [
            "Mempertahankan struktur historis penuh sehingga petunjuk radikal sering lebih utuh (mis. 學, 國, 飛).",
            "Dipasangkan dengan anotasi fonetik Bopomofo (Zhuyin) di buku pelajaran dan kamus Taiwan.",
            "Masih sering dicetak vertikal dari atas ke bawah, kolom kanan ke kiri, untuk buku sastra.",
        ],
        "features_en": [
            "Preserves full historical forms where semantic radicals remain visually transparent (e.g. 學, 國, 飛).",
            "Paired with Bopomofo (Zhuyin) ruby annotations in Taiwan textbooks and dictionaries.",
            "Commonly typeset vertically top-to-bottom, right-to-left in Taiwanese literature.",
        ],
        "sample": {
            "native": "人人生而自由，在尊嚴和權利上一律平等。",
            "translit": "ㄖㄣˊ ㄖㄣˊ ㄕㄥ ㄦˊ ㄗˋ ㄧㄡˊ，ㄗㄞˋ ㄗㄨㄣ ㄧㄢˊ ㄏㄜˊ ㄑㄩㄢˊ ㄌㄧˋ ㄕㄤˋ ㄧ ㄌㄩˋ ㄆㄧㄥˊ ㄉㄥˇ。",
            "id": "Semua orang dilahirkan merdeka dan mempunyai martabat serta hak yang sama.",
            "en": "All human beings are born free and equal in dignity and rights.",
        },
    },
    {
        "slug": "cantonese",
        "name_id": "Kanton Hong Kong (Pemula)",
        "name_en": "Hong Kong Cantonese (Beginner)",
        "native_name": "廣東話 · 粵語",
        "type_key": "logographic",
        "type_id": "Logografis + Karakter Vernakular Kanton",
        "type_en": "Logographic + Cantonese Vernacular Characters",
        "unicode": "U+4E00–U+9FFF + Extension A/B",
        "direction": "Kiri ke kanan",
        "lineage": "Aksara Han Tradisional + Karakter Lisan Yue/Kanton (Hong Kong)",
        "languages": "Kanton (Hong Kong, Makau, Guangdong)",
        "speech_lang": "zh-HK",
        "tts_voice": "zh-HK-HiuMaanNeural",
        "omniglot_url": "https://omniglot.com/chinese/cantonese.htm",
        "prompt_file": "plans/kanton_full_ready_prompts.json",
        "related": ["taiwan-tbcl1", "mandarin-hsk1"],
        "summary_id": "184 kosakata & aksara Kanton pemula termasuk karakter vernakular seperti 佢, 係, 喺, 唔, 冇, 嘅, 咗, 緊 dengan romanisasi Jyutping 6 nada.",
        "summary_en": "184 beginner Cantonese words & characters including vernacular glyphs like 佢, 係, 喺, 唔, 冇, 嘅, 咗, 緊 with 6-tone Jyutping.",
        "features_id": [
            "Memiliki 6 nada kontras dalam bahasa Kanton Hong Kong modern (ditandai angka 1–6 di Jyutping).",
            "Menggunakan karakter vernakular khusus untuk percakapan sehari-hari: 佢 (dia), 係 (adalah), 唔 (tidak), 冇 (tidak ada).",
            "Banyak mempertahankan bunyi akhir konsonan kuno (-p, -t, -k, -m, -n, -ng).",
        ],
        "features_en": [
            "Distinguishes 6 contrastive tones in modern Hong Kong Cantonese (numbered 1–6 in Jyutping).",
            "Uses dedicated vernacular characters in daily writing: 佢 (he/she), 係 (to be), 唔 (not), 冇 (not have).",
            "Preserves Middle Chinese checked syllable codas (-p, -t, -k) and -m endings.",
        ],
        "sample": {
            "native": "人人生而自由，喺尊嚴同權利上一律平等。",
            "translit": "jan4 jan4 sang1 ji4 zi6 jau4, hai2 zyun1 jim4 tung4 kyun4 lei6 soeng6 jat1 leot6 ping4 dang2.",
            "id": "Semua orang dilahirkan merdeka dan setara dalam martabat serta hak.",
            "en": "All human beings are born free and equal in dignity and rights.",
        },
    },
    {
        "slug": "bopomofo",
        "name_id": "Bopomofo / Zhuyin Fuhao",
        "name_en": "Bopomofo (Zhuyin Fuhao)",
        "native_name": "注音符號 · ㄅㄆㄇㄈ",
        "type_key": "featural",
        "type_id": "Sistem Fonetik Semi-Silabik",
        "type_en": "Semi-syllabic Phonetic Script",
        "unicode": "U+3105–U+312F (Bopomofo)",
        "direction": "Kiri ke kanan atau vertikal (anotasi Ruby)",
        "lineage": "Aksara Han Kuno (diringkas tahun 1913 oleh Komisi Penyatuan Pelafalan)",
        "languages": "Mandarin Taiwan, Hokkien, Hakka",
        "speech_lang": "zh-TW",
        "tts_voice": "zh-TW-HsiaoChenNeural",
        "omniglot_url": "https://omniglot.com/writing/zhuyin.htm",
        "prompt_file": "plans/bopomofo_ready_prompts.json",
        "related": ["taiwan-tbcl1", "mandarin-hsk1"],
        "summary_id": "37 simbol fonetik Bopomofo (21 konsonan awal, 3 medial, 13 vokal/akhir) beserta 5 tanda nada Taiwan.",
        "summary_en": "37 Bopomofo phonetic symbols (21 initials, 3 medials, 13 finals) plus 5 Taiwan tone marks.",
        "features_id": [
            "Setiap suku kata Mandarin dibangun maksimal dari 3 slot: Awal + Medial + Akhir + Tanda Nada.",
            "Berbeda dari Pinyin, satu simbol mewakili bunyi konsisten tanpa ejaan huruf Latin yang ambigu.",
            "Nada 1 tidak memakai tanda; Nada 2 (ˊ), Nada 3 (ˇ), Nada 4 (ˋ), Nada netral (˙).",
        ],
        "features_en": [
            "Every Mandarin syllable maps cleanly to at most 3 slots: Initial + Medial + Final + Tone mark.",
            "Avoids Latin spelling ambiguity: each symbol represents one fixed phonetic value.",
            "Tone 1 is unmarked; Tone 2 (ˊ), Tone 3 (ˇ), Tone 4 (ˋ), Neutral tone (˙).",
        ],
        "sample": {
            "native": "ㄅㄆㄇㄈ · ㄊㄞˊ ㄨㄢ",
            "translit": "b p m f · Táiwān",
            "id": "Empat konsonan pertama Bopomofo dan ejaan Taiwan.",
            "en": "The first four Bopomofo consonants and the spelling of Taiwan.",
        },
    },
    {
        "slug": "hiragana",
        "name_id": "Jepang Hiragana",
        "name_en": "Japanese Hiragana",
        "native_name": "平仮名 · ひらがな",
        "type_key": "syllabary",
        "type_id": "Silabarium (Moraik)",
        "type_en": "Syllabary (Moraic)",
        "unicode": "U+3040–U+309F (Hiragana)",
        "direction": "Kiri ke kanan atau vertikal",
        "lineage": "Kanji → Man'yōgana (kursif) → Hiragana (Abad ke-9 M)",
        "languages": "Jepang",
        "speech_lang": "ja-JP",
        "tts_voice": "ja-JP-NanamiNeural",
        "omniglot_url": "https://omniglot.com/writing/hiragana.htm",
        "prompt_file": "plans/kana_ready_prompts.json",
        "filter_field": ("script", "hiragana"),
        "related": ["katakana", "particles", "mandarin-hsk1"],
        "summary_id": "46 kana dasar Hiragana disusun dalam matriks Gojūon lengkap dengan data vektor KanjiVG dan template kuas membulat.",
        "summary_en": "46 core Hiragana syllabograms arranged in the Gojūon matrix with KanjiVG stroke vectors and rounded brush templates.",
        "features_id": [
            "Setiap karakter mewakili satu mora (vokal tunggal atau konsonan + vokal, kecuali ん).",
            "Digunakan untuk kata asli Jepang, akhiran kata kerja (okurigana), dan partikel tata bahasa.",
            "Tanda dakuten (゛) menyuarakan konsonan (k→g, s→z, t→d, h→b) dan handakuten (゜) mengubah h→p.",
        ],
        "features_en": [
            "Each character represents one mora (a vowel or consonant + vowel, except syllabic ん).",
            "Used for native Japanese words, verb/adjective inflections (okurigana), and grammar particles.",
            "Dakuten (゛) voices consonants (k→g, s→z, t→d, h→b) and handakuten (゜) marks h→p.",
        ],
        "sample": {
            "native": "すべての にんげんは、うまれながらにして じゆうであり、かつ、そんげんと けんりとに ついて びょうどうである。",
            "translit": "Subete no ningen wa, umarenagara ni shite jiyū de ari, katsu, songen to kenri to ni tsuite byōdō de aru.",
            "id": "Semua manusia dilahirkan merdeka dan mempunyai martabat serta hak yang sama.",
            "en": "All human beings are born free and equal in dignity and rights.",
        },
    },
    {
        "slug": "katakana",
        "name_id": "Jepang Katakana",
        "name_en": "Japanese Katakana",
        "native_name": "片仮名 · カタカナ",
        "type_key": "syllabary",
        "type_id": "Silabarium (Moraik)",
        "type_en": "Syllabary (Moraic)",
        "unicode": "U+30A0–U+30FF (Katakana)",
        "direction": "Kiri ke kanan atau vertikal",
        "lineage": "Fragmen guratan Kanji oleh biksu Buddha Jepang (Abad ke-9 M)",
        "languages": "Jepang, Ainu, Okinawa",
        "speech_lang": "ja-JP",
        "tts_voice": "ja-JP-NanamiNeural",
        "omniglot_url": "https://omniglot.com/writing/katakana.htm",
        "prompt_file": "plans/kana_ready_prompts.json",
        "filter_field": ("script", "katakana"),
        "related": ["hiragana", "particles"],
        "summary_id": "46 kana dasar Katakana dalam matriks Gojūon untuk kata serapan asing, onomatope, nama ilmiah, dan penekanan visual.",
        "summary_en": "46 core Katakana syllabograms in the Gojūon matrix for loanwords, onomatopoeia, scientific names, and visual emphasis.",
        "features_id": [
            "Memiliki bunyi identik 1-ke-1 dengan Hiragana, namun bergaya sudut tegas dan geometris.",
            "Vokal panjang ditulis menggunakan tanda garis pemanjang chōonpu (ー), mis. コーヒー (kōhī).",
            "Berfungsi mirip huruf miring (italic) untuk menonjolkan kata atau menulis istilah serapan modern.",
        ],
        "features_en": [
            "Shares a 1-to-1 phonetic mapping with Hiragana, but uses crisp angular strokes.",
            "Long vowels use the chōonpu length mark (ー), e.g. コーヒー (coffee).",
            "Functions like italics for emphasis as well as foreign loanwords and sound effects.",
        ],
        "sample": {
            "native": "コンピューター ・ コーヒー ・ カメラ",
            "translit": "Konpyūtā · Kōhī · Kamera",
            "id": "Komputer, kopi, kamera (kata serapan modern dalam Katakana).",
            "en": "Computer, coffee, camera (modern loanwords written in Katakana).",
        },
    },
    {
        "slug": "devanagari",
        "name_id": "Aksara Devanagari",
        "name_en": "Devanagari Script",
        "native_name": "देवनागरी",
        "type_key": "abugida",
        "type_id": "Abugida / Alfasilabarium",
        "type_en": "Abugida / Alphasyllabary",
        "unicode": "U+0900–U+097F (Devanagari)",
        "direction": "Kiri ke kanan (disatukan garis atap shirorekha)",
        "lineage": "Brahmi (~Abad ke-3 SM) → Gupta → Siddham → Nagari → Devanagari",
        "languages": "Hindi, Sanskerta, Marathi, Nepali, Bhojpuri",
        "speech_lang": "hi-IN",
        "tts_voice": "hi-IN-SwaraNeural",
        "omniglot_url": "https://omniglot.com/writing/devanagari.htm",
        "prompt_file": "plans/devanagari_ready_prompts.json",
        "related": ["greek"],
        "summary_id": "46 aksara inti Devanagari (13 vokal Swara + 33 konsonan Vyanjana yang tersusun berdasarkan tempat artikulasi fonetik).",
        "summary_en": "46 core Devanagari characters (13 Swara vowels + 33 Vyanjana consonants ordered scientifically by place of articulation).",
        "features_id": [
            "Setiap huruf konsonan sudah membawa vokal bawaan 'a' pendek (schwa) kecuali dimatikan tanda virama (्).",
            "Konsonan disusun secara ilmiah dari tenggorokan ke bibir: Velar (क–ङ), Palatal (च–ञ), Retrofleks (ट–ण), Dental (त–न), Labial (प–म).",
            "Garis horizontal di atas huruf (shirorekha) menyatukan huruf-huruf menjadi satu kata utuh.",
        ],
        "features_en": [
            "Every consonant carries an inherent short 'a' vowel unless muted by a virama (्) or modified by a vowel matra.",
            "Consonants are ordered phonetically from throat to lips: Velar, Palatal, Retroflex, Dental, Labial.",
            "The distinctive horizontal top bar (shirorekha) links letters together into whole words.",
        ],
        "sample": {
            "native": "सभी मनुष्यों को गौरव और अधिकारों के मामले में जन्मजात स्वतन्त्रता और समानता प्राप्त है।",
            "translit": "Sabhī manuṣyõ ko gaurav aur adhikārõ ke māmle mẽ janmajāt svatantratā aur samāntā prāpt hai.",
            "id": "Semua manusia dilahirkan merdeka dan mempunyai martabat serta hak yang sama.",
            "en": "All human beings are born free and equal in dignity and rights.",
        },
    },
    {
        "slug": "greek",
        "name_id": "Alfabet Yunani",
        "name_en": "Greek Alphabet",
        "native_name": "Ελληνικό αλφάβητο",
        "type_key": "alphabet",
        "type_id": "Alfabet Sejati (Vokal & Konsonan)",
        "type_en": "True Alphabet (Vowels & Consonants)",
        "unicode": "U+0370–U+03FF (Greek and Coptic)",
        "direction": "Kiri ke kanan",
        "lineage": "Proto-Sinaitic → Fenisia → Yunani Kuno (~Abad ke-8 SM) → induk Latin & Sirilik",
        "languages": "Yunani Modern & Kuno, serta simbol Matematika/Sains internasional",
        "speech_lang": "el-GR",
        "tts_voice": "el-GR-AthinaNeural",
        "omniglot_url": "https://omniglot.com/writing/greek.htm",
        "prompt_file": "plans/yunani_ready_prompts.json",
        "related": ["devanagari"],
        "summary_id": "24 huruf Yunani berpasangan besar & kecil (Α α sampai Ω ω), terbagi jelas atas Vokal dan Konsonan, lengkap dengan bunyi modern & mnemonik bentuk.",
        "summary_en": "24 paired uppercase & lowercase Greek letters (Α α through Ω ω), organized into Vowels and Consonants with modern sounds and shape mnemonics.",
        "features_id": [
            "Alfabet pertama dalam sejarah yang memisahkan huruf vokal penuh (Α, Ε, Η, Ι, Ο, Υ, Ω) dan konsonan secara sejajar.",
            "Huruf Sigma memiliki dua bentuk huruf kecil: σ di awal/tengah kata dan ς di akhir kata.",
            "Menjadi sumber langsung bagi simbol fisika, matematika, dan kimia (π, Δ, Ω, λ, μ, θ).",
        ],
        "features_en": [
            "The first true alphabet in history to represent vowels (Α, Ε, Η, Ι, Ο, Υ, Ω) as full, equal letters alongside consonants.",
            "Sigma has two lowercase forms: σ at the start/middle of a word and ς at the end.",
            "Serves globally as standard notation across mathematics, physics, and engineering (π, Δ, Ω, λ, μ, θ).",
        ],
        "sample": {
            "native": "Όλοι οι άνθρωποι γεννιούνται ελεύθεροι και ίσοι στην αξιοπρέπεια και τα δικαιώματα.",
            "translit": "Óloi oi ánthropoi gennioúntai eléftheroi kai ísoi stin axioprépeia kai ta dikaiómata.",
            "id": "Semua manusia dilahirkan merdeka dan mempunyai martabat serta hak yang sama.",
            "en": "All human beings are born free and equal in dignity and rights.",
        },
    },
    {
        "slug": "particles",
        "name_id": "Partikel Tata Bahasa Mandarin & Jepang",
        "name_en": "Mandarin & Japanese Grammar Particles",
        "native_name": "的 · 了 · は · が · を",
        "type_key": "grammar",
        "type_id": "Partikel Struktural & Wacana",
        "type_en": "Structural & Discourse Particles",
        "unicode": "CJK + Hiragana",
        "direction": "Kiri ke kanan",
        "lineage": "Mandarin Modern (HSK 3.0 L1) & Bahasa Jepang Standar",
        "languages": "Mandarin & Jepang",
        "speech_lang": "zh-CN",
        "tts_voice": "zh-CN-XiaoxiaoNeural / ja-JP-NanamiNeural",
        "omniglot_url": "https://omniglot.com/writing/japanese.htm",
        "prompt_file": "plans/partikel_ready_prompts.json",
        "related": ["mandarin-hsk1", "hiragana", "katakana"],
        "summary_id": "18 pelajaran partikel dua-tahap (8 partikel Mandarin HSK 3.0 Level 1 + 10 partikel Jepang) untuk memvisualisasikan fungsi tata bahasa.",
        "summary_en": "18 two-beat particle lessons (8 HSK 3.0 Level 1 Mandarin particles + 10 Japanese particles) visualizing grammatical roles.",
        "features_id": [
            "Partikel Mandarin umumnya dibaca dengan nada netral (轻声) dan menandai kepemilikan, perubahan situasi, atau pertanyaan.",
            "Partikel Jepang selalu menempel di belakang kata (postposisi) untuk menandai topik (は), subjek (が), objek (を), arah (へ/に), atau tempat aksi (で).",
        ],
        "features_en": [
            "Mandarin particles typically carry a light neutral tone and mark possession, aspect/change, or sentence mood.",
            "Japanese particles are postpositional markers following the noun/phrase they govern (topic は, subject が, object を, location で).",
        ],
        "sample": {
            "native": "这是我的书。 / わたしは ほんを よみます。",
            "translit": "Zhè shì wǒ de shū. / Watashi wa hon o yomimasu.",
            "id": "Ini buku saya. / Saya membaca buku.",
            "en": "This is my book. / I read a book.",
        },
    },
    {
        "slug": "hangul",
        "name_id": "Hangul Korea (Jamo Lengkap)",
        "name_en": "Korean Hangul (Full Jamo)",
        "native_name": "한글 · 자모",
        "type_key": "featural",
        "type_id": "Alfabet Fitur (Featural Alphabet)",
        "type_en": "Featural Alphabet",
        "unicode": "U+1100–U+11FF / U+3130–U+318F",
        "direction": "Kiri ke kanan (dirangkai dalam blok suku kata)",
        "lineage": "Diciptakan Raja Sejong Agung (1443, Hunminjeongeum)",
        "languages": "Korea, Jeju, Cia-Cia",
        "speech_lang": "ko-KR",
        "tts_voice": "ko-KR-HyunsuMultilingualNeural / ko-KR-SunHiNeural",
        "omniglot_url": "https://omniglot.com/writing/korean.htm",
        "prompt_file": "plans/hangul_ready_prompts.json",
        "related": ["bopomofo", "hiragana", "katakana"],
        "summary_id": "40 Jamo Hangul (14 konsonan dasar + 5 konsonan ganda + 10 vokal dasar + 11 vokal gabungan) beserta prinsip Langit, Bumi, Manusia.",
        "summary_en": "40 Hangul Jamo (14 basic consonants + 5 double consonants + 10 basic vowels + 11 compound vowels) built on vocal-organ geometry.",
        "features_id": [
            "Bentuk konsonan dasar meniru posisi lidah, bibir, gigi, dan tenggorokan saat diucapkan.",
            "Vokal dibentuk dari tiga unsur filosofis: titik/garis pendek (Langit), garis datar (Bumi), garis tegak (Manusia).",
            "Huruf-huruf dirangkai menjadi blok suku kata persegi (KVK), bukan ditulis memanjang satu baris.",
        ],
        "features_en": [
            "Basic consonant shapes visually model the tongue, lips, teeth, and throat during articulation.",
            "Vowels combine three elements: short stroke (Heaven), horizontal line (Earth), vertical line (Human).",
            "Letters stack into square syllable blocks (CVC) rather than linear strings.",
        ],
        "sample": {
            "native": "모든 인간은 태어날 때부터 자유로우며 그 존엄과 권리에 있어 동등하다.",
            "translit": "Modeun ingan-eun taeeonal ttaebuteo jayurowumyeo geu joneomgwa gwollie isseo dongdeunghada.",
            "id": "Semua manusia dilahirkan merdeka dan mempunyai martabat serta hak yang sama.",
            "en": "All human beings are born free and equal in dignity and rights.",
        },
    },
    {
        "slug": "arabic",
        "name_id": "Abjad Arab",
        "name_en": "Arabic Abjad",
        "native_name": "الأبجدية العربية",
        "type_key": "abjad",
        "type_id": "Abjad (Konsonan Utama + Harakat)",
        "type_en": "Abjad (Consonant-focused Script)",
        "unicode": "U+0600–U+06FF (Arabic)",
        "direction": "Kanan ke kiri (kursif bersambung)",
        "lineage": "Fenisia → Aram → Nabatea → Abjad Arab Klasik",
        "languages": "Arab, Persia, Urdu, Jawi Melayu, Kurdi",
        "speech_lang": "ar-SA",
        "tts_voice": "ar-SA-ZariyahNeural",
        "omniglot_url": "https://omniglot.com/writing/arabic.htm",
        "prompt_file": "plans/arab_ready_prompts.json",
        "related": ["greek", "devanagari"],
        "summary_id": "28 huruf inti abjad Arab yang ditulis bersambung dari kanan ke kiri, dikelompokkan berdasarkan bentuk dasar & posisi titik pembeda.",
        "summary_en": "28 core Arabic letters written cursively right-to-left, grouped by shared base shapes and distinguishing dot patterns.",
        "features_id": [
            "Ditulis dari kanan ke kiri; sebagian besar huruf berubah bentuk di posisi awal, tengah, akhir, atau berdiri sendiri.",
            "Banyak huruf berbagi bentuk rangka dasar yang sama (mis. ب ت ث atau ج ح خ) dan hanya dibedakan oleh jumlah serta letak titik.",
            "Vokal pendek biasanya ditandai harakat di atas/bawah huruf dalam teks pendidikan dan kitab suci.",
        ],
        "features_en": [
            "Written right-to-left; most letters change shape in isolated, initial, medial, and final positions.",
            "Many letters share an identical skeleton (e.g. ب ت ث or ج ح خ) distinguished solely by dot count and placement.",
            "Short vowels are optional diacritics (harakat) placed above or below consonants.",
        ],
        "sample": {
            "native": "يُولَدُ جَمِيعُ النَّاسِ أَحْرَارًا مُتَسَاوِينَ فِي الْكَرَامَةِ وَالْحُقُوقِ.",
            "translit": "Yūladu jamīʿu n-nāsi aḥrāran mutasāwīna fī l-karāmati wa-l-ḥuqūq.",
            "id": "Semua orang dilahirkan merdeka dan mempunyai martabat serta hak yang sama.",
            "en": "All human beings are born free and equal in dignity and rights.",
        },
    },
    {
        "slug": "cyrillic",
        "name_id": "Alfabet Sirilik (Rusia)",
        "name_en": "Cyrillic Alphabet (Russian)",
        "native_name": "Кириллица · Русский алфавит",
        "type_key": "alphabet",
        "type_id": "Alfabet Sejati (Vokal & Konsonan)",
        "type_en": "True Alphabet (Vowels & Consonants)",
        "unicode": "U+0400–U+04FF (Cyrillic)",
        "direction": "Kiri ke kanan",
        "lineage": "Alfabet Yunani + Glagolitik (Abad ke-9–10 M, Kekaisaran Bulgaria Pertama)",
        "languages": "Rusia, Ukraina, Bulgaria, Serbia, Kazakh, Mongolia",
        "speech_lang": "ru-RU",
        "tts_voice": "ru-RU-SvetlanaNeural",
        "omniglot_url": "https://omniglot.com/writing/cyrillic.htm",
        "prompt_file": "plans/sirilik_ready_prompts.json",
        "related": ["greek"],
        "summary_id": "33 huruf Sirilik Rusia berpasangan besar & kecil (А а sampai Я я), termasuk huruf vokal terpalatalisasi serta tanda keras & lembut (Ъ, Ь).",
        "summary_en": "33 paired Russian Cyrillic letters (А а through Я я), including palatalized vowels and the hard & soft signs (Ъ, Ь).",
        "features_id": [
            "Berakar langsung dari alfabet Yunani (П, Ф, Г, Д, Р), sehingga banyak huruf terlihat akrab namun berbunyi berbeda (mis. В=v, Р=r, С=s, Н=n).",
            "Memiliki 10 huruf vokal berpasangan keras-lembut serta dua tanda khusus tanpa bunyi sendiri: Ъ (tanda keras) dan Ь (tanda lembut).",
        ],
        "features_en": [
            "Derived from the Greek uncial script, creating visual false friends with Latin (В=v, Р=r, С=s, Н=n).",
            "Pairs hard and iotated vowels plus two silent modifiers: hard sign (Ъ) and soft sign (Ь).",
        ],
        "sample": {
            "native": "Все люди рождаются свободными и равными в своем достоинстве и правах.",
            "translit": "Vse lyudi rozhdayutsya svobodnymi i ravnymi v svoyom dostoinstve i pravakh.",
            "id": "Semua orang dilahirkan merdeka dan mempunyai martabat serta hak yang sama.",
            "en": "All human beings are born free and equal in dignity and rights.",
        },
    },
    {
        "slug": "thai",
        "name_id": "Aksara Thai (44 Konsonan Inti)",
        "name_en": "Thai Script (44 Consonants)",
        "native_name": "อักษรไทย · พยัญชนะ ๔๔ ตัว",
        "type_key": "abugida",
        "type_id": "Abugida (Tiga Kelas Konsonan Bernada)",
        "type_en": "Abugida (Three-Class Tonal Script)",
        "unicode": "U+0E00–U+0E7F (Thai)",
        "direction": "Kiri ke kanan (tanpa spasi antar kata)",
        "lineage": "Brahmi → Pallava → Khmer Kuno → Aksara Sukhothai (Raja Ramkhamhaeng, 1283)",
        "languages": "Thai, Thai Selatan, Isan",
        "speech_lang": "th-TH",
        "tts_voice": "th-TH-PremwadeeNeural",
        "omniglot_url": "https://omniglot.com/writing/thai.htm",
        "prompt_file": "plans/thai_ready_prompts.json",
        "related": ["devanagari"],
        "summary_id": "44 konsonan inti aksara Thai yang dikelompokkan menurut 3 kelas nada (Mid, High, Low) lengkap dengan nama kata jangkar tradisional (ก ไก่ dst.).",
        "summary_en": "44 core Thai consonants grouped by the 3 tone classes (Mid, High, Low) with traditional acrophonic anchor words (ko kai, etc.).",
        "features_id": [
            "Setiap konsonan tergolong kelas Tengah, Tinggi, atau Rendah yang menentukan nada suku kata bersama tanda nada.",
            "Secara tradisional diajarkan dengan kata kunci benda/hewan (mis. ก ไก่ ko kai = ayam) untuk membedakan bunyi yang mirip.",
            "Ditulis tanpa spasi antar kata; spasi hanya menandai jeda klausa atau kalimat.",
        ],
        "features_en": [
            "Consonants divide into Mid, High, and Low classes, interacting with tone marks to determine syllable tone.",
            "Traditionally memorized via acrophonic anchor words (e.g. ก ไก่ ko kai 'chicken') to distinguish homophonous consonants.",
            "Written continuously without word spaces; spaces mark phrase or sentence boundaries.",
        ],
        "sample": {
            "native": "มนุษย์ทั้งปวงเกิดมามีอิสระและเสมอภาคกันในศักดิ์ศรีและสิทธิ",
            "translit": "Manut thangpuang koet ma mi itsara lae samoe phak kan nai saksi lae sitthi.",
            "id": "Semua manusia dilahirkan merdeka dan mempunyai martabat serta hak yang sama.",
            "en": "All human beings are born free and equal in dignity and rights.",
        },
    },
    {
        "slug": "hebrew",
        "name_id": "Abjad Ibrani (Alef-Bet + Sofit)",
        "name_en": "Hebrew Abjad (Alef-Bet + Sofit)",
        "native_name": "אָלֶף־בֵּית עִבְרִי",
        "type_key": "abjad",
        "type_id": "Abjad (22 Huruf + 5 Bentuk Akhir)",
        "type_en": "Abjad (22 Letters + 5 Final Forms)",
        "unicode": "U+0590–U+05FF (Hebrew)",
        "direction": "Kanan ke kiri",
        "lineage": "Fenisia → Aram Kuno → Abjad Ibrani Persegi (Square Script)",
        "languages": "Ibrani Modern & Alkitabiah, Yiddish, Ladino",
        "speech_lang": "he-IL",
        "tts_voice": "he-IL-HilaNeural",
        "omniglot_url": "https://omniglot.com/writing/hebrew.htm",
        "prompt_file": "plans/ibrani_ready_prompts.json",
        "related": ["arabic", "greek"],
        "summary_id": "27 huruf Ibrani lengkap (22 konsonan inti + 5 bentuk akhir sofit: ך, ם, ן, ף, ץ).",
        "summary_en": "27 Hebrew letters (22 core consonants + 5 final sofit forms: ך, ם, ן, ף, ץ).",
        "features_id": [
            "Ditulis dari kanan ke kiri tanpa perbedaan huruf besar dan kecil.",
            "Lima huruf berubah menjadi bentuk ekor panjang (sofit) di akhir kata: ך, ם, ן, ף, ץ.",
        ],
        "features_en": [
            "Written right-to-left with no uppercase/lowercase distinction.",
            "Five letters take a special final (sofit) form at the end of words: ך, ם, ן, ף, ץ.",
        ],
        "sample": {
            "native": "כּל בני האדם נולדו בני חורין ושווים בערכם ובזכויותיהם.",
            "translit": "Kol benei ha-adam noldu benei chorin ve-shavim be-erkam u-ve-zechuyoteihem.",
            "id": "Semua manusia dilahirkan merdeka dan setara dalam martabat serta hak.",
            "en": "All human beings are born free and equal in dignity and rights.",
        },
    },
    {
        "slug": "georgian",
        "name_id": "Alfabet Georgia (Mkhedruli)",
        "name_en": "Georgian Alphabet (Mkhedruli)",
        "native_name": "ქართული დამწერლობა",
        "type_key": "alphabet",
        "type_id": "Alfabet Sejati (Unicase)",
        "type_en": "True Alphabet (Unicase)",
        "unicode": "U+10A0–U+10FF (Georgian)",
        "direction": "Kiri ke kanan",
        "lineage": "Asomtavruli → Nuskhuri → Mkhedruli (~Abad ke-10 M)",
        "languages": "Georgia, Mingrelia, Svan, Laz",
        "speech_lang": "ka-GE",
        "tts_voice": "ka-GE-EkaNeural",
        "omniglot_url": "https://omniglot.com/writing/georgian.htm",
        "prompt_file": "plans/georgia_ready_prompts.json",
        "related": ["greek", "cyrillic"],
        "summary_id": "33 huruf Mkhedruli Georgia modern yang unik dan sangat fonemis (satu huruf tepat satu bunyi).",
        "summary_en": "33 modern Georgian Mkhedruli letters with strict one-to-one phonemic spelling.",
        "features_id": [
            "Alfabet unicase tanpa huruf kapital, dengan bentuk melengkung organik khas Kaukasus.",
            "Ejaan sangat konsisten: setiap huruf selalu dibaca satu bunyi tetap.",
        ],
        "features_en": [
            "Unicase alphabet with flowing rounded arches and zero silent letters.",
            "Distinguishes aspirated vs ejective stops (თ/ტ, ფ/პ, ქ/კ).",
        ],
        "sample": {
            "native": "ყველა ადამიანი იბადება თავისუფალი და თანასწორი თავისი ღირსებითა და უფლებებით.",
            "translit": "Qvela adamiani ibadeba tavisupali da tanasts'ori tavisi ghirsebita da uplebebit.",
            "id": "Semua manusia dilahirkan merdeka dan setara dalam martabat serta hak.",
            "en": "All human beings are born free and equal in dignity and rights.",
        },
    },
    {
        "slug": "myanmar",
        "name_id": "Aksara Myanmar (Burma)",
        "name_en": "Burmese / Myanmar Script",
        "native_name": "မြန်မာအက္ခရာ",
        "type_key": "abugida",
        "type_id": "Abugida (Lingkaran Mulus)",
        "type_en": "Abugida (Circular Brahmic Script)",
        "unicode": "U+1000–U+109F (Myanmar)",
        "direction": "Kiri ke kanan",
        "lineage": "Brahmi → Kadamba/Pallava → Pyu/Mon → Aksara Myanmar (~Abad ke-11 M)",
        "languages": "Burma (Myanmar), Shan, Mon, Karen",
        "speech_lang": "my-MM",
        "tts_voice": "my-MM-NilarNeural",
        "omniglot_url": "https://omniglot.com/writing/burmese.htm",
        "prompt_file": "plans/myanmar_ready_prompts.json",
        "related": ["devanagari", "thai", "khmer"],
        "summary_id": "33 konsonan inti Myanmar berbentuk lingkaran mulus karena tradisi menulis di atas daun lontar.",
        "summary_en": "33 core Myanmar consonants famed for their circular forms evolved on palm-leaf manuscripts.",
        "features_id": [
            "Bentuk huruf hampir seluruhnya terdiri dari lingkaran agar stylus tidak merobek daun lontar.",
            "Menggunakan vokal bawaan 'a' dan tanda diakritik di sekeliling konsonan.",
        ],
        "features_en": [
            "Rounded shapes avoided tearing dried palm leaves when incised with a stylus.",
            "Carries an inherent 'a' vowel modified by surrounding vowel & tone signs.",
        ],
        "sample": {
            "native": "လူတိုင်းသည် တူညီလွတ်လပ်သော ဂုဏ်သိက္ခာဖြင့် မွေးဖွားလာသူများ ဖြစ်သည်။",
            "translit": "Lu-taing-thi tu-nyi lut-lat-thaw gon-theik-kha-hpyint mwe-hpwa-la-thu-mya hpyit-thi.",
            "id": "Semua manusia dilahirkan merdeka dan setara dalam martabat serta hak.",
            "en": "All human beings are born free and equal in dignity and rights.",
        },
    },
    {
        "slug": "khmer",
        "name_id": "Aksara Khmer (Kamboja)",
        "name_en": "Khmer Script (Cambodian)",
        "native_name": "អក្សរខ្មែរ",
        "type_key": "abugida",
        "type_id": "Abugida (Dua Seri Vokal Bawaan)",
        "type_en": "Abugida (Two-Register Inherent Vowel)",
        "unicode": "U+1780–U+17FF (Khmer)",
        "direction": "Kiri ke kanan",
        "lineage": "Brahmi → Pallava → Khmer Kuno (~Abad ke-7 M)",
        "languages": "Khmer (Kamboja)",
        "speech_lang": "km-KH",
        "tts_voice": "km-KH-SreymomNeural",
        "omniglot_url": "https://omniglot.com/writing/khmer.htm",
        "prompt_file": "plans/khmer_ready_prompts.json",
        "related": ["thai", "lao", "devanagari"],
        "summary_id": "33 konsonan inti aksara Khmer yang terbagi dalam dua seri vokal bawaan (seri a dan seri o).",
        "summary_en": "33 core Khmer consonants divided into two inherent-vowel registers (a-series and o-series).",
        "features_id": [
            "Setiap konsonan termasuk seri 'a' atau seri 'o' yang mengubah bunyi tanda vokal yang menempel.",
            "Menjadi induk langsung bagi bentuk aksara Thai dan Lao.",
        ],
        "features_en": [
            "Each consonant belongs to the a-series or o-series register, shifting attached vowel quality.",
            "Historical ancestor of both the Thai and Lao scripts.",
        ],
        "sample": {
            "native": "មនុស្សទាំងអស់ កើតមកមានសេរីភាព និងភាពស្មើគ្នា ក្នុងសិទ្ធិ និងសេចក្ដីថ្លៃថ្នូរ។",
            "translit": "Monuh teang ah kaet mok mean sereipheap ning pheap smae knea.",
            "id": "Semua manusia dilahirkan merdeka dan setara dalam martabat serta hak.",
            "en": "All human beings are born free and equal in dignity and rights.",
        },
    },
    {
        "slug": "lao",
        "name_id": "Aksara Lao",
        "name_en": "Lao Script",
        "native_name": "ອັກສອນລາວ",
        "type_key": "abugida",
        "type_id": "Abugida (Bernada)",
        "type_en": "Abugida (Tonal)",
        "unicode": "U+0E80–U+0EFF (Lao)",
        "direction": "Kiri ke kanan",
        "lineage": "Brahmi → Khmer → Sukhothai → Aksara Lao",
        "languages": "Lao, Khmu, Hmong Daw",
        "speech_lang": "lo-LA",
        "tts_voice": "lo-LA-KeomanyNeural",
        "omniglot_url": "https://omniglot.com/writing/lao.htm",
        "prompt_file": "plans/lao_ready_prompts.json",
        "related": ["thai", "khmer"],
        "summary_id": "27 konsonan inti aksara Lao yang lebih ringkas dan membulat dibandingkan Thai, dengan ejaan fonemis modern.",
        "summary_en": "27 core Lao consonants — sleeker, more rounded, and more strictly phonemic than Thai.",
        "features_id": [
            "Direformasi agar jauh lebih fonemis: huruf-huruf konsonan ganda historis disederhanakan menjadi 27 konsonan inti.",
            "Kerabat terdekat aksara Thai sehingga banyak bentuk huruf sangat mirip namun lebih membulat.",
        ],
        "features_en": [
            "Reformed for phonemic spelling, streamlining historical consonants down to 27 core letters.",
            "Closely related to Thai, with smoother rounded loops and no word spaces.",
        ],
        "sample": {
            "native": "ມະນຸດທຸກຄົນເກີດມາມີອິດສະຫຼະ ແລະ ສະເໝີພາບກັນໃນສັກສີ ແລະ ສິດທິ.",
            "translit": "Manut thuk khon koet ma mi itsala lae samoe phap kan nai saksi lae sitthi.",
            "id": "Semua manusia dilahirkan merdeka dan setara dalam martabat serta hak.",
            "en": "All human beings are born free and equal in dignity and rights.",
        },
    },
    {
        "slug": "tamil",
        "name_id": "Aksara Tamil",
        "name_en": "Tamil Script",
        "native_name": "தமிழ் அரிச்சுவடி",
        "type_key": "abugida",
        "type_id": "Abugida (Dravida)",
        "type_en": "Abugida (Dravidian)",
        "unicode": "U+0B80–U+0BFF (Tamil)",
        "direction": "Kiri ke kanan",
        "lineage": "Tamil-Brahmi (~Abad ke-3 SM) → Vatteluttu → Aksara Tamil Modern",
        "languages": "Tamil (India Selatan, Sri Lanka, Singapura, Malaysia)",
        "speech_lang": "ta-IN",
        "tts_voice": "ta-IN-PallaviNeural",
        "omniglot_url": "https://omniglot.com/writing/tamil.htm",
        "prompt_file": "plans/tamil_ready_prompts.json",
        "related": ["devanagari"],
        "summary_id": "30 aksara inti Tamil (12 vokal Uyir + 18 konsonan Mei) tanpa huruf konsonan berhembus.",
        "summary_en": "30 core Tamil letters (12 Uyir vowels + 18 Mei consonants) with a streamlined non-aspirated inventory.",
        "features_id": [
            "Membedakan vokal (Uyir / 'jiwa') dan konsonan (Mei / 'tubuh') yang bergabung menjadi aksara suku kata.",
            "Satu konsonan (mis. க) dapat berbunyi k, g, atau h bergantung pada posisinya di awal atau tengah kata.",
        ],
        "features_en": [
            "Separates 12 Uyir ('soul') vowels and 18 Mei ('body') consonants that fuse into syllabic glyphs.",
            "Single stop letters voice or soften allophonically between word-initial and intervocalic positions.",
        ],
        "sample": {
            "native": "மனிதப் பிறவியினர் சகலரும் சுதந்திரமாகவே பிறக்கின்றனர்.",
            "translit": "Manitap piraviyinar cakalarum cutantiramakave pirakkinranar.",
            "id": "Semua manusia dilahirkan merdeka dan mempunyai martabat serta hak yang sama.",
            "en": "All human beings are born free and equal in dignity and rights.",
        },
    },
    {
        "slug": "bengali",
        "name_id": "Aksara Bengali / Bangla",
        "name_en": "Bengali (Bangla) Script",
        "native_name": "বাংলা লিপি",
        "type_key": "abugida",
        "type_id": "Abugida (Brahmi Timur)",
        "type_en": "Abugida (Eastern Brahmic)",
        "unicode": "U+0980–U+09FF (Bengali)",
        "direction": "Kiri ke kanan",
        "lineage": "Brahmi → Siddham → Gaudi → Aksara Bengali-Assam",
        "languages": "Bengali (Bangla), Assam, Bishnupriya",
        "speech_lang": "bn-BD",
        "tts_voice": "bn-BD-NabanitaNeural",
        "omniglot_url": "https://omniglot.com/writing/bengali.htm",
        "prompt_file": "plans/bengali_ready_prompts.json",
        "related": ["devanagari", "gujarati", "tamil"],
        "summary_id": "50 aksara inti Bengali (11 vokal Swarabarna + 39 konsonan Byanjanbarna) dengan garis atap matra khas.",
        "summary_en": "50 core Bengali letters (11 Swarabarna vowels + 39 Byanjanbarna consonants) linked by a signature top matra bar.",
        "features_id": [
            "Garis horizontal matra di atas menyatukan banyak huruf, serupa shirorekha di Devanagari namun dengan sudut lebih mengalir.",
            "Vokal bawaan pada konsonan sering condong ke bunyi 'o' terbuka alih-alih 'a'.",
        ],
        "features_en": [
            "Many characters hang from a horizontal top matra bar while retaining flowing rounded triangles.",
            "The inherent consonant vowel typically rounds toward an open 'o' quality.",
        ],
        "sample": {
            "native": "সমস্ত মানুষ স্বাধীনভাবে সমান মর্যাদা এবং অধিকার নিয়ে জন্মগ্রহণ করে।",
            "translit": "Somosto manush shadhinbhabe soman morjada ebong odhikar niye jonmogrohon kore.",
            "id": "Semua manusia dilahirkan merdeka dan mempunyai martabat serta hak yang sama.",
            "en": "All human beings are born free and equal in dignity and rights.",
        },
    },
    {
        "slug": "gujarati",
        "name_id": "Aksara Gujarati",
        "name_en": "Gujarati Script",
        "native_name": "ગુજરાતી લિપિ",
        "type_key": "abugida",
        "type_id": "Abugida (Tanpa Garis Atap)",
        "type_en": "Abugida (Brahmic without Top Bar)",
        "unicode": "U+0A80–U+0AFF (Gujarati)",
        "direction": "Kiri ke kanan",
        "lineage": "Brahmi → Nagari → Devanagari → Aksara Gujarati (tanpa shirorekha)",
        "languages": "Gujarati, Kutchi, Avesta (liturgi Parsi)",
        "speech_lang": "gu-IN",
        "tts_voice": "gu-IN-DhwaniNeural",
        "omniglot_url": "https://omniglot.com/writing/gujarati.htm",
        "prompt_file": "plans/gujarati_ready_prompts.json",
        "related": ["devanagari", "bengali"],
        "summary_id": "47 aksara inti Gujarati (13 vokal + 34 konsonan) yang berkerabat dekat dengan Devanagari tanpa garis atap horizontal.",
        "summary_en": "47 core Gujarati letters (13 vowels + 34 consonants), closely related to Devanagari without the top horizontal bar.",
        "features_id": [
            "Berevolusi agar dapat ditulis cepat di atas kertas pembukuan tanpa perlu menarik garis atap shirorekha.",
            "Susunan vokal dan konsonannya tetap mengikuti urutan fonetik Sanskerta klasik.",
        ],
        "features_en": [
            "Dropped the Devanagari top shirorekha line to speed up cursive bookkeeping.",
            "Preserves the traditional Sanskrit phonetic grid across velar, palatal, retroflex, dental, and labial rows.",
        ],
        "sample": {
            "native": "પ્રત્યેક વ્યક્તિ જન્મથી જ સ્વતંત્ર છે અને સમાન ગૌરવ તથા અધિકારો ધરાવે છે.",
            "translit": "Pratyek vyakti janmathi j svatantra chhe ane saman gaurav tatha adhikaro dharave chhe.",
            "id": "Semua manusia dilahirkan merdeka dan mempunyai martabat serta hak yang sama.",
            "en": "All human beings are born free and equal in dignity and rights.",
        },
    },
    {
        "slug": "telugu",
        "name_id": "Aksara Telugu",
        "name_en": "Telugu Script",
        "native_name": "తెలుగు లిపి",
        "type_key": "abugida",
        "type_id": "Abugida (Dravida Selatan)",
        "type_en": "Abugida (Rounded South Brahmic)",
        "unicode": "U+0C00–U+0C7F (Telugu)",
        "direction": "Kiri ke kanan",
        "lineage": "Brahmi → Bhattiprolu → Telugu-Kannada → Aksara Telugu Modern",
        "languages": "Telugu, Gondi, Savara",
        "speech_lang": "te-IN",
        "tts_voice": "te-IN-ShrutiNeural",
        "omniglot_url": "https://omniglot.com/writing/telugu.htm",
        "prompt_file": "plans/telugu_ready_prompts.json",
        "related": ["kannada", "tamil", "malayalam"],
        "summary_id": "52 aksara inti Telugu (16 vokal Achulu + 36 konsonan Hallulu) bertanda centang atas talakattu yang khas.",
        "summary_en": "52 core Telugu letters (16 Achulu vowels + 36 Hallulu consonants) marked by the signature top talakattu tick.",
        "features_id": [
            "Bentuk huruf sangat membulat dan berkerabat amat dekat dengan aksara Kannada.",
            "Sebagian besar konsonan memakai tanda centang talakattu (✓) di puncak sebagai penanda vokal bawaan 'a'.",
        ],
        "features_en": [
            "Rounded script closely paired with Kannada, evolved to glide across palm leaves without splitting.",
            "Most consonants carry a top talakattu tick denoting the inherent 'a' vowel.",
        ],
        "sample": {
            "native": "ప్రతిపత్తి, హక్కుల విషయంలో మానవులందరూ జన్మతః స్వతంత్రులు మరియు సమానులు.",
            "translit": "Pratipatti, hakkula vishayamlo manavulandaru janmatah svatantrulu mariyu samanulu.",
            "id": "Semua manusia dilahirkan merdeka dan mempunyai martabat serta hak yang sama.",
            "en": "All human beings are born free and equal in dignity and rights.",
        },
    },
    {
        "slug": "kannada",
        "name_id": "Aksara Kannada",
        "name_en": "Kannada Script",
        "native_name": "ಕನ್ನಡ ಲಿಪಿ",
        "type_key": "abugida",
        "type_id": "Abugida (Dravida Selatan)",
        "type_en": "Abugida (Rounded South Brahmic)",
        "unicode": "U+0C80–U+0CFF (Kannada)",
        "direction": "Kiri ke kanan",
        "lineage": "Brahmi → Kadamba → Old Kannada → Aksara Kannada Modern",
        "languages": "Kannada, Tulu, Konkani, Kodava",
        "speech_lang": "kn-IN",
        "tts_voice": "kn-IN-SapnaNeural",
        "omniglot_url": "https://omniglot.com/writing/kannada.htm",
        "prompt_file": "plans/kannada_ready_prompts.json",
        "related": ["telugu", "tamil", "malayalam"],
        "summary_id": "49 aksara inti Kannada (15 vokal Svaragalu + 34 konsonan Vyanjanagalu) dengan lengkungan lembut dan jambul talakattu.",
        "summary_en": "49 core Kannada letters (15 Svaragalu vowels + 34 Vyanjanagalu consonants) with flowing loops and top crests.",
        "features_id": [
            "Berbagi leluhur langsung dengan aksara Telugu sehingga banyak hurufnya tampak kembar dengan gaya lengkung berbeda.",
            "Konsonan bersusun (ottakshara) diletakkan di bawah konsonan utama.",
        ],
        "features_en": [
            "Shares a direct ancestor with Telugu, yielding mutually recognizable rounded shapes.",
            "Stacked consonant clusters place secondary subscripts underneath the base glyph.",
        ],
        "sample": {
            "native": "ಎಲ್ಲಾ ಮಾನವರೂ ಸ್ವತಂತ್ರರಾಗಿಯೇ ಜನಿಸಿದ್ದಾರೆ ಮತ್ತು ಘನತೆ ಹಾಗೂ ಹಕ್ಕುಗಳಲ್ಲಿ ಸಮಾನರಾಗಿದ್ದಾರೆ.",
            "translit": "Ella manavaru svatantraragiye janisiddare mattu ghanate hagu hakkugalalli samanaragiddare.",
            "id": "Semua manusia dilahirkan merdeka dan mempunyai martabat serta hak yang sama.",
            "en": "All human beings are born free and equal in dignity and rights.",
        },
    },
    {
        "slug": "malayalam",
        "name_id": "Aksara Malayalam",
        "name_en": "Malayalam Script",
        "native_name": "മലയാളം ലിപി",
        "type_key": "abugida",
        "type_id": "Abugida (Dravida Grantha)",
        "type_en": "Abugida (Grantha-derived)",
        "unicode": "U+0D00–U+0D7F (Malayalam)",
        "direction": "Kiri ke kanan",
        "lineage": "Brahmi → Vatteluttu & Grantha → Aksara Malayalam Modern",
        "languages": "Malayalam, Paniya, Betta Kurumba",
        "speech_lang": "ml-IN",
        "tts_voice": "ml-IN-SobhanaNeural",
        "omniglot_url": "https://omniglot.com/writing/malayalam.htm",
        "prompt_file": "plans/malayalam_ready_prompts.json",
        "related": ["tamil", "kannada", "telugu"],
        "summary_id": "51 aksara inti Malayalam (15 vokal + 36 konsonan) berlekuk lembut khas Kerala, termasuk bunyi retrofleks ഴ (zha).",
        "summary_en": "51 core Malayalam letters (15 vowels + 36 consonants) famed for lush rounded curves and the retroflex ഴ (zha).",
        "features_id": [
            "Menggabungkan warisan Vatteluttu dengan Grantha sehingga dapat menuliskan baik kosakata Dravida maupun Sanskerta.",
            "Tanda vokal dapat muncul sebelum, sesudah, atau mengapit huruf konsonan di kedua sisi.",
        ],
        "features_en": [
            "Blends Grantha and Vatteluttu heritage to write both Dravidian and Sanskrit-origin vocabulary.",
            "Surrounding vowel signs can appear to the left, right, or split across both sides of a consonant.",
        ],
        "sample": {
            "native": "മനുഷ്യരെല്ലാവരും തുല്യാവകാശങ്ങളോടും അന്തസ്സോടും സ്വാതന്ത്ര്യത്തോടുംകൂടി ജനിച്ചവരാണ്.",
            "translit": "Manushyarellavarum tulyavakasangalodum antassodum svatantryattodumkudi janiccavaranu.",
            "id": "Semua manusia dilahirkan merdeka dan mempunyai martabat serta hak yang sama.",
            "en": "All human beings are born free and equal in dignity and rights.",
        },
    },
    {
        "slug": "sinhala",
        "name_id": "Aksara Sinhala",
        "name_en": "Sinhala Script",
        "native_name": "සිංහල අක්ෂර මාලාව",
        "type_key": "abugida",
        "type_id": "Abugida (Sri Lanka)",
        "type_en": "Abugida (Circular Insular Brahmic)",
        "unicode": "U+0D80–U+0DFF (Sinhala)",
        "direction": "Kiri ke kanan",
        "lineage": "Brahmi → Grantha / Kadamba → Aksara Sinhala",
        "languages": "Sinhala, Pali, Sanskerta (di Sri Lanka)",
        "speech_lang": "si-LK",
        "tts_voice": "si-LK-ThiliniNeural",
        "omniglot_url": "https://omniglot.com/writing/sinhala.htm",
        "prompt_file": "plans/sinhala_ready_prompts.json",
        "related": ["tamil", "malayalam", "myanmar"],
        "summary_id": "54 aksara inti Sinhala (18 vokal + 36 konsonan termasuk konsonan pranasalisasi nda) bergaya membulat khas naskah lontar Sri Lanka.",
        "summary_en": "54 core Sinhala letters (18 vowels + 36 consonants including prenasalized stops) shaped like smooth waves.",
        "features_id": [
            "Menyertakan vokal pendek/panjang unik (ä / ǟ) dan konsonan pranasalisasi khas (mis. ඬ = nda).",
            "Berbentuk amat membulat dan simetris karena penulisan tradisional di daun tal/lontar.",
        ],
        "features_en": [
            "Includes distinct ä / ǟ vowels and dedicated prenasalized stop letters like ඬ (nda).",
            "Curvilinear forms avoid straight horizontal cuts on Sri Lankan palm-leaf manuscripts.",
        ],
        "sample": {
            "native": "සියලු මනුෂ්‍යයෝ නිදහස්ව උපත ලබා ඇත. ගරුත්වයෙන් හා අයිතිවාසිකම්වලින් සමාන වෙති.",
            "translit": "Siyalu manushyayo nidahasva upata laba ata. Garutvayen ha ayitivasikamvalin samana veti.",
            "id": "Semua manusia dilahirkan merdeka dan mempunyai martabat serta hak yang sama.",
            "en": "All human beings are born free and equal in dignity and rights.",
        },
    },
    {
        "slug": "amharic",
        "name_id": "Aksara Amharik / Ge'ez (Fidel)",
        "name_en": "Amharic / Ge'ez Script (Fidel)",
        "native_name": "ፊደል · ግዕዝ",
        "type_key": "abugida",
        "type_id": "Abugida (Fidel Ethiopia)",
        "type_en": "Abugida (Ethiopic Fidel)",
        "unicode": "U+1200–U+137F (Ethiopic)",
        "direction": "Kiri ke kanan",
        "lineage": "Proto-Sinaitik → Arab Selatan Kuno → Abugida Ge'ez (~Abad ke-4 M) → Amharik",
        "languages": "Amharik, Tigrinya, Ge'ez (liturgi), Harari",
        "speech_lang": "am-ET",
        "tts_voice": "am-ET-MekdesNeural",
        "omniglot_url": "https://omniglot.com/writing/amharic.htm",
        "prompt_file": "plans/amharik_ready_prompts.json",
        "related": ["arabic", "hebrew"],
        "summary_id": "33 bentuk konsonan dasar ordo pertama Fidel Ge'ez yang menjadi fondasi 7 variasi vokal sistematis dalam bahasa Amharik.",
        "summary_en": "33 base first-order Ge'ez Fidel consonants anchoring Amharic's 7-vowel abugida matrix.",
        "features_id": [
            "Setiap dari 33 huruf dasar berubah menjadi 7 bentuk teratur untuk vokal: ä, u, i, a, e, ə, o.",
            "Meskipun berakar dari abjad Semitik (kerabat Arab & Ibrani), arah tulisnya kiri ke kanan.",
        ],
        "features_en": [
            "Each of the 33 base consonants systematically morphs across 7 vowel orders (ä, u, i, a, e, ə, o).",
            "Unlike Arabic and Hebrew despite Semitic roots, Ethiopic Fidel runs strictly left-to-right.",
        ],
        "sample": {
            "native": "የሰው ልጆች ሁሉ ሲወለዱ ነጻና በክብርና በመብትም እኩልነት ያላቸው ናቸው።",
            "translit": "Yäsäw ləjoch hullu siwälädu nätsana bäkəbərna bämäbtəm əkkulənnät yallachäw nachäw.",
            "id": "Semua manusia dilahirkan merdeka dan mempunyai martabat serta hak yang sama.",
            "en": "All human beings are born free and equal in dignity and rights.",
        },
    },
]

GREEK_VOWELS = {"Α", "Ε", "Η", "Ι", "Ο", "Υ", "Ω"}
CYR_VOWELS = {"А", "Е", "Ё", "И", "О", "У", "Ы", "Э", "Ю", "Я"}
CYR_SIGNS = {"Ъ", "Ь"}
THAI_MID = {"ก", "จ", "ฎ", "ฏ", "ด", "ต", "บ", "ป", "อ"}
THAI_HIGH = {"ข", "ฃ", "ฉ", "ฐ", "ถ", "ผ", "ฝ", "ศ", "ษ", "ส", "ห"}
KANA_VOWEL_COLS = ["a", "i", "u", "e", "o"]
KANA_ROW_PREFIXES = ["", "k", "s", "t", "n", "h", "m", "y", "r", "w"]


def classify_group(slug: str, row: dict[str, Any], idx: int) -> str:
    if slug == "greek":
        return "Vokal / Vowels (7)" if row.get("upper") in GREEK_VOWELS else "Konsonan / Consonants (17)"
    if slug == "cyrillic":
        up = row.get("upper", "")
        if up in CYR_VOWELS:
            return "Vokal / Vowels (10)"
        if up in CYR_SIGNS:
            return "Tanda Keras & Lembut / Signs (2)"
        return "Konsonan / Consonants (21)"
    if slug == "hangul":
        if idx < 14:
            return "Konsonan Dasar / Basic Consonants (14)"
        if idx < 24:
            return "Vokal Dasar / Basic Vowels (10)"
        if idx < 29:
            return "Konsonan Ganda / Double Consonants (5)"
        return "Vokal Gabungan / Compound Vowels (11)"
    if slug == "arabic":
        return "28 Huruf Inti Abjad Arab" if idx < 28 else "Harakat & Diakritik Vokal (8)"
    if slug == "thai":
        if idx >= 44:
            return "Vokal (Sara) & Tanda Nada (20)"
        g = row.get("glyph", "")
        if g in THAI_MID:
            return "Kelas Tengah / Mid Class (9)"
        if g in THAI_HIGH:
            return "Kelas Tinggi / High Class (11)"
        return "Kelas Rendah / Low Class (24)"
    if slug == "hebrew":
        return "22 Huruf Inti / Core Letters (22)" if idx < 22 else "Bentuk Akhir / Final Sofit (5)"
    if slug == "tamil":
        return "12 Vokal / Uyir (12)" if idx < 12 else "18 Konsonan / Mei (18)"
    if slug == "bengali":
        return "11 Vokal / Swarabarna (11)" if idx < 11 else "39 Konsonan / Byanjanbarna (39)"
    if slug == "gujarati":
        return "13 Vokal / Svara (13)" if idx < 13 else "34 Konsonan / Vyanjana (34)"
    if slug == "telugu":
        return "16 Vokal / Achulu (16)" if idx < 16 else "36 Konsonan / Hallulu (36)"
    if slug == "kannada":
        return "15 Vokal / Svaragalu (15)" if idx < 15 else "34 Konsonan / Vyanjanagalu (34)"
    if slug == "malayalam":
        return "15 Vokal / Swarangal (15)" if idx < 15 else "36 Konsonan / Vyanjanangal (36)"
    if slug == "sinhala":
        return "18 Vokal / Svara (18)" if idx < 18 else "36 Konsonan / Vyanjana (36)"
    if slug == "amharic":
        return "33 Huruf Dasar / Base Fidel Orders (33)"
    if slug in ("georgian", "myanmar", "khmer", "lao"):
        return f"Huruf Inti / Core Letters ({33 if slug != 'lao' else 27})"
    if slug == "devanagari":
        if idx < 13:
            return "Vokal / Swara (13)"
        if idx < 18:
            return "Velar (क–ङ)"
        if idx < 23:
            return "Palatal (च–ञ)"
        if idx < 28:
            return "Retroflex (ट–ण)"
        if idx < 33:
            return "Dental (त–न)"
        if idx < 38:
            return "Labial (प–म)"
        return "Approximants & Sibilants (य–ह)"
    if slug == "bopomofo":
        if idx < 21:
            return "Konsonan Awal / Initials (21)"
        if idx < 24:
            return "Medial / Medials (3)"
        return "Vokal & Akhir / Finals (13)"
    if slug in ("hiragana", "katakana"):
        return "Dakuten & Handakuten (25)" if row.get("variant") == "dakuten" else "Gojūon Matrix (46)"
    if slug == "particles":
        return "Mandarin HSK 3.0 L1 (8)" if row.get("language") == "mandarin" else "Jepang / Japanese (10)"
    if slug == "cantonese":
        return row.get("topic_en") or "General"
    if slug == "mandarin-hsk1":
        st = row.get("status", "queued")
        if st == "done_exemplar":
            return "Rendered Exemplars (11)"
        if st == "batch_ready":
            return "Batch Ready (23)"
        return "HSK 1 Queue (243)"
    return "All Entries"


def load_entries(spec: dict[str, Any]) -> list[dict[str, Any]]:
    raw = json.loads((ROOT / spec["prompt_file"]).read_text(encoding="utf-8"))
    if "filter_field" in spec:
        fk, fv = spec["filter_field"]
        raw = [x for x in raw if x.get(fk) == fv]
    return raw


def normalize_entry(spec: dict[str, Any], row: dict[str, Any], idx: int) -> dict[str, Any]:
    slug = spec["slug"]
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

    # Stroke data path (hanzi-writer JSON or KanjiVG SVG)
    stroke_json = f"../../stroke_data/{char_key}.json" if char_key and (ROOT / f"stroke_data/{char_key}.json").exists() else ""
    kana_svg = ""
    if slug in ("hiragana", "katakana"):
        kch = row.get("kana", "")
        if kch:
            cp = f"{ord(kch):05x}"
            if (ROOT / f"kana_stroke_data/{cp}.svg").exists():
                kana_svg = f"../../kana_stroke_data/{cp}.svg"

    speech_lang = spec["speech_lang"]
    if slug == "particles":
        speech_lang = "ja-JP" if row.get("language") == "japanese" else "zh-CN"

    return {
        "glyph": glyph,
        "speak_text": row.get("upper") or char_key or row.get("kana") or row.get("traditional") or glyph,
        "speech_lang": speech_lang,
        "reading": reading,
        "zhuyin": row.get("zhuyin", ""),
        "meaning_id": meaning_id,
        "meaning_en": meaning_en,
        "group": classify_group(slug, row, idx),
        "tts_id": " ".join((row.get("tts_id") or {}).values()),
        "tts_en": " ".join((row.get("tts_en") or {}).values()),
        "image_prompt": row.get("image_prompt", ""),
        "template_rel": tpl_rel,
        "video_id": vid_id,
        "video_en": vid_en,
        "stroke_json": stroke_json,
        "kana_svg": kana_svg,
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
main { max-width: 1200px; margin: 0 auto; padding: 1.8rem 1.4rem 4rem; }
.hero {
  background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 1.8rem; margin-bottom: 1.4rem;
}
.hero h1 { margin: 0 0 0.5rem; font-size: clamp(1.6rem, 3vw, 2.3rem); line-height: 1.2; }
.stats-row { display: flex; gap: 0.75rem; flex-wrap: wrap; margin-top: 1rem; }
.stat-pill {
  background: var(--pill-bg); padding: 0.42rem 0.9rem; border-radius: 999px; font-size: 0.88rem; font-weight: 600;
}
.controls { display: flex; gap: 0.8rem; flex-wrap: wrap; margin-bottom: 1.3rem; align-items: center; }
.controls input[type="search"] {
  flex: 1 1 280px; padding: 0.65rem 1rem; border-radius: 10px; border: 1px solid var(--border);
  background: var(--surface); color: var(--ink); font-size: 0.95rem;
}
.filter-pills { display: flex; gap: 0.45rem; flex-wrap: wrap; }
.filter-pills button {
  border: 1px solid var(--border); background: var(--surface); color: var(--ink);
  padding: 0.42rem 0.85rem; border-radius: 999px; cursor: pointer; font-size: 0.84rem; font-weight: 600;
}
.filter-pills button.active { background: var(--accent); color: #fff; border-color: var(--accent); }
.script-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(315px, 1fr)); gap: 1rem; }
.script-card {
  background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 1.25rem;
  display: flex; flex-direction: column; justify-content: space-between; transition: transform 0.12s ease, border-color 0.12s ease;
}
.script-card:hover { transform: translateY(-2px); border-color: var(--accent); text-decoration: none; }
.script-native { font-size: 1.45rem; font-weight: 700; color: var(--accent); margin-bottom: 0.25rem; }
.script-meta { font-size: 0.82rem; color: var(--muted); margin-bottom: 0.55rem; }
.progress-bar { height: 6px; background: var(--pill-bg); border-radius: 999px; overflow: hidden; margin: 0.6rem 0 0.4rem; }
.progress-fill { height: 100%; background: var(--accent); border-radius: 999px; }
.infobox {
  background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 1.2rem; margin-bottom: 1.3rem;
  display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 0.9rem;
}
.infobox dt { font-size: 0.76rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--muted); font-weight: 700; }
.infobox dd { margin: 0.15rem 0 0; font-weight: 600; font-size: 0.94rem; }
.two-col { display: grid; grid-template-columns: 1.2fr 1fr; gap: 1rem; margin-bottom: 1.5rem; }
@media (max-width: 820px) { .two-col { grid-template-columns: 1fr; } }
.panel {
  background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 1.15rem 1.3rem;
}
.panel h2 { margin: 0 0 0.6rem; font-size: 1.05rem; }
.sample-native { font-size: 1.22rem; font-weight: 600; color: var(--ink); margin-bottom: 0.35rem; }
.related-pills { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 0.8rem; }
.related-pill {
  background: var(--pill-bg); color: var(--ink); padding: 0.3rem 0.75rem; border-radius: 999px; font-size: 0.82rem; font-weight: 600;
}
.section-title { margin: 1.6rem 0 0.75rem; font-size: 1.15rem; border-bottom: 1px solid var(--border); padding-bottom: 0.35rem; }
.glyph-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(170px, 1fr)); gap: 0.8rem; }
.gojuon-grid { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 0.7rem; }
@media (max-width: 720px) { .gojuon-grid { grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); } }
.glyph-card {
  background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 0.9rem;
  cursor: pointer; text-align: left; transition: border-color 0.12s ease, transform 0.12s ease;
}
.glyph-card:hover { border-color: var(--accent); transform: translateY(-2px); }
.glyph-big { font-size: 2.25rem; font-weight: 700; color: var(--ink); line-height: 1.15; }
.glyph-reading { font-size: 0.86rem; font-weight: 700; color: var(--accent); margin-top: 0.25rem; }
.glyph-meaning { font-size: 0.82rem; color: var(--muted); margin-top: 0.2rem; }
.badge-row { display: flex; gap: 0.3rem; flex-wrap: wrap; margin-top: 0.4rem; }
.badge-video {
  font-size: 0.7rem; font-weight: 700; background: #1E2D4A; color: #fff; padding: 0.14rem 0.45rem; border-radius: 999px;
}
.badge-stroke {
  font-size: 0.7rem; font-weight: 700; background: var(--pill-bg); color: var(--ink); padding: 0.14rem 0.45rem; border-radius: 999px;
}
.btn-action {
  border: 1px solid var(--border); background: var(--pill-bg); color: var(--ink);
  border-radius: 8px; padding: 0.35rem 0.7rem; font-size: 0.82rem; font-weight: 700; cursor: pointer;
}
.btn-action:hover { border-color: var(--accent); color: var(--accent); }
dialog#entryModal {
  max-width: 820px; width: 94vw; border: 1px solid var(--border); border-radius: 16px;
  background: var(--surface); color: var(--ink); padding: 1.4rem;
}
dialog#entryModal::backdrop { background: rgba(30, 45, 74, 0.52); }
.modal-layout { display: grid; grid-template-columns: 1fr 1.4fr; gap: 1.2rem; align-items: start; }
@media (max-width: 680px) { .modal-layout { grid-template-columns: 1fr; } }
.modal-media img, .modal-media video, .stroke-stage {
  width: 100%; border-radius: 10px; border: 1px solid var(--border); background: var(--bg);
}
.stroke-stage { aspect-ratio: 1 / 1; display: flex; align-items: center; justify-content: center; margin-top: 0.6rem; }
.stroke-stage svg { width: 88%; height: 88%; }
.prompt-box {
  background: var(--bg); border: 1px solid var(--border); border-radius: 8px; padding: 0.75rem; font-size: 0.82rem; white-space: pre-wrap;
}
.global-results { margin-bottom: 1.5rem; }
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

  // Web Speech helper
  window.speakScript = function(text, lang) {
    if (!('speechSynthesis' in window) || !text) return;
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.lang = lang || 'en-US';
    u.rate = 0.85;
    window.speechSynthesis.speak(u);
  };

  // Search + filter
  const searchInput = document.getElementById('searchInput');
  const filterButtons = document.querySelectorAll('.filter-pills button');
  let activeType = 'all';
  function runFilter() {
    const q = (searchInput ? searchInput.value : '').trim().toLowerCase();
    document.querySelectorAll('[data-searchable]').forEach(card => {
      const hay = card.dataset.searchable.toLowerCase();
      const t = card.dataset.type || card.dataset.group || 'all';
      const okType = activeType === 'all' || t === activeType;
      const okQ = !q || hay.includes(q);
      card.style.display = (okType && okQ) ? '' : 'none';
    });
    // Hide empty group sections
    document.querySelectorAll('.group-block').forEach(sec => {
      const visible = sec.querySelectorAll('[data-searchable]:not([style*="display: none"])').length;
      sec.style.display = visible > 0 ? '' : 'none';
    });

    // Global homepage cross-script search
    const globalBox = document.getElementById('globalResults');
    if (globalBox && window.SCRIPTPEDIA_INDEX) {
      if (q.length < 1) { globalBox.innerHTML = ''; return; }
      const hits = window.SCRIPTPEDIA_INDEX.filter(it => it.s.includes(q)).slice(0, 12);
      if (!hits.length) { globalBox.innerHTML = ''; return; }
      globalBox.innerHTML = '<div class="glyph-grid">' + hits.map(h =>
        `<a class="glyph-card" href="scripts/${h.slug}.html?q=${encodeURIComponent(h.g)}">` +
        `<div class="glyph-big">${h.g}</div>` +
        `<div class="glyph-reading">${h.r} · ${h.slug}</div>` +
        `<div class="glyph-meaning">${(localStorage.getItem('scriptpedia_lang')==='en'?h.en:h.id)}</div></a>`
      ).join('') + '</div>';
    }
  }
  if (searchInput) {
    searchInput.addEventListener('input', runFilter);
    const params = new URLSearchParams(window.location.search);
    if (params.get('q')) { searchInput.value = params.get('q'); runFilter(); }
  }
  filterButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      activeType = btn.dataset.filter;
      filterButtons.forEach(b => b.classList.toggle('active', b === btn));
      runFilter();
    });
  });

  // Stroke-order SVG animator
  let animTimer = null;
  async function renderStrokes(d) {
    const stage = document.getElementById('mStrokeStage');
    const btn = document.getElementById('mReplayStroke');
    if (!stage) return;
    if (animTimer) { clearInterval(animTimer); animTimer = null; }
    stage.innerHTML = '';
    stage.style.display = 'none';
    if (btn) btn.style.display = 'none';

    if (d.stroke_json) {
      try {
        const res = await fetch(d.stroke_json);
        if (!res.ok) return;
        const data = await res.json();
        const radSet = new Set(data.radStrokes || []);
        stage.style.display = 'flex';
        if (btn) btn.style.display = 'inline-block';
        const svgNS = 'http://www.w3.org/2000/svg';
        const svg = document.createElementNS(svgNS, 'svg');
        svg.setAttribute('viewBox', '0 0 1024 1024');
        const g = document.createElementNS(svgNS, 'g');
        g.setAttribute('transform', 'scale(1, -1) translate(0, -900)');
        const paths = data.strokes.map((p, idx) => {
          const path = document.createElementNS(svgNS, 'path');
          path.setAttribute('d', p);
          path.setAttribute('fill', radSet.has(idx) ? '#C85A32' : '#1E2D4A');
          path.style.opacity = '0.15';
          path.style.transition = 'opacity 0.2s ease';
          g.appendChild(path);
          return path;
        });
        svg.appendChild(g);
        stage.appendChild(svg);
        const play = () => {
          if (animTimer) clearInterval(animTimer);
          paths.forEach(p => p.style.opacity = '0.12');
          let i = 0;
          animTimer = setInterval(() => {
            if (i >= paths.length) { clearInterval(animTimer); return; }
            paths[i].style.opacity = '1';
            i++;
          }, 380);
        };
        play();
        if (btn) btn.onclick = play;
      } catch (_) {}
    } else if (d.kana_svg) {
      try {
        const res = await fetch(d.kana_svg);
        if (!res.ok) return;
        const txt = await res.text();
        stage.style.display = 'flex';
        stage.innerHTML = txt;
        const svg = stage.querySelector('svg');
        if (svg) {
          svg.style.width = '88%'; svg.style.height = '88%';
          const paths = Array.from(svg.querySelectorAll('path'));
          paths.forEach(p => { p.style.stroke = '#1E2D4A'; p.style.strokeWidth = '5'; });
          if (btn) {
            btn.style.display = 'inline-block';
            const play = () => {
              if (animTimer) clearInterval(animTimer);
              paths.forEach(p => { p.style.stroke = '#DDD3C0'; });
              let i = 0;
              animTimer = setInterval(() => {
                if (i >= paths.length) { clearInterval(animTimer); return; }
                paths[i].style.stroke = '#C85A32';
                i++;
              }, 420);
            };
            play();
            btn.onclick = play;
          }
        }
      } catch (_) {}
    }
  }

  const modal = document.getElementById('entryModal');
  if (modal) {
    let currentEntry = null;
    document.querySelectorAll('.glyph-card').forEach(card => {
      card.addEventListener('click', () => {
        const d = JSON.parse(card.dataset.entry);
        currentEntry = d;
        const lang = localStorage.getItem('scriptpedia_lang') || 'id';
        document.getElementById('mGlyph').textContent = d.glyph;
        document.getElementById('mReading').textContent = d.reading + (d.zhuyin ? ' · ' + d.zhuyin : '');
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
        renderStrokes(d);
        modal.showModal();
      });
    });
    document.getElementById('mSpeak').addEventListener('click', () => {
      if (currentEntry) window.speakScript(currentEntry.speak_text, currentEntry.speech_lang);
    });
    document.getElementById('mCopyPrompt').addEventListener('click', () => {
      if (currentEntry && navigator.clipboard) navigator.clipboard.writeText(currentEntry.image_prompt || '');
    });
    document.getElementById('mClose').addEventListener('click', () => modal.close());
  }
})();
"""


def synth_sample_audio(spec: dict[str, Any]) -> bool:
    """Synthesize native neural audio sample MP3 for each script using edge-tts."""
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    slug = spec["slug"]
    out_mp3 = AUDIO_DIR / f"{slug}.mp3"
    if out_mp3.exists() and out_mp3.stat().st_size > 2048:
        return True
    voice = spec["tts_voice"].split("/")[0].strip()
    text = spec["sample"]["native"]
    if slug == "bopomofo":
        text = "台灣，注音符號。"
    elif slug == "particles":
        text = "这是我的书。"
    try:
        subprocess.run(
            [EDGE_TTS, "--voice", voice, "--text", text, "--write-media", str(out_mp3)],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30,
        )
        return out_mp3.exists() and out_mp3.stat().st_size > 2048
    except Exception as exc:
        print(f"[WARN] edge-tts sample audio failed for {slug} ({voice}): {exc}")
        return False


def build_site(refresh_omniglot: bool = False) -> None:
    (DOCS_DIR / "assets").mkdir(parents=True, exist_ok=True)
    (DOCS_DIR / "scripts").mkdir(parents=True, exist_ok=True)
    (DOCS_DIR / "assets" / "style.css").write_text(CSS_TEXT.strip() + "\n", encoding="utf-8")
    (DOCS_DIR / "assets" / "app.js").write_text(JS_TEXT.strip() + "\n", encoding="utf-8")

    with ThreadPoolExecutor(max_workers=2) as ex:
        audio_ok_list = list(ex.map(synth_sample_audio, SCRIPTS))
    audio_map = {s["slug"]: ok for s, ok in zip(SCRIPTS, audio_ok_list)}
    audio_count = sum(1 for ok in audio_ok_list if ok)

    total_entries = 0
    total_videos = 0
    total_strokes = 0
    script_cards_html = []
    global_index: list[dict[str, str]] = []
    slug_to_name = {s["slug"]: s["native_name"] + " · " + s["name_en"] for s in SCRIPTS}

    for spec in SCRIPTS:
        omni = fetch_omniglot(spec["omniglot_url"], spec["slug"], refresh=refresh_omniglot)
        raw_rows = load_entries(spec)
        entries = [normalize_entry(spec, r, i) for i, r in enumerate(raw_rows)]
        vid_count = sum(1 for e in entries if e["video_id"] or e["video_en"])
        stroke_count = sum(1 for e in entries if e["stroke_json"] or e["kana_svg"])
        tpl_count = sum(1 for e in entries if e["template_rel"])
        total_entries += len(entries)
        total_videos += vid_count
        total_strokes += stroke_count

        for e in entries:
            global_index.append({
                "slug": spec["slug"],
                "g": e["glyph"],
                "r": e["reading"],
                "id": e["meaning_id"][:60],
                "en": e["meaning_en"][:60],
                "s": f"{e['glyph']} {e['reading']} {e['meaning_id']} {e['meaning_en']}".lower(),
            })

        # Group entries in order of first appearance
        groups: dict[str, list[dict[str, Any]]] = {}
        for e in entries:
            groups.setdefault(e["group"], []).append(e)

        group_sections_html = []
        for grp_name, grp_entries in groups.items():
            grid_cls = "gojuon-grid" if spec["slug"] in ("hiragana", "katakana") else "glyph-grid"
            cards_html = []
            for e in grp_entries:
                entry_json = html.escape(json.dumps(e, ensure_ascii=False))
                search_blob = html.escape(f"{e['glyph']} {e['reading']} {e['zhuyin']} {e['meaning_id']} {e['meaning_en']}")
                badges = []
                if e["video_id"] or e["video_en"]:
                    badges.append('<span class="badge-video">▶ MP4</span>')
                if e["stroke_json"] or e["kana_svg"]:
                    badges.append('<span class="badge-stroke">✍ Strokes</span>')
                badge_html = f'<div class="badge-row">{"".join(badges)}</div>' if badges else ""
                cards_html.append(
                    f'<button class="glyph-card" data-searchable="{search_blob}" data-group="{html.escape(grp_name)}" data-entry="{entry_json}">'
                    f'<div class="glyph-big">{html.escape(e["glyph"])}</div>'
                    f'<div class="glyph-reading">{html.escape(e["reading"])}</div>'
                    f'<div class="glyph-meaning" data-id="{html.escape(e["meaning_id"])}" data-en="{html.escape(e["meaning_en"])}">{html.escape(e["meaning_id"])}</div>'
                    f"{badge_html}</button>"
                )
            group_sections_html.append(
                f'<div class="group-block"><h3 class="section-title">{html.escape(grp_name)}</h3>'
                f'<section class="{grid_cls}">{"".join(cards_html)}</section></div>'
            )

        feat_lis = "".join(
            f'<li data-id="{html.escape(fid)}" data-en="{html.escape(fen)}">{html.escape(fid)}</li>'
            for fid, fen in zip(spec["features_id"], spec["features_en"])
        )
        rel_links = "".join(
            f'<a class="related-pill" href="{html.escape(r)}.html">{html.escape(slug_to_name.get(r, r))}</a>'
            for r in spec.get("related", [])
        )
        samp = spec["sample"]
        omni_history = " ".join(omni.get("history", [])[:2])
        omni_hist_html = f'<p style="font-size:0.86rem;color:var(--muted);">{html.escape(omni_history)}</p>' if omni_history else ""
        audio_tag = (
            f'<audio controls preload="none" src="../assets/audio/{html.escape(spec["slug"])}.mp3" style="width:100%;margin:0.55rem 0;"></audio>'
            if audio_map.get(spec["slug"]) else ""
        )

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
      <div class="related-pills">{rel_links}</div>
    </section>

    <dl class="infobox">
      <div><dt data-id="Jenis Aksara" data-en="Script Type">Jenis Aksara</dt><dd data-id="{html.escape(spec['type_id'])}" data-en="{html.escape(spec['type_en'])}">{html.escape(spec['type_id'])}</dd></div>
      <div><dt>Unicode</dt><dd><code>{html.escape(spec['unicode'])}</code></dd></div>
      <div><dt data-id="Arah Penulisan" data-en="Direction">Arah Penulisan</dt><dd>{html.escape(spec['direction'])}</dd></div>
      <div><dt data-id="Silsilah Aksara" data-en="Lineage">Silsilah Aksara</dt><dd>{html.escape(spec['lineage'])}</dd></div>
      <div><dt data-id="Suara TTS Native" data-en="Native TTS Voice">Suara TTS Native</dt><dd><code>{html.escape(spec['tts_voice'])}</code></dd></div>
      <div><dt data-id="Kesiapan Aset" data-en="Asset Readiness">Kesiapan Aset</dt><dd>{len(entries)} entri · {tpl_count} template · {stroke_count} stroke · {vid_count} MP4</dd></div>
    </dl>

    <div class="two-col">
      <section class="panel">
        <h2 data-id="Ciri Khas Ortografi & Linguistik" data-en="Notable Orthographic Features">Ciri Khas Ortografi & Linguistik</h2>
        <ul>{feat_lis}</ul>
        {omni_hist_html}
        <p style="margin:0;"><a href="{html.escape(spec['omniglot_url'])}" target="_blank" rel="noopener">Omniglot Source ↗</a></p>
      </section>
      <section class="panel">
        <div style="display:flex;justify-content:space-between;align-items:center;gap:0.5rem;">
          <h2 data-id="Contoh Teks (UDHR / Klasik)" data-en="Sample Text">Contoh Teks (UDHR / Klasik)</h2>
          <button type="button" class="btn-action" onclick="speakScript({html.escape(json.dumps(samp['native']))}, '{html.escape(spec['speech_lang'])}')">🔊 Listen</button>
        </div>
        <div class="sample-native">{html.escape(samp['native'])}</div>
        {audio_tag}
        <div style="font-size:0.86rem;color:var(--accent);margin-bottom:0.4rem;"><code>{html.escape(samp['translit'])}</code></div>
        <div style="font-size:0.88rem;color:var(--muted);" data-id="{html.escape(samp['id'])}" data-en="{html.escape(samp['en'])}">{html.escape(samp['id'])}</div>
      </section>
    </div>

    <div class="controls">
      <input id="searchInput" type="search" placeholder="Cari huruf, bunyi, atau arti / Search glyph, sound, or meaning...">
    </div>

    {"".join(group_sections_html)}
  </main>

  <dialog id="entryModal">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.8rem;gap:0.5rem;">
      <strong id="mGlyph" style="font-size:1.85rem;"></strong>
      <div style="display:flex;gap:0.45rem;">
        <button id="mSpeak" type="button" class="btn-action">🔊 Pronounce</button>
        <button id="mReplayStroke" type="button" class="btn-action" style="display:none;">▶ Replay Strokes</button>
        <button id="mClose" type="button" class="btn-action">✕</button>
      </div>
    </div>
    <div class="modal-layout">
      <div>
        <div class="modal-media" id="mMedia"></div>
        <div class="stroke-stage" id="mStrokeStage" style="display:none;"></div>
      </div>
      <div>
        <p><strong id="mReading" style="color:var(--accent);"></strong> — <span id="mMeaning"></span></p>
        <p><strong data-id="Naskah TTS" data-en="TTS Script">Naskah TTS</strong></p>
        <div class="prompt-box" id="mTts"></div>
        <div style="display:flex;justify-content:space-between;align-items:center;margin-top:0.8rem;">
          <strong data-id="Prompt Ilustrasi" data-en="Illustration Prompt">Prompt Ilustrasi</strong>
          <button id="mCopyPrompt" type="button" class="btn-action">Copy Prompt</button>
        </div>
        <div class="prompt-box" id="mPrompt"></div>
      </div>
    </div>
  </dialog>
  <script src="../assets/app.js"></script>
</body>
</html>
"""
        (DOCS_DIR / "scripts" / f"{spec['slug']}.html").write_text(page_html, encoding="utf-8")

        pct = int((vid_count / max(1, len(entries))) * 100)
        tpl_pct = int((tpl_count / max(1, len(entries))) * 100)
        search_meta = html.escape(f"{spec['name_id']} {spec['name_en']} {spec['native_name']} {spec['type_id']} {spec['type_en']} {spec['languages']}")
        script_cards_html.append(
            f'<a class="script-card" href="scripts/{spec["slug"]}.html" data-searchable="{search_meta}" data-type="{spec["type_key"]}">'
            f'<div><div class="script-native">{html.escape(spec["native_name"])}</div>'
            f'<h2 style="margin:0 0 0.25rem;font-size:1.15rem;color:var(--ink);" data-id="{html.escape(spec["name_id"])}" data-en="{html.escape(spec["name_en"])}">{html.escape(spec["name_id"])}</h2>'
            f'<div class="script-meta">{html.escape(spec["type_en"])} · {len(entries)} entri · {stroke_count} stroke</div>'
            f'<p style="margin:0;color:var(--muted);font-size:0.89rem;" data-id="{html.escape(spec["summary_id"])}" data-en="{html.escape(spec["summary_en"])}">{html.escape(spec["summary_id"])}</p></div>'
            f'<div><div class="progress-bar" title="Template readiness {tpl_pct}% / MP4 {pct}%"><div class="progress-fill" style="width:{max(tpl_pct, pct)}%"></div></div>'
            f'<div style="display:flex;justify-content:space-between;font-size:0.78rem;color:var(--muted);"><span>Template {tpl_count}/{len(entries)}</span><span>MP4 {vid_count}/{len(entries)}</span></div>'
            f'<div style="margin-top:0.55rem;font-weight:700;font-size:0.85rem;color:var(--accent);">Buka Ensiklopedia →</div></div>'
            f"</a>"
        )

    index_json_js = json.dumps(global_index, ensure_ascii=False)
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
    <span class="brand">Script<span>Pedia</span> · Omniglot × Grokipedia AI Encyclopedia</span>
    <div class="lang-toggle" role="group" aria-label="Language">
      <button type="button" data-lang="id">ID</button>
      <button type="button" data-lang="en">EN</button>
    </div>
  </header>
  <main>
    <section class="hero">
      <h1 data-id="Ensiklopedia Sistem Tulisan & Studio Mnemonik" data-en="Writing Systems Encyclopedia & Mnemonic Studio">Ensiklopedia Sistem Tulisan & Studio Mnemonik</h1>
      <p data-id="Struktur taksonomi & fonetik lengkap ala Omniglot, disintesis otomatis ala Grokipedia, lengkap dengan animator urutan guratan interaktif, audio TTS, template 9:16, dan video mnemonik." data-en="Complete Omniglot-grade script taxonomy and phonetics, synthesized automatically like Grokipedia, with an interactive stroke-order animator, live speech audio, 9:16 templates, and mnemonic videos.">Struktur taksonomi & fonetik lengkap ala Omniglot, disintesis otomatis ala Grokipedia, lengkap dengan animator urutan guratan interaktif, audio TTS, template 9:16, dan video mnemonik.</p>
      <div class="stats-row">
        <span class="stat-pill">{len(SCRIPTS)} Sistem Tulisan</span>
        <span class="stat-pill">{total_entries} Huruf & Pelajaran</span>
        <span class="stat-pill">{total_strokes} Animator Guratan SVG</span>
        <span class="stat-pill">{audio_count} Native Neural Audio</span>
        <span class="stat-pill">{total_videos} Link Video MP4</span>
      </div>
    </section>
    <div class="controls">
      <input id="searchInput" type="search" placeholder="Cari aksara, huruf, bunyi, atau arti di semua bahasa / Cross-script search...">
      <div class="filter-pills">
        <button type="button" class="active" data-filter="all">All</button>
        <button type="button" data-filter="logographic">Logographic</button>
        <button type="button" data-filter="syllabary">Syllabary</button>
        <button type="button" data-filter="abugida">Abugida</button>
        <button type="button" data-filter="abjad">Abjad</button>
        <button type="button" data-filter="alphabet">Alphabet</button>
        <button type="button" data-filter="featural">Featural</button>
        <button type="button" data-filter="grammar">Grammar</button>
      </div>
    </div>
    <div id="globalResults" class="global-results"></div>
    <section class="script-grid">
      {"".join(script_cards_html)}
    </section>
  </main>
  <script>window.SCRIPTPEDIA_INDEX = {index_json_js};</script>
  <script src="assets/app.js"></script>
</body>
</html>
"""
    (DOCS_DIR / "index.html").write_text(index_html, encoding="utf-8")
    print(f"Built ScriptPedia v2: {len(SCRIPTS)} scripts, {total_entries} entries, {total_strokes} stroke animators, {audio_count} neural audio MP3s, {total_videos} video links.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build ScriptPedia v2 encyclopedia")
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
