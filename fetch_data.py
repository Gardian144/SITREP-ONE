import requests
import json
from datetime import datetime

# Configuration du secteur Moyen-Orient (Bounding Box)
# Format: Ouest, Sud, Est, Nord
EXTENT = "44,24,63,40" 
MAP_KEY = "3a967f64858b76c839f9b5a805a50785" # Clé d'accès API FIRMS

def fetch_nasa_alerts():
    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/VIIRS_SNPP_NRT/{EXTENT}/1"
    try:
        response = requests.get(url, timeout=15)
        if response.status_status != 200: return []
        
        lines = response.text.strip().split('\n')
        if len(lines) <= 1: return [] # Pas de nouvelles données

        new_events = []
        # On prend les 10 alertes les plus récentes pour ne pas surcharger
        for line in lines[1:11]: 
            cols = line.split(',')
            # Format NASA: latitude, longitude, bright_ti4, scan, track, acq_date, acq_time...
            lat, lon = cols[0], cols[1]
            time_str = f"{cols[5]} {cols[6][:2]}:{cols[6][2:]}"
            
            new_events.append({
                "id": f"nasa_{cols[5]}_{cols[6]}_{lat}",
                "time": cols[6][:2] + ":" + cols[6][2:],
                "lat": float(lat),
                "lng": float(lon),
                "title": "ANOMALIE THERMIQUE",
                "desc": f"Détection satellite VIIRS à {lat}, {lon}. Signature thermique élevée.",
                "type": "STRIKE"
            })
        return new_events
    except Exception as e:
        print(f"Erreur: {e}")
        return []

# Exécution et sauvegarde
alerts = fetch_nasa_alerts()
if alerts:
    # On garde les alertes actuelles pour ne pas tout effacer à chaque fois
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(alerts, f, indent=2, ensure_ascii=False)
    print(f"Succès: {len(alerts)} alertes ajoutées.")
else:
    print("Aucune nouvelle alerte détectée.")
