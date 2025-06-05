import os
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, StaleElementReferenceException

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    return webdriver.Chrome(options=options)

def search_game(driver, game_name):
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "store_nav_search_term"))
    )
    search_box.send_keys(game_name)
    search_box.send_keys(Keys.ENTER)

def click_first_game(driver):
    first_image = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "div.col.search_capsule img"))
    )
    first_image.click()

def extract_image_url(driver):
    try:
        image_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div#gameHeaderImageCtn img.game_header_image_full"))
        )
        image_url = image_element.get_attribute("src")

        image_urls_file = r"C:\Users\yvenl\OneDrive\Bureau\GameDevAssists\Data\image_urls.json"

        image_urls = []
        try:
            with open(image_urls_file, "r") as file:
                image_urls = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            image_urls = []

        image_urls.append(image_url)

        with open(image_urls_file, "w") as file:
            json.dump(image_urls, file, indent=4)

        print(f"Image URL saved: {image_url}")
    except Exception as e:
        print(f"Error extracting image URL: {e}")

def click_user_review(driver):
    try:
        review_links = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.user_reviews_summary_row"))
        )

        if len(review_links) < 2:
            print("Moins de 2 liens d’évaluations trouvés.")
            return

        link_to_click = review_links[1]
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link_to_click)
        time.sleep(1)

        try:
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.user_reviews_summary_row")))
            link_to_click.click()
            print("Clic direct sur le lien d’évaluation.")
        except ElementClickInterceptedException:
            print("Clic bloqué. Forçage avec JavaScript.")
            driver.execute_script("arguments[0].click();", link_to_click)
            print("Clic JS réussi.")
        except StaleElementReferenceException:
            print("Élément obsolète. Tentative de récupération...")
            updated_links = driver.find_elements(By.CSS_SELECTOR, "a.user_reviews_summary_row")
            if len(updated_links) >= 2:
                driver.execute_script("arguments[0].click();", updated_links[1])
                print("Clic JS sur élément mis à jour.")
            else:
                print("Impossible de retrouver le lien.")
    except TimeoutException:
        print("Aucun lien d’évaluation trouvé.")

def click_browse_reviews(driver):
    try:
        browse_reviews_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div#ViewAllReviewssummary"))
        )
        driver.execute_script("arguments[0].querySelector('a').click();", browse_reviews_div)
        print("Cliqué sur le lien 'Parcourir les évaluations' avec JavaScript.")
    except TimeoutException:
        print("Impossible de trouver la div 'ViewAllReviewssummary'.")
    except Exception as e:
        print(f"Une erreur est survenue lors du clic sur le lien : {e}")

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

def scroll_and_extract(driver, game_name, count_limit=45):
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

def save_json():
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(reviews_data, f, ensure_ascii=False, indent=4)

json_file = r"C:\Users\yvenl\OneDrive\Bureau\GameDevAssists\Data\games.json"

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

def main(game_name):
    driver = setup_driver()
    wait = WebDriverWait(driver, 10)

    try:
        driver.get("https://store.steampowered.com/")
        search_game(driver, game_name)
        click_first_game(driver)
        extract_image_url(driver)
        click_user_review(driver)
        click_browse_reviews(driver)

        scroll_and_extract(driver, game_name, count_limit=1500)

        print("Le navigateur reste ouvert. Fermez-le manuellement si nécessaire.")
        input("Appuyez sur Entrée pour quitter le script sans fermer le navigateur...")

    except Exception as e:
        print(f"Une erreur est survenue : {e}")

game_name = input("Veuillez entrer le nom du jeu : ")
main(game_name)
