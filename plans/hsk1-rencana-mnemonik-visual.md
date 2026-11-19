# Rencana mnemonik visual HSK 1

18 November 2026

[Rencana lintas jalur Indonesia–Inggris](kurikulum-lintas-jalur-id-en.md) · [Rencana partikel Mandarin](partikel-rencana-id-en.md) · [277 English image briefs](hsk1-visual-briefs-en.md)

## Cakupan

Mulai dari **246 karakter baca** pada lampiran HSK 3.0 Level 1, halaman cetak 265–266. Cek silang 300 entri kosakata Level 1 menghasilkan 248 karakter unik. **店** dan **饺** muncul di kosakata, walaupun keduanya absen dari lampiran karakter baca. Masukkan keduanya supaya pembelajar dapat membuka setiap karakter di kata yang ditampilkan. [Silabus CTI](https://hsk.cn-bj.ufileos.com/3.0/%E6%96%B0%E7%89%88HSK%E8%80%83%E8%AF%95%E5%A4%A7%E7%BA%B21219.pdf)

Katalog lama proyek berisi 178 karakter inti dan tiga bonus. Pertahankan **京 北 站 馆** dari katalog lama, serta **山** dari bonus lama. **休** dan **息**, yang sebelumnya bonus, sekarang juga masuk lampiran resmi. Target gabungan untuk proyek ini adalah **253 karakter unik**. Karakter pendukung dan homonim ditautkan sebagai materi tambahan. Keanggotaan HSK dicek per karakter, termasuk bila satu karakter berperan sebagai pendukung sekaligus anggota daftar inti. [Katalog lama proyek](../01_OFFICIAL_HSK1_LIST.md)

[Sketsa teks lanjutan](hsk1-sketsa-teks-lanjutan.md) melengkapi brief pertama dengan rancangan adegan untuk setiap Hanzi lainnya dalam daftar. [Daftar kerja per karakter](hsk1-daftar-kerja.tsv) memuat seluruh target, nomor lampiran bila ada, sumber daftar, kelompok riset, dan status brief. Referensi lokal untuk 300 kosakata ada di `ChineseGradedReader/App/Workspace/Reader/hsk3_official_vocabulary.json`.

[Indeks kandidat homonim](hsk1-kandidat-homonim.md) memuat 38 kelompok bunyi bernada untuk dipilih dan diperiksa sebelum ditampilkan.

## Cara sampai ke akar aksara

1. **Tetapkan bacaan dari kata HSK yang memakainya.** Catat Hanzi sederhana, pinyin bernada, satu arti Indonesia untuk konteks itu, serta audio. Jika ejaan sama punya bacaan berbeda, beri contoh terpisah pada saat bacaan kedua diperlukan. Catat juga bacaan di dalam kata bila berbeda, seperti **不 bù** yang terdengar **bú** sebelum nada keempat.
2. **Mulai dari bentuk modern yang benar.** Ambil guratan Hanzi sederhana dari Hanzi Writer Data, kemudian cek pembagian bentuk dengan kamus. Contoh koreksi untuk daftar awal proyek: **吃** memuat **乞**, **杯** memuat **不**, dan **店** memuat **占**. Objek gambar mengikuti bentuk yang benar sejak awal.
3. **Telusuri bentuk lama dan peran komponennya.** Gunakan basis data CUHK untuk bentuk yang terdokumentasi dan kamus Kementerian Pendidikan Taiwan atau kutipan *Shuōwén Jiězì* untuk membandingkan tafsir. Simpan tautan dan satu kalimat yang dapat ditunjukkan sumbernya. Untuk aksara sederhana yang mewarisi bentuk tradisional, catat jalur itu bila membantu menjelaskan bentuk sekarang. [Basis data CUHK](https://humanum.arts.cuhk.edu.hk/Lexis/lexi-mf/) · [Kamus Kementerian Pendidikan Taiwan](https://dict.variants.moe.edu.tw/)
4. **Bedakan fungsi setiap bagian.** Tulis apakah bagian itu memberi makna, membantu bunyi, atau dipakai untuk mengingat bentuk. Jika tafsir lama berbeda, beri catatan pendek yang bisa dibuka. Mnemoniknya tetap boleh sederhana dan masuk akal. Untuk **摘**, tangan **扌** menjelaskan makna memetik. Rangka kayu membantu mengingat bentuk **啇**, yang berperan sebagai petunjuk bunyi historis.
5. **Ajarkan karakter pendukung saat pertama dibutuhkan.** Beri bentuk, pinyin, arti, dan audio atau tautan singkat. Komponen seperti **氵** dikenalkan lewat karakter asalnya **水 (shuǐ, air)**. Ajarkan komponen yang benar-benar membantu mengingat bentuk atau yang berulang di banyak kata. Pada **不**, **飞 (fēi, terbang)** membantu adegan mnemonik meski guratan bawah **不** berbeda dari **飞**.
6. **Cari pasangan bunyi setelah bacaan inti pasti.** Cocokkan suku kata dan nada. **青 / 清 (qīng)** adalah homonim yang juga berbagi komponen. **请 (qǐng)** dan **晴 / 情 (qíng)** masuk keluarga bentuk **青** dengan nada berbeda. **晴 / 情** juga homonim satu sama lain. Pilih pasangan yang membantu memahami kata umum. Jika menambahkan contoh kata, seluruh karakter yang baru harus punya arti, pinyin, dan jalan langsung ke pelajarannya.
7. **Pisahkan aksara gabungan dari kata majemuk saat menjelaskan.** Pada **清**, **氵** memberi makna air dan **青** memberi bunyi. Pada **清水 (qīngshuǐ, air jernih)**, **清** menerangkan **水**. Tunjukkan keduanya hanya sesudah pembelajar mengenal tiap bagian.

## Cara merancang gambarnya

- **Gabungan selalu dua tahap.** Tahap pertama menunjukkan objek atau komponen acuan. Tahap kedua melakukan satu perubahan yang menjelaskan arti dan menampilkan Hanzi lengkap. Kedua tahap memakai sudut kamera yang sama bila memungkinkan. Latihan dan catatan etimologi ada di dalam tahap yang relevan atau di bawahnya.
- **Kunci bentuk Hanzi sebelum merancang adegan.** Pakai satu koordinat dan satu skala seragam untuk seluruh aksara. Sembunyikan guratan yang belum muncul. Tangan, mata, daun, dan benda lain yang disesuaikan dengan mal. Setiap brief menentukan objek, posisi, arah gerak, dan guratan yang diwakili. [Hanzi Writer Data](https://github.com/chanind/hanzi-writer-data)
- **Uji gambar bersih dulu.** Tanpa huruf dan teks, orang harus bisa melihat tindakan atau perbedaannya. Setelah itu, cek gambar dengan guratan. Jika pose yang masuk akal membuat guratan utama meleset, revisi konsep adegannya sebelum produksi. Aksara tunggal yang sudah jelas sebagai piktogram bisa memakai satu adegan sederhana.
- **Makna abstrak memakai konteks.** Untuk **的、了、吗、呢** atau kata sejenis, gambar menunjukkan hubungan, perubahan keadaan, atau jenis pertanyaan. Penanda bentuk bisa tampil di kartu kecil. Cerita gambar dan catatan asal aksara tetap terpisah.

## Brief pertama yang bisa dinilai sebelum produksi

Setiap baris sudah punya ide gambar. Hubungan etimologi dan bacaan tetap diperiksa per entri sebelum menjadi naskah final.

| Aksara dan arti | Tahap pertama | Tahap kedua atau penyelesaian | Pendukung yang perlu dikenalkan |
|---|---|---|---|
| **木 mù** · pohon | Pohon muda di latar tenang, batang tegak, satu tingkat dahan ke samping dan dua dahan menurun. | Satu adegan. Sorot batang dan dahan dengan empat guratan 木. | 木 dipakai kembali pada 本、休、杯. |
| **本 běn** · pangkal, dasar | Pakai pohon 木 yang sama. | Tanah bagian atas tersibak sedikit. Garis pendek menandai pangkal batang, membentuk 本. Pilih arti per kata, misalnya kata satuan untuk buku bila itu konteksnya. | 木 · pohon. |
| **休 xiū** · beristirahat | Pohon 木 berada di kanan dan memberi naungan. | Orang duduk menyandar dengan punggung ke batang di kiri. Siluet kiri menjadi 亻. | 人 rén · orang, bentuk kiri 亻. [Asal 休](https://humanum.arts.cuhk.edu.hk/Lexis/lexi-mf/oraclePiece.php?piece=%E4%BA%BA&start=30) |
| **生 shēng** · tumbuh | Tanah dilihat dari samping, garis permukaannya jelas. | Tunas menembus garis tanah. Batang dan daun menjadi acuan bentuk 生. | 一 yī · satu. Pada bentuk awal 生, garis bawah menggambarkan permukaan tanah. [Asal 生](https://humanum.arts.cuhk.edu.hk/Lexis/lexi-mf/search.php?word=%E7%94%9F) |
| **丹 dān** · mineral merah | Sebongkah mineral merah di atas batu pucat. | Bila dibuat satu adegan, mangkuk pigmen merah ada di sebelahnya untuk menghubungkan mineral dan warna. | Kaitkan kembali ke warna pot pada 青. [Arti 丹](https://dict.variants.moe.edu.tw/dictView.jsp?ID=189) |
| **青 qīng** · hijau atau biru kehijauan | Pot merah 丹 dengan kecambah kecil. Arti dan audio dān sudah tampil. | Batang dan daun hijau bertumbuh. Guratan 生 versi komponen melengkapi 青. | 生 shēng · tumbuh, 丹 dān · mineral merah. [Asal 青](https://humanum.arts.cuhk.edu.hk/Lexis/lexi-mf/search.php?word=%E9%9D%92) |
| **水 shuǐ** · air | Sungai dangkal dari atas, satu arus utama di tengah dan arus kecil di sisi. | Satu adegan utama dengan guratan 水, lalu tunjukkan bentuk kiri 氵 di sampingnya. | 氵 adalah bentuk komponen kiri 水. [Asal 水](https://dict.variants.moe.edu.tw/dictView.jsp?ID=23284) |
| **清 qīng** · jernih | Tanaman dan pot merah 青. | Pot berada di kanan sungai dangkal. Tiga guratan 氵 mengikuti riak di kiri. Batu di dasar terlihat lewat air. | 水 → 氵 · air, 青 · bunyi qīng. [Asal 清](https://humanum.arts.cuhk.edu.hk/Lexis/lexi-mf/search.php?word=%E6%B8%85) |
| **请 qǐng** · silakan, meminta | Pot 青 di kanan sebagai pengingat bunyi. | Di kiri, seorang tuan rumah mengucapkan “Silakan masuk” kepada tamu. Gunakan bentuk 讠 yang dikunci di dekat mulut, dengan gelembung ucapan kecil sebagai petunjuk aksi. | 言 yán · ujaran, bentuk sederhana 讠. 青 memberi petunjuk bunyi, nada 请 berbeda. |
| **晴 qíng** · cerah | Pot 青 di kanan terlihat di bawah bayangan. | Matahari muncul di kiri, membentuk 日. Cahaya pada pot dan tanah menunjukkan cuaca cerah. | 日 rì · matahari, 青 · petunjuk bunyi. |
| **情 qíng** · perasaan | Pot 青 di kanan dekat tempat dua orang bertemu. | Di kiri, orang meletakkan tangan di dada saat melihat orang yang dirindukan. Guratan 忄 di dekat dada menandai perasaan. | 心 xīn · hati, bentuk kiri 忄. Bandingkan dengan 晴 yang sama-sama qíng. |
| **人 rén** · orang | Orang berdiri dalam profil tiga perempat, dua garis utama tampak dari bentuk badan dan kaki. | Satu adegan. Tampilkan 人 dan bentuk miring 亻 dalam kartu pendukung kecil. | Dipakai kembali pada 休、你、他. |
| **目 mù** · mata | Perlihatkan satu mata yang memandang jauh. | Satu adegan. Sorot kelopak dan bentuk luar mata dengan guratan 目. | Bedakan dari 木: keduanya mù, gambarnya berbeda. |
| **手 shǒu** · tangan | Satu tangan normal dilihat dari samping, jari-jari lurus rileks dan menyambung ke lengan. | Satu adegan. Tunjukkan 手 dan peralihannya ke bentuk kiri 扌 dalam kartu kecil. | 扌 muncul pada 打、摘、找. |
| **看 kàn** · melihat | Pendaki menatap jauh. 目 sudah terlihat pada mata. | Tangan dan lengan terangkat menaungi mata. Empat guratan atas menyala untuk melengkapi 看. | 手 · tangan dan 目 · mata. |
| **飞 fēi** · terbang | Sayap dan ekor burung tampak saat burung terbang naik, dengan pose mengikuti 飞. | Satu adegan. Jaga kepakan dan ekor terbaca sebelum mal ditampilkan. | Motif dipakai kembali di 不. |
| **不 bù** · tidak | Burung naik mengikuti 飞. Garis 一 menandai balok langit-langit. | Paruh membentur balok. Sayap, tubuh, dan ekor melengkapi 不. Burung tidak bisa naik lebih tinggi. | 一 yī · satu dan 飞 fēi · terbang. Tafsir burung dicatat di *Shuōwén*. |
| **杯 bēi** · cangkir | Papan kayu 木 ada di kiri meja kerja. | Pengrajin menaruh cangkir kayu jadi di kanan. Pola guratan 不 ditampilkan pada sisi cangkir sebagai pengingat bentuk kanan. | 木 mù dan 不 bù. Periksa hubungan bunyi lama sebelum memberinya label sejarah. |
| **爪 zhǎo / zhuǎ** · cakar | Cakar burung terlihat jelas, dengan jari yang mencengkeram dahan. | Satu adegan utama. Tunjukkan bahwa bentuk 爫 di atas aksara dapat menggambarkan tangan yang meraih. | Baca dan dengarkan contoh 爪 pada halaman khususnya. |
| **采 cǎi** · memetik | Jari terulur seperti 爪 di atas pucuk sayur. Batang bawah membentuk 木. | Jari menjepit pucuk. Guratan atas berubah menjadi 爫, melengkapi 采. | 爪, 爫, 木. |
| **菜 cài** · sayur | Pakai gambar meraih pucuk dari 采. | Pakai versi dua pucuk kecil digenggam dari tangkapan layar. Tunjukkan 艹 di atas 采 dengan acuan 菜 utuh. | 艹 · tumbuhan, 采 cǎi · memetik dan petunjuk bunyi. [Asal 菜](https://humanum.arts.cuhk.edu.hk/Lexis/lexi-mf/search.php?word=%E8%8F%9C) |
| **摘 zhāi** · memetik | Ceri tergantung di ranting. Ranting dan kerangka kebun mengikuti 啇 di kanan. | Tangan datang dari kiri dan membawa ceri lepas dari ranting. Pastikan ada jarak yang terlihat antara tangkai dan ranting. | 扌 · tangan, 啇 · bentuk kanan dan petunjuk bunyi historis. [Asal 摘](https://humanum.arts.cuhk.edu.hk/Lexis/lexi-mf/search.php?word=%E6%91%98) |
| **口 kǒu** · mulut | Tampak dekat satu mulut terbuka. | Satu adegan. Bibir mengelilingi ruang terbuka yang mengikuti bentuk 口. | Dipakai pada 吃、喝、唱. |
| **吃 chī** · makan | Mulut 口 di kiri, satu suapan masih di kanan. | Orang memasukkan suapan. Siluet jalur sendok yang melengkung memberi jangkar untuk 乞. Perlihatkan 乞 sebagai bentuk tetap yang terpisah dari gambar bila posisi sendok kurang cocok. | 口 kǒu · mulut, 乞 qǐ · meminta. Bentuk sekarang memakai 乞. Kata ‘makan’ juga pernah ditulis 喫. [Riwayat 吃](https://humanum.arts.cuhk.edu.hk/Lexis/lexi-mf/search.php?word=%E5%90%83) |
| **渴 kě** · haus | Di kanan, pendaki beristirahat di bawah matahari. Aksen 曷 menjadi acuan bentuk. | Di kiri, tiga tetes air mengarah ke botol yang hampir kosong. Ekspresi dan botol kosong menunjukkan rasa haus. | 水 → 氵 dan 曷 hé. Lihat perbandingan dengan 喝. |
| **喝 hē** · minum | Pakai orang dan adegan yang sama dengan 渴. Tunjukkan posisi 曷 di kanan. | Mulut 口 di kiri menyentuh bibir cangkir. Satu tegukan jelas terbaca. | 口 dan 曷 hé. Tindakan membedakan 喝 dari keadaan haus pada 渴. |
| **电 diàn** · listrik | Lampu meja mati, kabel terlihat. | Saat sakelar dinyalakan, lampu menyala dan kabel melengkung mengikuti garis bawah 电. | Bentuk lama 電 dapat dikenalkan melalui kilat sebagai catatan singkat. |
| **店 diàn** · toko | Atap toko di atas dan kiri mengikuti 广. | Pedagang membuka loket di bawah atap. Tiang papan tanda serta jendela loket memberi bentuk 占. | 广 · unsur bangunan, 占 zhān/zhàn · ajarkan bacaan sesuai konteks. Bedakan dari 电 yang juga diàn. |

## Kelompok riset berikutnya

| Kelompok | Prioritas ilustrasi | Pasangan bunyi atau pembeda yang diperiksa |
|---|---|---|
| **1. Bentuk dan komponen pembuka** | Pohon, orang, tangan, air, pot, mulut, mata, dan garis dasar. Pakai kembali gambar yang sudah cocok untuk 看、不、采、菜、青、清 dan 摘. | 木 / 目 **mù**, 青 / 清 **qīng**, 晴 / 情 **qíng**. |
| **2. Aksi, makanan, dan keluarga** | Ambil satu aksi yang langsung terbaca, seperti duduk, membeli, menulis, minum, atau memanggil. Untuk keluarga, tempatkan orang dengan peran yang terlihat. | 做 / 坐 / 作 **zuò** pada bacaan yang relevan, 妈 **mā** / 吗 **ma**, 买 **mǎi** / 卖 **mài**. |
| **3. Benda, tempat, waktu, dan angka** | Benda dan tempat dipakai sesuai fungsi. Untuk waktu dan posisi, pakai benda acuan yang konsisten, seperti jam, matahari, meja, dan pintu. | 店 / 电 **diàn**, 在 / 再 **zài**, 衣 / 医 / 一 **yī** pada bacaan dasar, 时 / 十 **shí**, 午 / 五 **wǔ**. |
| **4. Partikel, kata sifat, dan hubungan** | Dua potret situasi atau dialog pendek. Beri satu konteks per makna yang diperkenalkan. | 是 / 事 / 市 **shì**, 对 / 队 **duì** bila 队 berguna sebagai pengayaan. |
| **5. Sisa daftar dan karakter lintas edisi** | Selesaikan semua baris yang masih menunggu di daftar kerja, termasuk karakter yang muncul hanya di kosakata. Cocokkan bahwa tautan pada contoh kata mengarah ke kartu yang tersedia. | Isi pasangan homonim yang berguna berdasarkan pinyin Mandarin bernada, dan tandai pendukung yang berada di luar cakupan Level 1. |

### Rancangan pembeda bunyi

- **木 / 目 · mù.** Dengarkan satu bunyi, lalu pilih antara dahan pohon dan mata pendaki. Pakai kembali gambar yang sudah dipelajari.
- **店 / 电 · diàn.** Satu pelajaran membuka loket toko, satu lagi menyalakan lampu. Saat dibandingkan, beri bunyi yang sama dengan dua gambar dan dua arti.
- **在 / 再 · zài.** Pakai satu anak dan satu bola. Untuk 在, bola berada di atas meja dan posisi tetap. Untuk 再, anak memantulkan bola sekali lagi setelah jeda. Pakai kartu aksara utuh jika ilustrasi aksi sulit mengikuti guratannya.
- **做 / 坐 / 作 · zuò.** Ajarkan contoh sesuai daftar. Pakai gambar tiga aksi yang bisa dibedakan sendiri, seperti anak membuat kerajinan, duduk di bangku, dan menghasilkan karya. Untuk 作, cek bacaan berdasarkan kata HSK yang dipilih sebelum membuat pembanding.
- **是 / 事 / 市 · shì.** Tampilkan satu per satu melalui konteks: mengidentifikasi suatu benda, membicarakan sebuah urusan, dan melihat pasar atau kota. Persamaan bunyi tidak mengharuskan asal aksara atau objeknya berhubungan.

## Urutan iterasi

- Kerjakan beberapa brief yang saling terkait dalam satu putaran. Mulai dari **木 → 本 → 休** dan **水 + 青 → 清**, lalu **青 → 请 / 晴 / 情**. Mereka memberi latihan bentuk, bunyi, dan nada dalam satu keluarga yang mudah dibandingkan.
- Sebelum sebuah brief siap digambar, periksa sumber asal, fungsi komponen, pinyin, kalimat mnemonik satu napas, posisi pada mal dan apakah perubahan antaradegan masuk akal. Tandai status per karakter. Jangan menganggap entry selesai hanya karena ada gambar lama.
- Periksa tiap sketsa dalam putaran teks sampai semua baris inti memiliki arti sesuai konteks, rencana audio, dan bentuk yang sesuai sumber. Setelah ada persetujuan untuk tahap visual, kerjakan dan periksa satu kelompok kecil pada satu waktu. Daftar kerja menandai perbedaan antara brief yang ditulis, akar yang diverifikasi, gambar yang ditinjau, dan demo yang diuji.

