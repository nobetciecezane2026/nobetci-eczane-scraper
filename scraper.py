import requests
from bs4 import BeautifulSoup
import json
import time
import os

with open("urls.json", "r", encoding="utf-8") as f:
    URLS = json.load(f)

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def clean(t):
    return " ".join(t.split()).strip()

def scrape_city(city, url):
    print(f"[+] {city} çekiliyor...")
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.encoding = 'utf-8'
        if r.status_code != 200: return []
    except: return []

    soup = BeautifulSoup(r.text, "lxml")
    lines = [clean(l) for l in soup.get_text("\n").split("\n") if clean(l)]
    
    pharmacies = []
    current = None

    for line in lines:
        # 1. İSİM TESPİTİ
        if "ECZANESİ" in line.upper() and len(line) < 60:
            if current: pharmacies.append(current)
            current = {"name": line, "ilce": "", "address": "", "phone": ""}
            continue

        if current:
            # 2. TELEFON TESPİTİ
            digits = "".join(filter(str.isdigit, line))
            if len(digits) >= 10 and not current["phone"]:
                current["phone"] = digits
                continue
            
            # 3. ADRES VE İLÇE TESPİTİ
            if not current["address"] and len(line) > 10:
                current["address"] = line
                # Akıllı İlçe Ayıklama: "Seyhan / Adana" formatını ara
                if "/" in line:
                    parts = line.split("/")
                    # Eğer / işaretinden sonra şehir adı geçiyorsa, öncesindeki kelime ilçedir
                    if city.upper() in parts[-1].upper():
                        current["ilce"] = parts[-2].strip().split()[-1]

    if current: pharmacies.append(current)
    return pharmacies

all_data = {}
for city, meta in URLS.items():
    if meta.get("scrape") is False: continue
    all_data[city] = scrape_city(city, meta["url"])
    time.sleep(1)

os.makedirs("data", exist_ok=True)
with open("data/eczaneler.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)
