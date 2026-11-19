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
- **Catatan Audit:** Label HSK/TOCFL tetap terpisah dari jalur Kanton; kata yang berbagi bentuk tradisional dengan Mandarin (`青`, `清`, `水`) dapat memakai ulang ilustrasi jika bentuk guratan cocok, sedangkan karakter khusus Kanton (`佢`, `係`, `喺`, `唔`, `冇`, `嘅`, `咗`, `緊`, `呀`, `食`, `飲`) memakai audio `zh-HK` + Jyutping bernomor nada (`m4`, `cing1`, dst. tidak dibacakan mentah sebagai huruf Latin oleh TTS non-Mandarin tanpa pembungkus kata).

## 3. Jalur Mandarin Tradisional Taiwan & Bopomofo (`bopomofo-rencana-id-en.md` + `kurikulum-lintas-jalur-id-en.md`)
- **Cakupan:** `37` simbol Bopomofo (`21` konsonan awal, `3` medial, `13` vokal/akhir) + `5` tanda nada (`ˊ`, `ˇ`, `ˋ`, `˙`, Nada 1 tanpa tanda) + contoh aksara tradisional Taiwan (`青`, `清`, `請`, `說`, `學`, `國`, `飛`, `嗎`, `們`).
- **Suara TTS Native (`edge-tts`):** Terverifikasi tersedia `zh-TW-HsiaoChenNeural`, `zh-TW-HsiaoYuNeural`, dan `zh-TW-YunJheNeural`.
- **Catatan Audit TTS:** Konsonan awal Bopomofo (`ㄅ, ㄆ, ㄇ, ...`) wajib disintesis atau diuji di dalam suku kata nyata (atau via `zh-TW`), dan label bacaan Latin (`b-`, `zh-`) tidak boleh memakai tanda `-` mentah di dalam segmen `id-ID-GadisNeural` / `en-US-JennyNeural`.
