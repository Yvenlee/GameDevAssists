import json
import re
from datetime import datetime

FRENCH_MONTHS = {
    "janvier": "January",
    "février": "February",
    "mars": "March",
    "avril": "April",
    "mai": "May",
    "juin": "June",
    "juillet": "July",
    "août": "August",
    "septembre": "September",
    "octobre": "October",
    "novembre": "November",
    "décembre": "December",
}

def parse_hours_played(hours_str):
    if not isinstance(hours_str, str):
        return None
    match = re.search(r"([\d,\.]+)\s*(hrs|h)", hours_str)
    if match:
        num_str = match.group(1).replace(",", "")
        try:
            return float(num_str)
        except ValueError:
            return None
    return None

def translate_french_date_to_english(date_str):
    for fr, en in FRENCH_MONTHS.items():
        date_str = re.sub(fr, en, date_str, flags=re.IGNORECASE)
    return date_str

def parse_date_posted(date_str):
    if not isinstance(date_str, str):
        return None

    date_str = date_str.strip()
    if date_str.lower().startswith("posted:"):
        date_part = date_str.replace("Posted:", "").strip()
    elif "Évaluation publiée le" in date_str:
        date_part = date_str.replace("Évaluation publiée le", "").strip()
        date_part = translate_french_date_to_english(date_part)
    else:
        return None

    for fmt in ("%B %d, %Y", "%d %B %Y", "%d %B, %Y"):
        try:
            dt = datetime.strptime(date_part, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    # Si pas d'année fournie, on ajoute l'année courante
    today = datetime.today()
    for fmt in ("%d %B", "%B %d"):
        try:
            dt = datetime.strptime(date_part, fmt)
            dt = dt.replace(year=today.year)
            if dt > today:
                dt = dt.replace(year=today.year - 1)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    return None

def clean_recommended(rec_str):
    if not isinstance(rec_str, str):
        return None
    rec_str = rec_str.strip().lower()
    if rec_str in ["recommended", "recommandé"]:
        return 1
    elif rec_str in ["not recommended", "non recommandé"]:
        return 0
    else:
        return None

def clean_games_data(input_path="../Notebooks/data/games.json", output_path="../Notebooks/data/games_cleaned.json"):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    cleaned_data = {}

    for game_name, reviews in data.items():
        cleaned_reviews = []
        for rev in reviews:
            recommended = clean_recommended(rev.get("Recommended"))
            if recommended is None:
                continue
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

    return output_path

if __name__ == "__main__":
    path = clean_games_data()
