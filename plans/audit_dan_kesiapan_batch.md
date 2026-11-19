# Audit Teks Video & Kesiapan Batch Lanjutan HSK 1

Tanggal audit: 19 November 2026

## 1. Hasil Audit 11 Karakter Terverifikasi (`22 Video ID & EN`)
Seluruh 11 karakter (`休`, `息`, `清`, `请`, `晴`, `情`, `渴`, `吃`, `明`, `好`, `看`) di [`build_one_exemplar.py`](../build_one_exemplar.py) lolos pemeriksaan otomatis:
- **TTS (`validate_tts_segment`):** `0` pelanggaran pada 22 konfigurasi bahasa (tidak ada simbol `/`, `+`, `()`, `→`, `·`, tidak ada karakter CJK bocor ke suara `id-ID-GadisNeural` / `en-US-JennyNeural`, tidak ada penyebutan `"Nada ..."` / `"Tone ..."` di audio).
- **Urutan Narasi Mnemonik:** 100% mengikuti pola `Arti → Hanzi` di Babak 3 dengan pemunculan ilustrasi komponen 1 terlebih dahulu sebelum komponen 2 ditulis.
- **Tata Letak Teks:** Lebar maksimum `hook_lines` adalah `761px` (batas dalam kartu `972px`), `0` teks meluber.

## 2. Audit Dataset Lama (`hsk1_characters.json`)
Dari `181` entri lama di [`hsk1_characters.json`](../hsk1_characters.json):
- `181 / 181` entri masih memuat jargon internal (`"Peran konsisten: ..."` / `"Consistent"`).
- `83` entri `meaning_id` dan `81` entri `meaning_en` masih mengandung tanda `/` yang wajib diganti menjadi `"atau"` / `"or"` untuk TTS.

## 3. Kelengkapan & Antrean Batch Siap Render (`23 Karakter`)
Seluruh `196` data guratan vektor resmi (`hanzi-writer-data@2.0.1`) kini sudah lengkap di [`stroke_data/`](../stroke_data/).  
Untuk mempercepat eksekusi segera setelah kuota generator gambar (`gemini-3.1-flash-image`) kembali tersedia, **23 karakter** berikut sudah dilengkapi template kuas bulat [`templates/`](../templates/), koordinat pemisahan komponen, naskah audio bersih (`0` galat `validate_tts_segment`), dan *prompt* ilustrasi Chineasy di [`batch_ready_prompts.json`](batch_ready_prompts.json):

| Batch | Karakter | Komponen (`split`) | Template & Prompt | Status TTS |
| :--- | :--- | :--- | :--- | :--- |
| **Batch 3 (sisa)** | `喝`, `妈`, `爸` | `口+曷 (3)`, `女+马 (3)`, `父+巴 (4)` | Siap | `0` galat |
| **Batch 4 (Orang & Keluarga)** | `姐`, `他`, `她`, `你`, `们`, `朋` | `女+且 (3)`, `亻+也 (2)`, `女+也 (3)`, `亻+尔 (2)`, `亻+门 (2)`, `月+月 (4)` | Siap | `0` galat |
| **Batch 5 (Aksi & Pikiran)** | `住`, `作`, `做`, `坐`, `想`, `听` | `亻+主 (2)`, `亻+乍 (2)`, `亻+故 (2)`, `从+土 (4)`, `相+心 (9)`, `口+斤 (3)` | Siap | `0` galat |
| **Batch 6 (Benda, Alam & Belajar)** | `杯`, `本`, `菜`, `茶`, `字`, `学`, `家`, `校` | `木+不 (4)`, `木+一 (4)`, `艹+采 (3)`, `艹+余 (3)`, `宀+子 (3)`, `⺍+子 (5)`, `宀+豕 (3)`, `木+交 (4)` | Siap | `0` galat |
