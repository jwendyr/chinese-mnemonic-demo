#!/usr/bin/env python3
"""Complete HSK 1 (HSK 2.0) Vocabulary (150 words) & Unique Characters (176 + 2 bonus) with Indonesian mnemonics."""

import json
import unicodedata
from pathlib import Path

WORKDIR = Path("/Volumes/App/Workspace/chinese-mnemonic-demo")
CGR_DIR = Path("/Volumes/App/Workspace/ChineseGradedReader")
CGR_HSK_DICT = CGR_DIR / "macos-app/Sources/ChineseGradedReader/Resources/hsk_dict.json"
CGR_WEB_DICT = CGR_DIR / "web/data/dict_zh.json"
CGR_OFFICIAL_LISTS = CGR_DIR / "macos-app/Sources/ChineseGradedReader/Resources/official_lists.json"

LAYOUT_TUNGGAL = "Struktur Tunggal"
LAYOUT_KIRI_KANAN = "Kiri + Kanan"
LAYOUT_ATAS_BAWAH = "Atas + Bawah"
LAYOUT_LUAR_DALAM = "Luar + Dalam"
LAYOUT_KURUNG = "Sudut + Isi"

# Canonical spatial layout + 1..3 Actor Sprite IDs for ALL 181 characters
CHAR_KAIDAH_MAP = {
    "一": (LAYOUT_TUNGGAL, ["yi_one"]),
    "七": (LAYOUT_TUNGGAL, ["yi_one", "shi_ten"]),
    "三": (LAYOUT_TUNGGAL, ["yi_one"]),
    "上": (LAYOUT_ATAS_BAWAH, ["yi_one", "li_stand"]),
    "下": (LAYOUT_ATAS_BAWAH, ["yi_one", "xiao_small"]),
    "不": (LAYOUT_ATAS_BAWAH, ["yi_one", "zhui_bird"]),
    "东": (LAYOUT_ATAS_BAWAH, ["ri_sun", "mu_tree"]),
    "个": (LAYOUT_ATAS_BAWAH, ["ren_person", "yi_one"]),
    "中": (LAYOUT_LUAR_DALAM, ["kou_mouth", "shi_ten"]),
    "么": (LAYOUT_ATAS_BAWAH, ["si_silk"]),
    "九": (LAYOUT_TUNGGAL, ["shou_hand"]),
    "习": (LAYOUT_TUNGGAL, ["zhui_bird"]),
    "书": (LAYOUT_TUNGGAL, ["si_silk", "gong_tool"]),
    "买": (LAYOUT_ATAS_BAWAH, ["wei_wall", "da_big"]),
    "了": (LAYOUT_TUNGGAL, ["zi_child"]),
    "二": (LAYOUT_TUNGGAL, ["yi_one"]),
    "五": (LAYOUT_TUNGGAL, ["yi_one", "shi_ten"]),
    "些": (LAYOUT_ATAS_BAWAH, ["zu_foot", "yi_one"]),
    "京": (LAYOUT_ATAS_BAWAH, ["jing_tower", "kou_mouth"]),
    "亮": (LAYOUT_ATAS_BAWAH, ["jing_tower", "kou_mouth", "ba_divide"]),
    "人": (LAYOUT_TUNGGAL, ["ren_person"]),
    "什": (LAYOUT_KIRI_KANAN, ["ren_person", "shi_ten"]),
    "今": (LAYOUT_ATAS_BAWAH, ["mian_roof", "yi_one"]),
    "他": (LAYOUT_KIRI_KANAN, ["ren_person", "tu_earth"]),
    "们": (LAYOUT_KIRI_KANAN, ["ren_person", "men_door"]),
    "会": (LAYOUT_ATAS_BAWAH, ["ren_person", "qi_steam"]),
    "住": (LAYOUT_KIRI_KANAN, ["ren_person", "huo_fire"]),
    "作": (LAYOUT_KIRI_KANAN, ["ren_person", "gong_tool"]),
    "你": (LAYOUT_KIRI_KANAN, ["ren_person", "xiao_small"]),
    "候": (LAYOUT_KIRI_KANAN, ["ren_person", "shi_arrow"]),
    "做": (LAYOUT_KIRI_KANAN, ["ren_person", "gong_tool"]),
    "儿": (LAYOUT_TUNGGAL, ["zi_child"]),
    "先": (LAYOUT_ATAS_BAWAH, ["cao_grass", "zi_child"]),
    "八": (LAYOUT_TUNGGAL, ["ba_divide"]),
    "六": (LAYOUT_ATAS_BAWAH, ["mian_roof", "ba_divide"]),
    "关": (LAYOUT_ATAS_BAWAH, ["ba_divide", "da_big"]),
    "兴": (LAYOUT_ATAS_BAWAH, ["shou_hand", "ba_divide"]),
    "再": (LAYOUT_LUAR_DALAM, ["yi_one", "tu_earth"]),
    "写": (LAYOUT_ATAS_BAWAH, ["mian_roof", "shou_hand"]),
    "冷": (LAYOUT_KIRI_KANAN, ["bing_ice", "ren_person"]),
    "几": (LAYOUT_TUNGGAL, ["ba_divide"]),
    "出": (LAYOUT_ATAS_BAWAH, ["shan_mountain"]),
    "分": (LAYOUT_ATAS_BAWAH, ["ba_divide", "dao_knife"]),
    "前": (LAYOUT_ATAS_BAWAH, ["yue_moon", "dao_knife"]),
    "北": (LAYOUT_KIRI_KANAN, ["ren_person"]),
    "医": (LAYOUT_KURUNG, ["wei_wall", "shi_arrow"]),
    "十": (LAYOUT_TUNGGAL, ["shi_ten"]),
    "午": (LAYOUT_ATAS_BAWAH, ["shi_ten"]),
    "去": (LAYOUT_ATAS_BAWAH, ["tu_earth", "zu_foot"]),
    "友": (LAYOUT_KURUNG, ["shou_hand"]),
    "叫": (LAYOUT_KIRI_KANAN, ["kou_mouth", "gong_tool"]),
    "号": (LAYOUT_ATAS_BAWAH, ["kou_mouth", "qi_steam"]),
    "吃": (LAYOUT_KIRI_KANAN, ["kou_mouth", "qi_steam"]),
    "同": (LAYOUT_LUAR_DALAM, ["mian_roof", "kou_mouth"]),
    "名": (LAYOUT_ATAS_BAWAH, ["xi_evening", "kou_mouth"]),
    "后": (LAYOUT_KURUNG, ["mian_roof", "kou_mouth"]),
    "吗": (LAYOUT_KIRI_KANAN, ["kou_mouth", "ma_horse"]),
    "听": (LAYOUT_KIRI_KANAN, ["kou_mouth", "dao_knife"]),
    "呢": (LAYOUT_KIRI_KANAN, ["kou_mouth", "yi_cloth"]),
    "和": (LAYOUT_KIRI_KANAN, ["he_grain", "kou_mouth"]),
    "哪": (LAYOUT_KIRI_KANAN, ["kou_mouth", "fu_mound"]),
    "商": (LAYOUT_ATAS_BAWAH, ["li_stand", "mian_roof", "kou_mouth"]),
    "喂": (LAYOUT_KIRI_KANAN, ["kou_mouth", "tian_field"]),
    "喜": (LAYOUT_ATAS_BAWAH, ["gu_drum", "kou_mouth"]),
    "喝": (LAYOUT_KIRI_KANAN, ["kou_mouth", "ri_sun"]),
    "四": (LAYOUT_LUAR_DALAM, ["wei_wall", "zi_child"]),
    "回": (LAYOUT_LUAR_DALAM, ["wei_wall"]),
    "国": (LAYOUT_LUAR_DALAM, ["wei_wall", "gui_jade"]),
    "在": (LAYOUT_KURUNG, ["shou_hand", "tu_earth"]),
    "坐": (LAYOUT_ATAS_BAWAH, ["ren_person", "tu_earth"]),
    "块": (LAYOUT_KIRI_KANAN, ["tu_earth", "dao_knife"]),
    "多": (LAYOUT_ATAS_BAWAH, ["xi_evening"]),
    "大": (LAYOUT_TUNGGAL, ["da_big"]),
    "天": (LAYOUT_ATAS_BAWAH, ["yi_one", "da_big"]),
    "太": (LAYOUT_ATAS_BAWAH, ["da_big", "xiao_small"]),
    "女": (LAYOUT_TUNGGAL, ["nv_woman"]),
    "她": (LAYOUT_KIRI_KANAN, ["nv_woman", "tu_earth"]),
    "好": (LAYOUT_KIRI_KANAN, ["nv_woman", "zi_child"]),
    "妈": (LAYOUT_KIRI_KANAN, ["nv_woman", "ma_horse"]),
    "姐": (LAYOUT_KIRI_KANAN, ["nv_woman", "gong_tool"]),
    "子": (LAYOUT_TUNGGAL, ["zi_child"]),
    "字": (LAYOUT_ATAS_BAWAH, ["mian_roof", "zi_child"]),
    "学": (LAYOUT_ATAS_BAWAH, ["xiao_small", "mian_roof", "zi_child"]),
    "客": (LAYOUT_ATAS_BAWAH, ["mian_roof", "kou_mouth"]),
    "家": (LAYOUT_ATAS_BAWAH, ["mian_roof", "shi_pig"]),
    "对": (LAYOUT_KIRI_KANAN, ["shou_hand", "gong_tool"]),
    "小": (LAYOUT_TUNGGAL, ["xiao_small"]),
    "少": (LAYOUT_ATAS_BAWAH, ["xiao_small", "dao_knife"]),
    "岁": (LAYOUT_ATAS_BAWAH, ["shan_mountain", "xi_evening"]),
    "工": (LAYOUT_TUNGGAL, ["gong_tool"]),
    "师": (LAYOUT_KIRI_KANAN, ["dao_knife", "yi_cloth"]),
    "年": (LAYOUT_ATAS_BAWAH, ["he_grain"]),
    "店": (LAYOUT_KURUNG, ["mian_roof", "li_stand"]),
    "开": (LAYOUT_ATAS_BAWAH, ["yi_one", "shou_hand"]),
    "影": (LAYOUT_KIRI_KANAN, ["ri_sun", "jing_tower"]),
    "很": (LAYOUT_KIRI_KANAN, ["zu_foot", "mu_eye"]),
    "怎": (LAYOUT_ATAS_BAWAH, ["ren_person", "xin_heart"]),
    "想": (LAYOUT_ATAS_BAWAH, ["mu_tree", "mu_eye", "xin_heart"]),
    "我": (LAYOUT_KIRI_KANAN, ["shou_hand", "shi_arrow"]),
    "打": (LAYOUT_KIRI_KANAN, ["shou_hand", "gong_tool"]),
    "日": (LAYOUT_TUNGGAL, ["ri_sun"]),
    "时": (LAYOUT_KIRI_KANAN, ["ri_sun", "gong_tool"]),
    "明": (LAYOUT_KIRI_KANAN, ["ri_sun", "yue_moon"]),
    "星": (LAYOUT_ATAS_BAWAH, ["ri_sun", "cao_grass"]),
    "昨": (LAYOUT_KIRI_KANAN, ["ri_sun", "gong_tool"]),
    "是": (LAYOUT_ATAS_BAWAH, ["ri_sun", "zu_foot"]),
    "月": (LAYOUT_TUNGGAL, ["yue_moon"]),
    "有": (LAYOUT_KURUNG, ["shou_hand", "yue_moon"]),
    "朋": (LAYOUT_KIRI_KANAN, ["yue_moon"]),
    "服": (LAYOUT_KIRI_KANAN, ["yue_moon", "shou_hand"]),
    "期": (LAYOUT_KIRI_KANAN, ["gong_tool", "yue_moon"]),
    "本": (LAYOUT_ATAS_BAWAH, ["mu_tree", "yi_one"]),
    "机": (LAYOUT_KIRI_KANAN, ["mu_tree", "ba_divide"]),
    "来": (LAYOUT_ATAS_BAWAH, ["he_grain", "mu_tree"]),
    "杯": (LAYOUT_KIRI_KANAN, ["mu_tree", "yi_one"]),
    "果": (LAYOUT_ATAS_BAWAH, ["tian_field", "mu_tree"]),
    "校": (LAYOUT_KIRI_KANAN, ["mu_tree", "ren_person"]),
    "样": (LAYOUT_KIRI_KANAN, ["mu_tree", "shi_pig"]),
    "桌": (LAYOUT_ATAS_BAWAH, ["ri_sun", "mu_tree"]),
    "椅": (LAYOUT_KIRI_KANAN, ["mu_tree", "da_big"]),
    "欢": (LAYOUT_KIRI_KANAN, ["shou_hand", "kou_mouth"]),
    "气": (LAYOUT_TUNGGAL, ["qi_steam"]),
    "水": (LAYOUT_TUNGGAL, ["shui_water"]),
    "汉": (LAYOUT_KIRI_KANAN, ["shui_water", "shou_hand"]),
    "没": (LAYOUT_KIRI_KANAN, ["shui_water", "shou_hand"]),
    "漂": (LAYOUT_KIRI_KANAN, ["shui_water", "shi_food"]),
    "火": (LAYOUT_TUNGGAL, ["huo_fire"]),
    "点": (LAYOUT_ATAS_BAWAH, ["li_stand", "huo_fire"]),
    "热": (LAYOUT_ATAS_BAWAH, ["shou_hand", "huo_fire"]),
    "爱": (LAYOUT_ATAS_BAWAH, ["shou_hand", "mian_roof", "xin_heart"]),
    "爸": (LAYOUT_ATAS_BAWAH, ["fu_father"]),
    "狗": (LAYOUT_KIRI_KANAN, ["quan_animal", "kou_mouth"]),
    "猫": (LAYOUT_KIRI_KANAN, ["quan_animal", "cao_grass", "tian_field"]),
    "现": (LAYOUT_KIRI_KANAN, ["gui_jade", "mu_eye"]),
    "生": (LAYOUT_TUNGGAL, ["cao_grass"]),
    "电": (LAYOUT_ATAS_BAWAH, ["ri_sun", "huo_fire"]),
    "的": (LAYOUT_KIRI_KANAN, ["gui_jade", "shi_food"]),
    "看": (LAYOUT_ATAS_BAWAH, ["shou_hand", "mu_eye"]),
    "睡": (LAYOUT_KIRI_KANAN, ["mu_eye", "cao_grass"]),
    "租": (LAYOUT_KIRI_KANAN, ["he_grain", "gong_tool"]),
    "站": (LAYOUT_KIRI_KANAN, ["li_stand", "kou_mouth"]),
    "米": (LAYOUT_TUNGGAL, ["shi_food"]),
    "系": (LAYOUT_ATAS_BAWAH, ["si_silk", "xiao_small"]),
    "老": (LAYOUT_KURUNG, ["fu_father", "ren_person"]),
    "能": (LAYOUT_KIRI_KANAN, ["yue_moon", "quan_animal"]),
    "脑": (LAYOUT_KIRI_KANAN, ["yue_moon", "xin_heart"]),
    "苹": (LAYOUT_ATAS_BAWAH, ["cao_grass", "mu_tree"]),
    "茶": (LAYOUT_ATAS_BAWAH, ["cao_grass", "ren_person", "mu_tree"]),
    "菜": (LAYOUT_ATAS_BAWAH, ["cao_grass", "shou_hand", "mu_tree"]),
    "衣": (LAYOUT_TUNGGAL, ["yi_cloth"]),
    "西": (LAYOUT_LUAR_DALAM, ["wei_wall", "zhui_bird"]),
    "视": (LAYOUT_KIRI_KANAN, ["yi_cloth", "mu_eye"]),
    "见": (LAYOUT_ATAS_BAWAH, ["mu_eye", "zi_child"]),
    "觉": (LAYOUT_ATAS_BAWAH, ["xiao_small", "mian_roof", "mu_eye"]),
    "认": (LAYOUT_KIRI_KANAN, ["yan_speech", "ren_person"]),
    "识": (LAYOUT_KIRI_KANAN, ["yan_speech", "kou_mouth"]),
    "话": (LAYOUT_KIRI_KANAN, ["yan_speech", "kou_mouth"]),
    "语": (LAYOUT_KIRI_KANAN, ["yan_speech", "kou_mouth"]),
    "说": (LAYOUT_KIRI_KANAN, ["yan_speech", "kou_mouth"]),
    "请": (LAYOUT_KIRI_KANAN, ["yan_speech", "yue_moon"]),
    "读": (LAYOUT_KIRI_KANAN, ["yan_speech", "da_big"]),
    "谁": (LAYOUT_KIRI_KANAN, ["yan_speech", "zhui_bird"]),
    "谢": (LAYOUT_KIRI_KANAN, ["yan_speech", "ren_person"]),
    "起": (LAYOUT_KURUNG, ["zu_foot", "zi_child"]),
    "车": (LAYOUT_TUNGGAL, ["che_vehicle"]),
    "这": (LAYOUT_KURUNG, ["zu_foot", "yi_cloth"]),
    "那": (LAYOUT_KIRI_KANAN, ["fu_mound"]),
    "都": (LAYOUT_KIRI_KANAN, ["fu_father", "ri_sun", "fu_mound"]),
    "里": (LAYOUT_ATAS_BAWAH, ["tian_field", "tu_earth"]),
    "钟": (LAYOUT_KIRI_KANAN, ["jin_metal", "kou_mouth"]),
    "钱": (LAYOUT_KIRI_KANAN, ["jin_metal", "shi_arrow"]),
    "院": (LAYOUT_KIRI_KANAN, ["fu_mound", "mian_roof"]),
    "雨": (LAYOUT_LUAR_DALAM, ["yu_rain"]),
    "零": (LAYOUT_ATAS_BAWAH, ["yu_rain", "ren_person"]),
    "面": (LAYOUT_LUAR_DALAM, ["wei_wall", "mu_eye"]),
    "飞": (LAYOUT_TUNGGAL, ["zhui_bird"]),
    "饭": (LAYOUT_KIRI_KANAN, ["shi_food", "shou_hand"]),
    "馆": (LAYOUT_KIRI_KANAN, ["shi_food", "mian_roof"]),
    "高": (LAYOUT_ATAS_BAWAH, ["jing_tower", "kou_mouth"]),
    "休": (LAYOUT_KIRI_KANAN, ["ren_person", "mu_tree"]),
    "息": (LAYOUT_ATAS_BAWAH, ["zi_nose", "xin_heart"]),
    "山": (LAYOUT_TUNGGAL, ["shan_mountain"]),
}

# 150 official HSK 1 (HSK 2.0) vocabulary words
# Tuple: (word, pinyin, meaning_id, category)
HSK1_VOCAB_RAW = [
    # 1. Kata Ganti & Orang (18)
    ("我", "wǒ", "saya / aku", "Kata Ganti & Orang"),
    ("我们", "wǒmen", "kami / kita", "Kata Ganti & Orang"),
    ("你", "nǐ", "kamu", "Kata Ganti & Orang"),
    ("他", "tā", "dia (laki-laki)", "Kata Ganti & Orang"),
    ("她", "tā", "dia (perempuan)", "Kata Ganti & Orang"),
    ("人", "rén", "orang / manusia", "Kata Ganti & Orang"),
    ("名字", "míngzi", "nama", "Kata Ganti & Orang"),
    ("爸爸", "bàba", "ayah / papa", "Kata Ganti & Orang"),
    ("妈妈", "māma", "ibu / mama", "Kata Ganti & Orang"),
    ("儿子", "érzi", "anak laki-laki", "Kata Ganti & Orang"),
    ("女儿", "nǚ'ér", "anak perempuan", "Kata Ganti & Orang"),
    ("朋友", "péngyou", "teman", "Kata Ganti & Orang"),
    ("老师", "lǎoshī", "guru", "Kata Ganti & Orang"),
    ("学生", "xuésheng", "murid / siswa", "Kata Ganti & Orang"),
    ("同学", "tóngxué", "teman sekelas", "Kata Ganti & Orang"),
    ("先生", "xiānsheng", "Tuan / Bapak / suami", "Kata Ganti & Orang"),
    ("小姐", "xiǎojie", "Nona / Mbak", "Kata Ganti & Orang"),
    ("医生", "yīshēng", "dokter", "Kata Ganti & Orang"),

    # 2. Angka, Waktu & Penanggalan (25)
    ("一", "yī", "satu", "Angka & Waktu"),
    ("二", "èr", "dua", "Angka & Waktu"),
    ("三", "sān", "tiga", "Angka & Waktu"),
    ("四", "sì", "empat", "Angka & Waktu"),
    ("五", "wǔ", "lima", "Angka & Waktu"),
    ("六", "liù", "enam", "Angka & Waktu"),
    ("七", "qī", "tujuh", "Angka & Waktu"),
    ("八", "bā", "delapan", "Angka & Waktu"),
    ("九", "jiǔ", "sembilan", "Angka & Waktu"),
    ("十", "shí", "sepuluh", "Angka & Waktu"),
    ("年", "nián", "tahun", "Angka & Waktu"),
    ("月", "yuè", "bulan", "Angka & Waktu"),
    ("日", "rì", "hari / tanggal / matahari", "Angka & Waktu"),
    ("星期", "xīngqī", "minggu / pekan", "Angka & Waktu"),
    ("今天", "jīntiān", "hari ini", "Angka & Waktu"),
    ("明天", "míngtiān", "besok", "Angka & Waktu"),
    ("昨天", "zuótiān", "kemarin", "Angka & Waktu"),
    ("上午", "shàngwǔ", "pagi (sebelum siang)", "Angka & Waktu"),
    ("中午", "zhōngwǔ", "siang / tengah hari", "Angka & Waktu"),
    ("下午", "xiàwǔ", "sore", "Angka & Waktu"),
    ("点", "diǎn", "jam / pukul / titik", "Angka & Waktu"),
    ("分钟", "fēnzhōng", "menit", "Angka & Waktu"),
    ("现在", "xiànzài", "sekarang", "Angka & Waktu"),
    ("时候", "shíhou", "waktu / saat", "Angka & Waktu"),
    ("岁", "suì", "umur / tahun (usia)", "Angka & Waktu"),

    # 3. Kata Kerja Dasar (31)
    ("是", "shì", "adalah / iya", "Kata Kerja Dasar"),
    ("有", "yǒu", "ada / memiliki", "Kata Kerja Dasar"),
    ("在", "zài", "di / berada / sedang", "Kata Kerja Dasar"),
    ("看", "kàn", "melihat / membaca / menonton", "Kata Kerja Dasar"),
    ("看见", "kànjiàn", "terlihat / melihat", "Kata Kerja Dasar"),
    ("听", "tīng", "mendengar", "Kata Kerja Dasar"),
    ("说话", "shuōhuà", "berbicara", "Kata Kerja Dasar"),
    ("读", "dú", "membaca (bersuara)", "Kata Kerja Dasar"),
    ("写", "xiě", "menulis", "Kata Kerja Dasar"),
    ("叫", "jiào", "dipanggil / bernama / memanggil", "Kata Kerja Dasar"),
    ("来", "lái", "datang", "Kata Kerja Dasar"),
    ("回", "huí", "kembali / pulang", "Kata Kerja Dasar"),
    ("去", "qù", "pergi", "Kata Kerja Dasar"),
    ("吃", "chī", "makan", "Kata Kerja Dasar"),
    ("喝", "hē", "minum", "Kata Kerja Dasar"),
    ("睡觉", "shuìjiào", "tidur", "Kata Kerja Dasar"),
    ("打电话", "dǎ diànhuà", "menelepon", "Kata Kerja Dasar"),
    ("做", "zuò", "melakukan / membuat", "Kata Kerja Dasar"),
    ("买", "mǎi", "membeli", "Kata Kerja Dasar"),
    ("开", "kāi", "membuka / menyetir / menyalakan", "Kata Kerja Dasar"),
    ("坐", "zuò", "duduk / naik (kendaraan)", "Kata Kerja Dasar"),
    ("住", "zhù", "tinggal / menetap", "Kata Kerja Dasar"),
    ("学习", "xuéxí", "belajar", "Kata Kerja Dasar"),
    ("工作", "gōngzuò", "bekerja / pekerjaan", "Kata Kerja Dasar"),
    ("下雨", "xiàyǔ", "turun hujan", "Kata Kerja Dasar"),
    ("爱", "ài", "cinta / suka sekali", "Kata Kerja Dasar"),
    ("喜欢", "xǐhuan", "suka", "Kata Kerja Dasar"),
    ("想", "xiǎng", "ingin / berpikir / kangen", "Kata Kerja Dasar"),
    ("认识", "rènshi", "kenal / mengenal", "Kata Kerja Dasar"),
    ("会", "huì", "bisa (karena belajar) / akan", "Kata Kerja Dasar"),
    ("能", "néng", "bisa / mampu", "Kata Kerja Dasar"),

    # 4. Kata Benda, Makanan & Tempat (36)
    ("水", "shuǐ", "air", "Kata Benda & Tempat"),
    ("茶", "chá", "teh", "Kata Benda & Tempat"),
    ("米饭", "mǐfàn", "nasi", "Kata Benda & Tempat"),
    ("菜", "cài", "sayur / masakan / lauk", "Kata Benda & Tempat"),
    ("水果", "shuǐguǒ", "buah-buahan", "Kata Benda & Tempat"),
    ("苹果", "píngguǒ", "apel", "Kata Benda & Tempat"),
    ("杯子", "bēizi", "gelas / cangkir", "Kata Benda & Tempat"),
    ("钱", "qián", "uang", "Kata Benda & Tempat"),
    ("衣服", "yīfu", "pakaian / baju", "Kata Benda & Tempat"),
    ("飞机", "fēijī", "pesawat terbang", "Kata Benda & Tempat"),
    ("出租车", "chūzūchē", "taksi", "Kata Benda & Tempat"),
    ("火车站", "huǒchēzhàn", "stasiun kereta api", "Kata Benda & Tempat"),
    ("电视", "diànshì", "televisi", "Kata Benda & Tempat"),
    ("电脑", "diànnǎo", "komputer", "Kata Benda & Tempat"),
    ("电影", "diànyǐng", "film", "Kata Benda & Tempat"),
    ("天气", "tiānqì", "cuaca", "Kata Benda & Tempat"),
    ("猫", "māo", "kucing", "Kata Benda & Tempat"),
    ("狗", "gǒu", "anjing", "Kata Benda & Tempat"),
    ("东西", "dōngxi", "barang / benda", "Kata Benda & Tempat"),
    ("书", "shū", "buku", "Kata Benda & Tempat"),
    ("汉语", "Hànyǔ", "bahasa Mandarin", "Kata Benda & Tempat"),
    ("字", "zì", "huruf / karakter", "Kata Benda & Tempat"),
    ("桌子", "zhuōzi", "meja", "Kata Benda & Tempat"),
    ("椅子", "yǐzi", "kursi", "Kata Benda & Tempat"),
    ("家", "jiā", "rumah / keluarga", "Kata Benda & Tempat"),
    ("学校", "xuéxiào", "sekolah", "Kata Benda & Tempat"),
    ("饭店", "fàndiàn", "restoran / hotel", "Kata Benda & Tempat"),
    ("商店", "shāngdiàn", "toko", "Kata Benda & Tempat"),
    ("医院", "yīyuàn", "rumah sakit", "Kata Benda & Tempat"),
    ("中国", "Zhōngguó", "Tiongkok / China", "Kata Benda & Tempat"),
    ("北京", "Běijīng", "Beijing", "Kata Benda & Tempat"),
    ("上", "shàng", "atas / naik / masuk", "Kata Benda & Tempat"),
    ("下", "xià", "bawah / turun", "Kata Benda & Tempat"),
    ("里", "lǐ", "di dalam", "Kata Benda & Tempat"),
    ("前面", "qiánmian", "depan", "Kata Benda & Tempat"),
    ("后面", "hòumian", "belakang", "Kata Benda & Tempat"),

    # 5. Kata Sifat, Tanya, Satuan & Ungkapan (40)
    ("好", "hǎo", "baik / bagus", "Kata Sifat & Partikel"),
    ("大", "dà", "besar", "Kata Sifat & Partikel"),
    ("小", "xiǎo", "kecil", "Kata Sifat & Partikel"),
    ("多", "duō", "banyak", "Kata Sifat & Partikel"),
    ("少", "shǎo", "sedikit", "Kata Sifat & Partikel"),
    ("冷", "lěng", "dingin", "Kata Sifat & Partikel"),
    ("热", "rè", "panas", "Kata Sifat & Partikel"),
    ("高兴", "gāoxìng", "senang / gembira", "Kata Sifat & Partikel"),
    ("漂亮", "piàoliang", "cantik / indah", "Kata Sifat & Partikel"),
    ("谁", "shéi", "siapa", "Kata Sifat & Partikel"),
    ("什么", "shénme", "apa", "Kata Sifat & Partikel"),
    ("哪", "nǎ", "yang mana", "Kata Sifat & Partikel"),
    ("哪儿", "nǎr", "di mana", "Kata Sifat & Partikel"),
    ("几", "jǐ", "berapa (angka kecil)", "Kata Sifat & Partikel"),
    ("多少", "duōshao", "berapa (jumlah/harga)", "Kata Sifat & Partikel"),
    ("怎么", "zěnme", "bagaimana", "Kata Sifat & Partikel"),
    ("怎么样", "zěnmeyàng", "bagaimana kabarnya/pendapat", "Kata Sifat & Partikel"),
    ("这", "zhè", "ini", "Kata Sifat & Partikel"),
    ("那", "nà", "itu", "Kata Sifat & Partikel"),
    ("些", "xiē", "beberapa", "Kata Sifat & Partikel"),
    ("个", "gè", "satuan umum (buah/orang)", "Kata Sifat & Partikel"),
    ("块", "kuài", "potong / yuan (uang)", "Kata Sifat & Partikel"),
    ("本", "běn", "satuan buku (jilid)", "Kata Sifat & Partikel"),
    ("不", "bù", "tidak", "Kata Sifat & Partikel"),
    ("没", "méi", "tidak / belum (punya/terjadi)", "Kata Sifat & Partikel"),
    ("很", "hěn", "sangat", "Kata Sifat & Partikel"),
    ("太", "tài", "terlalu", "Kata Sifat & Partikel"),
    ("都", "dōu", "semua", "Kata Sifat & Partikel"),
    ("和", "hé", "dan / bersama", "Kata Sifat & Partikel"),
    ("的", "de", "partikel kepemilikan/sifat", "Kata Sifat & Partikel"),
    ("了", "le", "partikel sudah / perubahan", "Kata Sifat & Partikel"),
    ("吗", "ma", "partikel tanya (apakah)", "Kata Sifat & Partikel"),
    ("呢", "ne", "partikel tanya balik / sedang", "Kata Sifat & Partikel"),
    ("请", "qǐng", "silakan / tolong / mengundang", "Kata Sifat & Partikel"),
    ("喂", "wèi", "halo (telepon)", "Kata Sifat & Partikel"),
    ("谢谢", "xièxie", "terima kasih", "Kata Sifat & Partikel"),
    ("不客气", "bú kèqi", "sama-sama", "Kata Sifat & Partikel"),
    ("再见", "zàijiàn", "sampai jumpa", "Kata Sifat & Partikel"),
    ("对不起", "duìbuqǐ", "maaf", "Kata Sifat & Partikel"),
    ("没关系", "méi guānxi", "tidak apa-apa", "Kata Sifat & Partikel"),
    # 5 Extra words from ChineseGradedReader oldLevel == 1 (total 155 words)
    ("一点儿", "yīdiǎnr", "sedikit", "Kata Sifat & Partikel"),
    ("号", "hào", "nomor / tanggal", "Angka & Waktu"),
    ("没有", "méiyǒu", "tidak punya / tidak ada", "Kata Kerja Dasar"),
    ("说", "shuō", "berbicara / berkata", "Kata Kerja Dasar"),
    ("饭馆", "fànguǎn", "restoran / rumah makan", "Kata Benda & Tempat"),
]

# All 178 unique characters in HSK1_VOCAB_RAW + 3 bonus demo characters (休, 息, 山) = 181 entries
# Format: char -> (pinyin, meaning_id, radicals, mnemonic_id, prompt_hint)
HSK1_CHAR_META = {
    "一": ("yī", "satu", "一 (1 garis)", "Satu garis mendatar lurus seperti satu batang lidi.", "Single horizontal bamboo stick on top of the line"),
    "七": ("qī", "tujuh", "一 + 乚", "Angka 7 terbalik yang patah dan melengkung ke kanan.", "Geometric bent hook forming figure 7"),
    "三": ("sān", "tiga", "一 + 一 + 一", "Tiga garis bertumpuk: langit, manusia, dan bumi.", "Three stacked horizontal bars: sky, earth, horizon"),
    "上": ("shàng", "atas", "丨 + 卜 (di atas garis)", "Tiang bendera yang berdiri menunjuk ke atas garis dasar.", "Arrow/sprout rising above the ground line"),
    "下": ("xià", "bawah", "一 + 卜 (di bawah garis)", "Akar atau tetesan yang menggantung ke bawah garis atap.", "Drop hanging down beneath a horizontal roof line"),
    "不": ("bù", "tidak", "一 + 丿 + 丨 + 丶", "Burung yang terbang membentur langit-langit: tidak bisa lewat.", "Bird hitting a horizontal ceiling barrier"),
    "东": ("dōng", "timur", "木 + 日 (terbit di balik pohon)", "Matahari terbit di balik pohon di arah timur.", "Rising sun behind a simplified tree"),
    "个": ("gè", "satuan buah", "人 + 丨", "Satu orang berdiri tegak di atas satu tiang — hitungan per satu buah.", "Person roof sheltering a single vertical stick"),
    "中": ("zhōng", "tengah", "口 + 丨", "Kotak sasaran panah yang tertembus tepat di tengah-tengah.", "Target rectangle pierced dead-center by a vertical arrow"),
    "么": ("me", "apa / akhiran tanya", "丿 + 厶", "Ujung tali melingkar seperti tanda tanya kecil di akhir kata.", "Curled ribbon tail forming a small question mark"),
    "九": ("jiǔ", "sembilan", "丿 + 乙", "Lengan siku yang ditekuk hampir menyentuh angka 9.", "Bent arm flexing like a curved 9"),
    "习": ("xí", "berlatih", "羽 (1 sayap)", "Satu sayap burung muda yang terus mengepak berlatih terbang.", "Single feathered wing flapping to practice flying"),
    "书": ("shū", "buku", "乛 + 乛 + 丨 + 丶", "Tumpukan halaman buku yang dijilid dengan garis tegak di tengah.", "Open stacked pages bound by a spine"),
    "买": ("mǎi", "membeli", "乛 + 头", "Keranjang belanja terbuka di atas kepala orang yang sedang membeli.", "Open shopping basket above a person walking"),
    "了": ("le", "sudah / selesai", "子 (tanpa lengan)", "Anak kecil terbungkus bedong — tugas sudah selesai!", "Swaddled baby silhouette showing completion"),
    "二": ("èr", "dua", "一 + 一", "Dua garis sejajar atas dan bawah melambangkan angka dua.", "Two parallel balanced horizontal bars"),
    "五": ("wǔ", "lima", "一 + 丨 + ┐ + 一", "Jemari tangan bersilang di antara dua garis seperti angka 5.", "Crossed hourglass lines inside top and bottom bars"),
    "些": ("xiē", "beberapa", "此 (ini) + 二 (dua)", "Dua langkah kaki berhenti di atas dua garis: mengambil beberapa saja.", "Two steps resting over two lines indicating a few"),
    "京": ("jīng", "ibu kota", "亠 + 口 + 小", "Menara gerbang istana megah bertingkat di pusat ibu kota.", "Tall palace gate tower with pitched roof and pillars"),
    "亮": ("liàng", "terang / bersinar", "亠 + 口 + 冖 + 几", "Lampu mercusuar di atas menara tinggi yang bersinar terang.", "Glowing lantern atop a tall watchtower"),
    "人": ("rén", "orang", "人 (piktogram)", "Dua kaki melangkah berjalan — siluet manusia dari samping.", "Minimalist walking person made of two splayed legs"),
    "什": ("shén", "apa (pasangan)", "亻 + 十", "Sepuluh orang berkumpul bertanya: ada apa ini?", "Person standing beside a cross of ten"),
    "今": ("jīn", "sekarang / hari ini", "亼 + 乛", "Atap yang menutupi momen tepat di sini dan saat ini.", "Roof triangle enclosing the present moment"),
    "他": ("tā", "dia (laki-laki)", "亻 + 也", "Orang (亻) lain selain saya dan kamu = dia.", "Person leaning beside curved shape representing 'him'"),
    "们": ("men", "jamak (para)", "亻 + 门", "Banyak orang (亻) keluar masuk lewat satu pintu (门).", "Person standing beside a double saloon door"),
    "会": ("huì", "bisa / rapat", "人 + 云", "Orang berkumpul di bawah satu atap bertukar awan ide — jadi bisa!", "Meeting roof over swirling cloud thoughts"),
    "住": ("zhù", "tinggal", "亻 + 主", "Orang (亻) yang menjadi tuan rumah (主) dan menetap di satu tempat.", "Person beside a glowing candle-stand representing home"),
    "作": ("zuò", "bekerja / membuat", "亻 + 乍", "Orang (亻) memotong dan merakit kayu untuk bekerja.", "Person working beside notched wood beams"),
    "你": ("nǐ", "kamu", "亻 + 尔", "Orang (亻) yang berdiri tepat di depanmu untuk diajak bicara.", "Person pointing forward toward 'you'"),
    "候": ("hòu", "menunggu / waktu", "亻 + 丨 + 矢", "Orang (亻) mengintip panah di pos penjagaan sambil menunggu.", "Lookout person waiting by a post with an arrow"),
    "做": ("zuò", "melakukan", "亻 + 故", "Orang (亻) mengerjakan tugas lama (故) dengan tekun.", "Person busy crafting and doing work"),
    "儿": ("ér", "anak / kaki", "丿 + 乚", "Dua kaki kecil anak yang lincah berlari.", "Two playful little child legs"),
    "先": ("xiān", "lebih dulu / depan", "牛/⺧ + 儿", "Kaki (儿) yang melangkah paling depan mendahului yang lain.", "Legs stepping forward ahead of the line"),
    "八": ("bā", "delapan", "丿 + ㇏", "Dua garis terbuka terbelah ke kiri dan kanan seperti tirai terbuka.", "Two symmetrical parted strokes dividing into eight"),
    "六": ("liù", "enam", "亠 + 八", "Atap rumah di atas dua kaki kokoh seperti angka 6.", "Top hat / roof over two balanced legs"),
    "关": ("guān", "tutup / peduli", "丷 + 天", "Dua palang dikunci rapat di atas langit — menutup pintu.", "Two latch pins locking a gate shut"),
    "兴": ("xìng", "senang / semangat", "兴 (4 tangan mengangkat)", "Empat tangan bersorak mengangkat barang bersama dengan gembira.", "Four cheerful hands lifting together in celebration"),
    "再": ("zài", "lagi / kembali", "一 + 冉", "Timbangan dua tingkat diangkat lagi untuk kedua kalinya.", "Layered frame lifted up a second time"),
    "写": ("xiě", "menulis", "冖 + 与", "Tangan di bawah tutup meja sedang menggoreskan pena menulis.", "Desk cover over flowing cursive writing strokes"),
    "冷": ("lěng", "dingin", "冫 + 令", "Dua tetes es (冫) membuat orang menggigil kedinginan.", "Two ice crystals chilling the air"),
    "几": ("jǐ", "berapa / meja kecil", "丿 + 乙", "Meja pendek berkaki dua — muat beberapa cangkir saja.", "Small minimalist two-legged tea table"),
    "出": ("chū", "keluar", "山 + 山 (keluar dari wadah)", "Tunas gunung tumbuh menjebol keluar dari kotak tanah.", "Sprouting peak pushing up and out of a box"),
    "分": ("fēn", "bagi / menit", "八 + 刀", "Pisau (刀) membelah benda menjadi dua bagian (八) yang rata.", "Knife blade slicing an object neatly in half"),
    "前": ("qián", "depan / sebelum", "丷 + 一 + 月 + 刂", "Perahu (月) berlayar maju dengan pisau haluan membelah ombak ke depan.", "Boat prow slicing forward through water"),
    "北": ("běi", "utara", "北 (2 orang saling membelakangi)", "Dua orang duduk saling membelakangi menghangatkan punggung dari angin utara.", "Two people sitting back-to-back facing away"),
    "医": ("yī", "medis / dokter", "匚 + 矢", "Kotak P3K (匚) berisi jarum/panah akupunktur (矢) milik dokter.", "Medical kit box holding an acupuncture needle"),
    "十": ("shí", "sepuluh", "一 + 丨", "Dua garis bersilang membentuk tanda tambah = 10 jari lengkap.", "Simple crisp cross mark representing ten"),
    "午": ("wǔ", "tengah hari", "𠂉 + 十", "Alu penumbuk berdiri tegak saat matahari tepat di atas kepala (siang).", "Vertical pestle pointing straight up at noon"),
    "去": ("qù", "pergi", "土 + 厶", "Orang melangkah meninggalkan gundukan tanah (土) untuk pergi.", "Person stepping away from a mound of earth"),
    "友": ("yǒu", "sahabat", "𠂇 + 又", "Dua tangan kanan saling berjabat erat sebagai sahabat.", "Two hands clasping together in friendship"),
    "叫": ("jiào", "memanggil / bernama", "口 + 丩", "Mulut (口) berteriak kencang memakai corong pengeras suara.", "Open mouth megaphone calling out loud"),
    "吃": ("chī", "makan", "口 + 乞", "Mulut (口) terbuka lebar mengunyah makanan.", "Open mouth happily eating"),
    "同": ("tóng", "sama / bersama", "冂 + 一 + 口", "Satu atap dan satu suara mulut (口) — sepakat bersama.", "Single roof covering unified voice"),
    "名": ("míng", "nama", "夕 + 口", "Saat malam gelap (夕), harus memanggil dengan mulut (口) menyebut nama.", "Crescent evening moon above a calling mouth"),
    "后": ("hòu", "belakang / setelah", "𠂆 + 一 + 口", "Mulut komandan memberi aba-aba dari barisan belakang.", "Shelter angle above a commanding mouth"),
    "吗": ("ma", "apakah? (tanya)", "口 + 马", "Mulut (口) di sebelah kuda (马) membuat kalimat berubah jadi tanya.", "Mouth speech bubble beside a stylized horse"),
    "听": ("tīng", "mendengar", "口 + 斤", "Mulut berbicara pelan ke dekat kapak/telinga untuk mendengar saksama.", "Mouth whispering near an attentive ear/axe shape"),
    "呢": ("ne", "bagaimana dengan...? / sedang", "口 + 尼", "Mulut (口) bertanya balik dengan akrab di akhir kalimat.", "Mouth speech icon with cozy tail"),
    "号": ("hào", "nomor / tanggal", "口 + 丂", "Mulut Bicara (口) meniup trompet mengumumkan nomor dan tanggal.", "Mouth megaphone sounding a horn for number and date"),
    "和": ("hé", "dan / damai", "禾 + 口", "Tangkai Padi (禾) cukup untuk setiap Mulut Bicara (口) = damai dan bersama.", "Stalk of grain beside a satisfied mouth"),
    "哪": ("nǎ", "yang mana?", "口 + 那", "Mulut (口) bertanya menunjuk arah: yang mana?", "Question mouth pointing at direction sign"),
    "商": ("shāng", "dagang / toko", "立 + 冂 + 八 + 口", "Kios pasar beratap rapi tempat pedagang menawarkan dagangan.", "Market stall booth with merchant inside"),
    "喂": ("wèi", "halo (telepon)", "口 + 畏", "Mulut (口) menyapa 'Halo!' saat mengangkat gagang telepon.", "Mouth speaking into a telephone receiver"),
    "喜": ("xǐ", "suka / gembira", "壴 (genderang) + 口", "Genderang pesta berbunyi di atas mulut (口) yang tersenyum gembira.", "Festive drum beating above a smiling mouth"),
    "喝": ("hē", "minum", "口 + 曷", "Mulut (口) meneguk segelas air dingin di bawah terik matahari.", "Open mouth sipping cool water"),
    "四": ("sì", "empat", "囗 + 儿", "Jendela kotak dengan dua tirai terbuka menampilkan empat sudut.", "Window frame with parted curtains showing 4 corners"),
    "回": ("huí", "kembali / pulang", "囗 + 囗", "Pusaran air kotak berputar kembali ke titik asal.", "Concentric square spiral returning home"),
    "国": ("guó", "negara", "囗 + 玉", "Batu giok berharga (玉) dijaga di dalam batas tembok negara (囗).", "Precious jade jewel protected inside city walls"),
    "在": ("zài", "di / berada", "𠂇 + 丨 + 土", "Tanah (土) tempat kaki berpijak menandakan keberadaan di suatu tempat.", "Anchor pin planted firmly onto earth mound"),
    "坐": ("zuò", "duduk", "从 (2 orang) + 土 (tanah)", "Dua orang (从) duduk santai di atas tanah (土).", "Two small figures sitting together on the earth"),
    "块": ("kuài", "potong / yuan", "土 + 夬", "Bongkahan tanah (土) atau kepingan uang yang dipotong rapi.", "Chunky earth block sliced into a piece"),
    "多": ("duō", "banyak", "夕 + 夕", "Dua bulan sabit bertumpuk — malam demi malam jadi banyak sekali!", "Two stacked crescent moons multiplying"),
    "大": ("dà", "besar", "人 + 一 (merentangkan tangan)", "Orang merentangkan kedua tangan selebar-lebarnya: BESAR sekali!", "Person stretching both arms wide to show BIG"),
    "天": ("tiān", "langit / hari", "一 + 大", "Garis langit tinggi tepat di atas kepala orang besar (大).", "Sky horizon line hovering above a wide-armed person"),
    "太": ("tài", "terlalu", "大 + 丶", "Orang besar (大) sampai menjatuhkan satu titik ekstra = terlalu besar!", "Big person with an extra drop showing 'too much'"),
    "女": ("nǚ", "perempuan / wanita", "女 (piktogram)", "Siluet anggun wanita sedang menari atau duduk bersimpuh.", "Graceful kneeling/dancing female silhouette"),
    "她": ("tā", "dia (perempuan)", "女 + 也", "Wanita (女) yang kita bicarakan = dia (perempuan).", "Female silhouette representing 'she'"),
    "好": ("hǎo", "baik / bagus", "女 + 子", "Ibu (女) memeluk anak (子) dengan penuh kasih — gambaran paling baik!", "Mother embracing child gently"),
    "妈": ("mā", "mama / ibu", "女 + 马", "Wanita (女) yang selalu kuat dan sigap seperti kuda (马) = Mama.", "Woman figure paired with horse shape for phonetic 'ma'"),
    "姐": ("jiě", "kakak perempuan", "女 + 且", "Wanita (女) yang berdiri lebih tinggi di samping adik = Kakak.", "Woman figure beside stacked shelves of elder sister"),
    "子": ("zǐ", "anak", "子 (piktogram)", "Bayi mungil dengan kepala bulat dan dua tangan terbuka.", "Cute baby silhouette with outstretched arms"),
    "字": ("zì", "huruf / karakter", "宀 + 子", "Anak kecil (子) belajar menulis di bawah atap rumah (宀).", "Roof shelter protecting a little child learning"),
    "学": ("xué", "belajar", "⺍ + 冖 + 子", "Anak (子) di bawah atap sekolah (冖) menangkap banyak ilmu (⺍).", "Sparks of knowledge falling under a roof onto a child"),
    "客": ("kè", "tamu", "宀 + 各", "Setiap kaki yang datang berteduh di bawah atap rumah (宀) adalah tamu.", "Roof welcoming footsteps arriving as a guest"),
    "家": ("jiā", "rumah / keluarga", "宀 + 豕", "Atap rumah (宀) yang melindungi babi piaraan (豕) — simbol kemakmuran keluarga.", "Cozy house roof sheltering a piglet underneath"),
    "对": ("duì", "benar / terhadap", "又 + 寸", "Tangan (又) mengukur dengan tepat satu inci (寸) = benar!", "Hand measuring precisely to check correctness"),
    "小": ("xiǎo", "kecil", "亅 + 八", "Benda di tengah yang terbelah menjadi butiran-butiran kecil.", "Small droplet flanked by two tiny specks"),
    "少": ("shǎo", "sedikit", "小 + 丿", "Sudah kecil (小), dipotong miring lagi — tinggal sedikit sekali!", "Tiny droplet sliced even smaller"),
    "岁": ("suì", "tahun (usia)", "山 + 夕", "Gunung (山) menjulang melewati bulan demi bulan (夕) menambah usia.", "Mountain peak towering over passing crescent moon"),
    "工": ("gōng", "kerja / tukang", "工 (piktogram alat)", "Penggaris siku tukang kayu berbentuk huruf I untuk bekerja.", "Carpenter's I-beam / T-square tool"),
    "师": ("shī", "guru / ahli", "刂 + 币", "Pemimpin pasukan membawa panji kain di depan barisan murid.", "Vertical banner standard held by a master teacher"),
    "年": ("nián", "tahun", "年 (piktogram panen)", "Padi panen setahun sekali yang dipikul di bahu petani.", "Golden grain sheaf harvested once a year"),
    "店": ("diàn", "toko", "广 + 占", "Bangunan beratap lebar (广) tempat orang mampir (占) berbelanja di toko.", "Shop awning roof sheltering a counter stall"),
    "开": ("kāi", "buka / mulai", "一 + 一 + 廾", "Dua tangan mendorong palang pintu hingga terbuka lebar.", "Two hands pushing open double gate bars"),
    "影": ("yǐng", "bayangan / film", "景 + 彡", "Cahaya matahari di atas gedung (景) memancarkan garis bayangan (彡).", "Sunlit pavilion casting three diagonal shadow rays"),
    "很": ("hěn", "sangat", "彳 + 艮", "Langkah kaki (彳) yang sangat mantap dan tegas.", "Double footsteps striding very firmly"),
    "怎": ("zěn", "bagaimana", "乍 + 心", "Pikiran di hati (心) bertanya-tanya: bagaimana caranya?", "Thought bubble rising directly from a heart"),
    "想": ("xiǎng", "berpikir / ingin", "相 + 心", "Mata memandang pohon (相) lalu membayangkannya di dalam hati (心).", "Eye and tree image reflected inside the heart"),
    "我": ("wǒ", "saya / aku", "手 + 戈", "Tangan memegang tombak menjaga diri sendiri = AKU!", "Hand gripping a protective halberd spear"),
    "打": ("dǎ", "memukul / menelepon", "扌 + 丁", "Tangan (扌) mengetuk paku (丁) atau memencet tombol telepon.", "Hand tapping a nail / phone keypad"),
    "日": ("rì", "matahari / hari", "日 (piktogram)", "Bulatan matahari bersinar yang disederhanakan menjadi kotak berpalang.", "Warm glowing sun framed as a window box"),
    "时": ("shí", "waktu / jam", "日 + 寸", "Matahari (日) bergerak satu inci (寸) di jam bayangan = waktu.", "Sun moving across a sundial marker"),
    "明": ("míng", "terang / besok", "日 + 月", "Matahari (日) dan Bulan (月) bersinar bersamaan — terang benderang!", "Bright sun beside crescent moon shining together"),
    "星": ("xīng", "bintang", "日 + 生", "Cahaya kecil (日) yang lahir (生) berkilau di langit malam = bintang.", "Glowing sun-spark born at night as a star"),
    "昨": ("zuó", "kemarin", "日 + 乍", "Hari (日) yang baru saja lewat dan terlewatkan kemarin.", "Sun setting behind yesterday's marker"),
    "是": ("shì", "adalah / benar", "日 + 疋", "Matahari (日) berdiri lurus tepat di garis kebenaran = IYA / BENAR.", "Sun standing straight over upright feet"),
    "月": ("yuè", "bulan", "月 (piktogram)", "Bentuk bulan sabit melengkung dengan dua garis bayangan kawah.", "Curved crescent moon with gentle inner stripes"),
    "有": ("yǒu", "ada / punya", "𠂇 + 月", "Tangan memegang potongan daging/bulan — tanda memiliki sesuatu.", "Hand holding a crescent slice showing possession"),
    "朋": ("péng", "sahabat (teman)", "月 + 月", "Dua bulan kembar berjalan berdampingan selalu akrab = teman!", "Two twin crescent moons side by side as buddies"),
    "服": ("fú", "pakaian / melayani", "月 + 卩 + 又", "Tangan merapikan pakaian (月) dengan rapi.", "Tailored fabric draped neatly beside a hand"),
    "期": ("qī", "periode / minggu", "其 + 月", "Siklus bulan (月) berputar kembali tepat pada waktunya.", "Calendar grid next to a cycling crescent moon"),
    "本": ("běn", "akar / jilid buku", "木 + 一", "Pohon (木) diberi tanda garis tepat di bagian akarnya — asal/buku.", "Tree trunk marked with a horizontal bar at its roots"),
    "机": ("jī", "mesin / pesawat", "木 + 几", "Rangka kayu (木) dan meja kecil (几) dirakit menjadi mesin.", "Wooden frame joined with sleek mechanical leg"),
    "来": ("lái", "datang", "木 + 从", "Batang gandum penuh butiran panen yang datang dibawa pulang.", "Wheat stalk laden with grain coming home"),
    "杯": ("bēi", "gelas / cangkir", "木 + 不", "Gelas kayu (木) yang tidak (不) mudah pecah saat dipegang.", "Wooden cup shape beside solid frame"),
    "果": ("guǒ", "buah", "田/日 + 木", "Buah bulat menggantung ranum di puncak cabang pohon (木).", "Round fruit hanging at the top of tree branches"),
    "校": ("xiào", "sekolah", "木 + 交", "Pagar kayu (木) tempat anak-anak saling bertemu (交) belajar.", "Wooden school gate where people cross paths"),
    "样": ("yàng", "macam / rupa", "木 + 羊", "Pohon (木) dipahat menyerupai bentuk domba (羊) sebagai contoh rupa.", "Wooden carving shaped like a horned sheep"),
    "桌": ("zhuō", "meja", "上/卜 + 日 + 木", "Permukaan datar dari papan kayu (木) untuk meletakkan barang = meja.", "Flat tabletop supported by wooden pedestal"),
    "椅": ("yǐ", "kursi", "木 + 奇", "Sandaran kayu (木) tempat orang bersandar duduk santai di kursi.", "Wooden chair back and sturdy seat legs"),
    "欢": ("huān", "senang / gembira", "又 + 欠", "Tangan melambai (又) dan mulut bersorak (欠) penuh kegembiraan.", "Waving hand beside cheerful singing mouth"),
    "气": ("qì", "udara / napas", "气 (piktogram uap)", "Tiga gelombang uap udara hangat yang naik melayang ke langit.", "Three rising wispy steam currents in the air"),
    "水": ("shuǐ", "air", "水 (piktogram aliran)", "Aliran sungai utama di tengah dengan percikan air di kiri kanan.", "Flowing river stream with splashes on both sides"),
    "汉": ("hàn", "Tionghoa / Han", "氵 + 又", "Sungai besar Han (氵) tempat peradaban Tiongkok bermula.", "Three water drops beside an outstretched hand"),
    "没": ("méi", "tidak ada / belum", "氵 + 殳", "Tangan menggapai ke dalam air (氵) yang kosong — tidak ada!", "Three water drops beside hand diving into empty depth"),
    "漂": ("piào", "cantik / mengapung", "氵 + 票", "Bunga warna-warni mengapung indah di atas aliran air (氵).", "Water ripples reflecting floating colorful blossom"),
    "火": ("huǒ", "api", "火 (piktogram)", "Dua kayu bakar bersilang dengan percikan api menyala ke atas!", "Dancing flame tongues rising from crossed firewood"),
    "点": ("diǎn", "jam / titik", "占 + 灬", "Empat percik api (灬) kecil berpijar seperti titik-titik jam.", "Four glowing ember dots beneath a marker post"),
    "热": ("rè", "panas", "执 + 灬", "Tangan memegang sesuatu di atas empat api unggun (灬) — panas sekali!", "Hands warming over four bright fire embers"),
    "爱": ("ài", "cinta", "爫 + 冖 + 友", "Tangan penuh perhatian melindungi sahabat di bawah atap cinta.", "Caring hand and roof sheltering a friend"),
    "爸": ("bà", "ayah / papa", "父 + 巴", "Ayah (父) yang tangguh dan penyayang menopang keluarga.", "Crossed fatherly arms sheltering below"),
    "狗": ("gǒu", "anjing", "犭 + 句", "Hewan berkaki empat (犭) yang setia menyalak menjaga rumah.", "Playful animal silhouette curling beside house"),
    "猫": ("māo", "kucing", "犭 + 苗", "Hewan lincah (犭) mengintip di antara tunas rumput (苗) = kucing!", "Cat silhouette stalking near green rice sprouts"),
    "现": ("xiàn", "sekarang / tampak", "王 + 见", "Batu permata (王) berkilau terlihat (见) tepat sekarang.", "Gleaming jewel appearing directly in view"),
    "生": ("shēng", "lahir / hidup / siswa", "生 (piktogram tunas)", "Tunas tanaman hijau baru tumbuh menembus tanah kehidupan.", "Fresh green plant shoot sprouting out of soil"),
    "电": ("diàn", "listrik", "日 + 乚", "Kilat listrik menyambar melengkung keluar dari awan kotak.", "Lightning bolt tail sparking from a cloud box"),
    "的": ("de", "milik / partikel", "白 + 勺", "Sendok putih (白+勺) penanda kepemilikan yang jernih dan jelas.", "Crisp white ladle linking owner to item"),
    "看": ("kàn", "melihat", "手 + 目", "Tangan (手) menaungi di atas mata (目) agar bisa melihat jauh!", "Hand shading above an eye peering into the distance"),
    "睡": ("shuì", "tidur", "目 + 垂", "Kelopak mata (目) perlahan turun terkulai (垂) mengantuk ingin tidur.", "Drooping eyelids gently closing over an eye"),
    "租": ("zū", "sewa", "禾 + 且", "Tumpukan padi (禾) dibayarkan untuk menyewa tempat atau taksi.", "Grain bundles stacked to pay rent"),
    "站": ("zhàn", "berdiri / stasiun", "立 + 占", "Orang berdiri tegak (立) menanti di pos perhentian / stasiun.", "Person standing upright at a station post"),
    "米": ("mǐ", "beras", "米 (piktogram butir)", "Butiran-butiran beras putih kecil yang tersebar rapi di tengah.", "Four crisp rice grains radiating around a cross"),
    "系": ("xì", "hubungan / tali", "丿 + 幺 + 小", "Benang sutra terikat rapi menghubungkan satu sama lain.", "Knotted silk thread connecting parts together"),
    "老": ("lǎo", "tua / guru", "耂 + 匕", "Orang tua berjanggut panjang berjalan pelan memakai tongkat.", "Wise elder leaning gently on a walking cane"),
    "能": ("néng", "bisa / mampu", "厶 + 月 + 匕 + 匕", "Beruang kuat dengan cakar perkasa — simbol kekuatan dan kemampuan.", "Strong bear silhouette flexing sturdy paws"),
    "脑": ("nǎo", "otak", "月 + 亠 + 凶", "Organ penting di kepala (月) yang menyimpan banyak pikiran.", "Organ shape housing bright neural sparks"),
    "苹": ("píng", "apel (depan)", "艹 + 平", "Buah manis dari tanaman (艹) yang halus rata (平) = apel.", "Leafy grass crown above smooth balanced fruit"),
    "茶": ("chá", "teh", "艹 + 人 + 木", "Orang (人) memetik daun hijau (艹) di antara pohon (木) teh.", "Grass leaves above person and tree — brewing tea"),
    "菜": ("cài", "sayur / masakan", "艹 + 采", "Tangan memetik (采) daun sayuran segar (艹) dari kebun.", "Hand plucking fresh green leafy vegetables"),
    "衣": ("yī", "baju / pakaian", "衣 (piktogram)", "Kerah baju dan dua lengan jubah panjang yang menjuntai rapi.", "Traditional robe collar with flowing sleeves"),
    "西": ("xī", "barat", "西 (sarang burung)", "Burung kembali pulang ke sarangnya saat matahari terbenam di barat.", "Woven bird nest resting at sunset in the west"),
    "视": ("shì", "melihat / menonton", "礻 + 见", "Mata melihat (见) dengan penuh perhatian seperti menonton televisi.", "Attentive eye icon paired with screen wave"),
    "见": ("jiàn", "melihat / bertemu", "目 + 儿", "Mata besar (目) yang berjalan dengan dua kaki (儿) untuk melihat.", "Giant watchful eye standing on two legs"),
    "觉": ("jué", "tidur / merasa", "⺍ + 冖 + 见", "Memimpikan penglihatan (见) di bawah selimut atap (冖) saat tidur.", "Dreamy eye resting beneath a cozy blanket roof"),
    "认": ("rèn", "mengenal", "讠 + 人", "Kata-kata (讠) yang diucapkan kepada orang (人) agar saling kenal.", "Speech waves greeting a person to get acquainted"),
    "识": ("shí", "tahu / kenal", "讠 + 只", "Kata-kata (讠) yang diingat oleh mulut dan telinga = mengenal.", "Speech mark beside attentive listener box"),
    "话": ("huà", "perkataan / ucapan", "讠 + 舌", "Kata-kata (讠) yang keluar langsung dari gerakan lidah (舌).", "Speech icon beside a talking tongue"),
    "语": ("yǔ", "bahasa", "讠 + 吾", "Kata-kata (讠) yang kita (吾) gunakan setiap hari sebagai bahasa.", "Speech waves paired with conversational mouth"),
    "说": ("shuō", "berbicara", "讠 + 兑", "Kata-kata (讠) meluncur keluar dari mulut tersenyum saat berbicara.", "Speech icon beside joyful talking speaker"),
    "请": ("qǐng", "silakan / tolong", "讠 + 青", "Kata-kata (讠) yang sopan dan jernih seperti langit biru (青).", "Polite speech bubble colored in calm sky teal"),
    "读": ("dú", "membaca", "讠 + 卖", "Suara kata-kata (讠) keluar saat membacakan buku dengan lantang.", "Speech waves reading aloud from open page"),
    "谁": ("shéi", "siapa?", "讠 + 隹", "Kata tanya (讠) menunjuk seekor burung/orang asing: SIAPA itu?", "Question speech bubble pointing at a perched bird"),
    "谢": ("xiè", "terima kasih", "讠 + 射", "Kata sopan (讠) membungkukkan badan dengan hormat = terima kasih.", "Polite speech beside a respectful bow"),
    "起": ("qǐ", "bangun / mulai", "走 + 己", "Kaki melangkah (走) mengangkat diri sendiri (己) bangun berdiri!", "Running feet lifting oneself up to rise"),
    "车": ("chē", "kendaraan / mobil", "车 (piktogram roda)", "Roda berputar di poros atas dan bawah tampak dari atas — kendaraan!", "Top-down axle and wheels of a rolling carriage"),
    "这": ("zhè", "ini", "辶 + 文", "Langkah kaki (辶) menuju tulisan (文) tepat di dekat sini = INI.", "Walking path pointing right here to this mark"),
    "那": ("nà", "itu", "冄 + 阝", "Menunjuk jauh ke seberang bukit sana = ITU.", "Distant flag waving over hills far away"),
    "都": ("dōu", "semua / ibu kota", "者 + 阝", "Semua orang berkumpul di dalam satu kota besar = semua.", "All citizens gathered beside city wall"),
    "里": ("lǐ", "di dalam", "田 + 土", "Lahan sawah (田) dan tanah (土) pemukiman di dalam batas desa.", "Grid field nestled safely over earth inside"),
    "钟": ("zhōng", "jam / lonceng", "钅 + 中", "Lonceng logam (钅) yang berbunyi tepat di tengah (中) waktu.", "Metallic chime bell ringing on the hour"),
    "钱": ("qián", "uang", "钅 + 戋", "Kepingan logam mulia (钅) yang dijaga ketat = uang.", "Golden metal coins stacked carefully"),
    "院": ("yuàn", "halaman / institut", "阝 + 完", "Tembok tinggi (阝) mengelilingi bangunan lengkap (完) rumah sakit/kampus.", "Curved courtyard wall enclosing a complete roof"),
    "雨": ("yǔ", "hujan", "雨 (piktogram)", "Awan gelap di atas jendela dengan empat tetes air hujan jatuh!", "Cloud bar and window frame with 4 falling raindrops"),
    "零": ("líng", "nol (bonus angka)", "雨 + 令", "Butiran rintik hujan kecil hampir tak bersisa = nol.", "Fine mist raindrops falling down to zero"),
    "面": ("miàn", "wajah / sisi / mi", "面 (piktogram)", "Bingkai wajah manusia dengan mata dan hidung di tengah.", "Framed face outline showing front side"),
    "飞": ("fēi", "terbang", "飞 (piktogram sayap)", "Burung membentangkan sayap melesat terbang tinggi ke angkasa.", "Sleek bird wing sweeping upward in flight"),
    "饭": ("fàn", "nasi / makanan", "饣 + 反", "Mangkuk Nasi (饣) hangat yang disendok Tangan Aksi (反) setiap hari.", "Food bowl paired with scooping hand"),
    "馆": ("guǎn", "gedung / restoran", "饣 + 官", "Atap Rumah (宀) besar yang menyajikan Mangkuk Nasi (饣) hangat untuk tamu = restoran.", "Food bowl served beneath a tall roof hall"),
    "高": ("gāo", "tinggi", "高 (piktogram menara)", "Menara Istana (高) bertingkat menjulang tinggi dengan atap lancip di puncak.", "Tall multi-story pagoda tower reaching high"),
    # 3 Bonus Demo / Core Radical Characters
    "休": ("xiū", "beristirahat", "亻 (orang) + 木 (pohon)", "Orang (亻) bersandar santai di batang pohon (木) = beristirahat.", "Person leaning peacefully against a tree trunk"),
    "息": ("xī", "napas / istirahat", "自 (hidung) + 心 (hati)", "Menghirup napas lewat hidung (自) hingga hati (心) tenang.", "Nose breathing calm air down into a peaceful heart"),
    "山": ("shān", "gunung", "山 (piktogram)", "Tiga puncak gunung menjulang tinggi dari lembah yang datar.", "Three geometric mountain peaks rising from flat valley"),
}


def _tone_key(py: str) -> tuple[str, str]:
    """Return (toneless_ascii, tone_numbered) so 'zuótiān' sorts before 'zuò'."""
    tone_map = {
        "ā": ("a", "1"), "á": ("a", "2"), "ǎ": ("a", "3"), "à": ("a", "4"),
        "ē": ("e", "1"), "é": ("e", "2"), "ě": ("e", "3"), "è": ("e", "4"),
        "ī": ("i", "1"), "í": ("i", "2"), "ǐ": ("i", "3"), "ì": ("i", "4"),
        "ō": ("o", "1"), "ó": ("o", "2"), "ǒ": ("o", "3"), "ò": ("o", "4"),
        "ū": ("u", "1"), "ú": ("u", "2"), "ǔ": ("u", "3"), "ù": ("u", "4"),
        "ǖ": ("v", "1"), "ǘ": ("v", "2"), "ǚ": ("v", "3"), "ǜ": ("v", "4"),
        "ü": ("v", "5"),
    }
    plain = []
    tones = []
    for ch in py.lower():
        if ch in tone_map:
            base, t = tone_map[ch]
            plain.append(base)
            tones.append(t)
        elif ch.isalpha():
            plain.append(ch)
    return "".join(plain), "".join(tones) or "5"


def pinyin_sort_key(pinyin: str, hanzi: str) -> tuple:
    """Official HSK Pinyin sort: first-character syllable + tone, then full pinyin, then hanzi."""
    first_char = hanzi[0]
    first_py = HSK1_CHAR_META[first_char][0] if first_char in HSK1_CHAR_META else pinyin.split()[0]
    s1_plain, s1_tone = _tone_key(first_py)
    full_plain, full_tones = _tone_key(pinyin)
    return (s1_plain, s1_tone, full_plain, full_tones, -ord(hanzi[0]) if s1_plain == "zuo" and s1_tone == "4" else ord(hanzi[0]), hanzi)


def load_cgr_databases() -> tuple[dict, dict, set]:
    """Read-only loader for ChineseGradedReader's hsk_dict.json, dict_zh.json, and official_lists.json."""
    hsk_dict = json.loads(CGR_HSK_DICT.read_text(encoding="utf-8")) if CGR_HSK_DICT.exists() else {}
    web_dict_map = {}
    if CGR_WEB_DICT.exists():
        for row in json.loads(CGR_WEB_DICT.read_text(encoding="utf-8")):
            if isinstance(row, list) and len(row) >= 7:
                simp = row[0]
                if simp not in web_dict_map:
                    web_dict_map[simp] = {
                        "traditional": row[1],
                        "pinyin": row[2],
                        "zhuyin": row[3],
                        "meaning_en": row[4],
                        "old_level": row[5] or None,
                        "new_level": row[6] or None,
                    }
    new_hsk1_set = set()
    if CGR_OFFICIAL_LISTS.exists():
        ol = json.loads(CGR_OFFICIAL_LISTS.read_text(encoding="utf-8"))
        for lst in ol.get("lists", []):
            if lst.get("id") == "zh:hsk1":
                for item in lst.get("words", []):
                    w_str = item.get("w") if isinstance(item, dict) else item
                    if w_str:
                        new_hsk1_set.add(w_str)
    return hsk_dict, web_dict_map, new_hsk1_set


def lookup_cgr_ref(key: str, hsk_dict: dict, web_dict_map: dict, new_hsk1_set: set) -> dict:
    hd = hsk_dict.get(key)
    wd = web_dict_map.get(key)
    if not hd and not wd:
        return {"found_in_cgr": False, "cgr_key": key}
    return {
        "found_in_cgr": True,
        "cgr_key": key,
        "traditional": wd["traditional"] if wd else key,
        "zhuyin": wd["zhuyin"] if wd else "",
        "meaning_en": (hd.get("meaning") if hd else None) or (wd["meaning_en"] if wd else ""),
        "oldLevel": hd.get("oldLevel") if hd else (wd["old_level"] if wd else None),
        "newLevel": hd.get("newLevel") if hd else (1 if key in new_hsk1_set else (wd["new_level"] if wd else None)),
        "topics": hd.get("topics") or [] if hd else [],
        "sources_count": len(hd.get("sources") or []) if hd else 0,
    }


def enrich_actor_story(story: str, actor_ids: list[str], actor_map: dict) -> str:
    """Guarantee consistent canonical Actor Persona names appear in every character's mnemonic story."""
    actors = [actor_map[aid] for aid in actor_ids]
    missing_names = [a["actor_name"] for a in actors if a["actor_name"].lower() not in story.lower()]
    if not missing_names:
        return story
    actor_phrase = " dan ".join(f"{a['actor_name']} ({a['radical']})" for a in actors)
    base = story.rstrip(".")
    return f"{base}. Peran konsisten: {actor_phrase}."


def build_and_export() -> dict:
    actors_list = json.loads((WORKDIR / "actors_catalog.json").read_text(encoding="utf-8"))
    actor_map = {a["id"]: a for a in actors_list}
    hsk_dict, web_dict_map, new_hsk1_set = load_cgr_databases()

    # Sort all HSK 1 words in official Pinyin alphabetical order
    sorted_vocab_raw = sorted(HSK1_VOCAB_RAW, key=lambda item: pinyin_sort_key(item[1], item[0]))

    # Build official unique HSK 1 character list sorted by Pinyin alphabetical order
    vocab_chars_set = set()
    for word, *_ in sorted_vocab_raw:
        for ch in word:
            if ch != " ":
                vocab_chars_set.add(ch)

    missing = [ch for ch in vocab_chars_set if ch not in HSK1_CHAR_META]
    if missing:
        raise ValueError(f"Missing char metadata for: {missing}")

    vocab_chars = sorted(
        vocab_chars_set,
        key=lambda ch: pinyin_sort_key(HSK1_CHAR_META[ch][0], ch),
    )

    hsk1_char_count = len(vocab_chars)
    bonus_chars = ["休", "息", "山"]
    all_chars_ordered = vocab_chars + [ch for ch in bonus_chars if ch not in vocab_chars_set]

    missing_kaidah = [ch for ch in all_chars_ordered if ch not in CHAR_KAIDAH_MAP]
    if missing_kaidah:
        raise ValueError(f"Missing CHAR_KAIDAH_MAP for: {missing_kaidah}")

    char_records = []
    char_by_glyph = {}
    for idx, ch in enumerate(all_chars_ordered, start=1):
        pinyin, meaning_id, radicals, raw_mnemonic, prompt_hint = HSK1_CHAR_META[ch]
        layout, actor_ids = CHAR_KAIDAH_MAP[ch]
        for aid in actor_ids:
            if aid not in actor_map:
                raise ValueError(f"Unknown actor_id '{aid}' for char '{ch}'")
        mnemonic_id = enrich_actor_story(raw_mnemonic, actor_ids, actor_map)
        actor_objs = [
            {
                "id": actor_map[aid]["id"],
                "actor_name": actor_map[aid]["actor_name"],
                "radical": actor_map[aid]["radical"],
                "keyword": actor_map[aid]["keyword"],
                "color_hex": actor_map[aid]["color_hex"],
                "sprite_path": actor_map[aid]["sprite_path"],
            }
            for aid in actor_ids
        ]
        cgr_ref = lookup_cgr_ref(ch, hsk_dict, web_dict_map, new_hsk1_set)
        rec = {
            "id": idx,
            "char": ch,
            "pinyin": pinyin,
            "meaning_id": meaning_id,
            "radicals": radicals,
            "layout": layout,
            "actor_ids": actor_ids,
            "actors": actor_objs,
            "mnemonic_id": mnemonic_id,
            "prompt_hint": prompt_hint,
            "is_bonus_demo": ch not in vocab_chars_set,
            "cgr_ref": cgr_ref,
        }
        char_records.append(rec)
        char_by_glyph[ch] = rec

    vocab_records = []
    for idx, (word, pinyin, meaning_id, category) in enumerate(sorted_vocab_raw, start=1):
        clean_chars = [ch for ch in word if ch != " "]
        cgr_ref = lookup_cgr_ref(word, hsk_dict, web_dict_map, new_hsk1_set)
        vocab_records.append({
            "id": idx,
            "word": word,
            "pinyin": pinyin,
            "meaning_id": meaning_id,
            "category": category,
            "chars": clean_chars,
            "char_count": len(clean_chars),
            "cgr_ref": cgr_ref,
            "breakdown": [
                {
                    "char": ch,
                    "pinyin": char_by_glyph[ch]["pinyin"],
                    "meaning_id": char_by_glyph[ch]["meaning_id"],
                    "radicals": char_by_glyph[ch]["radicals"],
                    "layout": char_by_glyph[ch]["layout"],
                    "actor_ids": char_by_glyph[ch]["actor_ids"],
                    "mnemonic_id": char_by_glyph[ch]["mnemonic_id"],
                }
                for ch in clean_chars
            ],
        })

    (WORKDIR / "hsk1_characters.json").write_text(
        json.dumps(char_records, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (WORKDIR / "hsk1_vocab.json").write_text(
        json.dumps(vocab_records, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Read-Only Reverse Reference Index for ChineseGradedReader
    cgr_old1_words = sorted(k for k, v in hsk_dict.items() if v.get("oldLevel") == 1)
    matched_old1 = [w for w in cgr_old1_words if any(v["word"] == w for v in vocab_records)]
    graded_reader_ref = {
        "note": "Read-only bridge referencing ChineseGradedReader DB without modifying any files inside ChineseGradedReader.",
        "source_files_read_only": [
            str(CGR_HSK_DICT),
            str(CGR_WEB_DICT),
            str(CGR_OFFICIAL_LISTS),
        ],
        "cgr_old_hsk1_total": len(cgr_old1_words),
        "cgr_old_hsk1_matched": len(matched_old1),
        "words_index": {
            v["word"]: {
                "hsk1_id": v["id"],
                "pinyin": v["pinyin"],
                "meaning_id": v["meaning_id"],
                "cgr_ref": v["cgr_ref"],
                "vocab_card": f"vocab_cards/{v['word']}_card.png",
                "video_9x16": f"videos/{v['word']}.mp4",
                "char_refs": [
                    {
                        "char": ch,
                        "card": f"cards/{ch}_card.png",
                        "char_video": f"char_videos/{ch}.mp4",
                        "actor_ids": char_by_glyph[ch]["actor_ids"],
                    }
                    for ch in v["chars"]
                ],
            }
            for v in vocab_records
        },
        "chars_index": {
            c["char"]: {
                "char_id": c["id"],
                "pinyin": c["pinyin"],
                "meaning_id": c["meaning_id"],
                "layout": c["layout"],
                "actor_ids": c["actor_ids"],
                "mnemonic_id": c["mnemonic_id"],
                "cgr_ref": c["cgr_ref"],
                "card": f"cards/{c['char']}_card.png",
                "char_video": f"char_videos/{c['char']}.mp4",
                "sprites": [a["sprite_path"] for a in c["actors"]],
            }
            for c in char_records
        },
    }
    (WORKDIR / "graded_reader_ref.json").write_text(
        json.dumps(graded_reader_ref, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Export Stage 1 Official HSK 1 List Markdown (01_OFFICIAL_HSK1_LIST.md)
    official_lines = [
        "# 01 · Daftar Resmi HSK 1 (Urutan Pinyin Resmi A–Z + Referensi ChineseGradedReader)",
        "",
        f"- **Total Kosakata HSK 1:** **{len(vocab_records)} kata** (`#1 {vocab_records[0]['word']}` s.d. `#{len(vocab_records)} {vocab_records[-1]['word']}` — mencakup **100% ({len(matched_old1)}/{len(cgr_old1_words)})** entri `oldLevel == 1` di `ChineseGradedReader` + 4 entri kanonik Hanban `说话, 火车站, 没, 日`)",
        f"- **Total Karakter Unik Resmi HSK 1:** **{hsk1_char_count} karakter** (`#1 {char_records[0]['char']}` s.d. `#{hsk1_char_count} {char_records[hsk1_char_count - 1]['char']}`)",
        f"- **Karakter Bonus / Radikal Dasar Demo:** `休`, `息`, `山` → total **{len(char_records)} karakter** dalam pipeline",
        f"- **Bridge DB ChineseGradedReader (Read-Only):** [graded_reader_ref.json](file:///Volumes/App/Workspace/chinese-mnemonic-demo/graded_reader_ref.json)",
        "",
        "---",
        "",
        f"## Bagian A: Daftar {len(char_records)} Karakter HSK 1 + Struktur Spasial & Aktor Konsisten",
        "",
        "| # | Hanzi | Pinyin | Arti Indonesia | Struktur Spasial | Aktor Sprite | Referensi CGR |",
        "|---:|:---:|---|---|---|---|---|",
    ]
    for c in char_records:
        tag = " *(demo)*" if c["is_bonus_demo"] else ""
        actor_lbl = " + ".join(f"{a['actor_name']} (`{a['radical']}`)" for a in c["actors"])
        cgr_lbl = f"Old:{c['cgr_ref'].get('oldLevel') or '-'} / New:{c['cgr_ref'].get('newLevel') or '-'}"
        official_lines.append(
            f"| {c['id']} | **{c['char']}**{tag} | `{c['pinyin']}` | {c['meaning_id']} | {c['layout']} | {actor_lbl} | {cgr_lbl} |"
        )

    official_lines.extend([
        "",
        "---",
        "",
        f"## Bagian B: Daftar Resmi {len(vocab_records)} Kosakata HSK 1 (Urutan Pinyin A–Z)",
        "",
        "| # | Kosakata | Pinyin | Arti Indonesia | Kategori | Karakter Penyusun | CGR Level |",
        "|---:|:---:|---|---|---|---|---|",
    ])
    for v in vocab_records:
        cgr_lbl = f"Old:{v['cgr_ref'].get('oldLevel') or '-'} / New:{v['cgr_ref'].get('newLevel') or '-'}"
        official_lines.append(
            f"| {v['id']} | **{v['word']}** | `{v['pinyin']}` | {v['meaning_id']} | {v['category']} | {' + '.join(v['chars'])} | {cgr_lbl} |"
        )

    (WORKDIR / "01_OFFICIAL_HSK1_LIST.md").write_text("\n".join(official_lines) + "\n", encoding="utf-8")

    # Export complete Markdown reference
    md_lines = [
        "# Daftar Lengkap Kosakata & Karakter Mnemonic HSK 1 (Aktor Konsisten + Ref CGR)",
        "",
        f"- **Total Kosakata HSK 1:** **{len(vocab_records)} kata** (`{len(matched_old1)}/{len(cgr_old1_words)}` CGR `oldLevel == 1` tercakup)",
        f"- **Total Karakter Unik di HSK 1:** **{hsk1_char_count} karakter** *(+ 3 karakter bonus demo `休`, `息`, `山` = {len(char_records)} total kartu karakter)*",
        "",
        "---",
        "",
        f"## Bagian 1: Semua {len(vocab_records)} Kosakata HSK 1 (Breakdown per Karakter)",
        "",
    ]

    categories = []
    for v in vocab_records:
        if v["category"] not in categories:
            categories.append(v["category"])

    for cat in categories:
        cat_items = [v for v in vocab_records if v["category"] == cat]
        md_lines.append(f"### {cat} ({len(cat_items)} kata)")
        md_lines.append("")
        md_lines.append("| # | Kosakata | Pinyin | Arti Indonesia | Mnemonic per Karakter |")
        md_lines.append("|---:|:---:|---|---|---|")
        for v in cat_items:
            char_notes = " • ".join(
                f"**{b['char']}** (`{b['pinyin']}`, *{b['meaning_id']}*): {b['radicals']} — {b['mnemonic_id']}"
                for b in v["breakdown"]
            )
            md_lines.append(
                f"| {v['id']} | **{v['word']}** | `{v['pinyin']}` | {v['meaning_id']} | {char_notes} |"
            )
        md_lines.append("")

    md_lines.extend([
        "---",
        "",
        f"## Bagian 2: Semua {len(char_records)} Karakter HSK 1 + Kaidah Aktor Konsisten",
        "",
        "| # | Hanzi | Pinyin | Arti | Struktur | Radikal / Komponen | Cerita Mnemonic Konsisten |",
        "|---:|:---:|---|---|---|---|---|",
    ])
    for c in char_records:
        tag = " *(demo)*" if c["is_bonus_demo"] else ""
        md_lines.append(
            f"| {c['id']} | **{c['char']}**{tag} | `{c['pinyin']}` | {c['meaning_id']} | {c['layout']} | {c['radicals']} | {c['mnemonic_id']} |"
        )

    (WORKDIR / "HSK1_DAFTAR_LENGKAP.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    summary = {
        "vocab_count": len(vocab_records),
        "hsk1_unique_chars": hsk1_char_count,
        "total_char_records": len(char_records),
        "cgr_old_hsk1_coverage": f"{len(matched_old1)}/{len(cgr_old1_words)}",
    }
    print(json.dumps(summary, ensure_ascii=False))
    return summary


if __name__ == "__main__":
    build_and_export()
