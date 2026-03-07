import requests
import json
import xml.etree.ElementTree as ET
from datetime import datetime
import os
import email.utils

NASA_KEY = "3a967f64858b76c839f9b5a805a50785"
AREA = "20,10,65,45"
DATA_FILE = 'data.json'

def get_war_news():
    news_output = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    sources = {
        "OPEX360": "https://www.opex360.com/feed/",
        "BFMTV": "https://www.bfmtv.com/rss/international/"
    }

    critical_keywords = ["GUERRE", "EXPLOSION", "FRAPPE", "MISSILE", "IRAN", "ISRAËL", "DRONE", "ATTAQUE", "URGENT"]
    france_keywords = ["FRANCE", "FRANÇAIS", "MARINE NATIONALE", "EMA"]

    for name, url in sources.items():
        try:
            r = requests.get(url, headers=headers, timeout=15)
            root = ET.fromstring(r.content)
            for item in root.findall('./channel/item')[:15]:
                title = item.find('title').text
                pub_date_raw = item.find('pubDate').text
                
                # --- EXTRACTION DU TEMPS RÉEL DE PUBLICATION ---
                # Convertit la date RSS (ex: Sat, 07 Mar 2026 10:51:00 +0100) en objet datetime
                parsed_date = email.utils.parsedate_to_datetime(pub_date_raw)
                
                time_val = parsed_date.strftime("%H:%M")
                date_val = parsed_date.strftime("%d/%m")
                timestamp_val = int(parsed_date.timestamp())
                
                news_output.append({
                    "id": f"{name}_{timestamp_val}", # ID unique basé sur la source et le temps réel
                    "source": name,
                    "text": title.upper(),
                    "urgent": any(w in title.upper() for w in critical_keywords),
                    "france_related": any(w in title.upper() for w in france_keywords),
                    "time": time_val,
                    "date": date_val,
                    "timestamp": timestamp_val
                })
        except Exception as e:
            print(f"Erreur sur la source {name}: {e}")
            continue
    return news_output

def get_full_intel():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                current_data = json.load(f)
        except: current_data = {"news": []}
    else: current_data = {"news": []}

    live_news = get_war_news()
    
    # Fusion sans doublons basée sur le texte de la news
    existing_texts = [n['text'] for n in current_data.get('news', [])]
    for n in live_news:
        if n['text'] not in existing_texts:
            current_data['news'].append(n)

    # TRI CHRONOLOGIQUE : Basé sur le timestamp réel (le plus récent en haut)
    current_data['news'].sort(key=lambda x: x.get('timestamp', 0), reverse=True)

    # Limitation aux 100 dernières entrées pour les archives
    current_data['news'] = current_data['news'][:100]

    # SCAN NASA (Signatures thermiques)
    impacts = []
    try:
        r_nasa = requests.get(f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{NASA_KEY}/VIIRS_SNPP_NRT/{AREA}/1", timeout=10)
        if r_nasa.status_code == 200:
            lines = r_nasa.text.strip().split('\n')[1:]
            for line in lines:
                c = line.split(',')
                if len(c) > 6:
                    impacts.append({
                        "lat": float(c[0]), 
                        "lng": float(c[1]), 
                        "time": f"{c[6][:2]}:{c[6][2:]}"
                    })
    except Exception as e:
        print(f"Erreur NASA: {e}")

    # Mise à jour globale du JSON
    current_data.update({
        "last_update": datetime.now().strftime("%d/%m %H:%M"),
        "impacts": impacts,
        "emergency": len(impacts) > 15,
        "france": {
            "forces": [
                {"n": "BAP Jordanie", "p": [32.16, 37.14], "t": "Base Aérienne", "s": "RAFALE OPS"},
                {"n": "BA 188 Djibouti", "p": [11.54, 43.15], "t": "Point d'Appui", "s": "VIGILANCE"},
                {"n": "BN Abu Dhabi", "p": [24.52, 54.37], "t": "Soutien Naval", "s": "ALINDIEN"}
            ]
        }
    })
    
    # Sauvegarde
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(current_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    get_full_intel()
