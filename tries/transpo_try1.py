import polib
from transformers import pipeline


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
            text_to_translate = entry.msgid

            # Building the prompt
            prompt = f"Translate to Spanish. Context: {context}\nText: {text_to_translate}"

            # Translate into Spanish
            translation = translator(prompt, src_lang="en_XX", tgt_lang="es_XX")[0]['translation_text']

            # Extract the translated part (after "Text: ")
            translation = translation.split("Text: ")[-1].strip()

            # Update translation
            entry.msgstr = translation

    # Save the new .po file
    po.save(output_file)


# Example of use
input_file = "input.po"
output_file = "output.es.po"
translate_po_file(input_file, output_file)