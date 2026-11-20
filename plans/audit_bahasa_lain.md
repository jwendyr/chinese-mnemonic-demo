# Audit Jalur Bahasa Lain (Jepang, Kanton, Taiwan/Bopomofo)

Tanggal audit: 19 November 2026

## 1. Jalur Jepang — Hiragana & Katakana (`kana-rencana-id-en.md` + `partikel-rencana-id-en.md`)
- **Cakupan Dasar:** `46` Hiragana + `46` Katakana (**`92` simbol**) + `10` partikel Jepang (`は, が, を, へ, に, で, の, も, と, か`).
- **Data Guratan Resmi (`KanjiVG`):** Seluruh **`92 / 92`** file SVG urutan guratan sudah diunduh ke [`kana_stroke_data/`](../kana_stroke_data/).
- **Template Kuas Bulat (`1080×1920`):** Seluruh **`92 / 92`** template bergaya bulat (`NAVY` untuk Hiragana, `TERRACOTTA` untuk Katakana) sudah dirender di [`templates_kana/`](../templates_kana/).
- **Suara TTS Native (`edge-tts`):** Terverifikasi tersedia `ja-JP-NanamiNeural` (wanita) dan `ja-JP-KeitaNeural` (pria).
- **Audit Teks & TTS (`kana_ready_prompts.json`):**
  - Terdeteksi dan diperbaiki 4 kasus simbol kurung pada bunyi `を` & `ヲ` (`"o (wo)"` → `"o"` untuk TTS agar `id-ID-GadisNeural` / `en-US-JennyNeural` tidak membaca tanda kurung).
  - Setelah pembersihan, seluruh **`92` entri Kana (`184` konfigurasi ID & EN)** lolos `validate_tts_segment` dengan **`0` galat**.
- **Catatan Konsistensi Font:** Karena macOS lokal tidak memiliki font tulisan tangan `Klee` bawaan (hanya `Hiragino Sans` & `Hiragino Mincho ProN`), seluruh teks Kana ukuran besar, judul hero, animasi `米字格` 30fps, dan *strip* urutan guratan wajib memakai perender vektor lengkung bulat dari `KanjiVG` (`kana_stroke_data/`) agar seragam bulat dan bebas font kotak.

## 2. Jalur Kanton Hong Kong (`kanton-rencana-id-en.md` + `kosakata/kanton-pemula-kosakata.md`)
- **Suara TTS Native (`edge-tts`):** Terverifikasi tersedia `zh-HK-HiuMaanNeural`, `zh-HK-HiuGaaiNeural`, dan `zh-HK-WanLungNeural`.
- **Template & Data Siap Pakai:** `15 / 15` template `hk_*.png` dirender di [templates_trad/](file:///Volumes/App/Workspace/chinese-mnemonic-demo/templates_trad) (`15` karakter inti Kanton, dengan `4` fallback `Kaiti.ttc index=3` untuk `佢, 喺, 冇, 咗` karena 404 di `hanzi-writer-data@2.0.1` + `20` data guratan Tradisional baru di [stroke_data/](file:///Volumes/App/Workspace/chinese-mnemonic-demo/stroke_data)).
- **Audit TTS & Prompt:** [kanton_ready_prompts.json](file:///Volumes/App/Workspace/chinese-mnemonic-demo/plans/kanton_ready_prompts.json) (`15` entri, `0` error `validate_tts_segment`).
- **Catatan Audit:** Label HSK/TOCFL tetap terpisah dari jalur Kanton; kata yang berbagi bentuk tradisional dengan Mandarin (`青`, `清`, `水`) dapat memakai ulang ilustrasi jika bentuk guratan cocok, sedangkan karakter khusus Kanton (`佢`, `係`, `喺`, `唔`, `冇`, `嘅`, `咗`, `緊`, `呀`, `食`, `飲`) memakai audio `zh-HK` + Jyutping bernomor nada (`m4`, `cing1`, dst. tidak dibacakan mentah sebagai huruf Latin oleh TTS non-Mandarin tanpa pembungkus kata).

## 3. Jalur Mandarin Tradisional Taiwan & Bopomofo (`bopomofo-rencana-id-en.md` + `kurikulum-lintas-jalur-id-en.md`)
- **Cakupan:** `37` simbol Bopomofo (`21` konsonan awal, `3` medial, `13` vokal/akhir) + `5` tanda nada (`ˊ`, `ˇ`, `ˋ`, `˙`, Nada 1 tanpa tanda) + `9` contoh aksara tradisional Taiwan (`青`, `清`, `請`, `說`, `學`, `國`, `飛`, `嗎`, `們`).
- **Suara TTS Native (`edge-tts`):** Terverifikasi tersedia `zh-TW-HsiaoChenNeural`, `zh-TW-HsiaoYuNeural`, dan `zh-TW-YunJheNeural`.
- **Template & Data Siap Pakai:**
  - `37 / 37` template Bopomofo (`Kaiti.ttc index=3`) di [templates_bopomofo/](file:///Volumes/App/Workspace/chinese-mnemonic-demo/templates_bopomofo).
  - `9 / 9` template Taiwan Tradisional `tw_*.png` di [templates_trad/](file:///Volumes/App/Workspace/chinese-mnemonic-demo/templates_trad) (`24` file total di `templates_trad/`: `15` `hk_*` + `9` `tw_*`).
- **Audit TTS & Prompt:**
  - [bopomofo_ready_prompts.json](file:///Volumes/App/Workspace/chinese-mnemonic-demo/plans/bopomofo_ready_prompts.json) (`37` entri, `0` error `validate_tts_segment`).
  - [taiwan_trad_ready_prompts.json](file:///Volumes/App/Workspace/chinese-mnemonic-demo/plans/taiwan_trad_ready_prompts.json) (`9` entri diperkaya glos ID/EN + prompt ilustrasi, `0` error `validate_tts_segment`).
- **Catatan Audit TTS:** Konsonan awal Bopomofo (`ㄅ, ㄆ, ㄇ, ...`) wajib disintesis atau diuji di dalam suku kata nyata (atau via `zh-TW`), dan label bacaan Latin (`b-`, `zh-`) tidak boleh memakai tanda `-` mentah di dalam segmen `id-ID-GadisNeural` / `en-US-JennyNeural`.

## 4. Jalur Partikel Mandarin & Jepang (`partikel-rencana-id-en.md`)
- **Cakupan:** `18` pelajaran partikel (`8` Mandarin HSK 3.0 Level 1: `的, 地, 了 (verba), 了 (akhir kalimat), 吗/嗎, 呢 (berlangsung), 呢 (pertanyaan balik), 吧` + `10` Jepang: `は, が, を, へ, に, で, の, も, と, か`).
- **Audit TTS & Prompt:** [partikel_ready_prompts.json](file:///Volumes/App/Workspace/chinese-mnemonic-demo/plans/partikel_ready_prompts.json) (`18` entri lengkap dengan prompt ilustrasi dua tahap `9:16` serta skrip `tts_id` & `tts_en`, `0` error `validate_tts_segment`).

## 5. Jalur Huruf Yunani (`yunani-rencana-id-en.md`)
- **Cakupan:** `24` huruf alfabet Yunani berpasangan huruf besar & kecil (`Α α` s.d. `Ω ω`).
- **Suara TTS Native (`edge-tts`):** Terverifikasi tersedia `el-GR-AthinaNeural` dan `el-GR-NestorasNeural`.
- **Template & Audit TTS:** `24 / 24` template (`Georgia Bold.ttf`) di [templates_greek/](file:///Volumes/App/Workspace/chinese-mnemonic-demo/templates_greek) + [yunani_ready_prompts.json](file:///Volumes/App/Workspace/chinese-mnemonic-demo/plans/yunani_ready_prompts.json) (`24` entri, `0` error `validate_tts_segment`).

## 6. Jalur Aksara Devanagari (`devanagari-rencana-id-en.md`)
- **Cakupan:** `46` aksara inti Devanagari (`13` vokal Swara + `33` konsonan Vyanjana).
- **Suara TTS Native (`edge-tts`):** Terverifikasi tersedia `hi-IN-SwaraNeural`, `hi-IN-MadhurNeural` (serta `mr-IN-AarohiNeural`, `mr-IN-ManoharNeural`, `ne-NP-HemkalaNeural`, `ne-NP-SagarNeural`).
- **Template & Audit TTS:** `46 / 46` template (`Kohinoor.ttc`) di [templates_devanagari/](file:///Volumes/App/Workspace/chinese-mnemonic-demo/templates_devanagari) + [devanagari_ready_prompts.json](file:///Volumes/App/Workspace/chinese-mnemonic-demo/plans/devanagari_ready_prompts.json) (`46` entri, `0` error `validate_tts_segment`).

## 7. Daftar Penuh HSK 1, TBCL 1 Taiwan & Kanton Pemula (`hsk1-daftar-kerja.tsv`, `tbcl-1-aksara.tsv`, `kanton-pemula-kosakata.tsv`)
- **Data Guratan (`stroke_data/`):** Total `543` file `stroke_data/*.json` (penambahan `327` karakter baru; hanya `7` karakter varian HK `佢, 冇, 咁, 哋, 啱, 啲, 眞` yang fallback bersih ke `Kaiti.ttc index=3`).
- **HSK 3.0 Level 1 Penuh (`277` karakter):** [hsk1_full_ready_prompts.json](file:///Volumes/App/Workspace/chinese-mnemonic-demo/plans/hsk1_full_ready_prompts.json) (`277` entri, `0` error `validate_tts_segment`) + seluruh template di [templates/](file:///Volumes/App/Workspace/chinese-mnemonic-demo/templates).
- **TBCL Level 1 Taiwan Penuh (`246` aksara):** [tbcl1_full_ready_prompts.json](file:///Volumes/App/Workspace/chinese-mnemonic-demo/plans/tbcl1_full_ready_prompts.json) (`246` entri, `0` error `validate_tts_segment`) + template `tbcl1_*.png` di [templates_trad/](file:///Volumes/App/Workspace/chinese-mnemonic-demo/templates_trad).
- **Kanton Pemula Penuh (`184` kosakata/aksara):** [kanton_full_ready_prompts.json](file:///Volumes/App/Workspace/chinese-mnemonic-demo/plans/kanton_full_ready_prompts.json) (`184` entri, `0` error `validate_tts_segment`) + template `hk_full_*.png` di [templates_trad/](file:///Volumes/App/Workspace/chinese-mnemonic-demo/templates_trad).
