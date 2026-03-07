import requests, json, xml.etree.ElementTree as ET
from datetime import datetime
import os
import time

DATA_FILE = 'data.json'
NASA_KEY = "3a967f64858b76c839f9b5a805a50785"
AREA = "20,10,65,45"

def get_war_news():
    news_output = []
    t = int(time.time())
    # URLs avec "Cache-Buster" pour forcer la mise à jour
    sources = {
        "OPEX360": f"https://www.opex360.com/feed/?t={t}",
        "BFMTV": f"https://www.bfmtv.com/rss/international/?t={t}"
    }
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    for source_name, url in sources.items():
        try:
            r = requests.get(url, headers=headers, timeout=15)
            r.encoding = 'utf-8'
            root = ET.fromstring(r.text)
            
            for item in root.findall('./channel/item')[:25]:
                title = item.find('title').text.upper()
                pub_date = item.find('pubDate').text
                
                # Conversion Date
                try:
                    dt_obj = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')
                except: continue

                # PAS DE FILTRE ICI : On prend tout pour tester la connexion
                news_output.append({
                    "id": f"{source_name}_{dt_obj.timestamp()}",
                    "source": source_name,
                    "text": title,
                    "urgent": any(word in title for word in ["URGENT", "ALERTE", "GUERRE", "FRAPPE", "MISSILE"]),
                    "france_related": any(word in title for word in ["FRANCE", "FRANÇAIS", "EMA"]),
                    "time": dt_obj.strftime("%H:%M"),
                    "date": dt_obj.strftime("%d/%m"),
                    "timestamp": dt_obj.timestamp() 
                })
        except Exception as e:
            print(f"Erreur {source_name}: {e}")
    return news_output

def run_update():
    # 1. Charger l'existant
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except: data = {"news": [], "impacts": []}
    else: data = {"news": [], "impacts": []}

    # 2. Récupérer le neuf
    new_stuff = get_war_news()
    
    # 3. Fusion sans doublons (basée sur l'ID)
    existing_ids = {n.get('id') for n in data['news']}
    for n in new_stuff:
        if n['id'] not in existing_ids:
            data['news'].append(n)

    # 4. Nettoyage : On ne garde que les news avec un timestamp (virer les 'undefined')
    data['news'] = [n for n in data['news'] if n.get('timestamp')]
    
    # 5. Tri CHRONOLOGIQUE : Le 07/03 doit être au-dessus du 06/03
    data['news'].sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Garder les 100 dernières
    data['news'] = data['news'][:100]

    # Données NASA
    try:
        res = requests.get(f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{NASA_KEY}/VIIRS_SNPP_NRT/{AREA}/1", timeout=10)
        if "latitude" in res.text:
            lines = res.text.strip().split('\n')[1:]
            data["impacts"] = []
            for line in lines:
                c = line.split(',')
                data["impacts"].append({"lat": float(c[0]), "lng": float(c[1]), "time": f"{c[6][:2]}:{c[6][2:]}"})
    except: pass

    data["last_update"] = datetime.now().strftime("%d/%m %H:%M")
    
    # Ajout des données France statiques si absentes
    data["france"] = {
        "forces": [
            {"n": "BAP Jordanie", "p": [32.16, 37.14], "t": "Base Aérienne", "s": "RAFALE OPS"},
            {"n": "BA 188 Djibouti", "p": [11.54, 43.15], "t": "Point d'Appui", "s": "VIGILANCE"},
            {"n": "BN Abu Dhabi", "p": [24.52, 54.37], "t": "Soutien Naval", "s": "ALINDIEN"}
        ]
    }

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    run_update()
