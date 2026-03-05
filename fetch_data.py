import requests, json, random
from datetime import datetime

MAP_KEY = "3a967f64858b76c839f9b5a805a50785"
EXTENT = "20,10,65,45"

def get_tactical_intel():
    # 1. RÉCUPÉRATION NASA (Frappes réelles)
    alerts = []
    try:
        r = requests.get(f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/VIIRS_SNPP_NRT/{EXTENT}/1", timeout=15)
        lines = r.text.strip().split('\n')
        for line in lines[1:21]:
            cols = line.split(',')
            alerts.append({"lat": float(cols[0]), "lng": float(cols[1]), "time": f"{cols[6][:2]}:{cols[6][2:]}"})
    except: pass

    # 2. SIMULATION NEWS AUTOMATIQUES (Mouvements US/Iran/France)
    news_pool = [
        "PENTAGONE : Déploiement immédiat d'un sous-marin classe Ohio en Mer Rouge.",
        "TEHERAN : Alerte balistique - Mouvements détectés sur les sites de lancement.",
        "US NAVY : Le groupe aéronaval du l'USS Abraham Lincoln entre en Mer d'Oman.",
        "FRANCE : Interception d'un drone non-identifié par la FREMM Alsace.",
        "UKRAINE : Intensification des frappes longue portée sur les hubs logistiques."
    ]
    
    # 3. GÉNÉRATION DE TRAJECTOIRES SI IMPACTS PROCHES
    trajectories = []
    for a in alerts[:3]: # On trace des lignes pour les 3 premières alertes
        # Si l'alerte est au sud, on simule un tir du Yémen, si c'est au nord, de l'Iran
        origin = [15.3, 44.2] if a['lat'] < 25 else [32.4, 53.6]
        trajectories.append({"from": origin, "to": [a['lat'], a['lng']]})

    return {
        "update": datetime.now().strftime("%H:%M"),
        "alerts": alerts,
        "news": random.sample(news_pool, 3),
        "trajectories": trajectories,
        "emergency": random.choice([True, False, False, False]), # 25% de chance d'alerte rouge
        "france": [
            {"n": "Charles de Gaulle", "p": [34.5, 30.1], "m": "SUPRÉMATIE AÉRIENNE"},
            {"n": "BAP Jordanie", "p": [31.8, 36.8], "m": "6x RAFALE EN ALERTE"}
        ]
    }

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(get_tactical_intel(), f, indent=2, ensure_ascii=False)
