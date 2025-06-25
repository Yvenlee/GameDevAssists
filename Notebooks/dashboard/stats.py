import pandas as pd, plotly.express as px, streamlit as st

def display_dashboard(data, game_name):
    df = pd.DataFrame(data)
    df["Recommended"] = pd.to_numeric(df["Recommended"], errors="coerce")
    df["Hours Played"] = pd.to_numeric(df["Hours Played"], errors="coerce")
    df["Date Posted"] = pd.to_datetime(df["Date Posted"], errors="coerce")

    st.markdown(f"### Jeu sélectionné pour le dashboard : **{game_name}**")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Nombre d'avis total", len(df))
    with c2:
        st.metric("Heures jouées moyenne", f"{df['Hours Played'].mean():.2f} h")
    with c3:
        st.metric("Heures jouées max", f"{df['Hours Played'].max():.2f} h")

    # Répartition des recommandations (pie)
    rec = df["Recommended"].value_counts().sort_index()
    fig1 = px.pie(
        names=rec.index.map({1: "Recommandé", 0: "Non recommandé"}),
        values=rec.values,
        title="Répartition des recommandations"
    )

    # Distribution des heures jouées (histogramme)
    fig2 = px.histogram(
        df.dropna(subset=["Hours Played"]),
        x="Hours Played",
        nbins=30,
        title="Distribution des heures jouées"
    )

    # Nombre d'avis postés dans le temps (timeline)
    times = df.dropna(subset=["Date Posted"]).groupby("Date Posted").size().reset_index(name="count")
    fig3 = px.line(
        times,
        x="Date Posted",
        y="count",
        title="Nombre d'avis postés au fil du temps"
    )

    # Nouveau graphique : boxplot des heures jouées selon recommandation
    box_df = df.dropna(subset=["Hours Played", "Recommended"])
    box_df["Recommended Label"] = box_df["Recommended"].map({1: "Recommandé", 0: "Non recommandé"})
    fig4 = px.box(
        box_df,
        x="Recommended Label",
        y="Hours Played",
        title="Répartition des heures jouées selon recommandation"
    )

    # Affichage en 2 colonnes, 2 graphiques par colonne
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig1, use_container_width=True)
        st.plotly_chart(fig3, use_container_width=True)
    with col2:
        st.plotly_chart(fig2, use_container_width=True)
        st.plotly_chart(fig4, use_container_width=True)