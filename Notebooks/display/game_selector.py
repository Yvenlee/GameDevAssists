import streamlit as st, difflib
from cleaner.traitement import clean_games_data
from data.loader import load_image_urls
import subprocess

def paginate_games(games, page, per_page=4):
    start = page * per_page
    return games[start:start+per_page]

def render_game_grid(game_names, game_logos):
    if 'page' not in st.session_state:
        st.session_state.page = 0

    total = len(game_names)
    per_page = 4
    pages = total // per_page + (1 if total % per_page else 0)
    games = paginate_games(game_names, st.session_state.page)

    cols = st.columns(4)
    for i, game in enumerate(games):
        with cols[i]:
            if i < len(game_logos):
                st.image(game_logos[game_names.index(game)], caption=game, use_container_width=True)
            if st.button(":star2: Sélectionner", key=f"sel_{st.session_state.page}_{i}"):
                st.session_state.selected_game = game

    col1, _, col3 = st.columns([3,16,1])
    with col1:
        if st.button("Précédent"):
            if st.session_state.page > 0:
                st.session_state.page -= 1
                _clear_selected_if_out_of_view(game_names, per_page)
                st.rerun()
    with col3:
        if st.button("Suivant"):
            if st.session_state.page < pages - 1:
                st.session_state.page += 1
                _clear_selected_if_out_of_view(game_names, per_page)
                st.rerun()

def _clear_selected_if_out_of_view(game_names, per_page):
    if 'selected_game' in st.session_state:
        selected = st.session_state.selected_game
        if selected in game_names:
            idx = game_names.index(selected)
            current_page = st.session_state.page
            if idx // per_page != current_page:
                del st.session_state.selected_game


def search_bar(game_names):
    if st.session_state.get('clear_search'):
        st.session_state['search'] = ''
        st.session_state['clear_search'] = False

    col1, col2 = st.columns([11, 1])
    with col1:
        search = st.text_input(
            label="",
            key='search',
            placeholder="Entrez votre jeu ici puis validez en cliquant sur Rechercher...",
            label_visibility="collapsed"
        )

    with col2:
        if st.button(":cyclone: Rechercher"):
            if search:
                lower_game_names = [g.lower() for g in game_names]
                matches = difflib.get_close_matches(search.lower(), lower_game_names, n=1, cutoff=0.68)

                if matches:
                    match_lower = matches[0]
                    match_index = lower_game_names.index(match_lower)
                    match = game_names[match_index]

                    page_index = match_index // 4

                    st.session_state.selected_game = match
                    st.session_state.page = page_index
                    st.session_state['search_result'] = ('success', f"🎯 Jeu trouvé : **{match}** (position : `{match_index}` → page `{page_index}`)")

                else:
                    st.session_state['search_result'] = ('warning', f"❌ Aucun jeu trouvé localement pour : {search}")
                    with st.spinner("🔄 Scraping en cours..."):
                        try:
                            result = subprocess.run(
                                ["python", r"C:\Users\yvenl\OneDrive\Bureau\GameDevAssists\Notebooks\scraping\scrapingfusion.py", search],
                                check=True,
                                capture_output=True,
                                text=True
                            )
                            st.session_state['clear_search'] = True
                            st.session_state['game_added'] = search
                            st.rerun()
                        except subprocess.CalledProcessError as e:
                            st.session_state['search_result'] = ('error', "❌ Échec du scraping.")
                            st.session_state['scraping_error'] = e.stderr
                            st.rerun()

    # 2. Affichage des messages en dessous de la barre
    if st.session_state.get('search_result'):
        msg_type, msg = st.session_state['search_result']
        if msg_type == 'success':
            st.success(msg)
        elif msg_type == 'warning':
            st.warning(msg)
        elif msg_type == 'error':
            st.error(msg)
        del st.session_state['search_result']

    if st.session_state.get('scraping_error'):
        st.text(st.session_state['scraping_error'])
        del st.session_state['scraping_error']

    if st.session_state.get('game_added'):
        st.success(f"Le jeu **{st.session_state['game_added']}** existe déjà localement (après scraping).")
        st.session_state['game_added'] = None

def search_bar(game_names):
    if st.session_state.get('clear_search'):
        st.session_state['search'] = ''
        st.session_state['clear_search'] = False

    # === 1. Barre de recherche ===
    col1, col2, col3 = st.columns([9, 1, 1])
    with col1:
        search = st.text_input(
            label="",
            key='search',
            placeholder="Entrez votre jeu ici puis validez en cliquant sur Rechercher...",
            label_visibility="collapsed"
        )

    with col2:
        if st.button(":cyclone: Rechercher"):
            if search:
                lower_game_names = [g.lower() for g in game_names]
                matches = difflib.get_close_matches(search.lower(), lower_game_names, n=1, cutoff=0.65)

                if matches:
                    match_lower = matches[0]
                    match_index = lower_game_names.index(match_lower)
                    match = game_names[match_index]
                    page_index = match_index // 4

                    st.session_state.selected_game = match
                    st.session_state.page = page_index
                    st.session_state['search_result'] = ('success', f"🎯 Jeu trouvé : **{match}** (position : `{match_index}` → page `{page_index}`)")

                else:
                    st.session_state['search_result'] = ('warning', f"❌ Aucun jeu trouvé localement pour : **{search}**")
                    st.session_state['missing_game'] = search

    with col3:
        if st.button(":dizzy: Optimisation"):
            with st.spinner("Nettoyage des données en cours..."):
                output_path = clean_games_data()
                st.session_state['search_result'] = ('success', f"Optimisation terminée. Vous pouvez désormais accéder à la partie Dashboard du jeu de votre choix.")

    # === 2. Scraping si le jeu est introuvable ===
    if st.session_state.get('missing_game'):
        game_to_scrape = st.session_state['missing_game']
        st.session_state['scrape_prompt'] = f"💡 Le jeu **{game_to_scrape}** n'existe pas dans la base. Voulez-vous le scraper ?"

        col_scrape, col_cancel = st.columns([2, 1])
        with col_scrape:
            if st.button("🔄 Lancer le scraping", key="scrape_button"):
                with st.spinner("🔄 Scraping en cours..."):
                    try:
                        result = subprocess.run(
                            ["python", "../Notebooks/scraping/scrapingfusion.py", game_to_scrape],
                            check=True,
                            capture_output=True,
                            text=True
                        )
                        st.session_state['clear_search'] = True
                        st.session_state['game_added'] = game_to_scrape
                        del st.session_state['missing_game']
                        st.rerun()
                    except subprocess.CalledProcessError as e:
                        st.session_state['search_result'] = ('error', "❌ Échec du scraping.")
                        st.session_state['scraping_error'] = e.stderr
                        del st.session_state['missing_game']
                        st.rerun()

        with col_cancel:
            if st.button("❌ Ne rien faire", key="cancel_scrape"):
                st.session_state['search_result'] = ('info', "Scraping annulé.")
                del st.session_state['missing_game']

    # === 3. Affichage centralisé des messages ===
    st.markdown("<hr style='margin-top:0;margin-bottom:10px;border:1px solid #444;'/>", unsafe_allow_html=True)

    if st.session_state.get('search_result'):
        msg_type, msg = st.session_state['search_result']
        if msg_type == 'success':
            st.success(msg)
        elif msg_type == 'warning':
            st.warning(msg)
        elif msg_type == 'error':
            st.error(msg)
        elif msg_type == 'info':
            st.info(msg)
        del st.session_state['search_result']

    if st.session_state.get('scrape_prompt'):
        st.info(st.session_state['scrape_prompt'])
        del st.session_state['scrape_prompt']

    if st.session_state.get('scraping_error'):
        st.text(st.session_state['scraping_error'])
        del st.session_state['scraping_error']

    if st.session_state.get('game_added'):
        st.success(f"✅ Le jeu **{st.session_state['game_added']}** a été ajouté avec succès (scraping terminé).")
        st.session_state['game_added'] = None
