import requests
from bs4 import BeautifulSoup
import json
import time

# Tüm URL'leri oku
with open("urls.json", "r", encoding="utf-8") as f:
    URLS = json.load(f)

headers = {
    "User-Agent": "Mozilla/5.0"
}

def clean(t):
    return t.replace("\n", " ").replace("\t", " ").strip()

def scrape_city(city, url):
    print(f"[+] {city} çekiliyor: {url}")
    try:
        r = requests.get(url, headers=headers, timeout=10)
    except:
        print(f"[!] Bağlantı sorunu: {city}")
        return []

    soup = BeautifulSoup(r.text, "lxml")

    text = soup.get_text("\n")
    lines = text.split("\n")

    pharmacies = []
    current = {
        "name": "",
        "address": "",
        "phone": ""
    }

    for line in lines:
        line = clean(line)

        # ECZANE isim yakalama
        if "ECZANESİ" in line.upper() and len(line) < 100:
            if current["name"]:
                pharmacies.append(current)
                current = {"name": "", "address": "", "phone": ""}

            current["name"] = line

        # Adres çekme
        if "Adres" in line or "adres" in line or "No:" in line:
            if current["address"] == "":
                current["address"] = line

        # Telefon numarası çekme
        if "Tel" in line or "Telefon" in line:
            digits = ''.join(filter(str.isdigit, line))
            current["phone"] = digits

    if current["name"]:
        pharmacies.append(current)

    return pharmacies

all_data = {}

# Sadece HTML kazıyıcı "Evet" olan illeri kullanacağız
for city, meta in URLS.items():
    if meta["scrape"] is False:
        continue

    url = meta["url"]
    all_data[city] = scrape_city(city, url)
    time.sleep(1)

# JSON çıktı kaydı
with open("nobetci_eczane_81il.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print("\n[✓] Bitti → nobetci_eczane_81il.json oluşturuldu.")
