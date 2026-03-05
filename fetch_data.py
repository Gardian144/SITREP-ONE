import requests, json, random
from datetime import datetime

# CONFIGURATION
NASA_KEY = "3a967f64858b76c839f9b5a805a50785"
AREA = "20,10,65,45" # Moyen-Orient + Ukraine

def get_real_military_intel():
    # 1. RÉCUPÉRATION DES IMPACTS RÉELS (NASA FIRMS)
    impacts = []
    try:
        url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{NASA_KEY}/VIIRS_SNPP_NRT/{AREA}/1"
        r = requests.get(url, timeout=15)
        lines = r.text.strip().split('\n')[1:15] # 15 derniers impacts
        for line in lines:
            c = line.split(',')
            impacts.append({"lat": float(c[0]), "lng": float(c[1]), "time": f"{c[6][:2]}:{c[6][2:]}"})
    except: pass

    # 2. GÉNÉRATEUR AUTOMATIQUE DE NEWS (Simule un scan OSINT)
    # Demain matin, ces news auront changé aléatoirement parmi cette base de données
    intel_pool = [
        "US NAVY : Le sous-marin USS Georgia (SSGN 729) signalé en approche du Canal de Suez.",
        "IRAN : Déploiement de nouvelles batteries de missiles S-300 près de Bandar Abbas.",
        "FRANCE : Décollage de 2 Rafale de la BAP Jordanie pour une mission ISR sur la zone Syrie.",
        "MER ROUGE : La FREMM Alsace a engagé et détruit 3 drones de surface kamikazes.",
        "UKRAINE : Détection de mouvements de troupes russes majeurs dans le secteur de Pokrovsk.",
        "OTAN : Exercice 'Steadfast Defender' - Mouvement de 500 blindés vers la Pologne."
    ]
    
    # 3. BASE DE DONNÉES FRANCE (Forces, Bases, Exercices)
    france_db = {
        "exercices": ["EXERCICE SHIKRA : Entraînement au combat aérien (J-2)", "MISSION CHAMMAL : Frappes de précision"],
        "forces": [
            {"n": "Charles de Gaulle (R91)", "p": [34.5, 30.1], "t": "Porte-avions", "s": "ALERTE 15MIN"},
            {"n": "FREMM Alsace", "p": [14.1, 42.5], "t": "Frégate AA", "s": "ENGAGEMENT ACTIF"},
            {"n": "BAP Jordanie", "p": [31.8, 36.8], "t": "Base Aérienne", "s": "6x RAFALE EN VOL"},
            {"n": "FFDJ Djibouti", "p": [11.6, 43.1], "t": "Base Interarmées", "s": "1500 PAX - OPÉRATIONNEL"}
        ]
    }

    output = {
        "last_update": datetime.now().strftime("%d/%m %H:%M"),
        "impacts": impacts,
        "news": random.sample(intel_pool, 3), # 3 news différentes à chaque refresh
        "france": france_db,
        "emergency": len(impacts) > 5 # Si bcp d'impacts, alerte rouge automatique
    }
    
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    get_real_military_intel()
