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

# Logos des jeux dans l'ordre de games.json
game_logos = [
    "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/291550/71448f1f413d5aac25b8dd08068f0f284f7bacf7/header.jpg?t=1747253897",
    "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/485510/header.jpg?t=1737983043",
    "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/230410/73f2628439b0f5e28bf9398405a78f8d5dedd73b/header.jpg?t=1748645305",
    "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/381210/header.jpg?t=1746584187",
    "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/588650/header.jpg?t=1747319767"
]

# Chargement JSON
def load_games_data():
    with open("games.json", "r", encoding="utf-8") as f:
        return json.load(f)

# Appel API
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
    return chat_response.choices[0].message.content

# Envoi Email
def send_email(receiver_email, file_path, game_title):
    sender_email = "yvenlycee@gmail.com"
    sender_password = "stsuvlpolprhvsbm"

    # Créer l'email
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = f"Rapport d'analyse - {game_title}"

    # Corps du message
    body = f"""Bonjour,

Veuillez trouver ci-joint le rapport d'analyse du jeu « {game_title} ».

Cordialement.
"""
    msg.attach(MIMEText(body, "plain"))

    # Joindre le fichier
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

    # Envoi via SMTP Gmail
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as serveur:
            serveur.login(sender_email, sender_password)
            serveur.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Erreur lors de l'envoi de l'email : {e}")
        return False


# Page setup et style
st.set_page_config(page_title="Analyse Jeux Steam", layout="wide")
st.markdown("""
    <style>
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

st.markdown('<h1 class="title">🎮 Mistral Vision Steam</h1>', unsafe_allow_html=True)

games_data = load_games_data()
game_names = list(games_data.keys())

# Barre de recherche
search_game = st.text_input("", placeholder="Cherchez votre jeu ici...").strip()
if search_game:
    st.session_state["selected_game"] = search_game

# Affichage logos uniquement si aucun texte saisi
if not search_game:
    st.markdown("### Choisis un jeu à analyser :")
    cols = st.columns(len(game_names))
    for i, col in enumerate(cols):
        with col:
            st.image(game_logos[i], caption=game_names[i], use_container_width=True)
            if st.button(f"🟢 Sélectionner", key=f"select_{i}"):
                st.session_state["selected_game"] = game_names[i]

# Suite après sélection
if "selected_game" in st.session_state:
    selected_game = st.session_state["selected_game"]
    st.markdown(f"## Jeu sélectionné : **{selected_game}**")

    if selected_game in games_data:
        raw_data = games_data[selected_game]
        df = pd.DataFrame(raw_data)[["Recommended", "Hours Played", "Date Posted", "Comment"]]
        st.markdown("### Base de données des avis collectés")
        st.dataframe(df, use_container_width=True, height=350)

        comments = [rev["Comment"].strip() for rev in raw_data if rev["Comment"].strip()]
    else:
        comments = []

    st.write(f"Nombre d'avis disponibles : {len(comments)}")

    if not comments:
        st.warning("Aucun commentaire disponible pour ce jeu.")
    else:
        # Utilisation de st.number_input pour choisir le nombre d'avis
        n_comments_input = st.number_input(
            "Nombre d'avis à analyser :",
            min_value=1,
            max_value=len(comments),
            value=min(5, len(comments)),
            key="n_comments_input"
        )

        # Mise à jour dynamique du slider
        if 'n_comments' not in st.session_state:
            st.session_state.n_comments = n_comments_input

        n_comments = st.slider(
            "Ajustez le nombre d'avis à analyser :",
            1,
            len(comments),
            st.session_state.n_comments,
            key="n_comments_slider"
        )

        # JavaScript pour mettre à jour le slider lorsque l'utilisateur appuie sur Entrée
        st.components.v1.html("""
            <script>
            document.addEventListener('keydown', function(event) {
                if (event.key === 'Enter') {
                    const input = document.querySelector('input[value=""" + str(n_comments_input) + """]');
                    if (input) {
                        const event = new Event('change');
                        input.dispatchEvent(event);
                        setTimeout(() => {
                            window.location.reload();
                        }, 100);
                    }
                }
            });
            </script>
        """)

        if st.button("Lancer l'analyse des sentiments"):
            selected_comments = comments[:n_comments]
            with st.spinner("Génération du rapport en cours..."):
                analysis_result = analyze_comments(selected_comments, selected_game)
                st.subheader("Rapport d'analyse généré")
                st.write(analysis_result)

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

# --- Charger les données nettoyées ---
@st.cache_data
def load_cleaned_data():
    with open("games_cleaned.json", "r", encoding="utf-8") as f:
        return json.load(f)

# --- Section Dashboard toujours visible ---
st.markdown("## 📊 Dashboard Statistiques & Graphiques")
cleaned_data = load_cleaned_data()

# Récupérer automatiquement le même jeu sélectionné
selected_game_dash = st.session_state.get("selected_game")

if selected_game_dash and selected_game_dash in cleaned_data:
    data = cleaned_data[selected_game_dash]
    df = pd.DataFrame(data)

    # Formatage des colonnes
    df["Recommended"] = pd.to_numeric(df["Recommended"], errors="coerce")
    df["Hours Played"] = pd.to_numeric(df["Hours Played"], errors="coerce")
    df["Date Posted"] = pd.to_datetime(df["Date Posted"], errors="coerce")

    st.markdown(f"### Jeu sélectionné pour le dashboard : **{selected_game_dash}**")

    # Statistiques globales
    st.write(f"- Nombre d'avis total : {len(df)}")
    st.write(f"- Heures jouées moyenne : {df['Hours Played'].mean():.2f} heures")
    st.write(f"- Heures jouées max : {df['Hours Played'].max():.2f} heures")

    # Pie chart recommandation
    rec_counts = df["Recommended"].value_counts().sort_index()
    fig_rec = px.pie(
        names=rec_counts.index.map({1: "Recommandé", 0: "Non recommandé"}),
        values=rec_counts.values,
        title="Répartition des recommandations"
    )
    st.plotly_chart(fig_rec, use_container_width=True)

    # Histogramme heures jouées
    fig_hours = px.histogram(
        df.dropna(subset=["Hours Played"]),
        x="Hours Played", nbins=30,
        title="Distribution des heures jouées"
    )
    st.plotly_chart(fig_hours, use_container_width=True)

    # Graph avis dans le temps
    df_sorted = df.dropna(subset=["Date Posted"]).sort_values("Date Posted")
    df_grouped = df_sorted.groupby("Date Posted").size().reset_index(name='count')
    fig_time = px.line(df_grouped, x="Date Posted", y="count",
                       title="Nombre d'avis postés au fil du temps")
    st.plotly_chart(fig_time, use_container_width=True)

    # 🗨️ Commentaires récents
    with st.expander("Voir quelques commentaires récents"):
        for c in df_sorted.sort_values("Date Posted", ascending=False)["Comment"].head(10):
            if c.strip():
                st.write("- ", c)

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

