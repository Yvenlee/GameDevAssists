from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import os

GECKODRIVER_PATH = 'C:/Users/yvenl/Downloads/geckodriver-v0.35.0-win32/geckodriver.exe'
FIREFOX_BINARY_PATH = "C:/Program Files/Mozilla Firefox/firefox.exe"

firefox_options = Options()
firefox_options.headless = True
firefox_options.binary_location = FIREFOX_BINARY_PATH
service = Service(executable_path=GECKODRIVER_PATH)

game_links = {
    "Brawlhalla": "https://steamcommunity.com/app/291550/reviews/?p=1&browsefilter=toprated",
    "Nioh": "https://steamcommunity.com/app/485510/reviews/?p=1&browsefilter=toprated",
    "Warframe": "https://steamcommunity.com/app/230410/reviews/?p=1&browsefilter=toprated",
    "Dead by Daylight": "https://steamcommunity.com/app/381210/reviews/?p=1&browsefilter=toprated",
}

json_file = "games.json"

if os.path.exists(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        reviews_data = json.load(f)
else:
    reviews_data = {}

seen_reviews = set()
for game, reviews in reviews_data.items():
    for review in reviews:
        review_id = f"{game}-{review['Recommended']}-{review['Hours Played']}-{review['Date Posted']}-{review['Comment'][:30]}"
        seen_reviews.add(review_id)

def save_json():
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(reviews_data, f, ensure_ascii=False, indent=4)

def extract_reviews(driver, game_name, remaining_limit):
    extracted_count = 0
    review_containers = driver.find_elements(By.CLASS_NAME, "apphub_Card")

    if game_name not in reviews_data:
        reviews_data[game_name] = []

    for container in review_containers:
        if extracted_count >= remaining_limit:
            break
        try:
            recommended = container.find_element(By.CLASS_NAME, "title").text.strip()
            hours_played = container.find_element(By.CLASS_NAME, "hours").text.strip()
            date = container.find_element(By.CLASS_NAME, "date_posted").text.strip()

            comment_container = container.find_element(By.CLASS_NAME, "apphub_CardTextContent")
            comment = driver.execute_script(
                "return arguments[0].childNodes[arguments[0].childNodes.length - 1].textContent;", 
                comment_container
            ).strip()

            review_id = f"{game_name}-{recommended}-{hours_played}-{date}-{comment[:30]}"
            if review_id not in seen_reviews:
                seen_reviews.add(review_id)
                review = {
                    "Recommended": recommended,
                    "Hours Played": hours_played,
                    "Date Posted": date,
                    "Comment": comment
                }
                reviews_data[game_name].append(review)
                extracted_count += 1

        except Exception as e:
            print(f"Erreur pour un avis : {e}")

    if extracted_count > 0:
        save_json()

    return extracted_count

def scroll_and_extract(driver, game_name, count_limit=1500):
    total_extracted = 0
    last_height = driver.execute_script("return document.body.scrollHeight")

    while total_extracted < count_limit:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)
        extracted = extract_reviews(driver, game_name, count_limit - total_extracted)
        total_extracted += extracted

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("Fin du scroll (plus de contenu).")
            break
        last_height = new_height

    print(f"{total_extracted} avis extraits pour {game_name}.")

for game_name, url in game_links.items():
    print(f"\n=== Scraping des avis pour : {game_name} ===")
    driver = webdriver.Firefox(service=service, options=firefox_options)
    try:
        driver.get(url)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "apphub_Card"))
        )
        scroll_and_extract(driver, game_name, count_limit=1500)
    except Exception as e:
        print(f"Erreur lors du scraping de {game_name} : {e}")
    finally:
        driver.quit()

print(f"\nScraping terminé. Données enregistrées dans : {json_file}")
