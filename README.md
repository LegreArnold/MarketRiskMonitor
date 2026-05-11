# MarketRiskMonitor
Conception d'un tableau de bord de surveillance des marchés léger permettant de suivre les pics de volatilité, de détecter les comportements anormaux du marché et d'analyser les corrélations entre les différentes classes d'actifs en temps réel.


# Market Risk Monitor

Systeme de surveillance en temps reel du risque marche financier.

**Dashboard live : [marketriskmonitor-a5fvzmwbtfutlqj2lcdvpn.streamlit.app](http://marketriskmonitor-a5fvzmwbtfutlqj2lcdvpn.streamlit.app)**

---

## Probleme resolu

Les analystes risque passent du temps a surveiller manuellement
les marches financiers. Market Risk Monitor automatise cette
surveillance et alerte en temps reel quand un actif devient anormal.

---

## Ce que fait le systeme

- Recupere automatiquement les donnees de 6 actifs financiers
  via l'API Yahoo Finance (S&P500, Nasdaq, Bitcoin, Apple, Tesla, EUR/USD)
- Calcule les metriques de risque : rendements, volatilite 30j,
  volatilite annualisee
- Detecte les anomalies par Z-Score statistique
- Genere des alertes a 3 niveaux : VERT, ORANGE, ROUGE
- Affiche tout dans un dashboard interactif en temps reel

---

## Architecture

MarketRiskMonitor/
├── src/
│   ├── data_collector.py     → Ingestion donnees Yahoo Finance
│   ├── risk_calculator.py    → Calcul rendements et volatilite
│   ├── anomaly_detector.py   → Detection anomalies Z-Score
│   └── alert_system.py       → Systeme d'alertes 3 niveaux
├── dashboard/
│   └── app.py                → Dashboard Streamlit interactif
└── requirements.txt


---

## Stack technique

- Python — pandas, scipy, numpy
- yfinance — ingestion donnees financieres temps reel
- Streamlit — dashboard interactif
- Plotly — visualisations financieres
- Git / GitHub — versioning

---

## Metriques calculees

| Metrique | Description |
|---|---|
| Rendement quotidien | Variation de prix jour a jour en % |
| Volatilite 30j | Ecart type des rendements sur 30 jours |
| Volatilite annualisee | Volatilite x racine(252) — standard industrie |
| Z-Score | Mesure statistique de l'anomalie d'une journee |

---

## Resultats sur 12 mois

- 6 actifs surveilles en temps reel
- 91 anomalies detectees automatiquement
- Bitcoin : actif le plus instable avec Z-Score record de -6.37
- Tesla : volatilite annualisee de 43.57% — la plus elevee du portefeuille

---

## Business Interpretation

La volatilite du Bitcoin depasse regulierement celle du Nasdaq
pendant les periodes macro-economiques tendues. Les anomalies
detectees sur Tesla coincident avec les annonces de resultats
trimestriels et les declarations publiques de son dirigeant.
Le S&P500 et le Nasdaq partagent systematiquement les memes
dates d'anomalies — confirmant leur forte correlation structurelle.

---

## Comment lancer en local

```bash
git clone https://github.com/LegreArnold/MarketRiskMonitor.git
cd MarketRiskMonitor
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run dashboard/app.py
```

---

