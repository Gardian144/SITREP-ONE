import requests, json, xml.etree.ElementTree as ET
from datetime import datetime

NASA_KEY = "3a967f64858b76c839f9b5a805a50785"
AREA = "20,10,65,45"

def get_war_news():
    news_output = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    # Sources : Nom -> URL RSS
    sources = {
        "OPEX360": "https://www.opex360.com/feed/",
        "BFMTV": "https://www.bfmtv.com/rss/international/"
    }

    critical_keywords = [
        "GUERRE", "EXPLOSION", "FRAPPE", "MISSILE", "INVASION", "LIBAN", 
        "ISRAËL", "COMBAT", "OFFENSIVE", "ALERTE", "DRONE", "SOUS-MARIN",
        "COULÉ", "ATTAQUE", "NUCLÉAIRE", "URGENT", "BREAKING", "HEZBOLLAH", 
        "IRAN", "BOMBARDEMENT", "FRONT", "SABOTAGE", "BALISTIQUE", "TEHERAN"
    ]
    
    # Mots-clés spécifiques pour filtrer les flux généralistes (BFM) vers l'Iran
    iran_keywords = ["IRAN", "TEHERAN", "REVOLUTIONNAIRE", "KHAMENEI", "ORAMUZ", "ISRAËL", "NUCLEAR"]
    france_keywords = ["FRANCE", "FRANÇAIS", "PARIS", "MARINE NATIONALE", "ARMÉE DE L'AIR", "EMA", "PORTE-AVIONS"]

    for source_name, url in sources.items():
        try:
            r = requests.get(url, headers=headers, timeout=10)
            root = ET.fromstring(r.content)
            for item in root.findall('./channel/item')[:15]:
                title = item.find('title').text
                title_upper = title.upper()
                
                # Filtrage : On prend tout de OPEX360, mais seulement le conflit de BFM
                is_relevant = True
                if source_name == "BFMTV":
                    is_relevant = any(word in title_upper for word in (critical_keywords + iran_keywords))
                
                if is_relevant:
                    pub_date = item.find('pubDate').text
                    try:
                        time_str = pub_date.split(' ')[4][:5] 
                    except:
                        time_str = "--:--"
                    
                    is_urgent = any(word in title_upper for word in critical_keywords)
                    is_france = any(word in title_upper for word in france_keywords)
                    
                    news_output.append({
                        "source": source_name,
                        "text": title.upper(),
                        "urgent": is_urgent,
                        "france_related": is_france,
                        "time": time_str
                    })
        except Exception as e:
            print(f"Erreur source {source_name}: {e}")

    # Tri global : Urgents d'abord, puis par heure
    news_output.sort(key=lambda x: (x['urgent'], x['time']), reverse=True)
    return news_output

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

    output = {
        "last_update": datetime.now().strftime("%d/%m %H:%M"),
        "impacts": impacts,
        "news": get_war_news(), 
        "france": {
            "forces": [
                {"n": "BAP Jordanie", "p": [32.16, 37.14], "t": "Base Aérienne", "s": "RAFALE OPS"},
                {"n": "BA 188 Djibouti", "p": [11.54, 43.15], "t": "Point d'Appui", "s": "VIGILANCE"},
                {"n": "BN Abu Dhabi", "p": [24.52, 54.37], "t": "Soutien Naval", "s": "ALINDIEN"}
            ]
        },
        "emergency": len(impacts) > 15
    }
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    get_full_intel()
