import requests
import json
from datetime import datetime

# Zone Iran / Moyen-Orient
EXTENT = "44,24,63,40" 
MAP_KEY = "3a967f64858b76c839f9b5a805a50785" 

def fetch_nasa_alerts():
    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/VIIRS_SNPP_NRT/{EXTENT}/1"
    try:
        response = requests.get(url, timeout=20)
        if response.status_code != 200:
            return []
            
        lines = response.text.strip().split('\n')
        if len(lines) <= 1:
            return [] 

        new_events = []
        # On traite les 15 points les plus récents
        for line in lines[1:16]: 
            cols = line.split(',')
            if len(cols) < 7: continue
            
            lat, lon = cols[0], cols[1]
            # On crée un objet propre pour le JSON
            new_events.append({
                "id": f"nasa_{cols[5]}_{cols[6]}_{lat}",
                "time": f"{cols[6][:2]}:{cols[6][2:]}",
                "lat": float(lat),
                "lng": float(lon),
                "title": "ALERTE THERMIQUE",
                "desc": f"Signature thermique détectée par satellite (VIIRS).",
                "type": "STRIKE"
            })
        return new_events
    except Exception as e:
        print(f"Erreur de connexion : {e}")
        return []

# Exécution
alerts = fetch_nasa_alerts()

# On n'écrase que si on a trouvé quelque chose, sinon on garde l'ancien
if alerts:
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(alerts, f, indent=2, ensure_ascii=False)
    print(f"Update : {len(alerts)} points trouvés.")
else:
    print("RAS : Pas de nouveau point de chaleur.")
