import pandas as pd
import plotly.express as px
import streamlit as st

def display_dashboard(data, game_name):
    df = pd.DataFrame(data)
    df["Recommended"] = pd.to_numeric(df["Recommended"], errors="coerce")
    df["Hours Played"] = pd.to_numeric(df["Hours Played"], errors="coerce")
    df["Date Posted"] = pd.to_datetime(df["Date Posted"], errors="coerce")

    st.markdown(f"### Jeu sélectionné pour le dashboard : **{game_name}**")

    # Métriques principales
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Nombre d'avis total", len(df))
    with c2:
        st.metric("Heures jouées moyenne", f"{df['Hours Played'].mean():.2f} h")
    with c3:
        st.metric("Heures jouées max", f"{df['Hours Played'].max():.2f} h")

    # Camembert recommandations
    rec_counts = {
        "Recommandé": df["Recommended"].eq(1).sum(),
        "Non recommandé": df["Recommended"].eq(0).sum()
    }
    rec_df = pd.DataFrame({
        "Recommandation": list(rec_counts.keys()),
        "Valeurs": list(rec_counts.values())
    })

    fig1 = px.pie(
        rec_df,
        names="Recommandation",
        values="Valeurs",
        title="Répartition des recommandations",
        color="Recommandation",
        color_discrete_map={
            "Recommandé": "#2ca02c",
            "Non recommandé": "#d62728"
        }
    )

    # Histogramme heures jouées
    fig2 = px.histogram(
        df.dropna(subset=["Hours Played"]),
        x="Hours Played",
        nbins=30,
        title="Distribution des heures jouées",
        labels={"Hours Played": "Heures jouées"},
        color_discrete_sequence=["#FFD700"]
    )

    # Barres empilées (avis par tranche d'heures)
    df_binned = df.dropna(subset=["Hours Played", "Recommended"]).copy()
    df_binned["Tranche d'heures"] = pd.cut(
        df_binned["Hours Played"],
        bins=[0, 1, 5, 20, 100, float("inf")],
        labels=["<1h", "1–5h", "5–20h", "20–100h", "100h+"]
    )
    counts = df_binned.groupby(["Tranche d'heures", "Recommended"]).size().reset_index(name="count")
    counts["Type d'avis"] = counts["Recommended"].map({1: "Positif", 0: "Négatif"})
    total_per_bin = counts.groupby("Tranche d'heures")["count"].transform("sum")
    counts["Pourcentage"] = counts["count"] / total_per_bin * 100

    fig3 = px.bar(
        counts,
        x="Tranche d'heures",
        y="Pourcentage",
        color="Type d'avis",
        title="Proportion d'avis positifs et négatifs par tranche d'heures jouées (100%)",
        labels={"Tranche d'heures": "Tranche d'heures jouées", "Pourcentage": "Pourcentage (%)"},
        text_auto=".1f",
        color_discrete_map={
            "Positif": "#2ca02c",
            "Négatif": "#d62728"
        }
    )
    fig3.update_layout(barmode="stack", yaxis=dict(ticksuffix="%"))

    # Boxplot (sans outliers)
    box_df = df.dropna(subset=["Hours Played", "Recommended"])
    Q1 = box_df["Hours Played"].quantile(0.25)
    Q3 = box_df["Hours Played"].quantile(0.75)
    IQR = Q3 - Q1
    box_df = box_df[(box_df["Hours Played"] >= Q1 - 1.5 * IQR) & (box_df["Hours Played"] <= Q3 + 1.5 * IQR)]
    box_df["Recommended Label"] = box_df["Recommended"].map({1: "Recommandé", 0: "Non recommandé"})

    fig4 = px.box(
        box_df,
        x="Recommended Label",
        y="Hours Played",
        title="Répartition des heures jouées selon recommandation (sans valeurs aberrantes)",
        labels={"Recommended Label": "Recommandation", "Hours Played": "Heures jouées"}
    )

    # Ligne évolution médiane
    df_time_hours = df.dropna(subset=["Date Posted", "Hours Played"]).copy()
    df_time_hours["Mois"] = df_time_hours["Date Posted"].dt.to_period("M").dt.to_timestamp()
    median_per_month = df_time_hours.groupby("Mois")["Hours Played"].median().reset_index()

    fig6 = px.line(
        median_per_month,
        x="Mois",
        y="Hours Played",
        title="Évolution médiane du temps de jeu (heures) par mois",
        labels={"Hours Played": "Heures jouées", "Mois": "Date"},
        markers=True,
        color_discrete_sequence=["#925dc4"]
    )

        # Tendance des avis au fil du temps
    df_time_rec = df.dropna(subset=["Date Posted", "Recommended"]).copy()
    df_time_rec["Mois"] = df_time_rec["Date Posted"].dt.to_period("M").dt.to_timestamp()
    df_time_rec["Type d'avis"] = df_time_rec["Recommended"].map({1: "Positif", 0: "Négatif"})
    rec_trend = df_time_rec.groupby(["Mois", "Type d'avis"]).size().reset_index(name="Nombre d'avis")

    fig7 = px.line(
        rec_trend,
        x="Mois",
        y="Nombre d'avis",
        color="Type d'avis",
        title="Évolution du nombre d'avis positifs et négatifs par mois",
        markers=True,
        labels={"Mois": "Date", "Nombre d'avis": "Nombre d'avis"},
        color_discrete_map={"Positif": "#2ca02c", "Négatif": "#d62728"}
    )

    

    # Affichage en colonnes
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig1, use_container_width=True)
        st.plotly_chart(fig3, use_container_width=True)
    with col2:
        st.plotly_chart(fig2, use_container_width=True)
        st.plotly_chart(fig4, use_container_width=True)

    # Ligne en bas
    st.plotly_chart(fig6, use_container_width=True)
    st.plotly_chart(fig7, use_container_width=True)

