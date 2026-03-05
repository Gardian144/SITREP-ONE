import requests, json, xml.etree.ElementTree as ET
from datetime import datetime

NASA_KEY = "3a967f64858b76c839f9b5a805a50785"
AREA = "20,10,65,45"

def get_war_news():
    """Récupère les dépêches militaires réelles (Opex360)"""
    news_list = []
    headers = {'User-Agent': 'Mozilla/5.0'} # Pour éviter le blocage GitHub
    try:
        # Flux de Zone Militaire (très réactif sur les conflits)
        rss_url = "https://www.opex360.com/feed/"
        r = requests.get(rss_url, headers=headers, timeout=15)
        root = ET.fromstring(r.content)
        
        for item in root.findall('./channel/item')[:12]:
            title = item.find('title').text
            # On formate pour que ça claque sur l'interface
            news_list.append(f"FLASH_INFO : {title.upper()}")
    except Exception as e:
        # Flux de secours si le premier tombe
        news_list = ["ALERTE : MISE À JOUR DU FLUX TACTIQUE EN COURS..."]
    return news_list

def get_full_intel():
    # 1. IMPACTS NASA (Les points rouges sur la carte)
    impacts = []
    try:
        url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{NASA_KEY}/VIIRS_SNPP_NRT/{AREA}/1"
        r = requests.get(url, timeout=15)
        lines = r.text.strip().split('\n')[1:]
        for line in lines:
            c = line.split(',')
            impacts.append({"lat": float(c[0]), "lng": float(c[1]), "time": f"{c[6][:2]}:{c[6][2:]}"})
    except: pass

    # 2. NEWS RÉELLES
    live_news = get_war_news()
    
    # 3. DISPOSITIF FRANCE (On garde tes bases stratégiques)
    france_db = {
        "exercices": [
            "OPÉRATION CHAMMAL : Appui aérien quotidien Irak/Syrie.",
            "MISSION AGÉNOR : Surveillance du détroit d'Ormuz.",
            "VIGIPIRATE : Niveau Urgence Attentat maintenu."
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
