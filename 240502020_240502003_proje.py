import random
import json
import os

MAX_HATA = 6
PUAN_DOGRU_HARF = 10
PUAN_YANLIS_HARF = -5
PUAN_DOGRU_ISLEM = 15
PUAN_YANLIS_ISLEM = -10
PUAN_KAZANMA = 50
PUAN_KAYBETME = -20

KELIMELER = {
    "meyve": ["elma", "armut", "muz", "çilek", "portakal"],
    "hayvan": ["kedi", "köpek", "aslan", "kuş", "tilki"],
    "teknoloji": ["ekran", "klavye", "internet", "yazılım"],
    "şehir": ["ankara", "istanbul", "izmir", "bursa", "antalya"],
    "renk": ["kırmızı", "mavi", "yeşil", "sarı", "mor"],
    "eşya": ["masa", "sandalye", "lamba", "kalem", "bilgisayar"],
    "ülke": ["türkiye", "japonya", "almanya", "fransa", "kanada"],
    "spor": ["futbol", "basketbol", "voleybol", "tenis"]
}

HANGMAN = [
    "+---+\n|   |\n    |\n    |\n    |\n=====",
    "+---+\n|   |\nO   |\n    |\n    |\n=====",
    "+---+\n|   |\nO   |\n|   |\n    |\n=====",
    "+---+\n|   |\nO   |\n/|  |\n    |\n=====",
    "+---+\n|   |\nO   |\n/|\\ |\n    |\n=====",
    "+---+\n|   |\nO   |\n/|\\ |\n/    |\n=====",
    "+---+\n|   |\nO   |\n/|\\ |\n/ \\  |\n====="
]

def skor_yukle():
    if not os.path.exists("scores.json"):
        return []
    try:
        with open("scores.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def skor_kaydet(isim, skor):
    kayitlar = skor_yukle()
    kayitlar.append({"isim": isim, "skor": skor})
    kayitlar = sorted(kayitlar, key=lambda x: x["skor"], reverse=True)[:5]
    with open("scores.json", "w", encoding="utf-8") as f:
        json.dump(kayitlar, f, ensure_ascii=False, indent=2)

def durum_goster(maskeli, tahminler, hata, bonus, kullanilan):
    print(HANGMAN[hata])
    print("Kelime:", " ".join(maskeli))
    print("Tahmin edilen harfler:", ", ".join(sorted(tahminler)) if tahminler else "-")
    print("Kalan hata hakkı:", MAX_HATA - hata)
    print("Bonus puan:", bonus)
    kalan = [i for i, v in kullanilan.items() if not v]
    print("Kalan işlemler:", ", ".join(kalan) if kalan else "YOK")

def harf_al():
    h = input("Harf gir: ").lower().strip()
    if len(h) != 1 or not h.isalpha():
        print("Sadece tek harf gir.")
        return None
    return h

def islem_al(kullanilan):
    kalan = [i for i, v in kullanilan.items() if not v]
    if not kalan:
        print("Kullanılacak işlem kalmadı.")
        return None, None, None
    print("Kalan işlemler:", ", ".join(kalan))
    islem = input("İşlem seç veya 'iptal' yaz: ").lower().strip()
    if islem == "iptal":
        return None, None, None
    if islem not in kalan:
        print("Bu işlem kullanılamaz.")
        return None, None, None
    try:
        a = float(input("Sayı 1: "))
        b = float(input("Sayı 2: "))
    except:
        print("Sayı girmelisin.")
        return None, None, None
    return islem, a, b

def islem_kontrol(islem, a, b):
    if islem == "bolme" and b == 0:
        print("0'a bölünmez!")
        return False
    if islem == "toplama":
        beklenen = a + b
    elif islem == "cikarma":
        beklenen = a - b
    elif islem == "carpma":
        beklenen = a * b
    else:
        beklenen = a / b
    try:
        sonuc = float(input("Sonucu yaz: "))
    except:
        return False
    return abs(sonuc - beklenen) <= 1e-6

def rastgele_harf_ac(kelime, maskeli):
    kapali = [i for i, h in enumerate(maskeli) if h == "_"]
    if kapali:
        i = random.choice(kapali)
        maskeli[i] = kelime[i]
    return maskeli

def oyun():
    kategori = random.choice(list(KELIMELER.keys()))
    kelime = random.choice(KELIMELER[kategori])
    maskeli = ["_" for _ in kelime]
    tahminler = set()
    kullanilan_islemler = {"toplama": False, "cikarma": False, "carpma": False, "bolme": False}
    hata = 0
    bonus = 0
    skor = 0

    print("=== Calc & Hang - İşlem Yap, Harfi Kurtar ===")

    while True:
        durum_goster(maskeli, tahminler, hata, bonus, kullanilan_islemler)

        if "_" not in maskeli:
            print("Tebrikler! Kelime:", kelime)
            skor += PUAN_KAZANMA
            print("Skor:", skor)
            isim = input("Skor kaydetmek için isim: ").strip()
            if isim:
                skor_kaydet(isim, skor)
            break

        if hata >= MAX_HATA:
            print("Kaybettin! Kelime:", kelime)
            skor += PUAN_KAYBETME
            print("Skor:", skor)
            isim = input("Skor kaydetmek için isim: ").strip()
            if isim:
                skor_kaydet(isim, skor)
            break

        print("\nSeçenekler: [H]arf tahmini | [İ]şlem çöz | [P]pucu | [C]ıkış")
        secim = input("Seçiminiz: ").lower().strip()

        if secim == "h":
            h = harf_al()
            if not h:
                continue
            if h in tahminler:
                print("Bu harfi zaten denedin.")
                continue
            tahminler.add(h)
            if h in kelime:
                skor += PUAN_DOGRU_HARF
                for i, c in enumerate(kelime):
                    if c == h:
                        maskeli[i] = h
            else:
                skor += PUAN_YANLIS_HARF
                hata += 1

        elif secim == "i":
            islem, a, b = islem_al(kullanilan_islemler)
            if not islem:
                continue
            kullanilan_islemler[islem] = True
            if islem_kontrol(islem, a, b):
                skor += PUAN_DOGRU_ISLEM
                bonus += 1
                maskeli = rastgele_harf_ac(kelime, maskeli)
            else:
                skor += PUAN_YANLIS_ISLEM
                hata += 1

        elif secim == "p":
            if bonus <= 0:
                print("Yeterli bonus yok.")
            else:
                bonus -= 1
                print("İpucu (Kategori):", kategori)

        elif secim == "c":
            print("Çıkış yapıldı. Skor:", skor)
            break

        else:
            print("Geçersiz seçim.")

if __name__ == "__main__":
    while True:
        oyun()
        if input("Yeniden oyna? (e/h): ").lower().strip() != "e":
            break
