import pandas as pd
import plotly.express as px
import streamlit as st
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import string
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from collections import Counter
import re
import difflib

def get_similar_to_game_name(game_name, comments, cutoff=0.75):
    game_tokens = re.findall(r"\w+", game_name.lower())
    game_joined = ''.join(game_tokens)

    all_words = set()
    for text in comments:
        tokens = re.findall(r"\w+", text.lower())
        all_words.update(tokens)

    similar_words = set()
    for word in all_words:
        ratio = difflib.SequenceMatcher(None, word, game_joined).ratio()
        if ratio >= cutoff:
            similar_words.add(word)
    return similar_words

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

    fig2 = px.histogram(
        df.dropna(subset=["Hours Played"]),
        x="Hours Played",
        nbins=30,
        title="Distribution des heures jouées",
        labels={"Hours Played": "Heures jouées"},
        color_discrete_sequence=["#FFD700"]
    )

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

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig1, use_container_width=True)
        st.plotly_chart(fig3, use_container_width=True)
    with col2:
        st.plotly_chart(fig2, use_container_width=True)
        st.plotly_chart(fig4, use_container_width=True)

    st.plotly_chart(fig6, use_container_width=True)
    st.plotly_chart(fig7, use_container_width=True)

    # Nuage de mots dynamique par année
    st.markdown("### Nuage de mots basé sur les commentaires (filtrable par année)")

    # Sélection de l’année
    df["Année"] = df["Date Posted"].dt.year
    années_disponibles = sorted(df["Année"].dropna().unique().astype(int), reverse=True)
    col_text, col_cloud = st.columns([1, 2])

    with col_text:
        annee_selectionnee = st.selectbox("Choisir une année :", années_disponibles)

    df_annee = df[df["Année"] == annee_selectionnee]
    comments = df_annee["Comment"].dropna().astype(str)

    similar_words = get_similar_to_game_name(game_name, comments, cutoff=0.5)

    custom_stopwords = set(STOPWORDS)
    custom_stopwords.update(similar_words)
    custom_stopwords.update([
        game_name.lower(),

        # Pronoms personnels français
        "je", "j'", "jai", "j'ai", "tu", "il", "elle", "on", "nous", "vous", "ils", "elles", "pas", "jeu"
        
        # Pronoms personnels anglais
        "i", "i'm", "im", "i am", "you", "u", "ur", "your", "you're", "youre", "he", "she", "we", "they", "me", "him", "her", "us", "them",
        "mine", "yours", "his", "hers", "ours", "theirs", "my", "our", "their", "its", "it's", "it is", "it",

        # Déterminants/articles français
        "le", "la", "les", "l", "un", "une", "des", "du", "de", "d", "ce", "cet", "cette", "ces", "mon", "ton", "son", "notre", "votre", "leur",
        
        # Déterminants/articles anglais
        "a", "an", "the",

        # Mots de liaison / prépositions / auxiliaires français
        "et", "ou", "où", "mais", "donc", "or", "ni", "car", "à", "en", "dans", "sur", "sous", "par", "pour", "avec", "sans", "comme",
        "que", "qui", "quoi", "dont", "au", "aux", "ceci", "cela", "ça", "c'", "cest", "c'est", "y", "là", "si", "se", "sa", "ses", "leurs",

        # Conjonctions / auxiliaires anglais
        "and", "or", "but", "so", "because", "if", "when", "then", "that", "which", "who", "whom", "whose", "what", "how", "this", "these", "those", "there", "here", "where", "while", "to", "of", "on", "in", "at", "by", "from", "with", "about", "into", "over", "under", "before", "after", "between", "during", "without", "again", "still",

        # Verbes avoir/être français
        "ai", "as", "a", "avons", "avez", "ont", "avais", "avait", "avions", "aviez", "avaient",
        "suis", "es", "est", "sommes", "êtes", "sont", "étais", "était", "étions", "étiez", "étaient",

        # Verbes être/avoir anglais
        "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having",

        # Contractions anglaises courantes
        "i've", "ive", "i'd", "id", "i'll", "ill", "you're", "youre", "you'll", "youve", "you'd", "youll",
        "he's", "hes", "he'll", "he'd", "she's", "shes", "she'll", "she'd", "we're", "were", "we've", "weve", "we'll", "we'd",
        "they're", "theyre", "they've", "theyve", "they'll", "they'd", "it's", "its", "it'll", "it'd", "that's", "thats", "there's", "theres",

        # Mots passe-partout inutiles
        "yes", "no", "ok", "okay", "lol", "lmao", "rofl", "haha", "mdr", "ptdr", "omg", "wtf", "bro", "dude", "man", "yo", "hey", "hi",
        "sorry", "welcome", "gg", "wp", "ez", "hard", "easy", "nice", "cool", "great", "awesome", "fun",

        # Mots liés au jeu (souvent présents)
        "game", "games", "gaming", "play", "played", "playing", "plays", "player", "players", "match", "matches", "round", "team", "teams",
        "win", "won", "lose", "lost", "victory", "defeat", "fight", "fighting", "killed", "kill", "kills", "death", "deaths", "jeux", "jeu",
        # Qualificatifs passe-partout
        "good", "bad", "better", "best", "worst", "amazing", "awful", "real", "really", "very", "too", "much", "many", "more", "most", "less",
        "few", "some", "same", "such", "other", "another", "each", "every", "all", "none", "nothing", "something", "anything", "everything",

        # Fausses itérations de mots fréquents
        "j", "j'ai", "jai", "im", "i'm", "ive", "i've", "id", "i'd", "ill", "i'll", "youre", "you're", "u", "ur", "c", "c'est", "cest", "dont", "didnt", "didn't", "wasnt", "wasn't", "isnt", "isn't", "cant", "can't",
        "couldnt", "couldn't", "wouldnt", "wouldn't", "shouldnt", "shouldn't", "wont", "won't", "dont", "don't", "doesnt", "doesn't",
    ])



    translator = str.maketrans('', '', string.punctuation + string.digits)
    words = [
        word.lower().translate(translator)
        for text in comments
        for word in text.split()
        if len(word) > 2 and word.lower().translate(translator) not in custom_stopwords
    ]
    cleaned_text = " ".join(words)
    word_freq = Counter(words)
    top_words = word_freq.most_common(5)

    with col_text:
        st.subheader(f"Top 5 mots ({annee_selectionnee})")
        for word, freq in top_words:
            st.metric(label=f"Mot : {word}", value=f"{freq} occurrences")

    with col_cloud:
        rainbow_cmap = LinearSegmentedColormap.from_list(
            "custom_rainbow",
            ["#9c0000", "#008cff", "#00790A", "#9c8500", "#e27900", "#602c85", "#a939ff"]
        )
        wordcloud = WordCloud(
            width=1000,
            height=500,
            background_color="#1e1e2f",
            max_words=150,
            stopwords=custom_stopwords,
            colormap=rainbow_cmap,
            collocations=False,
            prefer_horizontal=0.85,
            random_state=42
        ).generate(cleaned_text)

        fig_wc, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig_wc)
