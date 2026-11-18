#!/usr/bin/env python3
"""Stage 1A: Canonical Actor / Radical Sprite Engine (50 consistent Chineasy actors)."""

import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

WORKDIR = Path("/Volumes/App/Workspace/chinese-mnemonic-demo")
SPRITES_DIR = WORKDIR / "sprites"
SPRITE_CARDS_DIR = WORKDIR / "sprite_cards"
SPRITES_DIR.mkdir(parents=True, exist_ok=True)
SPRITE_CARDS_DIR.mkdir(parents=True, exist_ok=True)

BG_COLOR = (250, 246, 240)       # #FAF6F0
SOFT_DISC = (242, 234, 221)
CHARCOAL = (43, 45, 66)          # #2B2D42
TERRACOTTA = (217, 83, 79)       # #D9534F
FOREST = (46, 111, 94)           # #2E6F5E
MUSTARD = (214, 146, 48)         # warm amber-gold
BLUSH = (244, 165, 148)
MINT = (138, 189, 174)
CARD_BG = (255, 253, 249)
CARD_BORDER = (228, 221, 210)
MUTED = (108, 105, 100)

FONT_CJK = "/System/Library/Fonts/STHeiti Medium.ttc"
FONT_LATIN = "/System/Library/Fonts/Avenir Next.ttc"

# 50 Canonical Actors covering 100% of HSK 1 characters + 3 demo chars
# Format: (id, radical, actor_name, keyword, role_group, role_color_rgb, description)
ACTOR_DEFS = [
    ("ren_person", "人 / 亻", "Aktor Orang", "Orang", "Manusia", TERRACOTTA, "Siluet manusia berhelm/berkepala bulat merah yang selalu tampil sebagai pemeran utama."),
    ("nv_woman", "女", "Sang Ibu / Wanita", "Wanita", "Manusia", TERRACOTTA, "Sosok wanita anggun dengan sanggul terakota; lambang ibu, kakak, dan perempuan."),
    ("zi_child", "子 / 儿", "Si Anak Kecil", "Anak", "Manusia", TERRACOTTA, "Bayi atau anak kecil berlengan terbuka penuh semangat dan keingintahuan."),
    ("kou_mouth", "口", "Mulut Bicara", "Mulut", "Komunikasi", TERRACOTTA, "Mulut ekspresif untuk berbicara, makan, minum, dan bertanya."),
    ("yan_speech", "讠", "Gelombang Kata", "Kata-kata", "Komunikasi", FOREST, "Gelembung ucapan dan gelombang suara sebagai penanda bahasa, bicara, dan tanya."),
    ("mu_eye", "目 / 见", "Mata Pengamat", "Mata", "Indra", CHARCOAL, "Kotak mata pengamat dengan iris hijau hutan untuk melihat, menonton, dan tidur."),
    ("shou_hand", "手 / 扌 / 又", "Tangan Aksi", "Tangan", "Aksi", TERRACOTTA, "Tangan aktif yang memegang, mengetuk, menaungi mata, atau memberi aksi."),
    ("xin_heart", "心 / 忄", "Hati Perasaan", "Hati", "Perasaan", TERRACOTTA, "Jantung/hati hangat dengan denyut tenang sebagai pusat pikiran dan emosi."),
    ("zu_foot", "走 / 辶 / 止", "Langkah Kaki", "Langkah", "Gerak", CHARCOAL, "Jejak kaki melangkah di jalur jalan untuk bergerak, datang, dan pergi."),
    ("shui_water", "水 / 氵", "Tetes Air", "Air", "Alam", FOREST, "Tiga tetes dan aliran sungai biru-hijau untuk cairan, minum, dan mengapung."),
    ("mu_tree", "木", "Pohon Kayu", "Pohon", "Alam", FOREST, "Batang pohon kokoh dengan tajuk daun hijau hutan untuk kayu, buah, dan tempat teduh."),
    ("cao_grass", "艹 / 生", "Tunas Daun", "Tunas", "Alam", FOREST, "Dua helai tunas daun muda yang tumbuh segar untuk tumbuhan, sayur, dan teh."),
    ("ri_sun", "日 / 白", "Surya Bersinar", "Matahari", "Waktu & Alam", MUSTARD, "Matahari keemasan bercahaya sebagai penanda hari, waktu, dan kecerahan."),
    ("yue_moon", "月", "Sabit Bulan", "Bulan", "Waktu & Alam", CHARCOAL, "Bulan sabit malam yang berputar teratur untuk bulan, teman, dan malam."),
    ("huo_fire", "火 / 灬", "Api Menyala", "Api", "Alam & Energi", TERRACOTTA, "Lidah api menyala terang di atas kayu bakar untuk panas, api, dan titik cahaya."),
    ("shan_mountain", "山", "Puncak Gunung", "Gunung", "Alam", FOREST, "Tiga puncak gunung menjulang dengan pucuk salju sebagai penanda ketinggian."),
    ("tu_earth", "土", "Gundukan Tanah", "Tanah", "Alam & Tempat", MUSTARD, "Lapisan tanah datar dan gundukan bumi tempat berpijak, duduk, dan membangun."),
    ("mian_roof", "宀 / 冖 / 广", "Atap Rumah", "Atap", "Bangunan", CHARCOAL, "Atap pelindung yang menaungi keluarga, huruf, toko, dan ruang belajar."),
    ("men_door", "门 / 户", "Pintu Gerbang", "Pintu", "Bangunan", CHARCOAL, "Daun pintu gerbang tempat masuk, keluar, dan membuka ruangan."),
    ("wei_wall", "囗 / 匚", "Kotak Batas", "Batas Kotak", "Bangunan", CHARCOAL, "Bingkai dinding pelindung berbentuk kotak yang menjaga isi di dalamnya."),
    ("jin_metal", "钅", "Keping Logam", "Logam", "Benda & Nilai", MUSTARD, "Kilau logam mulia dan lonceng emas untuk uang koin dan penunjuk waktu."),
    ("shi_food", "饣 / 米", "Mangkuk Nasi", "Nasi/Makanan", "Makanan", MUSTARD, "Semangkuk nasi hangat dan butiran beras sumber energi harian."),
    ("he_grain", "禾", "Tangkai Padi", "Padi", "Alam & Pangan", MUSTARD, "Batang padi merunduk berisi bulir panen untuk keharmonisan dan sewa."),
    ("quan_animal", "犭", "Hewan Lincah", "Hewan", "Makhluk", TERRACOTTA, "Siluet hewan berkaki empat yang lincah seperti anjing penjaga dan kucing."),
    ("ma_horse", "马", "Kuda Tangguh", "Kuda", "Makhluk", CHARCOAL, "Kuda gagah berlari kencang — juga dipakai sebagai penanda bunyi 'ma'."),
    ("zhui_bird", "隹 / 羽 / 飞", "Burung Terbang", "Burung/Sayap", "Makhluk", FOREST, "Sayap burung yang mengepak terbang tinggi dan hinggap di dahan."),
    ("che_vehicle", "车", "Roda Kendaraan", "Kendaraan", "Transportasi", CHARCOAL, "Poros roda berputar tampak atas untuk mobil, taksi, dan kereta."),
    ("yu_rain", "雨", "Awan Hujan", "Hujan", "Cuaca", FOREST, "Awan gelap dengan empat rintik air hujan yang turun dari langit."),
    ("bing_ice", "冫", "Kristal Es", "Es", "Cuaca", FOREST, "Dua kristal es tajam yang membawa suhu dingin membeku."),
    ("tian_field", "田", "Petak Sawah", "Sawah", "Alam & Tempat", FOREST, "Petak sawah kotak terbagi empat rapi untuk lahan dan wilayah dalam."),
    ("dao_knife", "刀 / 刂", "Pisau Tajam", "Pisau", "Alat", CHARCOAL, "Bilah pisau tajam yang membelah bagian secara presisi."),
    ("gong_tool", "工 / 寸", "Alat Ukur", "Alat Ukur", "Alat & Kerja", CHARCOAL, "Penggaris siku tukang dan ukuran inci untuk bekerja dengan tepat."),
    ("yi_cloth", "衣 / 礻 / 巾", "Kain & Baju", "Kain", "Benda", TERRACOTTA, "Jubah pakaian berkerah dan kain panji untuk busana serta tata krama."),
    ("si_silk", "幺 / 系", "Benang Sutra", "Benang", "Benda", MUSTARD, "Untaian benang sutra terikat rapi yang menghubungkan satu hal dengan lainnya."),
    ("shi_arrow", "矢 / 戈", "Panah & Tombak", "Panah/Tombak", "Alat", CHARCOAL, "Mata panah dan tombak penjaga untuk ketepatan medis dan pertahanan diri."),
    ("li_stand", "立", "Berdiri Tegak", "Berdiri", "Aksi", CHARCOAL, "Orang berdiri tegak kokoh di atas garis tanah sambil menunggu."),
    ("yi_one", "一 / 二 / 三", "Garis Hitung", "Garis", "Angka & Ruang", CHARCOAL, "Garis mendatar lurus untuk hitungan dasar dan batas atas/bawah."),
    ("shi_ten", "十 / 午", "Silang Sepuluh", "Silang", "Angka", TERRACOTTA, "Tanda silang tegas melambangkan sepuluh jari lengkap dan titik tengah."),
    ("ba_divide", "八 / 几", "Belahan Simetris", "Terbagi", "Angka & Bentuk", MUSTARD, "Dua garis terbuka simetris atau meja kecil tempat berbagi rata."),
    ("da_big", "大 / 天 / 太", "Rentang Besar", "Besar", "Ukuran", TERRACOTTA, "Figur manusia merentangkan kedua tangan selebar mungkin: BESAR!"),
    ("xiao_small", "小 / 少", "Butiran Kecil", "Kecil", "Ukuran", FOREST, "Tetesan mungil di tengah dengan dua titik kecil di sisinya."),
    ("xi_evening", "夕 / 多", "Bulan Senja", "Senja", "Waktu", MUSTARD, "Sabit senja miring yang menandakan petang hari dan waktu berlalu."),
    ("zi_nose", "自", "Hidung Napas", "Hidung", "Tubuh", FOREST, "Batang hidung pengambil napas yang menenangkan diri sendiri."),
    ("qi_steam", "气", "Uap Udara", "Udara", "Alam", FOREST, "Tiga gelombang uap udara hangat yang mengalir naik ke angkasa."),
    ("gui_jade", "王 / 白", "Batu Permata", "Permata", "Benda", MUSTARD, "Batu giok berharga yang bersinar putih jernih dan berkilau."),
    ("shi_pig", "豕 / 羊", "Ternak Rumah", "Ternak", "Makhluk", TERRACOTTA, "Hewan ternak rumah tangga lambang kemakmuran keluarga dan rupa."),
    ("fu_father", "父 / 老", "Sosok Tetua", "Tetua", "Manusia", CHARCOAL, "Sosok ayah dan tetua bijak dengan tongkat yang mengayomi."),
    ("gu_drum", "壴 / 乐", "Genderang Pesta", "Genderang", "Perayaan", TERRACOTTA, "Genderang perayaan yang ditabuh penuh semangat dan kegembiraan."),
    ("jing_tower", "京 / 高", "Menara Istana", "Menara", "Bangunan", CHARCOAL, "Menara gerbang istana bertingkat tinggi di pusat ibu kota."),
    ("fu_mound", "阝", "Tembok Bukit", "Tembok/Bukit", "Bangunan", MUSTARD, "Dinding kota melengkung dan lereng bukit penanda tempat & arah."),
]


def draw_sprite_motif(aid: str, color: tuple[int, int, int]) -> Image.Image:
    """Draw a 1024x1024 supersampled flat-vector sprite and downsample to 512x512 RGBA."""
    S = 1024
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, cy = S // 2, S // 2

    # Soft circular badge backing for visual harmony
    d.ellipse([72, 72, S - 72, S - 72], fill=(250, 246, 240, 235), outline=color + (255,), width=14)

    if aid == "ren_person":
        d.ellipse([cx - 85, 190, cx + 85, 360], fill=color)
        d.rounded_rectangle([cx - 125, 368, cx + 45, 418], radius=24, fill=CHARCOAL)
        d.polygon([(cx - 12, 410), (cx + 42, 410), (cx - 165, 800), (cx - 235, 765)], fill=CHARCOAL)
        d.polygon([(cx - 20, 410), (cx + 45, 410), (cx + 225, 765), (cx + 155, 800)], fill=CHARCOAL)
        d.rounded_rectangle([cx - 265, 760, cx - 145, 825], radius=28, fill=color)
        d.rounded_rectangle([cx + 145, 760, cx + 265, 825], radius=28, fill=color)

    elif aid == "nv_woman":
        d.ellipse([cx + 40, 200, cx + 140, 300], fill=color)
        d.ellipse([cx - 85, 225, cx + 85, 395], fill=CHARCOAL)
        d.polygon([(cx - 25, 405), (cx + 25, 405), (cx - 190, 620), (cx + 180, 790), (cx + 115, 825), (cx - 255, 630)], fill=CHARCOAL)
        d.line([(240, 480), (784, 480)], fill=color, width=54)
        d.polygon([(cx + 120, 460), (cx + 185, 485), (cx - 160, 825), (cx - 220, 785)], fill=CHARCOAL)

    elif aid == "zi_child":
        d.ellipse([cx - 105, 190, cx + 105, 390], fill=color)
        d.ellipse([cx - 42, 260, cx - 18, 284], fill=(255, 255, 255))
        d.ellipse([cx + 18, 260, cx + 42, 284], fill=(255, 255, 255))
        d.arc([cx - 45, 290, cx + 45, 350], 15, 165, fill=(255, 255, 255), width=12)
        d.rounded_rectangle([cx - 240, 465, cx + 240, 525], radius=30, fill=color)
        d.rounded_rectangle([cx - 50, 390, cx + 50, 790], radius=32, fill=FOREST)
        d.line([(cx - 50, 620), (cx + 50, 570)], fill=(255, 255, 255), width=14)
        d.line([(cx - 50, 710), (cx + 50, 660)], fill=(255, 255, 255), width=14)

    elif aid == "kou_mouth":
        d.rounded_rectangle([240, 290, 784, 734], radius=76, outline=color, width=64)
        d.arc([340, 420, 684, 640], 10, 170, fill=CHARCOAL, width=28)
        d.arc([810, 380, 910, 640], -50, 50, fill=FOREST, width=22)

    elif aid == "yan_speech":
        d.rounded_rectangle([230, 260, 794, 650], radius=110, fill=color)
        d.polygon([(350, 640), (470, 640), (310, 780)], fill=color)
        for dy in (370, 455, 540):
            d.rounded_rectangle([330, dy, 694, dy + 32], radius=16, fill=(255, 255, 255))

    elif aid == "mu_eye":
        d.rounded_rectangle([280, 220, 744, 804], radius=36, outline=CHARCOAL, width=54)
        d.line([(280, 410), (744, 410)], fill=CHARCOAL, width=38)
        d.line([(280, 610), (744, 610)], fill=CHARCOAL, width=38)
        d.ellipse([cx - 120, cy - 120, cx + 120, cy + 120], fill=FOREST)
        d.ellipse([cx - 55, cy - 55, cx + 55, cy + 55], fill=CHARCOAL)
        d.ellipse([cx + 18, cy - 55, cx + 58, cy - 15], fill=(255, 255, 255))

    elif aid == "shou_hand":
        for i, (y, x0) in enumerate([(270, 230), (385, 210), (500, 220)]):
            d.rounded_rectangle([x0, y, 760, y + 72], radius=36, fill=color)
            d.ellipse([x0 + 14, y + 14, x0 + 56, y + 58], fill=(255, 255, 255))
        d.polygon([(470, 270), (545, 270), (370, 810), (295, 775)], fill=color)

    elif aid == "xin_heart":
        d.ellipse([250, 270, 520, 540], fill=color)
        d.ellipse([504, 270, 774, 540], fill=color)
        d.polygon([(262, 455), (762, 455), (cx, 810)], fill=color)
        d.arc([180, 420, 420, 780], 115, 210, fill=BLUSH, width=22)
        d.arc([604, 420, 844, 780], -30, 65, fill=BLUSH, width=22)

    elif aid == "zu_foot":
        d.path = None
        d.line([(230, 310), (340, 430), (260, 640), (790, 760)], fill=color, width=54, joint="curve")
        d.ellipse([440, 240, 560, 360], fill=TERRACOTTA)
        d.polygon([(500, 380), (570, 380), (700, 630), (625, 655)], fill=TERRACOTTA)
        d.polygon([(475, 420), (535, 420), (435, 640), (375, 615)], fill=TERRACOTTA)

    elif aid == "shui_water":
        for bx, by, sc in [(310, 280, 0.85), (512, 230, 1.05), (714, 290, 0.85)]:
            r = int(65 * sc)
            d.polygon([(bx, by - int(115 * sc)), (bx - r, by + 10), (bx + r, by + 10)], fill=color)
            d.ellipse([bx - r, by - 35, bx + r, by + int(95 * sc)], fill=color)
        d.arc([220, 560, 540, 760], 15, 165, fill=CHARCOAL, width=36)
        d.arc([484, 560, 804, 760], 15, 165, fill=CHARCOAL, width=36)

    elif aid == "mu_tree":
        d.ellipse([260, 175, 580, 495], fill=color)
        d.ellipse([440, 175, 760, 495], fill=color)
        d.ellipse([330, 120, 690, 460], fill=color)
        d.rectangle([cx - 32, 340, cx + 32, 815], fill=CHARCOAL)
        d.line([(250, 460), (774, 460)], fill=CHARCOAL, width=48)
        d.line([(cx, 480), (255, 760)], fill=CHARCOAL, width=42)
        d.line([(cx, 480), (769, 760)], fill=CHARCOAL, width=42)

    elif aid == "cao_grass":
        d.line([(220, 560), (804, 560)], fill=CHARCOAL, width=46)
        d.rectangle([cx - 24, 340, cx + 24, 800], fill=color)
        d.ellipse([260, 230, 500, 430], fill=color)
        d.ellipse([524, 230, 764, 430], fill=color)

    elif aid == "ri_sun":
        d.ellipse([cx - 175, cy - 175, cx + 175, cy + 175], fill=color)
        for deg in range(0, 360, 30):
            ang = math.radians(deg)
            x1 = cx + int(225 * math.cos(ang))
            y1 = cy + int(225 * math.sin(ang))
            x2 = cx + int(315 * math.cos(ang))
            y2 = cy + int(315 * math.sin(ang))
            d.line([(x1, y1), (x2, y2)], fill=TERRACOTTA, width=28)

    elif aid == "yue_moon":
        d.ellipse([260, 200, 780, 820], fill=CHARCOAL)
        d.ellipse([380, 170, 860, 760], fill=(250, 246, 240))
        for sx, sy, sr in [(690, 320, 44), (735, 590, 30)]:
            d.polygon([(sx, sy - sr), (sx + sr // 3, sy - sr // 3), (sx + sr, sy), (sx + sr // 3, sy + sr // 3), (sx, sy + sr), (sx - sr // 3, sy + sr // 3), (sx - sr, sy), (sx - sr // 3, sy - sr // 3)], fill=MUSTARD)

    elif aid == "huo_fire":
        d.line([(280, 780), (620, 520)], fill=CHARCOAL, width=54)
        d.line([(744, 780), (404, 520)], fill=CHARCOAL, width=54)
        d.polygon([(cx, 170), (cx - 125, 560), (cx + 125, 560)], fill=color)
        d.ellipse([cx - 125, 440, cx + 125, 680], fill=color)
        d.polygon([(cx, 290), (cx - 65, 570), (cx + 65, 570)], fill=MUSTARD)
        d.ellipse([260, 360, 355, 510], fill=color)
        d.ellipse([670, 360, 765, 510], fill=color)

    elif aid == "shan_mountain":
        d.polygon([(190, 740), (340, 370), (490, 740)], fill=color)
        d.polygon([(534, 740), (684, 390), (834, 740)], fill=color)
        d.polygon([(310, 740), (512, 220), (714, 740)], fill=FOREST)
        d.polygon([(512, 220), (455, 360), (512, 330), (569, 360)], fill=(255, 255, 255))
        d.line([(190, 740), (834, 740)], fill=CHARCOAL, width=42)

    elif aid == "tu_earth":
        d.ellipse([260, 510, 764, 830], fill=color)
        d.rectangle([200, 700, 824, 830], fill=(250, 246, 240))
        d.line([(200, 700), (824, 700)], fill=CHARCOAL, width=48)
        d.line([(320, 440), (704, 440)], fill=CHARCOAL, width=44)
        d.line([(cx, 240), (cx, 700)], fill=CHARCOAL, width=48)

    elif aid == "mian_roof":
        d.ellipse([cx - 42, 200, cx + 42, 284], fill=TERRACOTTA)
        d.polygon([(190, 480), (cx, 270), (834, 480), (760, 535), (cx, 350), (264, 535)], fill=color)
        d.rounded_rectangle([320, 540, 704, 780], radius=24, outline=MUSTARD, width=32)

    elif aid == "men_door":
        d.rounded_rectangle([240, 220, 490, 800], radius=24, outline=color, width=46)
        d.rounded_rectangle([534, 220, 784, 800], radius=24, outline=color, width=46)
        d.ellipse([415, 490, 455, 530], fill=TERRACOTTA)
        d.ellipse([569, 490, 609, 530], fill=TERRACOTTA)

    elif aid == "wei_wall":
        d.rounded_rectangle([220, 220, 804, 804], radius=36, outline=color, width=56)
        d.rounded_rectangle([360, 360, 664, 664], radius=24, outline=MUSTARD, width=42)

    elif aid == "jin_metal":
        d.ellipse([290, 240, 734, 684], fill=color, outline=CHARCOAL, width=32)
        d.rectangle([cx - 70, cy - 120, cx + 70, cy + 20], outline=(255, 255, 255), width=26)
        d.line([(240, 760), (784, 760)], fill=CHARCOAL, width=42)

    elif aid == "shi_food":
        d.chord([230, 360, 794, 790], 0, 180, fill=TERRACOTTA, outline=CHARCOAL, width=30)
        d.arc([290, 230, 734, 540], 180, 360, fill=(255, 255, 255), width=16)
        d.ellipse([290, 330, 734, 530], fill=color)
        d.line([(560, 210), (460, 440)], fill=CHARCOAL, width=26)
        d.line([(650, 225), (520, 440)], fill=CHARCOAL, width=26)

    elif aid == "he_grain":
        d.line([(cx, 260), (cx, 800)], fill=CHARCOAL, width=44)
        d.line([(280, 430), (744, 430)], fill=CHARCOAL, width=40)
        d.arc([340, 190, 680, 360], 120, 250, fill=color, width=42)
        d.ellipse([280, 250, 370, 340], fill=color)
        d.line([(cx, 430), (260, 710)], fill=color, width=38)
        d.line([(cx, 430), (764, 710)], fill=color, width=38)

    elif aid == "quan_animal":
        d.ellipse([330, 360, 690, 660], fill=color)
        d.polygon([(350, 420), (310, 230), (440, 360)], fill=color)
        d.polygon([(670, 420), (710, 230), (580, 360)], fill=color)
        d.ellipse([425, 455, 465, 495], fill=CHARCOAL)
        d.ellipse([555, 455, 595, 495], fill=CHARCOAL)
        d.ellipse([485, 520, 539, 560], fill=CHARCOAL)
        d.arc([230, 540, 450, 780], 110, 250, fill=CHARCOAL, width=32)

    elif aid == "ma_horse":
        d.rounded_rectangle([290, 380, 710, 580], radius=60, fill=color)
        d.polygon([(610, 420), (740, 240), (800, 310), (710, 490)], fill=color)
        d.polygon([(680, 265), (710, 185), (755, 255)], fill=TERRACOTTA)
        for lx in (320, 420, 580, 660):
            d.line([(lx, 540), (lx - 20, 790)], fill=color, width=38)

    elif aid == "zhui_bird":
        d.ellipse([330, 390, 700, 680], fill=color)
        d.ellipse([540, 240, 730, 430], fill=color)
        d.polygon([(710, 310), (830, 340), (710, 385)], fill=MUSTARD)
        d.ellipse([630, 295, 665, 330], fill=(255, 255, 255))
        d.line([(470, 660), (440, 800)], fill=CHARCOAL, width=28)
        d.line([(560, 660), (560, 800)], fill=CHARCOAL, width=28)

    elif aid == "che_vehicle":
        d.ellipse([230, 230, 794, 794], outline=color, width=54)
        d.line([(cx, 180), (cx, 844)], fill=TERRACOTTA, width=40)
        d.line([(180, cy), (844, cy)], fill=TERRACOTTA, width=40)
        d.ellipse([cx - 75, cy - 75, cx + 75, cy + 75], fill=MUSTARD)

    elif aid == "yu_rain":
        d.ellipse([240, 250, 520, 480], fill=CHARCOAL)
        d.ellipse([420, 190, 720, 470], fill=CHARCOAL)
        d.ellipse([560, 270, 800, 480], fill=CHARCOAL)
        d.rectangle([280, 360, 750, 480], fill=CHARCOAL)
        for rx, ry in [(340, 560), (455, 630), (575, 560), (690, 630)]:
            d.ellipse([rx - 28, ry - 45, rx + 28, ry + 45], fill=color)

    elif aid == "bing_ice":
        for bx, by in [(390, 340), (630, 620)]:
            d.polygon([(bx, by - 140), (bx + 90, by), (bx, by + 140), (bx - 90, by)], fill=color)
            d.polygon([(bx, by - 80), (bx + 50, by), (bx, by + 80), (bx - 50, by)], fill=MINT)

    elif aid == "tian_field":
        d.rounded_rectangle([240, 240, 784, 784], radius=36, fill=color, outline=CHARCOAL, width=48)
        d.line([(cx, 240), (cx, 784)], fill=CHARCOAL, width=40)
        d.line([(240, cy), (784, cy)], fill=CHARCOAL, width=40)

    elif aid == "dao_knife":
        d.polygon([(270, 640), (640, 220), (740, 290), (410, 740)], fill=color)
        d.rounded_rectangle([220, 650, 390, 790], radius=24, fill=TERRACOTTA)

    elif aid == "gong_tool":
        d.rounded_rectangle([240, 240, 784, 340], radius=24, fill=color)
        d.rectangle([cx - 50, 320, cx + 50, 700], fill=MUSTARD)
        d.rounded_rectangle([210, 680, 814, 784], radius=24, fill=color)

    elif aid == "yi_cloth":
        d.polygon([(220, 320), (390, 230), (cx, 340), (634, 230), (804, 320), (740, 480), (650, 450), (650, 790), (374, 790), (374, 450), (284, 480)], fill=color)
        d.polygon([(410, 235), (cx, 355), (614, 235)], fill=CHARCOAL)

    elif aid == "si_silk":
        d.arc([290, 220, 690, 560], 0, 360, fill=color, width=46)
        d.arc([340, 430, 730, 790], 0, 360, fill=TERRACOTTA, width=46)

    elif aid == "shi_arrow":
        d.line([(260, 760), (710, 310)], fill=color, width=48)
        d.polygon([(770, 250), (610, 280), (740, 410)], fill=TERRACOTTA)
        d.line([(240, 640), (380, 780)], fill=FOREST, width=38)

    elif aid == "li_stand":
        d.ellipse([cx - 65, 190, cx + 65, 320], fill=TERRACOTTA)
        d.line([(260, 370), (764, 370)], fill=color, width=46)
        d.line([(390, 410), (430, 720)], fill=color, width=42)
        d.line([(634, 410), (594, 720)], fill=color, width=42)
        d.line([(210, 750), (814, 750)], fill=color, width=52)

    elif aid == "yi_one":
        for y, c_bar in [(300, color), (512, TERRACOTTA), (724, color)]:
            d.rounded_rectangle([220, y - 34, 804, y + 34], radius=34, fill=c_bar)

    elif aid == "shi_ten":
        d.rounded_rectangle([210, cy - 48, 814, cy + 48], radius=34, fill=color)
        d.rounded_rectangle([cx - 48, 210, cx + 48, 814], radius=34, fill=CHARCOAL)

    elif aid == "ba_divide":
        d.polygon([(390, 250), (465, 250), (305, 760), (220, 725)], fill=color)
        d.polygon([(559, 250), (634, 250), (804, 725), (719, 760)], fill=CHARCOAL)

    elif aid == "da_big":
        d.ellipse([cx - 75, 185, cx + 75, 335], fill=color)
        d.rounded_rectangle([200, 365, 824, 445], radius=38, fill=color)
        d.polygon([(cx - 35, 380), (cx + 35, 380), (260, 810), (190, 770)], fill=CHARCOAL)
        d.polygon([(cx - 35, 380), (cx + 35, 380), (834, 770), (764, 810)], fill=CHARCOAL)

    elif aid == "xiao_small":
        d.ellipse([cx - 65, 260, cx + 65, 760], fill=color)
        d.ellipse([230, 440, 355, 620], fill=TERRACOTTA)
        d.ellipse([669, 440, 794, 620], fill=TERRACOTTA)

    elif aid == "xi_evening":
        d.ellipse([300, 220, 740, 760], fill=color)
        d.ellipse([430, 260, 840, 740], fill=(250, 246, 240))
        d.line([(400, 420), (540, 540)], fill=CHARCOAL, width=42)

    elif aid == "zi_nose":
        d.polygon([(cx - 40, 240), (cx + 40, 240), (cx + 125, 620), (cx - 125, 620)], fill=(214, 198, 178))
        d.rounded_rectangle([320, 310, 704, 650], radius=24, outline=CHARCOAL, width=42)
        d.arc([520, 560, 830, 760], -30, 140, fill=color, width=28)

    elif aid == "qi_steam":
        for wy in (310, 490, 670):
            d.arc([230, wy - 70, 520, wy + 70], 180, 360, fill=color, width=38)
            d.arc([504, wy - 70, 794, wy + 70], 0, 180, fill=MINT, width=38)

    elif aid == "gui_jade":
        d.polygon([(cx, 200), (770, 420), (cx, 820), (254, 420)], fill=color, outline=CHARCOAL, width=32)
        d.polygon([(cx, 290), (650, 420), (cx, 720), (374, 420)], fill=(255, 245, 210))

    elif aid == "shi_pig":
        d.ellipse([260, 340, 764, 720], fill=color)
        d.ellipse([420, 480, 604, 620], fill=BLUSH)
        d.ellipse([465, 530, 495, 565], fill=CHARCOAL)
        d.ellipse([530, 530, 560, 565], fill=CHARCOAL)
        d.polygon([(310, 400), (260, 240), (410, 340)], fill=color)
        d.polygon([(714, 400), (764, 240), (614, 340)], fill=color)

    elif aid == "fu_father":
        d.ellipse([cx - 75, 190, cx + 75, 340], fill=TERRACOTTA)
        d.line([(290, 390), (734, 760)], fill=color, width=54)
        d.line([(734, 390), (290, 760)], fill=color, width=54)

    elif aid == "gu_drum":
        d.ellipse([270, 280, 754, 460], fill=MUSTARD, outline=CHARCOAL, width=28)
        d.rectangle([270, 370, 754, 670], fill=color, outline=CHARCOAL, width=28)
        d.ellipse([270, 580, 754, 760], fill=color, outline=CHARCOAL, width=28)
        d.line([(210, 220), (450, 370)], fill=CHARCOAL, width=28)
        d.line([(814, 220), (574, 370)], fill=CHARCOAL, width=28)

    elif aid == "jing_tower":
        d.polygon([(260, 380), (cx, 200), (764, 380)], fill=TERRACOTTA)
        d.rectangle([340, 380, 684, 540], fill=color)
        d.polygon([(220, 560), (cx, 440), (804, 560)], fill=TERRACOTTA)
        d.rectangle([300, 560, 724, 780], fill=color)
        d.rectangle([cx - 55, 640, cx + 55, 780], fill=MUSTARD)

    elif aid == "fu_mound":
        d.arc([230, 240, 660, 550], 270, 90, fill=color, width=54)
        d.arc([230, 490, 720, 800], 270, 90, fill=color, width=54)
        d.line([(330, 240), (330, 810)], fill=CHARCOAL, width=54)

    return im.resize((512, 512), Image.Resampling.LANCZOS)


def build_sprites_and_catalog() -> list[dict]:
    chars_path = WORKDIR / "hsk1_characters.json"
    char_usage: dict[str, list[str]] = {}
    if chars_path.exists():
        for c in json.loads(chars_path.read_text(encoding="utf-8")):
            for aid in c.get("actor_ids", []):
                char_usage.setdefault(aid, []).append(c["char"])

    f_cjk_big = ImageFont.truetype(FONT_CJK, 140, index=0)
    f_title = ImageFont.truetype(FONT_LATIN, 56, index=6)
    f_pill = ImageFont.truetype(FONT_LATIN, 28, index=6)
    f_sub = ImageFont.truetype(FONT_LATIN, 34, index=0)
    f_cjk_sub = ImageFont.truetype(FONT_CJK, 36, index=0)

    catalog = []
    for idx, (aid, radical, actor_name, keyword, role_group, color, desc) in enumerate(ACTOR_DEFS, start=1):
        sprite = draw_sprite_motif(aid, color)
        sprite_path = SPRITES_DIR / f"{aid}.png"
        sprite.save(sprite_path)

        # Build 1080x1920 showcase sprite card
        card = Image.new("RGB", (1080, 1920), BG_COLOR)
        d = ImageDraw.Draw(card)
        # Top pill
        pill_txt = f"ACTOR SPRITE #{idx} · {role_group.upper()}"
        bb_p = d.textbbox((0, 0), pill_txt, font=f_pill)
        pw = (bb_p[2] - bb_p[0]) + 68
        d.rounded_rectangle([(1080 - pw) // 2, 85, (1080 + pw) // 2, 150], radius=32, fill=color)
        d.text(((1080 - (bb_p[2] - bb_p[0])) // 2 - bb_p[0], 117 - (bb_p[3] - bb_p[1]) // 2 - bb_p[1]), pill_txt, font=f_pill, fill=(255, 255, 255))

        # Radical & Name
        bb_r = d.textbbox((0, 0), radical, font=f_cjk_big)
        d.text(((1080 - (bb_r[2] - bb_r[0])) // 2 - bb_r[0], 190 - bb_r[1]), radical, font=f_cjk_big, fill=CHARCOAL)
        bb_t = d.textbbox((0, 0), f"{actor_name}  ({keyword})", font=f_title)
        d.text(((1080 - (bb_t[2] - bb_t[0])) // 2 - bb_t[0], 370 - bb_t[1]), f"{actor_name}  ({keyword})", font=f_title, fill=color)

        # Paste 720x720 sprite in center
        big_sprite = sprite.resize((720, 720), Image.Resampling.LANCZOS)
        card.paste(big_sprite, (180, 520), big_sprite)

        # Bottom card
        d.rounded_rectangle([68, 1340, 1012, 1820], radius=36, fill=CARD_BG, outline=CARD_BORDER, width=3)
        used_chars = char_usage.get(aid, [])
        used_str = " ".join(used_chars[:20]) + ("…" if len(used_chars) > 20 else "")
        # Wrap description simply
        words = desc.split()
        lines = []
        cur = ""
        for w in words:
            cand = f"{cur} {w}".strip()
            if d.textbbox((0, 0), cand, font=f_sub)[2] <= 840:
                cur = cand
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        y_txt = 1410
        for ln in lines[:3]:
            bb_l = d.textbbox((0, 0), ln, font=f_sub)
            d.text(((1080 - (bb_l[2] - bb_l[0])) // 2 - bb_l[0], y_txt - bb_l[1]), ln, font=f_sub, fill=CHARCOAL)
            y_txt += 52
        if used_chars:
            hdr = f"Dipakai konsisten pada {len(used_chars)} karakter:"
            bb_h = d.textbbox((0, 0), hdr, font=f_pill)
            d.text(((1080 - (bb_h[2] - bb_h[0])) // 2 - bb_h[0], 1630 - bb_h[1]), hdr, font=f_pill, fill=FOREST)
            bb_u = d.textbbox((0, 0), used_str, font=f_cjk_sub)
            d.text(((1080 - (bb_u[2] - bb_u[0])) // 2 - bb_u[0], 1690 - bb_u[1]), used_str, font=f_cjk_sub, fill=CHARCOAL)

        card_path = SPRITE_CARDS_DIR / f"{aid}_sprite.png"
        card.save(card_path)

        catalog.append({
            "id": aid,
            "radical": radical,
            "actor_name": actor_name,
            "keyword": keyword,
            "role_group": role_group,
            "color_hex": "#{:02X}{:02X}{:02X}".format(*color),
            "description": desc,
            "sprite_path": f"sprites/{aid}.png",
            "sprite_card_path": f"sprite_cards/{aid}_sprite.png",
            "used_in_chars": used_chars,
            "usage_count": len(used_chars),
        })

    (WORKDIR / "actors_catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Generated {len(catalog)} Actor Sprites -> sprites/, sprite_cards/, actors_catalog.json")
    return catalog


if __name__ == "__main__":
    build_sprites_and_catalog()
