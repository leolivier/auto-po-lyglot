import polib
from transformers import pipeline
import re

regex = re.compile(r'{[^}]*}|%[sd]|%\([^)]*\)s')


def replace_vars(text):
  placeholders = {}
  for i, match in enumerate(re.finditer(regex, text)):
    placeholder = f'__VAR{i}__'
    placeholders[placeholder] = match.group()
    text = text.replace(match.group(), placeholder, 1)
  return text, placeholders


def restore_vars(text, placeholders):
  for placeholder, original in placeholders.items():
    text = text.replace(placeholder, original)
  return text


def translate_po_file(input_file, output_file):
    # Load multilingual translation template
    translator = pipeline("translation", model="facebook/mbart-large-50-many-to-many-mmt")

    # Load input .po file
    po = polib.pofile(input_file)

    # Browse each entry and translate
    for entry in po:
        if entry.msgid and not entry.fuzzy:
            # Preparing the context and the text to be translated
            context = entry.msgstr if entry.msgstr else entry.msgid
            context, ctxt_placeholders = replace_vars(context)
            text_to_translate = entry.msgid
            text_to_translate_no_placeholders, placeholders = replace_vars(text_to_translate)

            # Building the prompt
            prompt = f"Translate to Spanish. Context: {context}\nText: {text_to_translate_no_placeholders}"

            # Translate into Spanish
            translation = translator(prompt, src_lang="en_XX", tgt_lang="es_XX")[0]['translation_text']

            # Extract the translated part (after "Text: ")
            translation = translation.split("Text: ")[-1].strip()

            # Reinsert placeholders into the translated text
            translation = restore_vars(translation, placeholders)

            # Update translation
            entry.msgstr = translation

            print(f"Text to translate: {text_to_translate}\nContext: {context}\nTranslation: {translation}")
    # Save the new .po file
    po.save(output_file)


# Example of use
translate_po_file("input.po", "output.es.po")