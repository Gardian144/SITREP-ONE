import requests, json, xml.etree.ElementTree as ET
from datetime import datetime
import os

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

    critical_keywords = ["GUERRE", "EXPLOSION", "FRAPPE", "MISSILE", "IRAN", "ISRAËL", "DRONE", "ATTAQUE", "NUCLÉAIRE", "URGENT"]
    france_keywords = ["FRANCE", "FRANÇAIS", "MARINE NATIONALE", "ARMÉE DE L'AIR", "EMA"]

    for source_name, url in sources.items():
        try:
            r = requests.get(url, headers=headers, timeout=10)
            root = ET.fromstring(r.content)
            for item in root.findall('./channel/item')[:15]:
                title = item.find('title').text.upper()
                
                if source_name == "BFMTV" and not any(w in title for w in critical_keywords):
                    continue

                pub_date = item.find('pubDate').text
                # Conversion robuste
                dt_obj = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')
                
                news_output.append({
                    "id": title + str(dt_obj.timestamp()), 
                    "source": source_name,
                    "text": title,
                    "urgent": any(word in title for word in critical_keywords),
                    "france_related": any(word in title for word in france_keywords),
                    "time": dt_obj.strftime("%H:%M"),
                    "date": dt_obj.strftime("%d/%m"),
                    "timestamp": dt_obj.timestamp() 
                })
        except Exception as e:
            print(f"Erreur source {source_name}: {e}")
    return news_output

def get_full_intel():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                current_data = json.load(f)
        except:
            current_data = {"news": [], "impacts": []}
    else:
        current_data = {"news": [], "impacts": []}

    new_news = get_war_news()
    
    # Fusion sans doublons
    existing_ids = {n.get('id') for n in current_data['news'] if n.get('id')}
    for n in new_news:
        if n['id'] not in existing_ids:
            current_data['news'].append(n)

    # NETTOYAGE : Supprime les entrées corrompues qui n'ont pas de timestamp
    current_data['news'] = [n for n in current_data['news'] if n.get('timestamp')]

    # TRI : Plus récent en haut
    current_data['news'].sort(key=lambda x: x.get('timestamp', 0), reverse=True)
    current_data['news'] = current_data['news'][:300]

    # Données NASA
    impacts = []
    try:
        url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{NASA_KEY}/VIIRS_SNPP_NRT/{AREA}/1"
        r = requests.get(url, timeout=15)
        lines = r.text.strip().split('\n')[1:]
        for line in lines:
            c = line.split(',')
            impacts.append({"lat": float(c[0]), "lng": float(c[1]), "time": f"{c[6][:2]}:{c[6][2:]}"})
    except: pass

    current_data["last_update"] = datetime.now().strftime("%d/%m %H:%M")
    current_data["impacts"] = impacts
    current_data["france"] = {
        "forces": [
            {"n": "BAP Jordanie", "p": [32.16, 37.14], "t": "Base Aérienne", "s": "RAFALE OPS"},
            {"n": "BA 188 Djibouti", "p": [11.54, 43.15], "t": "Point d'Appui", "s": "VIGILANCE"},
            {"n": "BN Abu Dhabi", "p": [24.52, 54.37], "t": "Soutien Naval", "s": "ALINDIEN"}
        ]
    }
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(current_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    get_full_intel()
