import json
import re
from datetime import datetime

def parse_hours_played(hours_str):
    if not isinstance(hours_str, str):
        return None
    match = re.search(r"([\d,\.]+)\s*hrs", hours_str)
    if match:
        num_str = match.group(1).replace(",", "")
        try:
            return float(num_str)
        except ValueError:
            return None
    return None

def parse_date_posted(date_str):
    if not isinstance(date_str, str):
        return None
    date_part = date_str.replace("Posted:", "").strip()
    for fmt in ("%d %B, %Y", "%B %d, %Y"):
        try:
            dt = datetime.strptime(date_part, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def clean_recommended(rec_str):
    if not isinstance(rec_str, str):
        return None
    rec_str = rec_str.strip().lower()
    if rec_str == "recommended":
        return 1
    elif rec_str == "not recommended":
        return 0
    else:
        return None

def clean_games_data(input_path="C:/Users/yvenl/OneDrive/Bureau/GameDevAssists/Data/games.json", output_path="games_cleaned.json"):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    cleaned_data = {}

    for game_name, reviews in data.items():
        cleaned_reviews = []
        for rev in reviews:
            recommended = clean_recommended(rev.get("Recommended"))
            if recommended is None:
                continue  # ignorer les avis ambigus
            hours_played = parse_hours_played(rev.get("Hours Played"))
            date_posted = parse_date_posted(rev.get("Date Posted"))
            comment = rev.get("Comment", "").strip()

            cleaned_review = {
                "Recommended": recommended,
                "Hours Played": hours_played,
                "Date Posted": date_posted,
                "Comment": comment
            }
            cleaned_reviews.append(cleaned_review)
        if cleaned_reviews:
            cleaned_data[game_name] = cleaned_reviews

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    clean_games_data()
    print("Nettoyage terminé, fichier games_cleaned.json créé.")
