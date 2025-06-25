import streamlit as st, difflib
from data.loader import load_image_urls
import subprocess

def paginate_games(games, page, per_page=4):
    start = page * per_page
    return games[start:start+per_page]

def render_game_grid(game_names, game_logos):
    if 'page' not in st.session_state:
        st.session_state.page = 0
    total = len(game_names)
    pages = total // 4 + (1 if total % 4 else 0)
    games = paginate_games(game_names, st.session_state.page)
    cols = st.columns(4)
    for i, game in enumerate(games):
        with cols[i]:
            if i < len(game_logos):
                st.image(game_logos[game_names.index(game)], caption=game, use_container_width=True)
            if st.button("🟢 Sélectionner", key=f"sel_{st.session_state.page}_{i}"):
                st.session_state.selected_game = game
    col1, _, col3 = st.columns([3,16,1])
    with col1:
        if st.button("Précédent"):
            if st.session_state.page > 0:
                st.session_state.page -= 1
                st.rerun()
    with col3:
        if st.button("Suivant"):
            if st.session_state.page < pages - 1:
                st.session_state.page += 1
                st.rerun()



def search_bar(game_names):
    # Réinitialisation de la barre si demandé
    if st.session_state.get('clear_search'):
        st.session_state['search'] = ''
        st.session_state['clear_search'] = False

    # Barre de recherche
    search = st.text_input("Cherchez votre jeu ici...", value=st.session_state.get('search', ''), key='search').strip()

    # Message après ajout via scraping
    if st.session_state.get('game_added'):
        st.success(f"✅ Le jeu **{st.session_state['game_added']}** existe déjà localement (après scraping).")
        st.session_state['game_added'] = None

    if search:
        lower_game_names = [g.lower() for g in game_names]
        matches = difflib.get_close_matches(search.lower(), lower_game_names, n=1, cutoff=0.6)

        if matches:
            match_lower = matches[0]
            match_index = lower_game_names.index(match_lower)
            match = game_names[match_index]

            # Calcul de la page (4 jeux par page)
            page_index = match_index // 4

            # Mise à jour de l'état
            st.session_state.selected_game = match
            st.session_state.page = page_index

            # Affichage du message
            st.success(f"🎯 Jeu trouvé : **{match}** (position : `{match_index}` → page `{page_index}`)")

        else:
            st.warning(f"❌ Aucun jeu trouvé localement pour : {search}")
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
                    st.error("❌ Échec du scraping.")
                    st.text(e.stderr)
                    st.rerun()





