# src/data_collector.py
# Module 1 - Recuperation automatique des donnees financieres

import yfinance as yf
import pandas as pd
from datetime import datetime

# Les actifs qu'on surveille
ACTIFS = {
    "SP500": "^GSPC",
    "Nasdaq": "^IXIC",
    "Bitcoin": "BTC-USD",
    "Apple": "AAPL",
    "Tesla": "TSLA",
    "EUR/USD": "EURUSD=X"
}

def recuperer_donnees(symbole, periode="1y"):
    """
    Recupere les donnees historiques d'un actif financier.
    periode : 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y
    """
    print(f"Recuperation des donnees pour {symbole}...")
    df = yf.download(symbole, period=periode, auto_adjust=True)
    df = df[["Close", "Volume"]].copy()
    df.columns = ["prix_cloture", "volume"]
    df.index.name = "date"
    return df

def recuperer_tous_les_actifs(periode="1y"):
    """
    Recupere les donnees de tous les actifs surveilles.
    """
    donnees = {}
    for nom, symbole in ACTIFS.items():
        try:
            df = recuperer_donnees(symbole, periode)
            donnees[nom] = df
            print(f"{nom} : {len(df)} jours de donnees recuperes")
        except Exception as e:
            print(f"Erreur pour {nom} : {e}")
    return donnees

if __name__ == "__main__":
    print("Demarrage de la recuperation des donnees...")
    print(f"Date : {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("-" * 50)
    
    donnees = recuperer_tous_les_actifs()
    
    print("\nResume :")
    for nom, df in donnees.items():
        print(f"{nom} : du {df.index[0].date()} au {df.index[-1].date()}")