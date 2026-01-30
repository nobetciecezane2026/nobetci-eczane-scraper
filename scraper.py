import requests
from bs4 import BeautifulSoup
import json
import time
import re
import os

# Tüm URL'leri oku
try:
    with open("urls.json", "r", encoding="utf-8") as f:
        URLS = json.load(f)
except Exception as e:
    print(f"[-] urls.json okuma hatası: {e}")
    URLS = {}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def clean(t):
    return " ".join(t.split()).strip()

def extract_ilce(address, city):
    """Adres içinden ilçe bilgisini ayıklar (Örn: Seyhan / Adana -> Seyhan)"""
    if "/" in address:
        parts = address.split("/")
        # Genelde 'İlçe / İl' formatında olur, sondan ikinciyi al
        if len(parts) >= 2:
            potential = parts[-2].strip().split()[-1]
            if potential.upper() != city.upper():
                return potential
    return ""

def scrape_city(city, url):
    print(f"[+] {city} çekiliyor: {url}")
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.encoding = 'utf-8' # Türkçe karakter sorunlarını önler
        if r.status_code != 200: return []
    except:
        return []

    soup = BeautifulSoup(r.text, "lxml")
    
    # Metni satırlara böl ve temizle
    lines = [clean(l) for l in soup.get_text("\n").split("\n") if clean(l)]
    
    pharmacies = []
    current = None

    for line in lines:
        # 1. ECZANE ADI TESPİTİ (Genelde büyük harf ve 'ECZANESİ' içerir)
        if "ECZANESİ" in line.upper() and len(line) < 60:
            if current and current["name"]:
                pharmacies.append(current)
            
            current = {
                "name": line,
                "ilce": "",
                "address": "",
                "phone": ""
            }
            continue

        if current:
            # 2. TELEFON TESPİTİ (Rakam kontrolü ile)
            digits = "".join(filter(str.isdigit, line))
            if (len(digits) >= 10) and not current["phone"]:
                current["phone"] = digits
                continue

            # 3. ADRES TESPİTİ (İçinde Mah, Cad, Sok gibi anahtarlar veya / işareti varsa)
            keywords = ["Mah", "Cad", "Sok", "No:", "Bulv", "Yol", "/", city.title()]
            if any(k in line for k in keywords) and not current["address"]:
                current["address"] = line
                current["ilce"] = extract_ilce(line, city)
                continue

    if current and current["name"]:
        pharmacies.append(current)

    return pharmacies

all_data = {}

for city, meta in URLS.items():
    if meta.get("scrape") is False:
        continue
    
    data = scrape_city(city, meta["url"])
    if data:
        all_data[city] = data
    time.sleep(2) # Siteyi engellenmemek için bekle

# Veriyi kaydet
os.makedirs("data", exist_ok=True)
with open("data/eczaneler.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print(f"\n[✓] Bitti -> {len(all_data)} şehir verisi kaydedildi.")
