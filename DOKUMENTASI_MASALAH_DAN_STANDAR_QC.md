# Dokumentasi Masalah, Akar Penyebab & Standar QC — Kartu & Video Mnemonik HSK 1

Dokumentasi ini merangkum seluruh masalah yang ditemukan pada iterasi awal pipeline pembuatan kartu dan video 9:16 HSK 1, akar penyebab teknisnya, perbaikan yang sudah dibuktikan pada 4 exemplar lintas 4 nada Mandarin (**`休 (xiū, Nada 1)`**, **`明 (míng, Nada 2)`**, **`好 (hǎo, Nada 3)`**, **`看 (kàn, Nada 4)`**), serta aturan wajib sebelum menjalankan proses batch apa pun.

**Implementasi acuan yang sudah terverifikasi (Gaya Kaligrafi Kuas Bulat / Kaiti Seragam):**
- Skrip exemplar: [`build_one_exemplar.py`](file:///Volumes/App/Workspace/chinese-mnemonic-demo/build_one_exemplar.py)
- Ilustrasi AI referensi (gaya coretan kuas bulat): [`好.jpg`](file:///Volumes/App/Workspace/chinese-mnemonic-demo/illustrations/好.jpg), [`看.jpg`](file:///Volumes/App/Workspace/chinese-mnemonic-demo/illustrations/看.jpg), [`明.jpg`](file:///Volumes/App/Workspace/chinese-mnemonic-demo/illustrations/明.jpg), [`休.jpg`](file:///Volumes/App/Workspace/chinese-mnemonic-demo/illustrations/休.jpg) (`1080×1920`)
- Template goresan kuas & data vektor SVG (`hanzi-writer-data`): [`templates/好.png`](file:///Volumes/App/Workspace/chinese-mnemonic-demo/templates/好.png), [`templates/看.png`](file:///Volumes/App/Workspace/chinese-mnemonic-demo/templates/看.png), [`templates/明.png`](file:///Volumes/App/Workspace/chinese-mnemonic-demo/templates/明.png), [`templates/休.png`](file:///Volumes/App/Workspace/chinese-mnemonic-demo/templates/休.png), [`stroke_data/`](file:///Volumes/App/Workspace/chinese-mnemonic-demo/stroke_data/)
- Kartu hasil QC:
  - Indonesia: [`cards/好.png`](file:///Volumes/App/Workspace/chinese-mnemonic-demo/cards/好.png), [`cards/看.png`](file:///Volumes/App/Workspace/chinese-mnemonic-demo/cards/看.png), [`cards/明.png`](file:///Volumes/App/Workspace/chinese-mnemonic-demo/cards/明.png), [`cards/休.png`](file:///Volumes/App/Workspace/chinese-mnemonic-demo/cards/休.png)
  - Inggris: [`cards_en/好.png`](file:///Volumes/App/Workspace/chinese-mnemonic-demo/cards_en/好.png), [`cards_en/看.png`](file:///Volumes/App/Workspace/chinese-mnemonic-demo/cards_en/看.png), [`cards_en/明.png`](file:///Volumes/App/Workspace/chinese-mnemonic-demo/cards_en/明.png), [`cards_en/休.png`](file:///Volumes/App/Workspace/chinese-mnemonic-demo/cards_en/休.png)
- Video 9:16 hasil QC (`1080×1920`, `30fps`, `20.37s – 23.67s`):
  - Indonesia: [`char_videos/好.mp4`](file:///Volumes/App/Workspace/chinese-mnemonic-demo/char_videos/好.mp4), [`char_videos/看.mp4`](file:///Volumes/App/Workspace/chinese-mnemonic-demo/char_videos/看.mp4), [`char_videos/明.mp4`](file:///Volumes/App/Workspace/chinese-mnemonic-demo/char_videos/明.mp4), [`char_videos/休.mp4`](file:///Volumes/App/Workspace/chinese-mnemonic-demo/char_videos/休.mp4)
  - Inggris: [`char_videos_en/好.mp4`](file:///Volumes/App/Workspace/chinese-mnemonic-demo/char_videos_en/好.mp4), [`char_videos_en/看.mp4`](file:///Volumes/App/Workspace/chinese-mnemonic-demo/char_videos_en/看.mp4), [`char_videos_en/明.mp4`](file:///Volumes/App/Workspace/chinese-mnemonic-demo/char_videos_en/明.mp4), [`char_videos_en/休.mp4`](file:///Volumes/App/Workspace/chinese-mnemonic-demo/char_videos_en/休.mp4)

---

## Ringkasan 8 Masalah & Solusi Wajib

### 1. TTS Membaca `"slash slash"` dan Melewati Karakter Mandarin
- **Gejala:** Pada audio narasi Inggris/Indonesia (misalnya contoh `"一 / 二 / 三"` atau `"to look / watch / read"`), suara TTS melewati karakter Hanzi begitu saja lalu membacakan simbol `/` secara harfiah sebagai **"slash slash"** (atau *"garis miring"*).
- **Akar Penyebab:** String mentah berisi campuran aksara Hanzi dan operator (`/`, `+`, `()`, `→`) dikirim langsung ke suara non-Mandarin (`id-ID-GadisNeural` dan `en-US-JennyNeural`), yang memang tidak bisa membaca CJK dan melafalkan tanda baca `/` sebagai kata.
- **Solusi & Aturan Wajib:**
  - Setiap huruf atau komponen Mandarin (`看`, `手`, `目`, dst.) **wajib** disintesis terpisah menggunakan suara Mandarin (`zh-CN-XiaoxiaoNeural`).
  - Naskah untuk `id-ID-GadisNeural` dan `en-US-JennyNeural` harus **100% bahasa Indonesia/Inggris murni** — ganti `" / "` menjadi `"atau"` / `"or"`.
  - Pasang penjaga validasi keras sebelum memanggil `edge-tts` (`validate_tts_segment` di `build_one_exemplar.py`): gagalkan eksekusi (*assert error*) jika teks ID/EN masih mengandung rentang CJK `U+2E80..U+9FFF` atau karakter `/ + ( ) → ↘ ·`.

---

### 2. Ilustrasi Tampak Seperti Gambar Anak Kecil (Vektor Pillow vs Model Gambar AI)
- **Gejala:** Ratusan kartu awal menggunakan ikon vektor sederhana buatan skrip Python Pillow (`01_build_actor_sprites.py` → `sprites/*.png`) yang ditempel di samping font komputer biasa (`illustrations_composed/*.png`), sehingga terlihat kaku seperti gambaran anak kecil dan bukan ilustrasi menyatu khas Chineasy.
- **Akar Penyebab:** Ketika kuota model gambar AI (`gemini-3.1-flash-image`) terkena batas limit (`429 RESOURCE_EXHAUSTED`), pipeline otomatis beralih ke fallback gambar geometris prosedural dan langsung merender massal tanpa persetujuan visual.
- **Solusi & Aturan Wajib:**
  - **Dilarang** menggambar ilustrasi karakter atau sprite aktor secara prosedural dengan bentuk geometris Pillow.
  - Ilustrasi harus dibuat oleh model gambar AI langsung di atas template goresan (`templates/<char>.png`), sehingga bentuk visualnya **menyatu menjadi goresan huruf** (contoh: goresan `手` menjadi tangan terakota, goresan `目` menjadi mata biru tua di [`看.jpg`](file:///Volumes/App/Workspace/chinese-mnemonic-demo/illustrations/看.jpg)).
  - Jika kuota model gambar AI sedang habis, **hentikan proses pembuatan gambar**, jangan paksakan fallback prosedural ke seluruh dataset.

---

### 3. Gambar Tidak Nyambung dengan Cerita Mnemonik (Kasus `儿 ér`)
- **Gejala:** Pada kartu seperti `儿 (ér)`, teks cerita menulis *"two playful child legs"*, padahal ikon yang tampil adalah gambar bayi dibedong tanpa kaki, dan goresan karakter `儿` tidak memiliki ilustrasi kaki sama sekali.
- **Akar Penyebab:** Penulisan teks diambil otomatis dari tabel definisi komponen abstrak terpisah, bukan berdasarkan objek visual yang benar-benar digambar pada ilustrasi kartunya.
- **Solusi & Aturan Wajib:**
  - Wajib ada keselarasan **1:1** antara gambar ilustrasi AI, warna label komponen, dan teks mnemonik.
  - Pada exemplar `看`: gambar AI memperlihatkan tangan merah di atas (`手`) dan mata biru tua di bawah (`目`); rumus komponen diberi warna yang sama persis (`手` terakota + `目` biru tua); cerita menjelaskan secara harfiah adegan di gambar.

---

### 4. Tidak Ada Pinyin, Petunjuk Nada (`Petunjuk Nada`), & Hook Mnemonik Pendek
- **Gejala:** Kartu dan video sebelumnya hanya mencantumkan arti kamus dan deskripsi panjang prompt gambar, tanpa memberi tahu nada pengucapan secara eksplisit dan tanpa *hook* mnemonik singkat yang gampang diingat.
- **Akar Penyebab:** Template kartu memakai metadata mentah (`meaning` + `prompt`) tanpa merancang struktur belajar inti untuk pemula.
- **Solusi & Aturan Wajib:** Setiap kartu & frame video harus memuat empat elemen inti secara jelas:
  1. **Hanzi + Pinyin besar** (`看  kàn`).
  2. **Pill Petunjuk Nada + Diagram Kontur Vektor** (contoh: `Nada 4 · Turun Tegas (5 ke 1)` dengan garis panah 5→1), ditambah **tip pengucapan singkat** (`Ucapkan "kan!" tegas turun seperti suara menghentak`).
  3. **Rumus komponen sederhana** berwarna senada dengan ilustrasi (`手 (shǒu · tangan) + 目 (mù · mata)`).
  4. **Hook mnemonik 1 kalimat pendek yang lengket:** *"Tangan (手) menaungi mata (目) menatap jauh = MELIHAT!"*.

---

### 5. Kebocoran Istilah Internal Pipeline (`"Consistent actors"` / `"Peran konsisten"`)
- **Gejala:** Muncul teks seperti `"Consistent actors: ..."`, `"Peran konsisten: ..."`, dan label `"AKTOR SPRITE"` di bagian kartu maupun pembacaan voiceover.
- **Akar Penyebab:** Label desain sistem internal yang dipakai saat mengelompokkan radikal komponen ikut dimasukkan ke field teks tampilan pengguna.
- **Solusi & Aturan Wajib:** Seluruh istilah arsitektur internal (`consistent actor`, `peran konsisten`, `sprite`, nama file/ID) dilarang tampil di kartu visual, galeri, maupun naskah TTS.

---

### 6. Jeda Hening Panjang (~1,3 Detik) Antar Potongan Suara `edge-tts`
- **Gejala:** Saat audio Mandarin + Indonesia digabung per segmen (`6` klip di Scene 1 + `2` klip di Scene 2), video `看` yang seharusnya padat ~15 detik melar menjadi `29.63s` dengan jeda mati ~1,4 detik setiap selesai mengucapkan satu huruf Mandarin (`看` … *hening 1,4 detik* … `Nada empat...`).
- **Akar Penyebab:** Setiap keluaran MP3 dari `edge-tts` membawa *trailing silence* bawaan `900–1400ms` dan *leading silence* `155–217ms` sebelum audio bicara benar-benar mulai.
- **Solusi & Aturan Wajib:**
  - Terapkan fungsi pemangkas keheningan berbasis level sampel PCM 16-bit (`trim_pcm_silence` di `build_one_exemplar.py`) yang hanya menyisakan margin `30ms` di awal dan `60ms` di akhir dengan `6ms` *fade*, lalu sisipkan jeda terkontrol `110–240ms`.
  - Efek terukur pada exemplar `看`: durasi video Indonesia menyusut dari **`29.63s` → `20.48s`**, dan video Inggris menyusut dari **`23.98s` → `14.93s`** (hemat ~9 detik jeda kosong per video).

---

### 7. Index Font Latin Salah (Tercetak Italic) & Glyph Simbol Hilang (`[?]`)
- **Gejala:** Teks judul di skrip lama tercetak miring (*italic*) padahal dimaksudkan tebal tegak (*semibold*), serta karakter Unicode langka atau panah tertentu berubah menjadi kotak kosong `[?]` pada font yang tidak mendukung.
- **Akar Penyebab:**
  - Di `/System/Library/Fonts/Avenir Next.ttc`, `index=6` ternyata **Medium Italic**, sedangkan `Bold=0`, `Demi Bold=2`, `Medium=5`, dan `Regular=7`.
  - Font `/System/Library/Fonts/STHeiti Medium.ttc` memiliki dua subfont (`index=0` = *Heiti TC / Traditional*, `index=1` = *Heiti SC / Simplified*), dan font Latin `Avenir Next` tidak memiliki glyph CJK atau simbol panah/stroke tertentu.
- **Solusi & Aturan Wajib:**
  - Gunakan `index=1` (*Heiti SC Medium*) untuk Hanzi HSK 1 yang disederhanakan (*Simplified Chinese*) dan pisahkan segmen karakter melalui `split_runs()`.
  - Pakai index eksplisit untuk `Avenir Next.ttc` (`bold=0`, `demi=2`, `medium=5`, `regular=7`).
  - Gambar elemen grafis seperti diagram kontur nada 5→1 secara **vektor langsung di Pillow** (`draw_tone4_pill`), jangan andalkan glyph font Unicode panah.

---

### 8. Dependensi Homebrew Rusak (`ffmpeg`/`numpy`) & Aturan Workflow Anti-Boros Kredit
- **Kondisi Lingkungan macOS Ini:**
  - `/opt/homebrew/bin/ffmpeg` dan `ffprobe` crash saat startup karena `Library not loaded: /opt/homebrew/opt/libvpx/lib/libvpx.12.dylib`.
  - `numpy` Python gagal diimpor karena `Library not loaded: /opt/homebrew/opt/libomp/lib/libomp.dylib`.
  - Jalur aman tanpa Homebrew yang sudah teruji: konversi audio memakai `/usr/bin/afconvert` + modul bawaan Python (`wave`, `array`) + pengkodean & penggabungan MP4 memakai Swift `AVFoundation` ([`render_mp4.swift`](file:///Volumes/App/Workspace/chinese-mnemonic-demo/render_mp4.swift) dan [`concat_mp4.swift`](file:///Volumes/App/Workspace/chinese-mnemonic-demo/concat_mp4.swift)).
- **Aturan Wajib Workflow:**
  - **Dilarang langsung menjalankan render batch penuh (181 huruf / 155 kata)** sebelum **1 kartu + 1 video exemplar** selesai dibuat, diperiksa visualnya satu per satu dengan mata (`read_file`), didengarkan/diperiksa naskah dan durasi audionya, serta disetujui kualitasnya.
  - Database [`ChineseGradedReader`](file:///Volumes/App/Workspace/ChineseGradedReader) diperlakukan strictly **read-only** melalui referensi [`graded_reader_ref.json`](file:///Volumes/App/Workspace/chinese-mnemonic-demo/graded_reader_ref.json).

---

### 9. Asal-Usul Tiap Komponen Wajib Ditampilkan Satu per Satu Sebelum Gabungan
- **Gejala:** Video/kartu sebelumnya langsung membahas karakter gabungan (`看 = 手 + 目`), sekadar menyebut "tangan di atas, mata di bawah" tanpa memperlihatkan ilustrasi dan asal-usul piktograf komponen `手` dan `目` satu per satu terlebih dahulu.
- **Akar Penyebab:** Pipeline hanya membuat 1 ilustrasi untuk huruf gabungan dan melewatkan tahapan pengenalan visual masing-masing radikal pembentuknya.
- **Solusi & Aturan Wajib:**
  - Setiap karakter majemuk harus disusun dalam **alur progresif 3 langkah (`① → ② → ③`)**:
    1. **Langkah ① (Komponen 1):** Tampilkan ilustrasi AI komponen pertama berdiri sendiri + Hanzi + Pinyin + Nada + asal-usul piktografnya.
    2. **Langkah ② (Komponen 2):** Tampilkan ilustrasi AI komponen kedua berdiri sendiri + Hanzi + Pinyin + Nada + asal-usul piktografnya.
    3. **Langkah ③ (Gabungan):** Tampilkan cara kedua ilustrasi/makna itu menyatu menjadi karakter baru beserta hook mnemonik pendeknya.
  - Kartu statis (`cards/`) juga wajib menampilkan kartu mini asal-usul ① + ② bersebelahan lengkap dengan thumbnail ilustrasi AI masing-masing sebelum ilustrasi gabungan ③ di bagian tengah.

---

### 10. Evaluasi Ilustrasi AI `看.jpg` vs Standar Chineasy Asli & Pembaruan Kuas
- **Gejala Awal:** Pada versi awal (`STHeiti`), [`看.jpg`](file:///Volumes/App/Workspace/chinese-mnemonic-demo/illustrations/看.jpg) terlalu kaku menyerupai balok font biasa (tangan `手` seperti 3 balok diberi kuku kecil dan mata `目` kaku).
- **Solusi & Aturan Wajib:**
  - Prompt AI image generation memberi kebebasan siluet organik yang jelas langsung terbaca sebagai objek sambil menjaga kerangka guratan karakter.
  - Begitu kuota `gemini-3.1-flash-image` kembali pulih, [`看.jpg`](file:///Volumes/App/Workspace/chinese-mnemonic-demo/illustrations/看.jpg) dan [`好.jpg`](file:///Volumes/App/Workspace/chinese-mnemonic-demo/illustrations/好.jpg) di-generate ulang di atas template kaligrafi kuas bulat ([`templates/看.png`](file:///Volumes/App/Workspace/chinese-mnemonic-demo/templates/看.png) & [`templates/好.png`](file:///Volumes/App/Workspace/chinese-mnemonic-demo/templates/好.png)): tangan merah organik bertumpu menaungi mata bertoreh kuas biru tua dengan iris teal ekspresif untuk `看`, dan ibu bertusuk konde merah merengkuh bayi dibedong untuk `好`.

---

### 11. Naskah Bertele-tele, Penjelasan Posisi Tidak Perlu & Batas Durasi 20–30 Detik
- **Gejala:** Video 3-langkah awal terasa lambat (`45–53 detik`) karena naskah berulang-ulang menjelaskan hal yang sudah jelas di gambar (*"Mari lihat asal-usul komponennya satu per satu. Pertama, komponen di sebelah kiri..."*, *"Kedua, komponen di bagian bawah..."*, *"yang miring ke kiri saat berada di bagian atas..."*).
- **Akar Penyebab:** Narasi menguraikan posisi tata letak spasial (*kiri/kanan/atas/bawah*) dan kalimat pembuka yang panjang, padahal pemirsa langsung melihat posisi dan visualnya di layar.
- **Solusi & Aturan Wajib:**
  - **Hapus seluruh penjelasan posisi spasial** dari judul kartu (`ASAL KARAKTER 1` / `ASAL KARAKTER 2`, bukan `KOMPONEN KIRI/KANAN`), deskripsi piktograf, maupun naskah suara.
  - Gunakan kalimat super singkat, padat, dan langsung pada inti makna + gambar (*contoh per babak:* `"女。 Artinya perempuan atau ibu, berasal dari gambar sosok ibu yang duduk bersimpuh dengan anggun."`).
  - **Target durasi wajib video Shorts 3-langkah:** **20 sampai 30 detik (`20.0s – 30.0s`)**, ditegakkan langsung melalui assertion di [`build_one_exemplar.py`](file:///Volumes/App/Workspace/chinese-mnemonic-demo/build_one_exemplar.py).

---

### 12. Jangan Menyebut Nomor/Arah Nada di Narasi Voiceover (Sudah Terlihat di Layar & Diucapkan Penutur Mandarin)
- **Gejala:** Narator Indonesia/Inggris sebelumnya terus mengucapkan `"Nada tiga, ..."` atau `"Third dipping tone, ..."` dan mencetak baris tips verbal berulang di bawah kartu.
- **Akar Penyebab:** Informasi pelafalan yang sudah dibacakan oleh suara Mandarin asli (`zh-CN-XiaoxiaoNeural`) dan sudah ditampilkan jelas lewat Pinyin + pill kontur nada di layar tetap diulang secara verbal.
- **Solusi & Aturan Wajib:**
  - **Hapus seluruh penyebutan nomor/arah nada** (`"Nada tiga"`, `"Nada empat"`, `"Third dipping tone"`, `"Fourth falling tone"`) dari naskah suara ID/EN, dan hapus baris tips pengucapan di bagian bawah kartu ringkasan.
  - Biarkan penutur asli Mandarin langsung melafalkan karakter dengan nada aslinya, sementara indikator visual Pinyin + kontur nada tetap tampil bersih di layar, sehingga narator ID/EN langsung fokus menjelaskan **arti, gambar piktograf asal, dan cerita gabungannya**.

---

### 13. Koreografi Sinkronisasi 3 Babak: Animasi Urutan Guratan → Transisi Gradual Ilustrasi AI + Mnemonik 3 Karakter
- **Gejala:** Sebelumnya animasi menulis terpisah di babak ke-4 (membuat video lebih panjang), babak 1–2 masih statis, dan kalimat mnemonik belum secara eksplisit memakai ketiga karakter pembentuk sekaligus (`Komponen 1` + `Komponen 2` = `Karakter 3`).
- **Solusi & Aturan Wajib:**
  - Gunakan **3 babak animasi 30fps yang tersinkron langsung ke timestamp suara (`build_one_exemplar.py`)**:
    1. **Babak 1 (Karakter Asal 1):** Saat nama & arti karakter 1 diucapkan, guratan resmi (`hanzi-writer-data`) digambar sesuai urutan guratan (`女` = 3 guratan, `手` = 4 guratan). Tepat saat narator menyebut asal gambar (*"Berasal dari..."* / *"Coming from..."*), guratan huruf berubah **gradual (*smoothstep crossfade*)** memunculkan ilustrasi AI-nya.
    2. **Babak 2 (Karakter Asal 2):** Alur yang sama untuk komponen kedua (`子` = 3 guratan, `目` = 5 guratan) — digambar berurutan lalu transisi gradual memunculkan ilustrasi AI komponen kedua saat narator menyebut asal gambarnya.
    3. **Babak 3 (Mnemonik 3 Karakter + Animasi Menulis Utuh):** Saat narasi mengucapkan mnemonik natural yang memakai ketiga karakter (*"Saat 女 ibu, memeluk 子 anak, rasanya 好 artinya baik atau suka"* / *"Taruh 手 tangan, di atas 目 mata, untuk 看 artinya melihat"*), kuas menggambar guratan komponen 1 dan komponen 2 secara berurutan tepat mengikuti timing ucapan, lalu memunculkan ilustrasi gabungan AI secara gradual di akhir.
  - **Validasi posisi nomor guratan:** Algoritma penempatan lencana angka (`1..N`) menggeser otomatis titik awal bila dua guratan berawal dekat (contoh guratan `5` & `6` pada `看`) agar angka tidak saling menumpuk.
  - **Durasi tetap ketat di rentang 20–30 detik** untuk seluruh bahasa.

---

### 14. Urutan TTS Mnemonik Alami (`Arti → Hanzi`) & Keseragaman 1:1 Tulisan vs Ilustrasi
- **Gejala:**
  1. Pada narasi mnemonik Babak 3, urutan sempat menyebut `"Saat 女, ibu,"` yang terasa terbalik secara logika bahasa Indonesia/Inggris dibandingkan *"Saat ibu (女)..."*.
  2. Animasi tulisan dan ilustrasi AI harus berbagi sistem koordinat yang sama persis supaya transisi *morph* mulus tanpa efek ganda (*ghosting*).
- **Solusi & Aturan Wajib:**
  - **Urutan bicara mnemonik wajib `Arti → Hanzi`:** Gunakan alur bicara alami (*"Saat ibu, 女，memeluk anak, 子，rasanya baik dan suka, 好..."* / *"Taruh tangan, 手，di atas mata, 目，untuk melihat jauh, 看..."*) dan selaraskan dengan teks tertulisnya (*"Saat ibu (女) memeluk anak (子)..."*).
  - **Koordinat tunggal `BRUSH_SPECS`:** Kotak pemotongan tiap komponen (`comp1`, `comp2`) dan gabungan (`combined`) dipakai bersama secara 1:1 oleh perender guratan maupun pemotong ilustrasi AI.

---

### 15. Keseragaman Font Kaligrafi Kuas Bulat (`Coretan Kuas` / Kaiti) di Seluruh Komponen (Tanpa Font Kotak `STHeiti`)
- **Gejala:** Font `STHeiti Medium` berbentuk kaku/mengotak (*sans-serif*), sehingga kurang alami untuk pembelajaran menulis kaligrafi Mandarin maupun ilustrasi bergaya kuas Chineasy; selain itu penggunaan dua font berbeda antara header hero, mini-card, teks kalimat, animasi tulisan, dan ilustrasi memicu ketidakseragaman bentuk huruf.
- **Akar Penyebab:** Skrip sebelumnya memakai `STHeiti Medium.ttc` (`index=1`) untuk teks/header/template sekaligus mencampurnya dengan sumber font lain.
- **Solusi & Aturan Wajib:**
  - **Hapus total penggunaan font kotak `STHeiti`** di seluruh pipeline visual (`build_one_exemplar.py`).
  - **Gunakan satu keluarga gaya kaligrafi kuas bulat (`Kaiti` / `hanzi-writer-data`) secara seragam untuk 100% komponen:**
    1. **Template karakter (`templates/好.png`, `templates/看.png`)**: dirender langsung dari poligon vektor kuas [`stroke_data/`](file:///Volumes/App/Workspace/chinese-mnemonic-demo/stroke_data/) (`hanzi-writer-data@2.0.1`).
    2. **Ilustrasi AI (`illustrations/好.jpg`, `illustrations/看.jpg`)**: di-generate langsung di atas template coretan kuas tersebut.
    3. **Animasi guratan 30fps (`米字格`) & Strip urutan guratan (`1..N`)**: dirender 2× *supersampled* dari data poligon & median kuas yang sama (`build_brush_stroke_masks`).
    4. **Judul Hero Hanzi (Babak 1, 2, 3) & Mini-Card Komponen**: dirender dari poligon vektor kuas yang sama persis (`render_brush_glyph_rgba` / `draw_brush_hero_with_pinyin`).
    5. **Teks CJK sebaris** (*formula `女 + 子 = 好`, kalimat mnemonik*): memakai font kaligrafi Kaiti bawaan macOS (`Kaiti.ttc`, `index=3` = `Kaiti SC Bold`).

---

### 16. Layering Wajib: Goresan Karakter Menimpa Gambar Ilustrasi (`Karakter di Atas, Ilustrasi di Belakang`)
- **Gejala:** Ketika transisi akhir memakai `Image.blend(completed_strokes_tile, art_tile, alpha)` dari `0.0 → 1.0`, ilustrasi AI justru menimpa dan menutupi penuh goresan karakter (terutama komponen bayi terakota `子` di `好` dan tangan merah `手` di `看`), sehingga huruf Mandarin-nya tidak lagi terbaca di kartu maupun akhir setiap babak.
- **Akar Penyebab:** Transisi *crossfade* menggantikan layer guratan huruf dengan gambar ilustrasi rata (`opacity = 1.0`) tanpa mempertahankan layer guratan karakter di lapisan teratas.
- **Solusi & Aturan Wajib (`_composite_strokes_over_art`):**
  - **Karakter selalu menimpa gambar (lapisan teratas permanen):** Setelah ditulis pada fase `a_*`, guratan kaligrafi kuas (`masks[0..N-1]`) **tidak pernah menghilang** — ilustrasilah yang muncul perlahan di **belakang karakter** (`illus_alpha = 0.0 → 1.0` pada opasitas halus maksimal `76%` di atas latar `#F9F5EC`).
  - **Halo pemisah & tinta kontras tinggi:** Sisipkan halo krem `#F9F5EC` tipis (`MaxFilter(7)` untuk kotak utama, `MaxFilter(5)` untuk mini-thumbnail) di antara ilustrasi dan guratan, lalu render guratan huruf di lapisan paling atas memakai tinta kontras tinggi (`#14203A` biru tua dan `#A52622` merah-terakota tua; dua batang dalam `目` sedikit diredam ke `86%` agar iris mata teal di belakangnya tetap terbaca).
  - **Konsisten di seluruh kartu & mini-card:** Babak 1, Babak 2, Babak 3, thumbnail mini-card ① & ②, dan seluruh kartu statis (`cards/` & `cards_en/`) menerapkan komposisi karakter-di-atas-ilustrasi ini.

---

### 17. Penghapusan Bayangan Ganda Bawaan Gambar AI & Mata Diputar Tegak (`Anti Bayangan Karakter`)
- **Gejala:**
  1. Pada `看` (`手 + 目`), ilustrasi awal mata manusia tergambar mendatar di samping bingkai huruf daripada tegak mengikuti batang vertikal `目`, serta sempat muncul bayangan pinggir guratan `目` yang sedikit bergeser (*ghost stroke shadow / bayangan karakter*) saat model AI mengedit gambar langsung.
  2. Pada ilustrasi komponen lain (`休`, `明`), sisa piksel guratan terakota/navy tipis di luar mask vektor resmi atau piksel pinggir bertempo rendah dapat memunculkan pinggiran ganda (*halo kotor*) atau celah titik saat dipotong ke mini-card.
- **Akar Penyebab:** Generator gambar AI sering meninggalkan *baked-in stroke outline* yang sedikit bergeser dari koordinat poligon kuas resmi (`hanzi-writer-data`), atau piksel warna tepi (*dark rim* / *anti-aliased fringe*) tidak tercakup di filter mask komponen.
- **Solusi & Aturan Wajib:**
  - **Bersihkan seluruh bayangan karakter bawaan AI di luar mask resmi (`_build_canvas_stroke_mask` + `MaxFilter(3)`):** Goresan kaligrafi final berasal tunggal dari mask poligon resmi di lapisan paling atas (`_composite_strokes_over_art(..., halo_filter_size=3)`).
  - **Mata manusia di `看` wajib diputar 90° tegak (`Mata manusia yang diputar tegak`):** Digambar presisi *4× supersampled* tepat di dalam bingkai kuas `目` (`x=478..634, y=966..1154`) dengan iris teal terpusat di antara dua palang horizontal `目` (guratan 7 & 8) — nol bayangan karakter ganda.
  - **Pemisahan warna komponen akurat:** Pada `明`, ambang batas warna biru bulan sabit (`(r < 110 and g < 115 and b < 140)`) melindungi gradasi biru muda bulan `月`; pada `休`, filter `is_sage` mencakup piksel rim daun hijau gelap (`121, 154, 137`) maupun pinggiran anti-aliased tanpa titik bolong dan bebas goresan rambut liar di luar kepala.

---

### 18. Pemunculan Ilustrasi Komponen 1 Sebelum Penulisan Komponen 2 di Babak 3 (`Stage 1A → 1B → 2A → 2B`)
- **Gejala:** Pada Babak 3 (Babak Gabungan), sebelumnya seluruh guratan komponen 1 (`0 .. split - 1`) dan komponen 2 (`split .. n_strokes - 1`) langsung digambar berturut-turut, baru ilustrasi gabungan dimunculkan sekaligus di akhir. Akibatnya saat komponen 1 sudah selesai ditulis (misalnya `日` matahari pada `明`, `人` orang pada `休`, `女` ibu pada `好`, `手` tangan pada `看`), gambar komponen pertamanya belum terlihat sebelum komponen kedua mulai ditulis.
- **Akar Penyebab:** `render_combined_synced_scene` hanya memanggil perender guratan polos untuk fase `p1` dan `p2`, lalu memudar ke `artworks["combined"]` pada fase `p3` tanpa jeda pemunculan ilustrasi komponen 1 (`combined_c1`).
- **Solusi & Aturan Wajib (`_render_s3_progressive_tile` + 4 Tahap Babak 3):**
  - Tambahkan crop komponen 1 pada koordinat penuh gabungan (`artworks["combined_c1"]` di `build_aligned_ai_artworks`) serta perpanjang jeda transisi narasi Babak 3 (`inter_phase_ms = 480`).
  - Jalankan koreografi progresif 4 tahap di Babak 3 (`render_combined_synced_scene`):
    1. **Tahap 1A (`p1_write`):** Tulis guratan komponen 1 (`0 .. split - 1`) di atas kotak `米字格`.
    2. **Tahap 1B (`p1_morph`):** Begitu komponen 1 selesai ditulis, pudarkan ilustrasi komponen 1 (`artworks["combined_c1"]`) masuk di belakang goresan komponen 1 (sambil tetap mempertahankan garis bantu `米字格` untuk area komponen 2) dan tahan jelas sebelum komponen 2 dimulai.
    3. **Tahap 2A (`p2_write`):** Tulis guratan komponen 2 (`split .. n_strokes - 1`) sementara ilustrasi komponen 1 tetap tampil penuh di belakang goresan komponen 1 (`c1_illus_alpha = 1.0`).
    4. **Tahap 2B (`p3_morph`) + Tahan Akhir:** Pudarkan ilustrasi komponen 2 ke komposisi penuh (`artworks["combined"]`) sementara seluruh goresan huruf tetap menimpa di lapisan teratas.
  - **Terverifikasi lintas 4 exemplar (ID & EN):** [`明_s3_c1_morph_id.png`](file:///Volumes/App/Workspace/chinese-mnemonic-demo/exemplars/明_s3_c1_morph_id.png) → [`明_s3_write_p2_id.png`](file:///Volumes/App/Workspace/chinese-mnemonic-demo/exemplars/明_s3_write_p2_id.png), beserta `休`, `好`, dan `看` (seluruh 8 MP4 terverifikasi `20.37s – 23.67s`).
