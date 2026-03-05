import requests
import json
from datetime import datetime
import random

# Configuration
EXTENT = "20,10,65,45" 
MAP_KEY = "3a967f64858b76c839f9b5a805a50785" 

def fetch_nasa_alerts():
    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/VIIRS_SNPP_NRT/{EXTENT}/1"
    processed = []
    try:
        response = requests.get(url, timeout=20)
        lines = response.text.strip().split('\n')
        if len(lines) > 1:
            for line in lines[1:21]:
                cols = line.split(',')
                processed.append({
                    "type": "STRIKE",
                    "title": "IMPACT KINÉTIQUE DÉTECTÉ",
                    "lat": float(cols[0]), "lng": float(cols[1]),
                    "time": f"{cols[6][:2]}:{cols[6][2:]}",
                    "details": "Signature thermique compatible avec une frappe."
                })
    except: pass
    return processed

def get_tactical_assets():
    # Simulation des mouvements de la Marine et de l'Air
    return {
        "navy": [
            {"n": "Charles de Gaulle (R91)", "lat": 34.5, "lng": 28.2, "status": "OPS", "act": "Lancement Rafale M"},
            {"n": "FREMM Languedoc", "lat": 12.8, "lng": 43.2, "status": "FEU", "act": "Interception drone"},
            {"n": "FS Forbin", "lat": 33.9, "lng": 34.5, "status": "POS", "act": "Surveillance zone côtière"}
        ],
        "air_ops": [
            {"unit": "Rafale B (Chammal)", "base": "BAP Jordanie", "mission": "Reconnaissance ISR", "zone": "Syrie/Irak"},
            {"unit": "A330 MRTT", "base": "Al Dhafra", "mission": "Ravitaillement", "zone": "Golfe"},
            {"unit": "Drones Reaper", "base": "Niamey (Archive)", "mission": "Surveillance", "zone": "Sahel Est"}
        ]
    }

# Compilation de toutes les données
data = {
    "sync_time": datetime.now().strftime("%H:%M"),
    "alerts": fetch_nasa_alerts(),
    "tactical": get_tactical_assets(),
    "intel": [
        "Mouvement de convoi repéré au Sud Liban",
        "Alerte drone Mer Rouge : Interception réussie par la Marine",
        "Exercice aérien conjoint France-Jordanie en cours"
    ]
}

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
