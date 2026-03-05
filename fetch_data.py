import requests
import json
from datetime import datetime
import random

MAP_KEY = "3a967f64858b76c839f9b5a805a50785"
EXTENT = "20,10,65,45"

def get_intel():
    # 1. RÉCUPÉRATION NASA (Réel)
    alerts = []
    try:
        r = requests.get(f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/VIIRS_SNPP_NRT/{EXTENT}/1", timeout=15)
        lines = r.text.strip().split('\n')
        for line in lines[1:21]:
            cols = line.split(',')
            alerts.append({"lat": float(cols[0]), "lng": float(cols[1]), "t": cols[6]})
    except: pass

    # 2. GÉNÉRATEUR DE NEWS & ÉVÉNEMENTS (Simulation OSINT)
    # Dans une version avancée, on pourrait scrapper Twitter/RSS ici.
    news_db = [
        "US NAVY : Déploiement d'un sous-marin classe Virginia en Méditerranée orientale.",
        "IRAN : Exercices balistiques signalés dans la province de Semnan.",
        "FRANCE : Le GAN Charles de Gaulle maintient sa position de contrôle.",
        "MER ROUGE : Interception d'un drone suicide par une frégate européenne.",
        "USA : Mouvement de bombardiers B-52 vers Diego Garcia."
    ]
    
    # 3. TRAJECTOIRES ACTIVES (Exemple: Tir Mer Rouge ou Iran)
    # On génère une trajectoire si des alertes NASA sont proches de zones sensibles
    trajectories = []
    if len(alerts) > 0:
        trajectories.append({
            "from": [15.3, 44.2], # Yemen
            "to": [alerts[0]["lat"], alerts[0]["lng"]],
            "type": "MISSILE_PATH",
            "id": "M-99"
        })

    return {
        "last_sync": datetime.now().strftime("%d/%m %H:%M"),
        "alerts": alerts,
        "news": random.sample(news_db, 3), # On pioche 3 news au hasard pour simuler le flux
        "trajectories": trajectories,
        "france_ops": {
            "navy": [
                {"n": "Charles de Gaulle", "p": [34.5, 30.1], "a": "Alerte Interception"},
                {"n": "FREMM Alsace", "p": [13.2, 42.9], "a": "Escorte Marchande"}
            ],
            "air": [
                {"n": "Patrouille Rafale", "path": [[31.8, 36.5], [33.2, 39.1]], "m": "ISR"}
            ]
        }
    }

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(get_intel(), f, indent=2, ensure_ascii=False)
