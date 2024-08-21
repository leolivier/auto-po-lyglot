import os

# .po file context:
# primary language (msgids)
original_language = "English"
# and translation language (msgstrs)
context_language = "French"

# chose the LLM client and model
from transpo_openai_ollama import OllamaClient                                          # noqa
client = OllamaClient(original_language, context_language, "", "gemma2:2b")
# uses the default model llama3.1:8b
# client = OllamaClient(original_language, context_language, "")

# uses OpenAI get4o model
# from transpo_openai_ollama import OpenAIClient                                            # noqa
# client = OpenAIClient(original_language, context_language, "")

# uses Claude Sonnet 3.5
# from transpo_claude import ClaudeClient                                                   # noqa
# client = ClaudeClient(original_language, context_language, "")

# choose the prompt implementation
from transpo_prompts import TranspoPromptsImpl1 as TranspoPromptsImplementation             # noqa
# from transpo_prompts import TranspoPromptsImpl2 as TranspoPromptsImplementation

# some ambiguous english sentences and their French translations for testing
TestTranslations = [
  {"english_phrase": "She broke down", "french_translation": "Elle est tombée en panne"},
  {"english_phrase": "She broke down", "french_translation": "Elle s'est effondrée"},
  {"english_phrase": "bank", "french_translation": "rive"},
  {"english_phrase": "bank", "french_translation": "banque"},
  {"english_phrase": "He saw the light.", "french_translation": "Il a compris."},
  {"english_phrase": "He saw the light.", "french_translation": "Il a vu la lumière."},
  {"english_phrase": "She made a call.", "french_translation": "Elle a passé un appel."},
  {"english_phrase": "She made a call.", "french_translation": "Elle a pris une décision."},
  {"english_phrase": "They left the room.", "french_translation": "Ils ont quitté la pièce."},
  {"english_phrase": "They left the room.", "french_translation": "Ils ont laissé la pièce en l'état."},
  {"english_phrase": "He gave her a ring.", "french_translation": "Il lui a donné une bague."},
  {"english_phrase": "He gave her a ring.", "french_translation": "Il lui a passé un coup de fil."},
]
# the target languages to test for translation
TestTargetLanguages = ["Italian", "Spanish", "German"]


def main():

    outfile_name = f"output-{client.model.replace(':', '-')}.md"
    i = 2
    while os.path.exists(outfile_name):
      outfile_name = f"output{i}-{client.model.replace(':', '-')}.md"
      i += 1
    with open(outfile_name, 'w', newline='', encoding='utf-8') as outfile:
      for tr in TestTranslations:
        for target_language in TestTargetLanguages:
          client.target_language = target_language
          translation = client.translate(TranspoPromptsImplementation, tr['english_phrase'], tr['french_translation'])
          out = f"""
=================
English: "{tr['english_phrase']}", French: "{tr['french_translation']}", {target_language}: "{translation}"
"""
          print(out)
          outfile.write(out)


if __name__ == "__main__":
    main()
