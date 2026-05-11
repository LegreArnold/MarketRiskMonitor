# src/anomaly_detector.py
# Module 3 - Detection d'anomalies par Z-Score

import pandas as pd
import numpy as np
from data_collector import recuperer_tous_les_actifs
from risk_calculator import calculer_rendements, calculer_volatilite

def calculer_zscore(df):
    """
    Calcule le Z-Score de chaque rendement quotidien.
    Z-Score = (rendement - moyenne) / ecart_type
    Un Z-Score > 2 ou < -2 indique une anomalie.
    """
    df = df.copy()
    moyenne = df["rendement"].mean()
    ecart_type = df["rendement"].std()
    df["zscore"] = (df["rendement"] - moyenne) / ecart_type
    return df

def detecter_anomalies(df, seuil=2.0):
    """
    Detecte les journees anormales selon le Z-Score.
    seuil : nombre d'ecarts types au-dela duquel on considere une anomalie
    """
    df = calculer_zscore(df)
    anomalies = df[abs(df["zscore"]) > seuil].copy()
    anomalies["type_anomalie"] = anomalies["zscore"].apply(
        lambda z: "Hausse anormale" if z > 0 else "Baisse anormale"
    )
    anomalies["intensite"] = anomalies["zscore"].apply(
        lambda z: "Extreme" if abs(z) > 3 else "Forte"
    )
    return anomalies

def rapport_anomalies(nom_actif, anomalies):
    """
    Affiche un rapport clair des anomalies detectees.
    """
    print(f"\nActif : {nom_actif}")
    print(f"Anomalies detectees : {len(anomalies)}")
    
    if len(anomalies) == 0:
        print("Aucune anomalie detectee sur la periode.")
        return
    
    hausses = anomalies[anomalies["type_anomalie"] == "Hausse anormale"]
    baisses = anomalies[anomalies["type_anomalie"] == "Baisse anormale"]
    extremes = anomalies[anomalies["intensite"] == "Extreme"]
    
    print(f"  Hausses anormales  : {len(hausses)}")
    print(f"  Baisses anormales  : {len(baisses)}")
    print(f"  Anomalies extremes : {len(extremes)}")
    
    print(f"\n  Top 3 journees les plus anormales :")
    top3 = anomalies.reindex(
        anomalies["zscore"].abs().nlargest(3).index
    )
    for date, row in top3.iterrows():
        print(f"  {date.date()} | {row['type_anomalie']} | "
              f"Rendement : {round(row['rendement']*100, 2)}% | "
              f"Z-Score : {round(row['zscore'], 2)}")

if __name__ == "__main__":
    print("Detection des anomalies en cours...")
    print("=" * 60)
    
    donnees = recuperer_tous_les_actifs()
    
    toutes_anomalies = {}
    for nom, df in donnees.items():
        df = calculer_rendements(df)
        df = calculer_volatilite(df)
        anomalies = detecter_anomalies(df, seuil=2.0)
        toutes_anomalies[nom] = anomalies
        rapport_anomalies(nom, anomalies)
    
    print("\n" + "=" * 60)
    print("RESUME GLOBAL")
    print("=" * 60)
    total = sum(len(a) for a in toutes_anomalies.values())
    print(f"Total anomalies detectees sur tous les actifs : {total}")
    actif_plus_risque = max(
        toutes_anomalies,
        key=lambda x: len(toutes_anomalies[x])
    )
    print(f"Actif le plus instable : {actif_plus_risque}")