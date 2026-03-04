import requests
import json
from datetime import datetime

# Paramètres NASA pour l'Iran
AREA = "44,25,63,40"  # Coordonnées (Long/Lat) du secteur
MAP_KEY = "3a967f64858b76c839f9b5a805a50785" # Clé publique pour l'exemple

def get_nasa_data():
    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/VIIRS_SNPP_NRT/{AREA}/1"
    try:
        response = requests.get(url)
        lines = response.text.split('\n')[1:] # On saute l'en-tête
        events = []
        for line in lines:
            if not line: continue
            val = line.split(',')
            # On transforme chaque point de chaleur en événement "STRIKE"
            events.append({
                "id": val[0] + val[1],
                "time": datetime.now().strftime("%H:%M"),
                "lat": float(val[0]),
                "lng": float(val[1]),
                "title": "ANOMALIE THERMIQUE",
                "desc": "Source de chaleur intense détectée par satellite (NASA VIIRS).",
                "type": "STRIKE"
            })
        return events
    except:
        return []

# Mise à jour du fichier data.json
new_events = get_nasa_data()
if new_events:
    with open('data.json', 'w') as f:
        json.dump(new_events, f, indent=2)
