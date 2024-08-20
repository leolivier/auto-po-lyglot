from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Charger le modèle mT5 et le tokenizer
model_name = "google/mt5-large"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# Phrase en anglais à traduire
text_to_translate = "He went to the bank"

# Traduction contextuelle en français (connue)
context_translation = "Il est allé au bord de la rivière"

# Création du prompt avec une structure claire
prompt = (
    f"Translate the English sentence to Spanish using the French context provided.\n\n"
    f"English: {text_to_translate}\n"
    f"French context: {context_translation}\n"
    f"Spanish:"
)

# Tokeniser le prompt
inputs = tokenizer(prompt, return_tensors="pt")

# Générer la traduction en espagnol
translated_tokens = model.generate(**inputs)
translated_text = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)

# Afficher la traduction en espagnol
print(translated_text)
