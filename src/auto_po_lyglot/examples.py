# This file contains some examples of translations in the different languages. These examples will be embedded in the
# system prompt as a guide to the LLM so they must be highly accurate.
# You can specify here 3 kind of examples: basic ones, ambiguous ones and po placeholder ones.
# The examples are providing English, Italian, Spanish, German, Portuguese and French translations and for ambiguous
# examples, orginal and contextual translations are only provided for English/French couple.
# You can another language by simply adding an entry in *ALL* corresponding lists. For ambiguous examples, you can also
# provide other couples than English/French;
# Basic examples is just a list of translations in different languages for the same simple phrase.
basic_examples = [
  {
    "English": "Hello",
    "French": "Bonjour",
    "Italian": "Ciao",
    "Spanish": "Hola",
    "German": "Hallo",
    "Portuguese": "Ola"
  },
  {
    "English": "Goodbye",
    "French": "Au revoir",
    "Italian": "Arrivederci",
    "Spanish": "Adios",
    "German": "Auf Wiedersehen",
    "Portuguese": "Tchau"
  },
]

# Ambiguous examples is a list of translations in different languages for one original phrase and its contextual translation.
ambiguous_examples = [
  {
    "original_language": "English",
    "context_language": "French",
    "explanation": """
Explanation: This {target_language} translation reflects the meaning of the French phrase, which indicates that the person
made a phone call, not that he gave a ring. The English phrase "He gave her a ring" can be ambiguous, as it can mean both
"giving a ring" and "making a phone call" colloquially. The French translation makes it clear that it is a phone call, so
the {target_language} version "{target_translation}" follows this interpretation.""",
    "English": "He gave her a ring.",
    "French": "Il lui a passé un coup de fil.",
    "Italian": "Le ha fatto una telefonata.",
    "Spanish": "Le llamó por teléfono.",
    "German": "Er hat sie angerufen.",
    "Portuguese": "Ele telefonou-lhe."
  },
  {
    "original_language": "French",
    "context_language": "English",
    "explanation": """
Dans ce contexte, "s'effondrer" fait référence à une rupture émotionnelle plutôt qu'à une défaillance
mécanique, comme le confirme la traduction anglaise "broke down". La traduction {target_language} "{target_translation}"
reflète ce sens de rupture émotionnelle ou physique.""",
    "French": "Elle s'est effondrée",
    "English": "She broke down",
    "Italian": "Si è crollata",
    "Spanish": "Ella se derrumbó",
    "German": "Sie brach zusammen",
    "Portuguese": "Ela se derrubou."
  },
]

# PO placeholder examples is a list of translations in different languages a sentence containing a set of placeholders.
# The placeholders should represent the different forms of mlaceholers supported by po files ie %(something)s, {something}
# and %s or %d.
po_placeholder_examples = [
  {
    "English": "%(follower_name)s has created a new %(followed_type)s: %(followed_object_name)s",
    "French": "%(follower_name)s a créé un nouveau %(followed_type)s: %(followed_object_name)s",
    "Italian": "%(follower_name)s ha creato un nuovo %(followed_type)s: %(followed_object_name)s",
    "Spanish": "%(follower_name)s ha creado un nuevo %(followed_type)s: %(followed_object_name)s",
    "German": "%(follower_name)s hat ein neues %(followed_type)s erstellt: %(followed_object_name)s",
    "Portuguese": "%(follower_name)s criou um novo %(followed_type)s: %(followed_object_name)s"
  },
  {
    "English": "{follower_name} has created a new {followed_type}: {followed_object_name}",
    "French": "{follower_name} a créé un nouveau {followed_type}: {followed_object_name}",
    "Italian": "{follower_name} ha creato un nuovo {followed_type}: {followed_object_name}",
    "Spanish": "{follower_name} ha creado un nuevo {followed_type}: {followed_object_name}",
    "German": "{follower_name} hat ein neues {followed_type} erstellt: {followed_object_name}",
    "Portuguese": "{follower_name} criou um novo {followed_type}: {followed_object_name}"
  },
  {
    "English": "%s has created a new %s: %s",
    "French": "%s a créé un nouveau %s: %s",
    "Italian": "%s ha creato un nuovo %s: %s",
    "Spanish": "%s ha creado un nuevo %s: %s",
    "German": "%s hat ein neues %s erstellt: %s",
    "Portuguese": "%s criou um novo %s: %s"
  },
]
