# Where tests results will be stored. Can be overriden on the command line
from os import environ


OUTPUT_DIRECTORY = "./tests/output"

# Some ambiguous sentences in the ORIGINAL_LANGUAGE and their CONTEXT_LANGUAGE translations for testing
# WARNING: assumes target language is Italian!
TEST_TRANSLATIONS = [
      {
        "original_phrase": "He gave her a ring.",
        "context_translation": "Il lui a donné une bague.",
        "target_translation": {
          "gemma2:2b": "Lui ha dato una collana.",
          "phi3": "Ha dato a lei una collana."
        }
      },
      {
        "original_phrase": "She made a call.",
        "context_translation": "Elle a pris une décision.",
        "target_translation": {
          "gemma2:2b": "Lei ha preso una decisione.",
          "phi3": "Ha preso una decisione."
        }
      },
      {
        "original_phrase": "They left the room.",
        "context_translation": "Ils ont quitté la pièce.",
        "target_translation": {
          "gemma2:2b": "Si sono andati dalla stanza.",
          "phi3": "Hanno lasciato la stanza."
        }
      },
      {
        "original_phrase": "He gave her a ring.",
        "context_translation": "Il lui a passé un coup de fil.",
        "target_translation": {
          "gemma2:2b": "Gli ha passato un colpo di telefono.",
          "phi3": "Ha fatto una telefonata."
        }
      },
      {
        "original_phrase": "She broke down",
        "context_translation": "Elle est tombée en panne",
        "target_translation": {
          "gemma2:2b": "Si è spenta", "phi3": "È crollata."
        }
      },
      {
        "original_phrase": "She broke down",
        "context_translation": "Elle s'est effondrée",
        "target_translation": {
          "gemma2:2b": "Si è spezzata", "phi3": "Si è rotta"
        }
      },
      {
        "original_phrase": "bank",
        "context_translation": "rive",
        "target_translation": {"gemma2:2b": "Banca", "phi3": ""}
      },
      {
        "original_phrase": "bank",
        "context_translation": "banque",
        "target_translation": {"gemma2:2b": "Banca", "phi3": "Banca"}
      },
      {
        "original_phrase": "He saw the light.",
        "context_translation": "Il a compris.",
        "target_translation": {"gemma2:2b": "Ha visto la luce.", "phi3": "Ha capito il sole."}
      },
      {
        "original_phrase": "He saw the light.",
        "context_translation": "Il a vu la lumière.",
        "target_translation": {"gemma2:2b": "Ha visto la luce.", "phi3": "Ha visto la luce."}
      },
      {
        "original_phrase": "She made a call.",
        "context_translation": "Elle a passé un appel.",
        "target_translation": {"gemma2:2b": "Ha fatto una chiamata.", "phi3": "Le ha fatto una telefonata."}
      },
      {
        "original_phrase": "They left the room.",
        "context_translation": "Ils ont laissé la pièce en l'état.",
        "target_translation": {"gemma2:2b": "Si sono andati dalla stanza.", "phi3": "Hanno lasciato il salotto in stato puro."}
      },
    ]

# use only 2 first translations for github actions
if environ.get("GITHUB_ACTIONS") == "true":
  TEST_TRANSLATIONS = TEST_TRANSLATIONS[:2]
