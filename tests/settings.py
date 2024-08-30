# Where tests results will be stored. Can be overriden on the command line
from os import environ


OUTPUT_DIRECTORY = "./tests/output"

# Some ambiguous sentences in the ORIGINAL_LANGUAGE and their CONTEXT_LANGUAGE translations for testing
TEST_TRANSLATIONS = [
      {
        "original_phrase": "He gave her a ring.",
        "context_translation": "Il lui a donné une bague.",
        "target_translation": "Lui ha regalato un anello."
      },
      {
        "original_phrase": "She made a call.",
        "context_translation": "Elle a pris une décision.",
        "target_translation": "Lei ha preso una decisione."
      },
      {
        "original_phrase": "They left the room.",
        "context_translation": "Ils ont quitté la pièce.",
        "target_translation": "Si sono andati dalla stanza."
      },
      {
        "original_phrase": "He gave her a ring.",
        "context_translation": "Il lui a passé un coup de fil.",
        "target_translation": "Lui ha regalato un anello."
      },
      {
        "original_phrase": "She broke down",
        "context_translation": "Elle est tombée en panne",
        "target_translation": "Lei si è guastata"
      },
      {
        "original_phrase": "She broke down",
        "context_translation": "Elle s'est effondrée",
        "target_translation": "Lei si è sbandita"
      },
      {
        "original_phrase": "bank",
        "context_translation": "rive",
        "target_translation": "la banca"
      },
      {
        "original_phrase": "bank",
        "context_translation": "banque",
        "target_translation": "Banca"
      },
      {
        "original_phrase": "He saw the light.",
        "context_translation": "Il a compris.",
        "target_translation": "Lui è capitato la luce."
      },
      {
        "original_phrase": "He saw the light.",
        "context_translation": "Il a vu la lumière.",
        "target_translation": "Lui è stata vista la luce."
      },
      {
        "original_phrase": "She made a call.",
        "context_translation": "Elle a passé un appel.",
        "target_translation": "Lei ha fatto una chiamata."
      },
      {
        "original_phrase": "They left the room.",
        "context_translation": "Ils ont laissé la pièce en l'état.",
        "target_translation": "Si hanno lasciato la stanza."
      },
    ]

# use only 2 first translations for github actions
if environ.get("GITHUB_ACTIONS") == "true":
  TEST_TRANSLATIONS = TEST_TRANSLATIONS[:2]
