import requests
import json
from datetime import datetime

# Zone Moyen-Orient élargie (Bounding Box)
EXTENT = "30,10,65,45" 
MAP_KEY = "3a967f64858b76c839f9b5a805a50785" 

def get_location_label(lat, lon):
    """Analyse les coordonnées pour nommer la menace"""
    lat, lon = float(lat), float(lon)
    
    # Zone ISRAËL / LIBAN
    if 29.5 < lat < 33.5 and 34.2 < lon < 36.5:
        return "🚀 IMPACT DÉTECTÉ (ZONE ISRAËL/PALESTINE)"
    
    # Zone TÉHÉRAN
    if 35.5 < lat < 36.5 and 51.0 < lon < 52.0:
        return "🔥 EXPLOSION / FRAPPE (SECTEUR TÉHÉRAN)"
    
    # Zone MER ROUGE (Navires/Houthis)
    if 12.0 < lat < 20.0 and 38.0 < lon < 45.0:
        return "⚓ ENGAGEMENT NAVAL (MER ROUGE / YÉMEN)"
    
    # Zone GOLFE PERSIQUE
    if 24.0 < lat < 30.0 and 48.0 < lon < 56.0:
        return "🚢 ACTIVITÉ THERMIQUE (GOLFE ARABO-PERSIQUE)"
    
    return "ALERTE THERMIQUE (MOYEN-ORIENT)"

def fetch_nasa_alerts():
    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/VIIRS_SNPP_NRT/{EXTENT}/1"
    try:
        response = requests.get(url, timeout=20)
        if response.status_code != 200:
            print(f"Erreur NASA : {response.status_code}")
            return []
            
        lines = response.text.strip().split('\n')
        if len(lines) <= 1:
            return [] 

        new_events = []
        # On traite les 20 points les plus récents pour plus de data
        for line in lines[1:21]: 
            cols = line.split(',')
            if len(cols) < 7: continue
            
            lat, lon = cols[0], cols[1]
            title = get_location_label(lat, lon)
            
            new_events.append({
                "id": f"nasa_{cols[5]}_{cols[6]}_{lat}",
                "time": f"{cols[6][:2]}:{cols[6][2:]}",
                "lat": float(lat),
                "lng": float(lon),
                "title": title,
                "desc": f"Détection satellite VIIRS - Signature thermique haute intensité.",
                "type": "STRIKE"
            })
        return new_events
    except Exception as e:
        print(f"Erreur de connexion : {e}")
        return []

# Exécution du scan
alerts = fetch_nasa_alerts()

if alerts:
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(alerts, f, indent=2, ensure_ascii=False)
    print(f"Update : {len(alerts)} cibles identifiées.")
else:
    print("RAS : Aucune signature thermique détectée dans les secteurs clés.")
