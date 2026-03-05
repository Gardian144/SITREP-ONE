import requests, json, random
from datetime import datetime

# CONFIGURATION
NASA_KEY = "3a967f64858b76c839f9b5a805a50785"
AREA = "20,10,65,45" 

def get_full_intel():
    # 1. RÉCUPÉRATION NASA (Tous les impacts récents)
    impacts = []
    try:
        url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{NASA_KEY}/VIIRS_SNPP_NRT/{AREA}/1"
        r = requests.get(url, timeout=15)
        lines = r.text.strip().split('\n')[1:] # On prend TOUT, pas de limite
        for line in lines:
            c = line.split(',')
            impacts.append({"lat": float(c[0]), "lng": float(c[1]), "time": f"{c[6][:2]}:{c[6][2:]}"})
    except: pass

    # 2. BASE DE NEWS OSINT (Toutes les news détectées)
    # Dans le futur, on peut connecter une API de news ici
    intel_feed = [
        "FRANCE : Déploiement du Chasseur de mines 'Eridan' en zone maritime Nord.",
        "US NAVY : Mouvements confirmés du groupe aéronaval Lincoln vers Oman.",
        "IRAN : Test de propulsion solide détecté sur le site de Shahrud.",
        "FRANCE : Exercice interarmées 'BACCARAT' débuté dans l'Est de la France.",
        "MER ROUGE : Alerte drone sur le corridor Bab-el-Mandeb.",
        "ISRAËL : Activation des systèmes de réserve Iron Dome Nord."
    ]
    
    # 3. BASE DE DONNÉES FRANCE (Forces et Bases)
    # J'ajoute plus de points pour que la page France soit remplie
    france_db = {
        "exercices": [
            "OPÉRATION CHAMMAL : Soutien aérien Irak/Syrie (Rafale B).",
            "MISSION AGÉNOR : Protection du détroit d'Ormuz (Frégate).",
            "EXERCICE SENTINELLE : Surveillance territoire national (10k PAX)."
        ],
        "forces": [
            {"n": "Charles de Gaulle", "p": [34.5, 30.1], "t": "Porte-avions", "s": "ALERTE S-1"},
            {"n": "FREMM Alsace", "p": [13.2, 42.9], "s": "ENGAGEMENT ACTIF", "t": "Frégate"},
            {"n": "BAP Jordanie", "p": [31.8, 36.8], "s": "DÉPLOIEMENT RAFALE", "t": "Base Aérienne"},
            {"n": "Base Abu Dhabi", "p": [24.4, 54.3], "s": "SOUTIEN LOG", "t": "Base Navale"},
            {"n": "Éléments FFDJ", "p": [11.6, 43.1], "s": "SURVEILLANCE", "t": "Djibouti"}
        ]
    }

    output = {
        "last_update": datetime.now().strftime("%d/%m %H:%M"),
        "impacts": impacts,
        "news": intel_feed, # On envoie TOUTE la liste
        "france": france_db,
        "emergency": len(impacts) > 10
    }
    
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    get_full_intel()
