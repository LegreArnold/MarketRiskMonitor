# src/alert_system.py
# Module 4 - Systeme d'alertes de risque

import pandas as pd
import numpy as np
from datetime import datetime
from data_collector import recuperer_tous_les_actifs
from risk_calculator import calculer_rendements, calculer_volatilite
from anomaly_detector import calculer_zscore

# Seuils d'alerte
SEUIL_VOLATILITE_ORANGE = 2.0  # % par jour
SEUIL_VOLATILITE_ROUGE = 3.5   # % par jour
SEUIL_ZSCORE_ORANGE = 2.0
SEUIL_ZSCORE_ROUGE = 3.0
SEUIL_BAISSE_ROUGE = -5.0      # % en une journee

def evaluer_niveau_alerte(volatilite_30j, zscore_dernier_jour, rendement_dernier_jour):
    """
    Evalue le niveau d'alerte selon 3 criteres :
    - La volatilite actuelle
    - Le Z-Score du dernier jour
    - Le rendement du dernier jour
    """
    niveau = "VERT"
    raisons = []

    # Verification volatilite
    if volatilite_30j > SEUIL_VOLATILITE_ROUGE:
        niveau = "ROUGE"
        raisons.append(f"Volatilite tres elevee : {round(volatilite_30j, 2)}%")
    elif volatilite_30j > SEUIL_VOLATILITE_ORANGE:
        if niveau != "ROUGE":
            niveau = "ORANGE"
        raisons.append(f"Volatilite elevee : {round(volatilite_30j, 2)}%")

    # Verification Z-Score
    if abs(zscore_dernier_jour) > SEUIL_ZSCORE_ROUGE:
        niveau = "ROUGE"
        raisons.append(f"Mouvement extreme detecte : Z-Score {round(zscore_dernier_jour, 2)}")
    elif abs(zscore_dernier_jour) > SEUIL_ZSCORE_ORANGE:
        if niveau != "ROUGE":
            niveau = "ORANGE"
        raisons.append(f"Mouvement anormal detecte : Z-Score {round(zscore_dernier_jour, 2)}")

    # Verification baisse brutale
    if rendement_dernier_jour < SEUIL_BAISSE_ROUGE:
        niveau = "ROUGE"
        raisons.append(f"Baisse brutale : {round(rendement_dernier_jour, 2)}%")

    if not raisons:
        raisons.append("Situation normale")

    return niveau, raisons

def generer_alertes(donnees):
    """
    Genere les alertes pour tous les actifs.
    """
    alertes = []

    for nom, df in donnees.items():
        df = calculer_rendements(df)
        df = calculer_volatilite(df)
        df = calculer_zscore(df)

        # On prend les valeurs du dernier jour
        dernier_jour = df.iloc[-1]
        volatilite_30j = dernier_jour["volatilite_30j"] * 100
        zscore = dernier_jour["zscore"]
        rendement = dernier_jour["rendement"] * 100

        niveau, raisons = evaluer_niveau_alerte(
            volatilite_30j, zscore, rendement
        )

        alerte = {
            "actif": nom,
            "date": df.index[-1].date(),
            "prix": round(dernier_jour["prix_cloture"], 2),
            "rendement_jour": round(rendement, 2),
            "volatilite_30j": round(volatilite_30j, 2),
            "zscore": round(zscore, 2),
            "niveau": niveau,
            "raisons": raisons
        }
        alertes.append(alerte)

    return alertes

def afficher_alertes(alertes):
    """
    Affiche les alertes de facon claire et lisible.
    """
    couleurs = {
        "ROUGE": "ALERTE ROUGE",
        "ORANGE": "ALERTE ORANGE",
        "VERT": "SITUATION NORMALE"
    }

    print(f"\nRAPPORT D'ALERTES - {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 60)

    # Trier par niveau de risque
    ordre = {"ROUGE": 0, "ORANGE": 1, "VERT": 2}
    alertes_triees = sorted(alertes, key=lambda x: ordre[x["niveau"]])

    for a in alertes_triees:
        print(f"\n{couleurs[a['niveau']]} - {a['actif']}")
        print(f"  Date           : {a['date']}")
        print(f"  Prix           : {a['prix']}")
        print(f"  Rendement jour : {a['rendement_jour']} %")
        print(f"  Volatilite 30j : {a['volatilite_30j']} %")
        print(f"  Z-Score        : {a['zscore']}")
        print(f"  Analyse        : {' | '.join(a['raisons'])}")

    print("\n" + "=" * 60)
    print("RESUME")
    print("=" * 60)
    rouges = len([a for a in alertes if a["niveau"] == "ROUGE"])
    oranges = len([a for a in alertes if a["niveau"] == "ORANGE"])
    verts = len([a for a in alertes if a["niveau"] == "VERT"])
    print(f"ROUGE  : {rouges} actif(s)")
    print(f"ORANGE : {oranges} actif(s)")
    print(f"VERT   : {verts} actif(s)")

if __name__ == "__main__":
    print("Demarrage du systeme d'alertes...")
    donnees = recuperer_tous_les_actifs()
    alertes = generer_alertes(donnees)
    afficher_alertes(alertes)