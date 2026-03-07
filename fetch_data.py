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
                # Conversion en objet datetime pour un tri réel
                dt_obj = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')
                
                news_output.append({
                    "id": title + str(dt_obj.timestamp()), 
                    "source": source_name,
                    "text": title,
                    "urgent": any(word in title for word in critical_keywords),
                    "france_related": any(word in title for word in france_keywords),
                    "time": dt_obj.strftime("%H:%M"),
                    "date": dt_obj.strftime("%d/%m"),
                    "timestamp": dt_obj.timestamp() # <--- LE SECRET EST ICI
                })
        except Exception as e:
            print(f"Erreur source {source_name}: {e}")
    return news_output

def get_full_intel():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            current_data = json.load(f)
    else:
        current_data = {"news": [], "impacts": []}

    new_news = get_war_news()
    
    existing_ids = {n.get('id') for n in current_data['news']}
    for n in new_news:
        if n['id'] not in existing_ids:
            current_data['news'].append(n)

    # TRI PAR TIMESTAMP (Le plus grand nombre = le plus récent)
    current_data['news'].sort(key=lambda x: x.get('timestamp', 0), reverse=True)
    
    # On garde les 300 dernières pour l'historique
    current_data['news'] = current_data['news'][:300]

    # ... (Reste du code NASA identique) ...
    current_data["last_update"] = datetime.now().strftime("%d/%m %H:%M")
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(current_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    get_full_intel()
