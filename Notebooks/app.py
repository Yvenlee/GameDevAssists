import pandas as pd
import streamlit as st
import threading
import time
import json

# --- Tes imports habituels ---
from scraping.scrapingfusion import scraping_generator
from data.loader import load_games_data, load_image_urls, load_cleaned_data
from display.styles import apply_styles
from display.game_selector import search_bar, render_game_grid
from analysis.sentiment import analyze_comments
from dashboard.stats import display_dashboard
from Mail.send_mail import envoyer_email
from cleaner.traitement import clean_games_data

# Applique les styles
apply_styles()

# Chargement données
game_logos = load_image_urls()
games_data = load_games_data()
cleaned_data = load_cleaned_data()
game_names = list(games_data.keys())

st.markdown("<h1 style='text-align: center; color: white;'>Mistral Vision Steam</h1>", unsafe_allow_html=True)
search_bar(game_names) or render_game_grid(game_names, game_logos)

if "selected_game" in st.session_state:
    selected = st.session_state.selected_game
    st.markdown(f"## Jeu sélectionné : **{selected}**")

    # Initialisation état scraping dans session_state
    if "scraping_thread" not in st.session_state:
        st.session_state.scraping_thread = None
    if "stop_flag" not in st.session_state:
        st.session_state.stop_flag = {"stop": False}
    if "extracted_count" not in st.session_state:
        st.session_state.extracted_count = 0
    if "scraping_done" not in st.session_state:
        st.session_state.scraping_done = False

    def run_scraping():
        st.session_state.stop_flag["stop"] = False
        st.session_state.scraping_done = False
        for count in scraping_generator(selected, st.session_state.stop_flag):
            st.session_state.extracted_count = count
            time.sleep(0.1)
            if st.session_state.stop_flag["stop"]:
                break
        st.session_state.scraping_done = True
        st.rerun()

    if selected not in games_data or not games_data[selected]:
        st.warning(f"Le jeu '{selected}' n'a pas été trouvé dans la base de données locale.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Lancer scraping"):
                if st.session_state.scraping_thread and st.session_state.scraping_thread.is_alive():
                    st.warning("Scraping déjà en cours.")
                else:
                    st.session_state.extracted_count = 0
                    st.session_state.stop_flag["stop"] = False
                    thread = threading.Thread(target=run_scraping, daemon=True)
                    st.session_state.scraping_thread = thread
                    thread.start()
        with col2:
            if st.button("Stop scraping"):
                st.session_state.stop_flag["stop"] = True
                st.success("Arrêt du scraping demandé.")

        st.markdown(f"**Avis extraits en live :** {st.session_state.extracted_count}")
        
        st.stop()

    raw = games_data[selected]
    df = pd.DataFrame(raw)[["Recommended","Hours Played","Date Posted","Comment"]]
    st.markdown("Base de données des avis collectés")
    st.dataframe(df, use_container_width=True, height=350)
    
    comments = [r["Comment"].strip() for r in raw if r["Comment"].strip()]
    st.markdown(f"""<div style="border-left:4px solid #1a7fdd;padding-left:10px;margin-bottom:20px;">
        <div style="font-size:14px;color:#aaa;">Nombre d'avis disponibles</div>
        <div style="font-size:24px;color:#1a7fdd;font-weight:bold;">{len(comments)}</div>
    </div>""", unsafe_allow_html=True)
    
    if comments:
        nmax = len(comments)
        sel = st.number_input("Nombre d'avis à analyser :",1,nmax,value=min(5,nmax))
        n = st.slider("Ajustez le nombre d'avis :",1,nmax, sel)
        if st.button("Lancer l'analyse des sentiments"):
            with st.spinner("Génération du rapport en cours..."):
                result = analyze_comments(comments[:n], selected)
                st.subheader("Rapport généré")
                fname = f"rapport_{selected.replace(' ','_')}.txt"
                open(fname,"w",encoding="utf-8").write(result)
                st.download_button("📥 Télécharger le rapport (.txt)", data=result, file_name=fname, mime="text/plain")
                with st.expander("✉️ Envoyer un email avec ou sans pièce jointe"):
                    dest = st.text_input("✉️ Adresse email", "equipedevsteam@gmail.com")
                    subj = st.text_input("📝 Sujet", f"Rapport d'analyse - {selected}")
                    body = st.text_area("📄 Contenu", f"Bonjour,\n\nVeuillez trouver ci-joint le rapport d'analyse du jeu « {selected} ».\nCordialement.",height=150)
                    upload = st.file_uploader("📎 Fichier à joindre", type=["txt","pdf","csv","docx"])
                    use_gen = st.checkbox("📌 Utiliser rapport généré", value=True)
                    if st.button("📨 Envoyer l'e-mail"):
                        if not dest or not subj or not body:
                            st.warning("Merci de remplir tous les champs obligatoires.")
                        else:
                            file_obj = upload if upload else (open(fname,"rb") if use_gen else None)
                            with st.spinner("Envoi en cours..."):
                                ok,msg = envoyer_email(dest, subj, body, file_obj)
                                st.success("✅ "+msg) if ok else st.error("❌ "+msg)
                                if file_obj and not upload: file_obj.close()
    else:
        st.warning("Aucun commentaire disponible pour ce jeu.")

# Dashboard
if st.session_state.get("selected_game") and st.session_state.selected_game in cleaned_data:
    display_dashboard(cleaned_data[st.session_state.selected_game], st.session_state.selected_game)
else:
    st.info("Veuillez sélectionner un jeu pour afficher les statistiques.")

with st.expander("A Propos de cette application", expanded=False):
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1f2937, #374151);
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.6);
        color: #e0e7ff;
        font-family: 'Courier New', Courier, monospace;
        line-height: 1.6;
        border: 1px solid #3b82f6;
    ">
    <strong>Cette application vous permet de rechercher des jeux Steam et d'analyser les avis des utilisateurs grâce à un processus de scraping en temps réel.</strong>
    <br><br>
    <u>Fonctionnalités principales :</u>
    <ul>
        <li>Recherche et sélection de jeux via une barre de recherche ou une grille de jeux.</li>
        <li>Scraping des avis utilisateurs en direct si le jeu n’est pas présent en local.</li>
        <li>Affichage des avis collectés avec possibilité d'analyser les sentiments.</li>
        <li>Génération et téléchargement d'un rapport d'analyse.</li>
        <li>Envoi d'e-mails avec ou sans pièce jointe contenant le rapport.</li>
        <li>Visualisation des statistiques détaillées via un dashboard.</li>
    </ul>
    <u>Développeurs :</u><br>
    - Yvenlee<br>
    - Harrison Ndiba<br>
    </div>
    """, unsafe_allow_html=True)
