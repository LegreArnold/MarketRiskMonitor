# src/risk_calculator.py
# Module 2 - Calcul des rendements et de la volatilite

import pandas as pd
import numpy as np
from data_collector import recuperer_tous_les_actifs

def calculer_rendements(df):
    """
    Calcule le rendement quotidien de chaque actif.
    Rendement = (Prix aujourd'hui - Prix hier) / Prix hier
    """
    df = df.copy()
    df["rendement"] = df["prix_cloture"].pct_change()
    return df

def calculer_volatilite(df, fenetre=30):
    """
    Calcule la volatilite sur une fenetre glissante de 30 jours.
    La volatilite c'est l'ecart type des rendements.
    Plus elle est elevee, plus l'actif est agite.
    """
    df = df.copy()
    df["volatilite_30j"] = df["rendement"].rolling(window=fenetre).std()
    df["volatilite_annualisee"] = df["volatilite_30j"] * np.sqrt(252)
    return df

def calculer_metriques_risque(df, nom_actif):
    """
    Calcule un resume des metriques de risque pour un actif.
    """
    rendements = df["rendement"].dropna()
    
    metriques = {
        "actif": nom_actif,
        "prix_actuel": round(df["prix_cloture"].iloc[-1], 2),
        "rendement_moyen_quotidien": round(rendements.mean() * 100, 4),
        "volatilite_30j": round(df["volatilite_30j"].iloc[-1] * 100, 4),
        "volatilite_annualisee": round(df["volatilite_annualisee"].iloc[-1] * 100, 2),
        "meilleur_jour": round(rendements.max() * 100, 2),
        "pire_jour": round(rendements.min() * 100, 2),
        "nb_jours_positifs": int((rendements > 0).sum()),
        "nb_jours_negatifs": int((rendements < 0).sum()),
    }
    return metriques

if __name__ == "__main__":
    print("Calcul des metriques de risque...\n")
    
    donnees = recuperer_tous_les_actifs()
    
    resultats = []
    for nom, df in donnees.items():
        df = calculer_rendements(df)
        df = calculer_volatilite(df)
        metriques = calculer_metriques_risque(df, nom)
        resultats.append(metriques)
    
    print("=" * 60)
    print("RAPPORT DE RISQUE - MarketRiskMonitor")
    print("=" * 60)
    
    for m in resultats:
        print(f"\nActif : {m['actif']}")
        print(f"  Prix actuel          : {m['prix_actuel']}")
        print(f"  Rendement moyen/jour : {m['rendement_moyen_quotidien']} %")
        print(f"  Volatilite 30j       : {m['volatilite_30j']} %")
        print(f"  Volatilite annualisee: {m['volatilite_annualisee']} %")
        print(f"  Meilleur jour        : +{m['meilleur_jour']} %")
        print(f"  Pire jour            : {m['pire_jour']} %")
        print(f"  Jours positifs       : {m['nb_jours_positifs']}")
        print(f"  Jours negatifs       : {m['nb_jours_negatifs']}")