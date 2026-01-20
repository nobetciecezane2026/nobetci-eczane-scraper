from fastapi import FastAPI
import json

app = FastAPI()

@app.get("/eczane/{city}")
def get_city(city: str):
    try:
        with open("data/eczaneler.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        return {"error": "Veri dosyası bulunamadı"}

    city = city.capitalize()

    if city in data:
        return {"city": city, "eczaneler": data[city]}

    return {"error": "Şehir bulunamadı"}
