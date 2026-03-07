import requests, json, xml.etree.ElementTree as ET
from datetime import datetime

NASA_KEY = "3a967f64858b76c839f9b5a805a50785"
AREA = "20,10,65,45"

def get_war_news():
    news_output = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    critical_keywords = [
        "GUERRE", "EXPLOSION", "FRAPPE", "MISSILE", "INVASION", "LIBAN", 
        "ISRAËL", "COMBAT", "OFFENSIVE", "ALERTE", "DRONE", "SOUS-MARIN",
        "COULÉ", "NAVIR", "TORPILLE", "ATTAQUE", "FEU", "MORT", "CONFLIT",
        "NUCLÉAIRE", "URGENT", "BREAKING", "TSARHAL", "HEZBOLLAH", "IRAN",
        "BOMBARDEMENT", "FRONT", "SABOTAGE", "BALISTIQUE", "INTERCEPTION"
    ]
    
    france_keywords = ["FRANCE", "FRANÇAIS", "PARIS", "MARINE NATIONALE", "ARMÉE DE L'AIR", "BARKHANE", "CHAMMAL", "VIGIPIRATE", "EMA"]

    try:
        rss_url = "https://www.opex360.com/feed/"
        r = requests.get(rss_url, headers=headers, timeout=15)
        root = ET.fromstring(r.content)
        
        for item in root.findall('./channel/item')[:20]:
            title = item.find('title').text
            # Extraction de l'heure
            pub_date = item.find('pubDate').text
            time_str = pub_date.split(' ')[4][:5] if pub_date else "--:--"
            
            title_upper = title.upper()
            is_urgent = any(word in title_upper for word in critical_keywords)
            is_france = any(word in title_upper for word in france_keywords)
            
            news_output.append({
                "text": title.upper(),
                "urgent": is_urgent,
                "france_related": is_france,
                "time": time_str
            })
            
        news_output.sort(key=lambda x: x['urgent'], reverse=True)
        return news_output
    except Exception:
        return [{"text": "ERREUR SYNC FLUX : RECONNEXION SATELLITE...", "urgent": True, "france_related": False, "time": "00:00"}]

def get_full_intel():
    impacts = []
    try:
        url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{NASA_KEY}/VIIRS_SNPP_NRT/{AREA}/1"
        r = requests.get(url, timeout=15)
        lines = r.text.strip().split('\n')[1:]
        for line in lines:
            c = line.split(',')
            impacts.append({"lat": float(c[0]), "lng": float(c[1]), "time": f"{c[6][:2]}:{c[6][2:]}"})
    except: pass

    live_news = get_war_news()
    
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
