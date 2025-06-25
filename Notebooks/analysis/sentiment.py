import time, streamlit as st
from config.mistral_config import CLIENT, MODEL
from utils.markdown import clean_markdown

def incremental_display(text, delay=0.5):
    disp = st.empty()
    cleaned = clean_markdown(text)
    full = "<div style=\"background-color:#1f1f1f; border:2px solid #1DB954; padding:20px; margin-top:20px; margin-bottom:30px; max-height:400px; overflow-y:auto; font-family:'Arial'; font-size:1em; line-height:1.6; color:#fff;\">"
    for sec in cleaned.split("\n\n"):
        full += f"{sec}<br><br>"
        time.sleep(delay)
        disp.markdown(f'{full}▌</div>', unsafe_allow_html=True)
    disp.markdown(f'{full}</div>', unsafe_allow_html=True)

def analyze_comments(comments, game_name):
    start = time.time()
    prompt = (
        f"Analyse les avis suivants pour {game_name}…\n\n" +
        "\n".join([f"{i+1}. \"{c}\"" for i, c in enumerate(comments)]) +
        "\n\nSynthèse :"
    )
    resp = CLIENT.chat.complete(model=MODEL, messages=[{"role":"system","content":prompt}])
    elapsed = time.time() - start
    st.write(f"Temps d'analyse : {elapsed:.2f} secondes pour {len(comments)} avis.")
    content = resp.choices[0].message.content
    incremental_display(content)
    return content
