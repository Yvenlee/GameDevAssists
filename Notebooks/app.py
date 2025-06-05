import os
import json
import time
import streamlit as st
from mistralai import Mistral
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
import plotly.express as px

# Configuration API Mistral
api_key = "Hs0BhW1vJsSKYV41n7QNkFiZNOnTAjcQ"
model = "mistral-large-2411"
client = Mistral(api_key=api_key)
st.set_page_config(page_title="Analyse Jeux Steam", layout="wide")

def load_image_urls():
    file_path = os.path.join("C:\\Users\\yvenl\\OneDrive\\Bureau\\GameDevAssists\\Data", "image_urls.json")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

game_logos = load_image_urls()

def load_games_data():
    file_path = os.path.join("C:\\Users\\yvenl\\OneDrive\\Bureau\\GameDevAssists\\Data", "games.json")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def paginate_games(games, page, per_page=4):
    start = page * per_page
    end = start + per_page
    return games[start:end]

st.markdown("""
    <style>
    .incremental-text {
        font-family: 'Arial', sans-serif;
        font-size: 1em;
    }
    .section-title {
        font-weight: bold;
        margin-top: 10px;
    }
    .title {
        text-align: center;
        font-size: 3em;
        margin-top: -30px;
        margin-bottom: 20px;
        color: #1DB954;
    }
    .game-img {
        transition: transform 0.2s ease;
        border-radius: 12px;
        border: 2px solid transparent;
    }
    .game-img:hover {
        transform: scale(1.03);
        border-color: #1DB954;
        cursor: pointer;
    }
    .footer {
        margin-top: 3rem;
        text-align: center;
        font-size: 0.9em;
        color: #aaa;
    }
    .stApp {
        background: linear-gradient(135deg, #1a1a1a, #2b2b2b);
        color: #fff;
    }
    input::placeholder {
        color: #aaa;
        font-style: italic;
        opacity: 0.7;
    }
    </style>
""", unsafe_allow_html=True)

def incremental_text_display(text, delay=0.02):
    text_display = st.empty()
    full_response = ""
    sections = text.split('\n\n')
    for section in sections:
        if section.startswith("## "):
            full_response += f'<p class="section-title">{section}</p>'
        else:
            full_response += section + '\n\n'
        time.sleep(delay)
        text_display.markdown(f'<div class="incremental-text">{full_response}▌</div>', unsafe_allow_html=True)
    text_display.markdown(f'<div class="incremental-text">{full_response}</div>', unsafe_allow_html=True)

def analyze_comments(selected_comments, game_name):
    start_time = time.time()
    prompt = (
        f"Analyse les avis suivants pour le jeu « {game_name} » et génère une synthèse :\n"
        "1. Quel est le sentiment général pour chaque avis (positif, neutre, négatif) ?\n"
        "2. Quel est l'avis général sur le jeu ?\n"
        "3. Quels sont les points forts et les points faibles mentionnés ?\n"
        "4. Que faut-il améliorer selon les joueurs ?\n\n"
        "Avis :\n" +
        "\n".join([f"{i+1}. \"{c}\"" for i, c in enumerate(selected_comments) if c]) +
        "\n\nSynthèse :"
    )
    message = [{"role": "system", "content": prompt}]
    chat_response = client.chat.complete(model=model, messages=message)
    end_time = time.time()
    elapsed_time = end_time - start_time
    st.write(f"Temps d'analyse : {elapsed_time:.2f} secondes pour {len(selected_comments)} avis.")

    incremental_text_display(chat_response.choices[0].message.content)

    return chat_response.choices[0].message.content

def send_email(receiver_email, file_path, game_title):
    sender_email = "yvenlycee@gmail.com"
    sender_password = "stsuvlpolprhvsbm"

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = f"Rapport d'analyse - {game_title}"

    body = f"""Bonjour,

Veuillez trouver ci-joint le rapport d'analyse du jeu « {game_title} ».

Cordialement.
"""
    msg.attach(MIMEText(body, "plain"))

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            attachment = MIMEText(f.read(), _subtype="plain")
            attachment.add_header(
                "Content-Disposition",
                "attachment",
                filename=os.path.basename(file_path)
            )
            msg.attach(attachment)
    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier à joindre : {e}")
        return False

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as serveur:
            serveur.login(sender_email, sender_password)
            serveur.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Erreur lors de l'envoi de l'email : {e}")
        return False

st.markdown('<h1 class="title">🎮 Mistral Vision Steam</h1>', unsafe_allow_html=True)

games_data = load_games_data()
game_names = list(games_data.keys())

search_game = st.text_input("", placeholder="Cherchez votre jeu ici...").strip()
if search_game:
    st.session_state["selected_game"] = search_game

if not search_game:
    st.markdown("### Choisis un jeu à analyser :")

    if 'page' not in st.session_state:
        st.session_state.page = 0

    games_per_page = 4
    total_pages = len(game_names) // games_per_page + (1 if len(game_names) % games_per_page else 0)

    paginated_games = paginate_games(game_names, st.session_state.page, games_per_page)

    cols = st.columns(len(paginated_games))
    for i, col in enumerate(cols):
        with col:
            game_index = game_names.index(paginated_games[i])
            if game_index < len(game_logos):
                st.image(game_logos[game_index], caption=paginated_games[i], use_container_width=True)
            if st.button(f"🟢 Sélectionner", key=f"select_{i}"):
                st.session_state["selected_game"] = paginated_games[i]

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("Précédent") and st.session_state.page > 0:
            st.session_state.page -= 1
            st.rerun()

    with col3:
        if st.button("Suivant") and st.session_state.page < total_pages - 1:
            st.session_state.page += 1
            st.rerun()

if "selected_game" in st.session_state:
    selected_game = st.session_state["selected_game"]
    st.markdown(f"## Jeu sélectionné : **{selected_game}**")

    if selected_game in games_data:
        raw_data = games_data[selected_game]
        df = pd.DataFrame(raw_data)[["Recommended", "Hours Played", "Date Posted", "Comment"]]
        st.markdown("Base de données des avis collectés")
        st.dataframe(df, use_container_width=True, height=350)

        comments = [rev["Comment"].strip() for rev in raw_data if rev["Comment"].strip()]
    else:
        comments = []


    # Fonction pour créer un metric personnalisé avec une couleur spécifique
    def custom_metric(label, value, color):
        return f"""
        <div style="border-left: 4px solid {color}; padding-left: 10px; margin-bottom: 20px;">
            <div style="font-size: 14px; color: #aaa;">{label}</div>
            <div style="font-size: 24px; color: {color}; font-weight: bold;">{value}</div>
        </div>
        """

    # Utilisation de la fonction custom_metric
    st.markdown(custom_metric("Nombre d'avis disponibles", len(comments), "#1a7fdd"), unsafe_allow_html=True)


    if not comments:
        st.warning("Aucun commentaire disponible pour ce jeu.")
    else:
        n_comments_input = st.number_input(
            "Nombre d'avis à analyser :",
            min_value=1,
            max_value=len(comments),
            value=min(5, len(comments)),
            key="n_comments_input"
        )

        if 'n_comments' not in st.session_state:
            st.session_state.n_comments = n_comments_input

        n_comments = st.slider(
            "Ajustez le nombre d'avis à analyser :",
            1,
            len(comments),
            st.session_state.n_comments,
            key="n_comments_slider"
        )

        if st.button("Lancer l'analyse des sentiments"):
            selected_comments = comments[:n_comments]
            with st.spinner("Génération du rapport en cours..."):
                analysis_result = analyze_comments(selected_comments, selected_game)
                st.subheader("Rapport d'analyse généré")

                file_name = f"rapport_{selected_game.replace(' ', '_')}.txt"
                with open(file_name, "w", encoding="utf-8") as f:
                    f.write(analysis_result)

                st.download_button("📥 Télécharger le rapport (.txt)", data=analysis_result, file_name=file_name, mime="text/plain")

                with st.expander("✉️ Envoyer le rapport par email"):
                    receiver_email = st.text_input("Adresse du destinataire :", value="harrisonndiba338@gmail.com")
                    if st.button("📨 Envoyer par email"):
                        with st.spinner("Envoi en cours..."):
                            if send_email(receiver_email, file_name, selected_game):
                                st.success("✅ Email envoyé avec succès !")

@st.cache_data
def load_cleaned_data():
    file_path = os.path.join("C:\\Users\\yvenl\\OneDrive\\Bureau\\GameDevAssists\\Data", "games_cleaned.json")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# --- Section Dashboard toujours visible ---
st.markdown("## 📊 Dashboard Statistiques & Graphiques")
cleaned_data = load_cleaned_data()

selected_game_dash = st.session_state.get("selected_game")

if selected_game_dash and selected_game_dash in cleaned_data:
    data = cleaned_data[selected_game_dash]
    df = pd.DataFrame(data)

    # Formatage des colonnes
    df["Recommended"] = pd.to_numeric(df["Recommended"], errors="coerce")
    df["Hours Played"] = pd.to_numeric(df["Hours Played"], errors="coerce")
    df["Date Posted"] = pd.to_datetime(df["Date Posted"], errors="coerce")

    st.markdown(f"### Jeu sélectionné pour le dashboard : **{selected_game_dash}**")

    # Utilisation de st.metric pour les statistiques globales
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Nombre d'avis total", value=len(df))
    with col2:
        st.metric(label="Heures jouées moyenne", value=f"{df['Hours Played'].mean():.2f} heures")
    with col3:
        st.metric(label="Heures jouées max", value=f"{df['Hours Played'].max():.2f} heures")

    # Création des graphiques côte à côte
    col1, col2 = st.columns(2)

    with col1:
        # Pie chart recommandation
        rec_counts = df["Recommended"].value_counts().sort_index()
        fig_rec = px.pie(
            names=rec_counts.index.map({1: "Recommandé", 0: "Non recommandé"}),
            values=rec_counts.values,
            title="Répartition des recommandations"
        )
        st.plotly_chart(fig_rec, use_container_width=True)

    with col2:
        # Histogramme heures jouées
        fig_hours = px.histogram(
            df.dropna(subset=["Hours Played"]),
            x="Hours Played",
            nbins=30,
            title="Distribution des heures jouées"
        )
        st.plotly_chart(fig_hours, use_container_width=True)

    # Graph avis dans le temps
    fig_time = px.line(
        df.dropna(subset=["Date Posted"]).groupby("Date Posted").size().reset_index(name='count'),
        x="Date Posted",
        y="count",
        title="Nombre d'avis postés au fil du temps"
    )
    st.plotly_chart(fig_time, use_container_width=True)


    # 🧠 Informations sur le modèle
    with st.expander("Informations sur le modèle"):
        st.markdown("""
        - **Modèle utilisé** : `mistral-large-2411`
        - **API provider** : [Mistral AI](https://mistral.ai)
        - **Utilisation** : Analyse de sentiment sur les commentaires des utilisateurs
        - **Objectif** : Identifier sentiments, points positifs/négatifs, et suggestions d'amélioration.
        """)

    # ℹ️ À propos de l'application
    with st.expander("À propos de"):
        st.markdown("""
        Cette application a été développée pour analyser les avis Steam de jeux vidéo à l’aide d’un modèle LLM.

        **Fonctionnalités principales :**
        - Analyse sémantique des avis
        - Génération de rapport synthétique
        - Envoi du rapport par email
        - Visualisation de statistiques et graphiques dynamiques

        👨‍💻 *Développé avec amour par un passionné de data & IA.*
        """)
else:
    st.info("Veuillez sélectionner un jeu pour afficher les statistiques.")

