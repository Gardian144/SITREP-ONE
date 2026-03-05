import requests, json, xml.etree.ElementTree as ET
from datetime import datetime

NASA_KEY = "3a967f64858b76c839f9b5a805a50785"
AREA = "20,10,65,45"

def get_live_news():
    """Récupère les dernières dépêches internationales en temps réel"""
    news_list = []
    try:
        # Flux France 24 - Actualités Internationales
        rss_url = "https://www.france24.com/fr/actualites/rss"
        r = requests.get(rss_url, timeout=10)
        root = ET.fromstring(r.content)
        
        for item in root.findall('./channel/item')[:10]: # On prend les 10 dernières
            title = item.find('title').text
            # On filtre un peu pour garder le côté "SITREP"
            news_list.append(f"BREAKING : {title.upper()}")
    except Exception as e:
        news_list = ["ERREUR : Liaison agence de presse interrompue"]
    return news_list

def get_full_intel():
    # 1. IMPACTS NASA
    impacts = []
    try:
        url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{NASA_KEY}/VIIRS_SNPP_NRT/{AREA}/1"
        r = requests.get(url, timeout=15)
        lines = r.text.strip().split('\n')[1:]
        for line in lines:
            c = line.split(',')
            impacts.append({"lat": float(c[0]), "lng": float(c[1]), "time": f"{c[6][:2]}:{c[6][2:]}"})
    except: pass

    # 2. NEWS RÉELLES (Flux Agence)
    live_news = get_live_news()
    
    # 3. DISPOSITIF FRANCE (Statique mais précis)
    france_db = {
        "exercices": [
            "OPÉRATION CHAMMAL : Appui aérien quotidien Irak/Syrie.",
            "MISSION AGÉNOR : Surveillance du détroit d'Ormuz.",
            "FFDJ : Alerte renforcée sur le corridor Mer Rouge."
        ],
        "forces": [
            {"n": "BAP Jordanie", "p": [32.16, 37.14], "t": "Base Aérienne", "s": "RAFALE OPS"},
            {"n": "BA 188 Djibouti", "p": [11.54, 43.15], "t": "Point d'Appui", "s": "VIGILANCE"},
            {"n": "BN Abu Dhabi", "p": [24.52, 54.37], "t": "Soutien Naval", "s": "ALINDIEN"}
        ]
    }

    output = {
        "last_update": datetime.now().strftime("%d/%m %H:%M"),
        "impacts": impacts,
        "news": live_news, 
        "france": france_db,
        "emergency": len(impacts) > 15
    }
    
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    get_full_intel()
