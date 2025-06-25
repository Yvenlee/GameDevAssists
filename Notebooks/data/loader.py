import json
import os

def load_json(filename):
    base_dir = os.path.dirname(__file__)
    path = os.path.join(base_dir, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_image_urls():
    try:
        return load_json("image_urls.json")
    except Exception:
        return {}

def load_games_data():
    return load_json("games.json")

def load_cleaned_data():
    return load_json("games_cleaned.json")
