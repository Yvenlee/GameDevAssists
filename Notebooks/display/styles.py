import streamlit as st

def apply_styles():
    st.set_page_config(page_title="Analyse Jeux Steam", layout="wide")
    st.markdown("""
    <style>
    .incremental-text { font-family: 'Arial', sans-serif; font-size: 1em; }
    .section-title { font-weight: bold; margin-top: 10px; }
    .title { text-align: center; font-size: 3em; margin-top: -30px; margin-bottom: 20px; color: #1DB954; }
    .game-img { transition: transform 0.2s ease; border-radius: 12px; border: 2px solid transparent; }
    .game-img:hover { transform: scale(1.03); border-color: #1DB954; cursor: pointer; }
    .footer { margin-top: 3rem; text-align: center; font-size: 0.9em; color: #aaa; }
    .stApp { background: linear-gradient(135deg, #2a4b7d, #2b2b2b); color: #fff; }
    input::placeholder { color: #aaa; font-style: italic; opacity: 0.7; }
    </style>
    """, unsafe_allow_html=True)
