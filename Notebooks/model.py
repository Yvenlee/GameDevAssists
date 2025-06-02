import json
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

model_id = "mistralai/Mistral-7B-Instruct-v0.1"

tokenizer = AutoTokenizer.from_pretrained(model_id, use_auth_token=True)
model = AutoModelForCausalLM.from_pretrained(model_id, use_auth_token=True, device_map="auto", torch_dtype="auto")

pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)

with open("games.json", "r", encoding="utf-8") as f:
    games_data = json.load(f)

selected_game = "Brawlhalla" 

comments = [rev["Comment"].strip() for rev in games_data.get(selected_game, []) if rev["Comment"].strip()]
comments_to_use = comments[:30]
prompt = f"Voici des avis de joueurs pour le jeu '{selected_game}' :\n"
for i, comment in enumerate(comments_to_use, 1):
    prompt += f"{i}. \"{comment}\"\n"

prompt += """
Génère une synthèse : Quel est l'avis général ? Que faut-il améliorer ?
"""
result = pipe(prompt, max_new_tokens=300, do_sample=True, temperature=0.7)

print(result[0]["generated_text"])
