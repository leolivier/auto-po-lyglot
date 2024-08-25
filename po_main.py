#!/usr/bin/env python
from getenv import TranspoParams
from pathlib import Path
import polib
from base import Logger
import langcodes

logger = Logger(__name__)


def get_language_code(language_name):
    try:
        # Search language by name
        lang = langcodes.find(language_name)
        # Returns ISO 639-1 code (2 characters)
        return lang.language
    except LookupError:
        return None


def get_outfile_name(model_name, input_po, target_language, context_language):
    """
    Generates a unique output file name based on the given model name and the parameters.

    Args:
        model_name (str): The name of the model.
        params (TranspoParams): The parameters for the translation.
    Returns:
        Path: A unique output po file name in the format "{input_po}_{target_language}_{i}.po".
    """
    p = Path(input_po)
    parent = p.parent
    grandparent = parent.parent
    context_lang_code = get_language_code(context_language)
    if parent.name == 'LC_MESSAGES' and grandparent.name == context_lang_code:
      # we're in something like .../locale/<lang_code>/LC_MESSAGES/file.po
      # let's try to build the same with the target language code
      target_code = get_language_code(target_language)
      dir = grandparent.parent / target_code / 'LC_MESSAGES'
      # create the directory if it doesn't exist
      dir.mkdir(parents=True, exist_ok=True)
      outfile = dir / p.name
    else:  # otherwise, just add the target language code
      outfile = p.with_suffix('_{target_code}.po')

    logger.vprint("Output file:", outfile)
    if outfile.exists():
      logger.vprint("Output file already exists, won't overwrite.")
      i = 0
      i_outfile = outfile
      # append a number to the filename
      while i_outfile.exists():
        i_outfile = outfile.with_suffix('-{i}.po')
        i += 1
      outfile = i_outfile
      logger.vprint("Output file:", outfile)

    return outfile


def main():
    """
    This is the main function of the program. It generates a translation file using a given model.
    It iterates over a list of test translations containing the original phrase and its translation
    within a context language, and for each target language, translates the original phrase
    into the target language helped with the context translation, by using the provided client and
    prompt implementation.
    The translations are then written to an output file and printed to the console.

    Parameters:
        None

    Returns:
        None
    """

    additional_args = [
      {
         'arg': '--input_po',
         'env': 'INPUT_PO',
         'type': str,
         'help': 'the .po file containing the msgids (phrases to be translated) and msgstrs (context translations)',
         'default': 'tests/input/input.po'
      },
    ]

    params = TranspoParams(additional_args)

    client = params.get_client()

    logger.vprint(f"Using model {client.params.model} to translate {params.input_po} from {params.original_language} -> "
                  f"{params.context_language} -> {params.test_target_languages} with an {params.llm_client} client")
    for target_language in params.test_target_languages:
      client.target_language = target_language
      output_file = get_outfile_name(client.params.model, params.input_po, target_language, params.context_language)
      # Load input .po file
      po = polib.pofile(params.input_po)
      for entry in po:
        if entry.msgid and not entry.fuzzy:
          context_translation = entry.msgstr if entry.msgstr else entry.msgid
          original_phrase = entry.msgid
          translation_result = client.translate(original_phrase, context_translation).split('\n')
          translation = translation_result[0].strip('"')
          explanation = 'Not provided'
          if len(translation_result) > 1:
            translation_result.pop(0)
            translation_result = [line for line in translation_result if line]
            explanation = '\n'.join(translation_result)
            entry.comment = explanation
          # Update translation
          entry.msgstr = translation
          logger.vprint(f"""==================
English: "{original_phrase}"
French: "{context_translation}"
{target_language}: "{translation}"
Comment:{explanation}
""")
      # Save the new .po file
      po.save(output_file)


if __name__ == "__main__":
    main()
