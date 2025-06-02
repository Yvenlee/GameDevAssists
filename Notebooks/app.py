import streamlit as st
import json
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

@st.cache_data
def load_games_data():
    with open("games.json", "r", encoding="utf-8") as f:
        return json.load(f)

@st.cache_resource
def load_pipeline():
    model_id = "mistralai/Mistral-7B-Instruct-v0.1"
    tokenizer = AutoTokenizer.from_pretrained(model_id, use_auth_token=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        use_auth_token=True,
        device_map="auto",
        torch_dtype="auto",
    )
    return pipeline("text-generation", model=model, tokenizer=tokenizer)

st.title("🎮 Analyse des Avis Joueurs (Steam)")

games_data = load_games_data()

selected_game = st.selectbox("Sélectionne un jeu :", list(games_data.keys()))

if selected_game:
    comments = [rev["Comment"].strip() for rev in games_data[selected_game] if rev["Comment"].strip()]
    st.write(f"Nombre d'avis disponibles : {len(comments)}")

    if len(comments) == 0:
        st.warning("Aucun commentaire disponible pour ce jeu.")
    else:
        if st.button("🔍 Lancer l'analyse des sentiments"):
            pipe = load_pipeline()

            comments_to_use = comments[:30]

            prompt = f"Voici des avis de joueurs pour le jeu '{selected_game}' :\n"
            for i, comment in enumerate(comments_to_use, 1):
                prompt += f"{i}. \"{comment}\"\n"

            prompt += """
Génère une synthèse : Quel est l'avis général ? Que faut-il améliorer ?
"""

            with st.spinner("Génération du rapport en cours..."):
                result = pipe(prompt, max_new_tokens=300, do_sample=True, temperature=0.7)

            st.subheader("📋 Rapport d'analyse généré")
            st.write(result[0]["generated_text"])
