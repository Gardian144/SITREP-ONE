import requests, json, xml.etree.ElementTree as ET
from datetime import datetime
import os
import time

NASA_KEY = "3a967f64858b76c839f9b5a805a50785"
AREA = "20,10,65,45"
DATA_FILE = 'data.json'

def get_war_news():
    news_output = []
    # On ajoute un paramètre aléatoire à l'URL pour forcer BFMTV à nous donner le frais
    timestamp_url = int(time.time())
    sources = {
        "OPEX360": f"https://www.opex360.com/feed/?v={timestamp_url}",
        "BFMTV": f"https://www.bfmtv.com/rss/international/?v={timestamp_url}"
    }
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    # Élargissement des mots-clés pour ne rien rater d'important
    critical_keywords = ["GUERRE", "EXPLOSION", "FRAPPE", "MISSILE", "IRAN", "ISRAËL", "DRONE", "ATTAQUE", "NUCLÉAIRE", "URGENT", "CONFLIT", "ARME", "TENSION", "MILITAIRE", "STRIPE"]
    france_keywords = ["FRANCE", "FRANÇAIS", "MARINE NATIONALE", "ARMÉE DE L'AIR", "EMA", "PARIS", "LECORNU"]

    for source_name, url in sources.items():
        try:
            r = requests.get(url, headers=headers, timeout=15)
            r.encoding = 'utf-8'
            root = ET.fromstring(r.text)
            
            # On passe à 30 items au lieu de 15 pour être sûr de remonter assez loin
            for item in root.findall('./channel/item')[:30]:
                title = item.find('title').text.upper()
                pub_date = item.find('pubDate').text
                
                # Conversion Date
                try:
                    dt_obj = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')
                except:
                    continue # Skip si format date illisible

                is_urgent = any(word in title for word in critical_keywords)
                
                # BFMTV est très pollué, on ne garde que le critique. 
                # OPEX360 est 100% militaire, on garde TOUT.
                if source_name == "BFMTV" and not is_urgent:
                    continue

                news_output.append({
                    "id": f"{source_name}_{dt_obj.timestamp()}", # ID plus fiable
                    "source": source_name,
                    "text": title,
                    "urgent": is_urgent,
                    "france_related": any(word in title for word in france_keywords),
                    "time": dt_obj.strftime("%H:%M"),
                    "date": dt_obj.strftime("%d/%m"),
                    "timestamp": dt_obj.timestamp() 
                })
        except Exception as e:
            print(f"Erreur source {source_name}: {e}")
    return news_output

def get_full_intel():
    # Chargement propre
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except: data = {"news": [], "impacts": []}
    else: data = {"news": [], "impacts": []}

    # On récupère le neuf
    fresh_news = get_war_news()
    
    # Fusion par ID pour éviter les doublons mais garder l'historique
    existing_ids = [n.get('id') for n in data['news']]
    added_count = 0
    for n in fresh_news:
        if n['id'] not in existing_ids:
            data['news'].append(n)
            added_count += 1

    # NETTOYAGE & TRI
    # 1. On vire les vieux trucs ou les trucs cassés
    data['news'] = [n for n in data['news'] if n.get('timestamp')]
    
    # 2. Tri CHRONOLOGIQUE STRICT (Le plus récent en premier)
    data['news'].sort(key=lambda x: x['timestamp'], reverse=True)
    
    # 3. On garde les 200 dernières news
    data['news'] = data['news'][:200]

    # Données NASA (inchangé mais sécurisé)
    try:
        url_nasa = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{NASA_KEY}/VIIRS_SNPP_NRT/{AREA}/1"
        res = requests.get(url_nasa, timeout=10)
        if "latitude" in res.text:
            lines = res.text.strip().split('\n')[1:]
            data["impacts"] = []
            for line in lines:
                c = line.split(',')
                data["impacts"].append({"lat": float(c[0]), "lng": float(c[1]), "time": f"{c[6][:2]}:{c[6][2:]}"})
    except: pass

    data["last_update"] = datetime.now().strftime("%d/%m %H:%M")
    
    # Sauvegarde
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Update terminé. {added_count} nouvelles news intégrées.")

if __name__ == "__main__":
    get_full_intel()
