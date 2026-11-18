# 03 · Laporan Audit Satu-per-Satu Kaidah Mnemonic, Actor Sprites, Video 9:16 & Referensi ChineseGradedReader

- **Status Audit:** PASSED ✅ (0 errors)
- **Referensi DB `ChineseGradedReader` (Read-Only):** `151/151` entri `oldLevel == 1` tercakup (+ 4 entri kanonik Hanban = **155 kata / 178 karakter unik + 3 demo = 181 karakter**)
- **Kaidah 1 — Konsistensi Aktor Sprite:** `50/50` Actor Sprites & showcase cards valid; **181/181** karakter konsisten menyebut aktor kanoniknya
- **Kaidah 2 — Struktur Spasial:** **181/181** karakter terklasifikasi spasial (`0` missing glyph di font `STHeiti Medium`)
- **Kaidah 3 — Visual & Kartu (`1080×1920`):** **8** ilustrasi Nano-Banana + **173** ilustrasi komposisi Actor-Sprite = **181/181** kartu karakter & **155/155** kartu kosakata
- **Kaidah 4 — Video Karakter Mandiri (9:16 `1080×1920`):** ID **181/181** (`char_videos/`) | EN **181/181** (`char_videos_en/`)
- **Kaidah 5 — Modularitas Video Gabungan Tanpa Re-generasi:** `single_copy=84/84` & `compound_stitch=71/71` | ID **155/155** (`videos/`, total `160`) | EN **155/155** (`videos_en/`, total `156`)
- **Kartu Grafis EN (`1080×1920`):** `cards_en` **181/181**, `vocab_cards_en` **155/155**, `sprite_cards_en` **50/50**

---

## Katalog 50 Canonical Actor Sprites

| # | ID | Radikal | Nama Aktor | Keyword | Warna | Dipakai pada Karakter |
|---:|---|---|---|---|---|---|
| 1 | `ren_person` | 人 / 亻 | **Aktor Orang** | Orang | `#D9534F` | 北 茶 个 候 会 老 冷 们 你 人 认 什 他 校 谢 怎 住 坐 做 作 休 |
| 2 | `nv_woman` | 女 | **Sang Ibu / Wanita** | Wanita | `#D9534F` | 好 姐 妈 女 她 |
| 3 | `zi_child` | 子 / 儿 | **Si Anak Kecil** | Anak | `#D9534F` | 儿 好 见 了 起 四 先 学 子 字 |
| 4 | `kou_mouth` | 口 | **Mulut Bicara** | Mulut | `#D9534F` | 吃 高 狗 号 喝 和 后 话 欢 叫 京 客 亮 吗 名 哪 呢 商 识 说 听 同 喂 喜 语 站 中 钟 |
| 5 | `yan_speech` | 讠 | **Gelombang Kata** | Kata-kata | `#2E6F5E` | 读 话 请 认 谁 识 说 谢 语 |
| 6 | `mu_eye` | 目 / 见 | **Mata Pengamat** | Mata | `#2B2D42` | 很 见 觉 看 面 视 睡 现 想 |
| 7 | `shou_hand` | 手 / 扌 / 又 | **Tangan Aksi** | Tangan | `#D9534F` | 爱 菜 打 对 饭 服 汉 欢 九 开 看 没 热 我 写 兴 友 有 在 |
| 8 | `xin_heart` | 心 / 忄 | **Hati Perasaan** | Hati | `#D9534F` | 爱 脑 想 怎 息 |
| 9 | `zu_foot` | 走 / 辶 / 止 | **Langkah Kaki** | Langkah | `#2B2D42` | 很 起 去 是 些 这 |
| 10 | `shui_water` | 水 / 氵 | **Tetes Air** | Air | `#2E6F5E` | 汉 没 漂 水 |
| 11 | `mu_tree` | 木 | **Pohon Kayu** | Pohon | `#2E6F5E` | 杯 本 菜 茶 东 果 机 来 苹 想 校 样 椅 桌 休 |
| 12 | `cao_grass` | 艹 / 生 | **Tunas Daun** | Tunas | `#2E6F5E` | 菜 茶 猫 苹 生 睡 先 星 |
| 13 | `ri_sun` | 日 / 白 | **Surya Bersinar** | Matahari | `#D69230` | 电 东 都 喝 明 日 时 是 星 影 桌 昨 |
| 14 | `yue_moon` | 月 | **Sabit Bulan** | Bulan | `#2B2D42` | 服 明 脑 能 朋 期 前 请 有 月 |
| 15 | `huo_fire` | 火 / 灬 | **Api Menyala** | Api | `#D9534F` | 点 电 火 热 住 |
| 16 | `shan_mountain` | 山 | **Puncak Gunung** | Gunung | `#2E6F5E` | 出 岁 山 |
| 17 | `tu_earth` | 土 | **Gundukan Tanah** | Tanah | `#D69230` | 块 里 去 他 她 再 在 坐 |
| 18 | `mian_roof` | 宀 / 冖 / 广 | **Atap Rumah** | Atap | `#2B2D42` | 爱 店 馆 后 家 今 觉 客 六 商 同 写 学 院 字 |
| 19 | `men_door` | 门 / 户 | **Pintu Gerbang** | Pintu | `#2B2D42` | 们 |
| 20 | `wei_wall` | 囗 / 匚 | **Kotak Batas** | Batas Kotak | `#2B2D42` | 国 回 买 面 四 西 医 |
| 21 | `jin_metal` | 钅 | **Keping Logam** | Logam | `#D69230` | 钱 钟 |
| 22 | `shi_food` | 饣 / 米 | **Mangkuk Nasi** | Nasi/Makanan | `#D69230` | 的 饭 馆 米 漂 |
| 23 | `he_grain` | 禾 | **Tangkai Padi** | Padi | `#D69230` | 和 来 年 租 |
| 24 | `quan_animal` | 犭 | **Hewan Lincah** | Hewan | `#D9534F` | 狗 猫 能 |
| 25 | `ma_horse` | 马 | **Kuda Tangguh** | Kuda | `#2B2D42` | 妈 吗 |
| 26 | `zhui_bird` | 隹 / 羽 / 飞 | **Burung Terbang** | Burung/Sayap | `#2E6F5E` | 不 飞 谁 西 习 |
| 27 | `che_vehicle` | 车 | **Roda Kendaraan** | Kendaraan | `#2B2D42` | 车 |
| 28 | `yu_rain` | 雨 | **Awan Hujan** | Hujan | `#2E6F5E` | 雨 |
| 29 | `bing_ice` | 冫 | **Kristal Es** | Es | `#2E6F5E` | 冷 |
| 30 | `tian_field` | 田 | **Petak Sawah** | Sawah | `#2E6F5E` | 果 里 猫 喂 |
| 31 | `dao_knife` | 刀 / 刂 | **Pisau Tajam** | Pisau | `#2B2D42` | 分 块 前 少 师 听 |
| 32 | `gong_tool` | 工 / 寸 | **Alat Ukur** | Alat Ukur | `#2B2D42` | 打 对 工 叫 姐 期 时 书 租 昨 做 作 |
| 33 | `yi_cloth` | 衣 / 礻 / 巾 | **Kain & Baju** | Kain | `#D9534F` | 呢 师 视 衣 这 |
| 34 | `si_silk` | 幺 / 系 | **Benang Sutra** | Benang | `#D69230` | 么 书 系 |
| 35 | `shi_arrow` | 矢 / 戈 | **Panah & Tombak** | Panah/Tombak | `#2B2D42` | 候 钱 我 医 |
| 36 | `li_stand` | 立 | **Berdiri Tegak** | Berdiri | `#2B2D42` | 点 店 商 上 站 |
| 37 | `yi_one` | 一 / 二 / 三 | **Garis Hitung** | Garis | `#2B2D42` | 杯 本 不 二 个 今 开 七 三 上 天 五 下 些 一 再 |
| 38 | `shi_ten` | 十 / 午 | **Silang Sepuluh** | Silang | `#D9534F` | 七 什 十 五 午 中 |
| 39 | `ba_divide` | 八 / 几 | **Belahan Simetris** | Terbagi | `#D69230` | 八 分 关 机 几 亮 六 兴 |
| 40 | `da_big` | 大 / 天 / 太 | **Rentang Besar** | Besar | `#D9534F` | 大 读 关 买 太 天 椅 |
| 41 | `xiao_small` | 小 / 少 | **Butiran Kecil** | Kecil | `#2E6F5E` | 觉 你 少 太 系 下 小 学 |
| 42 | `xi_evening` | 夕 / 多 | **Bulan Senja** | Senja | `#D69230` | 多 名 岁 |
| 43 | `zi_nose` | 自 | **Hidung Napas** | Hidung | `#2E6F5E` | 息 |
| 44 | `qi_steam` | 气 | **Uap Udara** | Udara | `#2E6F5E` | 吃 号 会 气 |
| 45 | `gui_jade` | 王 / 白 | **Batu Permata** | Permata | `#D69230` | 的 国 现 |
| 46 | `shi_pig` | 豕 / 羊 | **Ternak Rumah** | Ternak | `#D9534F` | 家 样 |
| 47 | `fu_father` | 父 / 老 | **Sosok Tetua** | Tetua | `#2B2D42` | 爸 都 老 |
| 48 | `gu_drum` | 壴 / 乐 | **Genderang Pesta** | Genderang | `#D9534F` | 喜 |
| 49 | `jing_tower` | 京 / 高 | **Menara Istana** | Menara | `#2B2D42` | 高 京 亮 影 |
| 50 | `fu_mound` | 阝 | **Tembok Bukit** | Tembok/Bukit | `#D69230` | 都 哪 那 院 |

---

## Audit Satu-per-Satu Seluruh 181 Karakter

| # | Hanzi | Pinyin | Struktur Spasial | Aktor Sprite | Mode Visual | K1 | K2 | K3 | K4 | Status |
|---:|:---:|---|---|---|---|:-:|:-:|:-:|:-:|:-:|
| 1 | **爱** | `ài` | Atas + Bawah | `shou_hand + mian_roof + xin_heart` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 2 | **八** | `bā` | Struktur Tunggal | `ba_divide` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 3 | **爸** | `bà` | Atas + Bawah | `fu_father` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 4 | **杯** | `bēi` | Kiri + Kanan | `mu_tree + yi_one` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 5 | **北** | `běi` | Kiri + Kanan | `ren_person` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 6 | **本** | `běn` | Atas + Bawah | `mu_tree + yi_one` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 7 | **不** | `bù` | Atas + Bawah | `yi_one + zhui_bird` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 8 | **菜** | `cài` | Atas + Bawah | `cao_grass + shou_hand + mu_tree` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 9 | **茶** | `chá` | Atas + Bawah | `cao_grass + ren_person + mu_tree` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 10 | **车** | `chē` | Struktur Tunggal | `che_vehicle` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 11 | **吃** | `chī` | Kiri + Kanan | `kou_mouth + qi_steam` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 12 | **出** | `chū` | Atas + Bawah | `shan_mountain` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 13 | **打** | `dǎ` | Kiri + Kanan | `shou_hand + gong_tool` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 14 | **大** | `dà` | Struktur Tunggal | `da_big` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 15 | **的** | `de` | Kiri + Kanan | `gui_jade + shi_food` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 16 | **点** | `diǎn` | Atas + Bawah | `li_stand + huo_fire` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 17 | **店** | `diàn` | Sudut + Isi | `mian_roof + li_stand` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 18 | **电** | `diàn` | Atas + Bawah | `ri_sun + huo_fire` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 19 | **东** | `dōng` | Atas + Bawah | `ri_sun + mu_tree` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 20 | **都** | `dōu` | Kiri + Kanan | `fu_father + ri_sun + fu_mound` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 21 | **读** | `dú` | Kiri + Kanan | `yan_speech + da_big` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 22 | **对** | `duì` | Kiri + Kanan | `shou_hand + gong_tool` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 23 | **多** | `duō` | Atas + Bawah | `xi_evening` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 24 | **儿** | `ér` | Struktur Tunggal | `zi_child` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 25 | **二** | `èr` | Struktur Tunggal | `yi_one` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 26 | **饭** | `fàn` | Kiri + Kanan | `shi_food + shou_hand` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 27 | **飞** | `fēi` | Struktur Tunggal | `zhui_bird` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 28 | **分** | `fēn` | Atas + Bawah | `ba_divide + dao_knife` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 29 | **服** | `fú` | Kiri + Kanan | `yue_moon + shou_hand` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 30 | **高** | `gāo` | Atas + Bawah | `jing_tower + kou_mouth` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 31 | **个** | `gè` | Atas + Bawah | `ren_person + yi_one` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 32 | **工** | `gōng` | Struktur Tunggal | `gong_tool` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 33 | **狗** | `gǒu` | Kiri + Kanan | `quan_animal + kou_mouth` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 34 | **关** | `guān` | Atas + Bawah | `ba_divide + da_big` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 35 | **馆** | `guǎn` | Kiri + Kanan | `shi_food + mian_roof` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 36 | **国** | `guó` | Luar + Dalam | `wei_wall + gui_jade` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 37 | **果** | `guǒ` | Atas + Bawah | `tian_field + mu_tree` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 38 | **汉** | `hàn` | Kiri + Kanan | `shui_water + shou_hand` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 39 | **好** | `hǎo` | Kiri + Kanan | `nv_woman + zi_child` | Nano-Banana | ✅ | ✅ | ✅ | ✅ | PASS |
| 40 | **号** | `hào` | Atas + Bawah | `kou_mouth + qi_steam` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 41 | **喝** | `hē` | Kiri + Kanan | `kou_mouth + ri_sun` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 42 | **和** | `hé` | Kiri + Kanan | `he_grain + kou_mouth` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 43 | **很** | `hěn` | Kiri + Kanan | `zu_foot + mu_eye` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 44 | **候** | `hòu` | Kiri + Kanan | `ren_person + shi_arrow` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 45 | **后** | `hòu` | Sudut + Isi | `mian_roof + kou_mouth` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 46 | **话** | `huà` | Kiri + Kanan | `yan_speech + kou_mouth` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 47 | **欢** | `huān` | Kiri + Kanan | `shou_hand + kou_mouth` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 48 | **回** | `huí` | Luar + Dalam | `wei_wall` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 49 | **会** | `huì` | Atas + Bawah | `ren_person + qi_steam` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 50 | **火** | `huǒ` | Struktur Tunggal | `huo_fire` | Nano-Banana | ✅ | ✅ | ✅ | ✅ | PASS |
| 51 | **机** | `jī` | Kiri + Kanan | `mu_tree + ba_divide` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 52 | **几** | `jǐ` | Struktur Tunggal | `ba_divide` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 53 | **家** | `jiā` | Atas + Bawah | `mian_roof + shi_pig` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 54 | **见** | `jiàn` | Atas + Bawah | `mu_eye + zi_child` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 55 | **叫** | `jiào` | Kiri + Kanan | `kou_mouth + gong_tool` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 56 | **姐** | `jiě` | Kiri + Kanan | `nv_woman + gong_tool` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 57 | **今** | `jīn` | Atas + Bawah | `mian_roof + yi_one` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 58 | **京** | `jīng` | Atas + Bawah | `jing_tower + kou_mouth` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 59 | **九** | `jiǔ` | Struktur Tunggal | `shou_hand` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 60 | **觉** | `jué` | Atas + Bawah | `xiao_small + mian_roof + mu_eye` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 61 | **开** | `kāi` | Atas + Bawah | `yi_one + shou_hand` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 62 | **看** | `kàn` | Atas + Bawah | `shou_hand + mu_eye` | Nano-Banana | ✅ | ✅ | ✅ | ✅ | PASS |
| 63 | **客** | `kè` | Atas + Bawah | `mian_roof + kou_mouth` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 64 | **块** | `kuài` | Kiri + Kanan | `tu_earth + dao_knife` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 65 | **来** | `lái` | Atas + Bawah | `he_grain + mu_tree` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 66 | **老** | `lǎo` | Sudut + Isi | `fu_father + ren_person` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 67 | **了** | `le` | Struktur Tunggal | `zi_child` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 68 | **冷** | `lěng` | Kiri + Kanan | `bing_ice + ren_person` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 69 | **里** | `lǐ` | Atas + Bawah | `tian_field + tu_earth` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 70 | **亮** | `liàng` | Atas + Bawah | `jing_tower + kou_mouth + ba_divide` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 71 | **六** | `liù` | Atas + Bawah | `mian_roof + ba_divide` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 72 | **妈** | `mā` | Kiri + Kanan | `nv_woman + ma_horse` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 73 | **吗** | `ma` | Kiri + Kanan | `kou_mouth + ma_horse` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 74 | **买** | `mǎi` | Atas + Bawah | `wei_wall + da_big` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 75 | **猫** | `māo` | Kiri + Kanan | `quan_animal + cao_grass + tian_field` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 76 | **么** | `me` | Atas + Bawah | `si_silk` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 77 | **没** | `méi` | Kiri + Kanan | `shui_water + shou_hand` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 78 | **们** | `men` | Kiri + Kanan | `ren_person + men_door` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 79 | **米** | `mǐ` | Struktur Tunggal | `shi_food` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 80 | **面** | `miàn` | Luar + Dalam | `wei_wall + mu_eye` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 81 | **名** | `míng` | Atas + Bawah | `xi_evening + kou_mouth` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 82 | **明** | `míng` | Kiri + Kanan | `ri_sun + yue_moon` | Nano-Banana | ✅ | ✅ | ✅ | ✅ | PASS |
| 83 | **哪** | `nǎ` | Kiri + Kanan | `kou_mouth + fu_mound` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 84 | **那** | `nà` | Kiri + Kanan | `fu_mound` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 85 | **脑** | `nǎo` | Kiri + Kanan | `yue_moon + xin_heart` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 86 | **呢** | `ne` | Kiri + Kanan | `kou_mouth + yi_cloth` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 87 | **能** | `néng` | Kiri + Kanan | `yue_moon + quan_animal` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 88 | **你** | `nǐ` | Kiri + Kanan | `ren_person + xiao_small` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 89 | **年** | `nián` | Atas + Bawah | `he_grain` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 90 | **女** | `nǚ` | Struktur Tunggal | `nv_woman` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 91 | **朋** | `péng` | Kiri + Kanan | `yue_moon` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 92 | **漂** | `piào` | Kiri + Kanan | `shui_water + shi_food` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 93 | **苹** | `píng` | Atas + Bawah | `cao_grass + mu_tree` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 94 | **七** | `qī` | Struktur Tunggal | `yi_one + shi_ten` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 95 | **期** | `qī` | Kiri + Kanan | `gong_tool + yue_moon` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 96 | **起** | `qǐ` | Sudut + Isi | `zu_foot + zi_child` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 97 | **气** | `qì` | Struktur Tunggal | `qi_steam` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 98 | **前** | `qián` | Atas + Bawah | `yue_moon + dao_knife` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 99 | **钱** | `qián` | Kiri + Kanan | `jin_metal + shi_arrow` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 100 | **请** | `qǐng` | Kiri + Kanan | `yan_speech + yue_moon` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 101 | **去** | `qù` | Atas + Bawah | `tu_earth + zu_foot` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 102 | **热** | `rè` | Atas + Bawah | `shou_hand + huo_fire` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 103 | **人** | `rén` | Struktur Tunggal | `ren_person` | Nano-Banana | ✅ | ✅ | ✅ | ✅ | PASS |
| 104 | **认** | `rèn` | Kiri + Kanan | `yan_speech + ren_person` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 105 | **日** | `rì` | Struktur Tunggal | `ri_sun` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 106 | **三** | `sān` | Struktur Tunggal | `yi_one` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 107 | **商** | `shāng` | Atas + Bawah | `li_stand + mian_roof + kou_mouth` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 108 | **上** | `shàng` | Atas + Bawah | `yi_one + li_stand` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 109 | **少** | `shǎo` | Atas + Bawah | `xiao_small + dao_knife` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 110 | **谁** | `shéi` | Kiri + Kanan | `yan_speech + zhui_bird` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 111 | **什** | `shén` | Kiri + Kanan | `ren_person + shi_ten` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 112 | **生** | `shēng` | Struktur Tunggal | `cao_grass` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 113 | **师** | `shī` | Kiri + Kanan | `dao_knife + yi_cloth` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 114 | **十** | `shí` | Struktur Tunggal | `shi_ten` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 115 | **时** | `shí` | Kiri + Kanan | `ri_sun + gong_tool` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 116 | **识** | `shí` | Kiri + Kanan | `yan_speech + kou_mouth` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 117 | **是** | `shì` | Atas + Bawah | `ri_sun + zu_foot` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 118 | **视** | `shì` | Kiri + Kanan | `yi_cloth + mu_eye` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 119 | **书** | `shū` | Struktur Tunggal | `si_silk + gong_tool` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 120 | **水** | `shuǐ` | Struktur Tunggal | `shui_water` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 121 | **睡** | `shuì` | Kiri + Kanan | `mu_eye + cao_grass` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 122 | **说** | `shuō` | Kiri + Kanan | `yan_speech + kou_mouth` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 123 | **四** | `sì` | Luar + Dalam | `wei_wall + zi_child` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 124 | **岁** | `suì` | Atas + Bawah | `shan_mountain + xi_evening` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 125 | **他** | `tā` | Kiri + Kanan | `ren_person + tu_earth` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 126 | **她** | `tā` | Kiri + Kanan | `nv_woman + tu_earth` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 127 | **太** | `tài` | Atas + Bawah | `da_big + xiao_small` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 128 | **天** | `tiān` | Atas + Bawah | `yi_one + da_big` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 129 | **听** | `tīng` | Kiri + Kanan | `kou_mouth + dao_knife` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 130 | **同** | `tóng` | Luar + Dalam | `mian_roof + kou_mouth` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 131 | **喂** | `wèi` | Kiri + Kanan | `kou_mouth + tian_field` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 132 | **我** | `wǒ` | Kiri + Kanan | `shou_hand + shi_arrow` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 133 | **五** | `wǔ` | Struktur Tunggal | `yi_one + shi_ten` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 134 | **午** | `wǔ` | Atas + Bawah | `shi_ten` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 135 | **西** | `xī` | Luar + Dalam | `wei_wall + zhui_bird` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 136 | **习** | `xí` | Struktur Tunggal | `zhui_bird` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 137 | **喜** | `xǐ` | Atas + Bawah | `gu_drum + kou_mouth` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 138 | **系** | `xì` | Atas + Bawah | `si_silk + xiao_small` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 139 | **下** | `xià` | Atas + Bawah | `yi_one + xiao_small` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 140 | **先** | `xiān` | Atas + Bawah | `cao_grass + zi_child` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 141 | **现** | `xiàn` | Kiri + Kanan | `gui_jade + mu_eye` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 142 | **想** | `xiǎng` | Atas + Bawah | `mu_tree + mu_eye + xin_heart` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 143 | **小** | `xiǎo` | Struktur Tunggal | `xiao_small` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 144 | **校** | `xiào` | Kiri + Kanan | `mu_tree + ren_person` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 145 | **些** | `xiē` | Atas + Bawah | `zu_foot + yi_one` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 146 | **写** | `xiě` | Atas + Bawah | `mian_roof + shou_hand` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 147 | **谢** | `xiè` | Kiri + Kanan | `yan_speech + ren_person` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 148 | **星** | `xīng` | Atas + Bawah | `ri_sun + cao_grass` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 149 | **兴** | `xìng` | Atas + Bawah | `shou_hand + ba_divide` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 150 | **学** | `xué` | Atas + Bawah | `xiao_small + mian_roof + zi_child` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 151 | **样** | `yàng` | Kiri + Kanan | `mu_tree + shi_pig` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 152 | **一** | `yī` | Struktur Tunggal | `yi_one` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 153 | **医** | `yī` | Sudut + Isi | `wei_wall + shi_arrow` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 154 | **衣** | `yī` | Struktur Tunggal | `yi_cloth` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 155 | **椅** | `yǐ` | Kiri + Kanan | `mu_tree + da_big` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 156 | **影** | `yǐng` | Kiri + Kanan | `ri_sun + jing_tower` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 157 | **友** | `yǒu` | Sudut + Isi | `shou_hand` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 158 | **有** | `yǒu` | Sudut + Isi | `shou_hand + yue_moon` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 159 | **语** | `yǔ` | Kiri + Kanan | `yan_speech + kou_mouth` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 160 | **雨** | `yǔ` | Luar + Dalam | `yu_rain` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 161 | **院** | `yuàn` | Kiri + Kanan | `fu_mound + mian_roof` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 162 | **月** | `yuè` | Struktur Tunggal | `yue_moon` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 163 | **再** | `zài` | Luar + Dalam | `yi_one + tu_earth` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 164 | **在** | `zài` | Sudut + Isi | `shou_hand + tu_earth` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 165 | **怎** | `zěn` | Atas + Bawah | `ren_person + xin_heart` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 166 | **站** | `zhàn` | Kiri + Kanan | `li_stand + kou_mouth` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 167 | **这** | `zhè` | Sudut + Isi | `zu_foot + yi_cloth` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 168 | **中** | `zhōng` | Luar + Dalam | `kou_mouth + shi_ten` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 169 | **钟** | `zhōng` | Kiri + Kanan | `jin_metal + kou_mouth` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 170 | **住** | `zhù` | Kiri + Kanan | `ren_person + huo_fire` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 171 | **桌** | `zhuō` | Atas + Bawah | `ri_sun + mu_tree` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 172 | **子** | `zǐ` | Struktur Tunggal | `zi_child` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 173 | **字** | `zì` | Atas + Bawah | `mian_roof + zi_child` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 174 | **租** | `zū` | Kiri + Kanan | `he_grain + gong_tool` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 175 | **昨** | `zuó` | Kiri + Kanan | `ri_sun + gong_tool` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 176 | **坐** | `zuò` | Atas + Bawah | `ren_person + tu_earth` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 177 | **做** | `zuò` | Kiri + Kanan | `ren_person + gong_tool` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 178 | **作** | `zuò` | Kiri + Kanan | `ren_person + gong_tool` | Actor-Sprite | ✅ | ✅ | ✅ | ✅ | PASS |
| 179 | **休** | `xiū` | Kiri + Kanan | `ren_person + mu_tree` | Nano-Banana | ✅ | ✅ | ✅ | ✅ | PASS |
| 180 | **息** | `xī` | Atas + Bawah | `zi_nose + xin_heart` | Nano-Banana | ✅ | ✅ | ✅ | ✅ | PASS |
| 181 | **山** | `shān` | Struktur Tunggal | `shan_mountain` | Nano-Banana | ✅ | ✅ | ✅ | ✅ | PASS |
