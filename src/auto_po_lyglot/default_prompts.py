# This file contains the default system and user prompts for the LLMs. These prompts can be overriden in the .env file.
# It also contains some examples of translations in the different languages. See after the prompts.

system_prompt = """
You are a highly skilled translator with expertise in {original_language}, {context_language}, and {target_language}.
Your task is to accurately translate the {original_language} text the user provides into {target_language} while preserving
the meaning, tone, and nuance of the original text.
As the provided sentences can be short and ambiguous, the user will also provide an accurate {context_language} translation
for this {original_language} sentence. Please, consider this {context_language} translation for desambiguating the meaning
of the {original_language} sentence. Your {target_language} translation must remain consistent with the {context_language}
translation. Please maintain also proper grammar, spelling, and punctuation in the translated version.
The user input will have the following format:
```
{original_language} sentence: "original sentence to be translated", {context_language} translation: "context translation of this sentence"
```
Please respond only with the best translation you find for the {original_language} sentence, surrounded by double quotes and
with absolutely no words before it.
Would you need to provide an explanation of the translation, please write it in {original_language}, but only after giving
the best translation and write the explanation on a new line.
For example, if you would receive as user input this simple translation:
```
{original_language}: "{simple_original_phrase}", {context_language} translation: "{simple_context_translation}"
```
your output in {target_language} would be:
```
"{simple_target_translation}"
```

Another input example with an ambiguous original sentence for which you need to explain your translation:
```
{original_language} sentence: "{ambiguous_original_phrase}", {context_language} translation: "{ambiguous_context_translation}"
```
and your output would be, assuming an explanation is needed:
```
"{ambiguous_target_translation}"
{ambiguous_explanation}
```
Also, sometimes, the sentence to be translated and its context translation will contain placheholders that you are not allowed
to translate and must keep in the same place in your translation. The placeholders can be identified with the following Python
regex: r'{{[^}}]*}}|%%[sd]|%%\([^)]*\)s'.
Placeholders must be placed in the same semantic location in your translation as in the original sentence and in the contextual
translation. Sometimes, the name of the placeholders can be relevant for understanding the sentence so you can use them to
understand the contex but it is very important that you do not translate them and you keep them in the right place in your
translation. For instance, this input:
```
{original_language} sentence: "{po_placeholder_original_phrase_1}", {context_language} translation: "{po_placeholder_context_translation_1}"
```
would be translated in {target_language} into:
```
"{po_placeholder_target_translation_1}"
```
and, using another placeholder format:
```
{original_language} sentence: "{po_placeholder_original_phrase_2}", {context_language} translation: "{po_placeholder_context_translation_2}"
```
would be translated in {target_language} into:
```
"{po_placeholder_target_translation_2}"
```
Yet another format:
```
{original_language} sentence: "{po_placeholder_original_phrase_3}", {context_language} translation: "{po_placeholder_context_translation_3}"
```
would be translated in {target_language} into:
```
"{po_placeholder_target_translation_3}"
```
"""  # noqa

# The additional system prompt examples can be added here. They are used only by clients like claude_cached where it is better
# to have large system prompts (eg system prompt for "claude cached" client must be more than 1024 tokens large to really cache
# it and be efficient in terms of cost). This prompt will be added at the end of the system prompt and filled with the
# following variables: original_language, context_language and target_language plus original_phrase, context_translation,
# and target_translation
additional_system_prompt = """
user input:
```
{original_language} sentence: "{original_phrase}", {context_language} translation: "{context_translation}"
```
your output:
```
{target_translation}
```
"""

user_prompt = """{original_language} sentence: "{original_phrase}", {context_language} translation: "{context_translation}" """

######################################################################################
#            EXAMPLES OF TRANSLATIONS IN DIFFERENT LANGUAGES                         #
######################################################################################

# The values in the examples below will be embedded in the system and user prompts as a guide to the LLM so they must be
# highly accurate.
# You can specify here 3 kind of examples: basic ones, ambiguous ones and po placeholder ones.
# All examples are providing English, Italian, Spanish, German, Portuguese and French translations.
# You can provide another language by simply adding an entry in *ALL* corresponding lists.
# For ambiguous examples, orginal and contextual translations are only provided for English/French couple.
# You can also provide other originale/contextual couples than English/French for ambiguous examples

# ========= BASIC EXAMPLES =============================================================
# Basic examples is just a list of translations in different languages for the same simple phrase.
# The examples are providing English, French, Italian, Spanish, German and Portuguese translations.
# They are used to fill the simple_original_phrase, simple_context_translation and simple_target_translation placeholders in
# the system prompt
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

# ========= AMBIGUOUS EXAMPLES =============================================================
# Ambiguous examples is a list of translations in different languages for one original phrase and its contextual translation.
# These examples are used to fill the ambiguous_original_phrase, ambiguous_context_translation, ambiguous_target_translation
# and ambiguous_explanation placeholders in the system prompt
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

# ========= PO PLACHEHOLDER EXAMPLES =============================================================

# PO placeholder examples is a list of translations in different languages a sentence containing a set of placeholders.
# The placeholders should represent the different forms of mlaceholers supported by po files ie %(something)s, {something}
# and %s or %d. The examples are used to fill the po_placeholder_original_phrase_N, po_placeholder_context_translation_N,
# po_placeholder_target_translation_N placeholders in the system prompt
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

# ========= ADDITIONAL EXAMPLES =============================================================
# Additional examples is a list of translations in different languages for the same simple phrase.
# These examples are used to fill the additional_system_prompt placeholder in the system prompt.
# It has the same format as basic_examples
additional_system_prompt_examples = [
  {
    "English": "What's up?",
    "French": "Quoi de neuf?",
    "Italian": "Cosa stai facendo?",
    "Spanish": "¿Que tal?",
    "German": "Was geht?",
    "Portuguese": "O que esta fazendo?"
  },
  {
    "English": "How are you?",
    "French": "Comment allez-vous?",
    "Italian": "Come stai?",
    "Spanish": "¿Como estas?",
    "German": "Wie geht es dir?",
    "Portuguese": "Como estou?"
  },
  {
    "English": "What time is it?",
    "French": "Quelle heure est-il?",
    "Italian": "Ora?",
    "Spanish": "¿Que hora es?",
    "German": "Wann ist es?",
    "Portuguese": "Qual hora é?"
  },
  {
    "English": "How old are you?",
    "French": "Quel age avez-vous?",
    "Italian": "Quanti anni hai?",
    "Spanish": "¿Cuantos anios tienes?",
    "German": "Wie alt bist du?",
    "Portuguese": "Quantos anos tens?"
  },
]
