# dashboard/app.py
# Module 5 - Dashboard Streamlit Market Risk Monitor

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_collector import recuperer_tous_les_actifs
from risk_calculator import calculer_rendements, calculer_volatilite, calculer_metriques_risque
from anomaly_detector import detecter_anomalies, calculer_zscore
from alert_system import generer_alertes

# --- CONFIG ---
st.set_page_config(
    page_title="Market Risk Monitor",
    page_icon="📈",
    layout="wide"
)

# --- CHARGEMENT DES DONNEES ---
@st.cache_data(ttl=3600)
def charger_donnees():
    donnees = recuperer_tous_les_actifs()
    donnees_enrichies = {}
    for nom, df in donnees.items():
        df = calculer_rendements(df)
        df = calculer_volatilite(df)
        df = calculer_zscore(df)
        donnees_enrichies[nom] = df
    return donnees_enrichies

# --- INTERFACE ---
st.title("Market Risk Monitor")
st.markdown("**Surveillance en temps reel du risque marche**")
st.divider()

with st.spinner("Chargement des donnees financieres..."):
    donnees = charger_donnees()

alertes = generer_alertes(donnees)

# --- SIDEBAR ---
st.sidebar.title("Parametres")
actif_selectionne = st.sidebar.selectbox(
    "Choisir un actif",
    list(donnees.keys())
)
periode_affichage = st.sidebar.slider(
    "Periode d'affichage (jours)",
    30, 365, 180
)

# --- PAGE PRINCIPALE ---
pages = st.tabs([
    "Vue Generale",
    "Analyse du Risque",
    "Anomalies",
    "Alertes"
])

# =====================
# PAGE 1 - VUE GENERALE
# =====================
with pages[0]:
    st.header("Vue generale du marche")

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    nb_rouges = len([a for a in alertes if a["niveau"] == "ROUGE"])
    nb_oranges = len([a for a in alertes if a["niveau"] == "ORANGE"])
    nb_verts = len([a for a in alertes if a["niveau"] == "VERT"])
    total_anomalies = sum(
        len(detecter_anomalies(donnees[nom]))
        for nom in donnees
    )

    col1.metric("Actifs surveilles", len(donnees))
    col2.metric("Alertes rouges", nb_rouges, delta=None)
    col3.metric("Alertes oranges", nb_oranges)
    col4.metric("Anomalies detectees", total_anomalies)

    st.divider()

    # Graphique prix
    st.subheader(f"Evolution du prix — {actif_selectionne}")
    df = donnees[actif_selectionne].tail(periode_affichage)

    fig_prix = go.Figure()
    fig_prix.add_trace(go.Scatter(
        x=df.index,
        y=df["prix_cloture"],
        mode="lines",
        name="Prix cloture",
        line=dict(color="#1f77b4", width=2)
    ))
    fig_prix.update_layout(
        xaxis_title="Date",
        yaxis_title="Prix",
        height=400,
        template="plotly_white"
    )
    st.plotly_chart(fig_prix, use_container_width=True)

    # Graphique rendements
    st.subheader(f"Rendements quotidiens — {actif_selectionne}")
    fig_rend = go.Figure()
    fig_rend.add_trace(go.Bar(
        x=df.index,
        y=df["rendement"] * 100,
        name="Rendement %",
        marker_color=df["rendement"].apply(
            lambda x: "#2ecc71" if x >= 0 else "#e74c3c"
        )
    ))
    fig_rend.update_layout(
        xaxis_title="Date",
        yaxis_title="Rendement (%)",
        height=300,
        template="plotly_white"
    )
    st.plotly_chart(fig_rend, use_container_width=True)

# ==========================
# PAGE 2 - ANALYSE DU RISQUE
# ==========================
with pages[1]:
    st.header("Analyse du risque")

    # Tableau metriques
    st.subheader("Metriques de risque par actif")
    metriques_liste = []
    for nom, df in donnees.items():
        m = calculer_metriques_risque(df, nom)
        metriques_liste.append(m)

    df_metriques = pd.DataFrame(metriques_liste)
    df_metriques = df_metriques[[
        "actif", "prix_actuel", "rendement_moyen_quotidien",
        "volatilite_annualisee", "meilleur_jour", "pire_jour"
    ]]
    df_metriques.columns = [
        "Actif", "Prix actuel", "Rendement moy/j (%)",
        "Volatilite annualisee (%)", "Meilleur jour (%)", "Pire jour (%)"
    ]
    st.dataframe(df_metriques, use_container_width=True)

    st.divider()

    # Graphique comparaison volatilite
    st.subheader("Comparaison de la volatilite annualisee")
    fig_vol = px.bar(
        df_metriques,
        x="Actif",
        y="Volatilite annualisee (%)",
        color="Volatilite annualisee (%)",
        color_continuous_scale="RdYlGn_r",
        title="Volatilite annualisee par actif"
    )
    fig_vol.update_layout(height=400, template="plotly_white")
    st.plotly_chart(fig_vol, use_container_width=True)

    # Volatilite glissante
    st.subheader(f"Volatilite glissante 30j — {actif_selectionne}")
    df = donnees[actif_selectionne].tail(periode_affichage)
    fig_vgl = go.Figure()
    fig_vgl.add_trace(go.Scatter(
        x=df.index,
        y=df["volatilite_30j"] * 100,
        mode="lines",
        name="Volatilite 30j",
        line=dict(color="#e74c3c", width=2),
        fill="tozeroy",
        fillcolor="rgba(231, 76, 60, 0.1)"
    ))
    fig_vgl.update_layout(
        xaxis_title="Date",
        yaxis_title="Volatilite (%)",
        height=350,
        template="plotly_white"
    )
    st.plotly_chart(fig_vgl, use_container_width=True)

# =================
# PAGE 3 - ANOMALIES
# =================
with pages[2]:
    st.header("Detection des anomalies")

    st.subheader(f"Anomalies detectees — {actif_selectionne}")
    df = donnees[actif_selectionne]
    anomalies = detecter_anomalies(df)

    if len(anomalies) == 0:
        st.success("Aucune anomalie detectee sur cet actif.")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total anomalies", len(anomalies))
        col2.metric(
            "Hausses anormales",
            len(anomalies[anomalies["type_anomalie"] == "Hausse anormale"])
        )
        col3.metric(
            "Baisses anormales",
            len(anomalies[anomalies["type_anomalie"] == "Baisse anormale"])
        )

        # Graphique Z-Score
        df_plot = donnees[actif_selectionne].tail(periode_affichage)
        fig_z = go.Figure()
        fig_z.add_trace(go.Scatter(
            x=df_plot.index,
            y=df_plot["zscore"],
            mode="lines",
            name="Z-Score",
            line=dict(color="#3498db", width=1.5)
        ))
        fig_z.add_hline(y=2, line_dash="dash",
                        line_color="orange", annotation_text="Seuil orange")
        fig_z.add_hline(y=-2, line_dash="dash",
                        line_color="orange")
        fig_z.add_hline(y=3, line_dash="dash",
                        line_color="red", annotation_text="Seuil rouge")
        fig_z.add_hline(y=-3, line_dash="dash",
                        line_color="red")
        fig_z.update_layout(
            title="Z-Score quotidien",
            xaxis_title="Date",
            yaxis_title="Z-Score",
            height=400,
            template="plotly_white"
        )
        st.plotly_chart(fig_z, use_container_width=True)

        # Tableau anomalies
        st.subheader("Detail des anomalies")
        df_anom = anomalies[["prix_cloture", "rendement",
                              "zscore", "type_anomalie", "intensite"]].copy()
        df_anom["rendement"] = (df_anom["rendement"] * 100).round(2)
        df_anom.columns = ["Prix", "Rendement (%)",
                           "Z-Score", "Type", "Intensite"]
        st.dataframe(df_anom, use_container_width=True)

# ================
# PAGE 4 - ALERTES
# ================
with pages[3]:
    st.header("Tableau de bord des alertes")
    st.markdown(f"**Mise a jour : {alertes[0]['date']}**")

    couleurs_badge = {
        "ROUGE": "🔴",
        "ORANGE": "🟠",
        "VERT": "🟢"
    }

    ordre = {"ROUGE": 0, "ORANGE": 1, "VERT": 2}
    alertes_triees = sorted(alertes, key=lambda x: ordre[x["niveau"]])

    for a in alertes_triees:
        badge = couleurs_badge[a["niveau"]]
        with st.expander(f"{badge} {a['actif']} — {a['niveau']}"):
            col1, col2, col3 = st.columns(3)
            col1.metric("Prix actuel", a["prix"])
            col2.metric("Rendement du jour", f"{a['rendement_jour']} %")
            col3.metric("Volatilite 30j", f"{a['volatilite_30j']} %")
            st.info(f"Analyse : {' | '.join(a['raisons'])}")