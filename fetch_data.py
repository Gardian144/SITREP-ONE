import requests, json, random
from datetime import datetime

NASA_KEY = "3a967f64858b76c839f9b5a805a50785"
AREA = "20,10,65,45" 

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

    # News dynamiques (on peut en mettre autant qu'on veut)
    intel_feed = [
        "FRANCE : La frégate 'Alsace' confirme la destruction de drones hostiles en Mer Rouge.",
        "US NAVY : Le porte-avions USS Abraham Lincoln est entré en zone de responsabilité Alindien.",
        "IRAN : Activité inhabituelle détectée sur le pas de tir de Semnan (Imagerie Satellite).",
        "JORDANIE : Rotation de 2 Rafale français sur la BAP Prince-Hassan.",
        "DJIBOUTI : Exercice de sécurisation du détroit de Bab-el-Mandeb par les FFDj.",
        "ISRAËL : Alerte interception secteur Galilée - Systèmes de défense actifs."
    ]
    
    # Données réelles de l'EMA
    france_db = {
        "exercices": [
            "OPÉRATION CHAMMAL : Appui aérien quotidien sur la zone Irak/Syrie.",
            "MISSION AGÉNOR : Protection du trafic maritime civil (Détroit d'Ormuz).",
            "POSTURE SENTINELLE : 7 000 militaires en alerte sur le territoire national."
        ],
        "forces": [
            {"n": "BAP Jordanie (Prince-Hassan)", "p": [32.1608, 37.1497], "t": "Base Aérienne Projetée", "s": "RAFALE / OPS"},
            {"n": "BA 188 Djibouti", "p": [11.5469, 43.1514], "t": "Base de Soutien", "s": "VIGILANCE MER ROUGE"},
            {"n": "Base Navale Port Zayed", "p": [24.5244, 54.3725], "t": "Base Navale", "s": "ALINDIEN"},
            {"n": "GAN (Charles de Gaulle)", "p": [34.5, 30.1], "t": "Porte-avions", "s": "DÉPLOIEMENT EN COURS"},
            {"n": "FFDJ (Forces Djibouti)", "p": [11.59, 43.14], "t": "Infanterie/Terre", "s": "OPÉRATIONNEL"}
        ]
    }

    output = {
        "last_update": datetime.now().strftime("%d/%m %H:%M"),
        "impacts": impacts,
        "news": intel_feed, 
        "france": france_db,
        "emergency": len(impacts) > 12
    }
    
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    get_full_intel()
