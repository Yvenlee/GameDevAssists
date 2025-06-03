import json
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

MODEL_ID = "mistralai/Mistral-7B-Instruct-v0.1"
SELECTED_GAME = "Brawlhalla"
MAX_COMMENTS = 10

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, use_auth_token=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    use_auth_token=True,
    device_map="auto",
    torch_dtype="auto"
)
pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)

with open("games.json", "r", encoding="utf-8") as f:
    games_data = json.load(f)

comments = [
    rev["Comment"].strip()
    for rev in games_data.get(SELECTED_GAME, [])
    if rev.get("Comment", "").strip()
]
selected_comments = comments[:MAX_COMMENTS]

comment_lines = [f"{i+1}. \"{comment}\"" for i, comment in enumerate(selected_comments)]
prompt = (
    f"Voici des avis de joueurs pour le jeu '{SELECTED_GAME}' :\n" +
    "\n".join(comment_lines) +
    "\n\nGénère une synthèse : Quel est l'avis général ? Que faut-il améliorer ?"
)

result = pipe(prompt, max_new_tokens=300, do_sample=True, temperature=0.7)
print(result[0]["generated_text"])
