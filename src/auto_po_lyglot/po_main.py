#!/usr/bin/env python

import langcodes
import logging
import polib
from pathlib import Path
from time import sleep

from .getenv import ParamsLoader
from .default_prompts import system_prompt, user_prompt

logger = logging.getLogger(__name__)


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
    target_code = get_language_code(target_language)
    if parent.name == 'LC_MESSAGES' and grandparent.name == context_lang_code:
      # we're in something like .../locale/<lang_code>/LC_MESSAGES/file.po
      # let's try to build the same with the target language code
      dir = grandparent.parent / target_code / 'LC_MESSAGES'
      # create the directory if it doesn't exist
      dir.mkdir(parents=True, exist_ok=True)
      outfile = dir / p.name
    else:  # otherwise, just add the model name and the target language code in the file name
      model_name = model_name.replace(':', '-')
      outfile = p.with_suffix(f'.{model_name}.{target_code}.po')

    logger.info(f"Output file: {outfile}")
    if outfile.exists():
      logger.info("Output file already exists, won't overwrite.")
      i = 0
      i_outfile = outfile
      # append a number to the filename
      while i_outfile.exists():
        i_outfile = outfile.with_suffix(f'.{i}.po')
        i += 1
      outfile = i_outfile
      logger.info(f"Corrected output file: {outfile}")

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

    params = ParamsLoader()

    if params.show_prompts:
        print(f">>>>>>>>>>System prompt:\n{system_prompt}\n\n>>>>>>>>>>>>User prompt:\n{user_prompt}")
        exit(0)

    client = params.get_client()

    logger.info(f"Using model {client.params.model} to translate {params.input_po} from {params.original_language} -> "
                f"{params.context_language} -> {params.test_target_languages} with an {params.llm_client} client")
    for target_language in params.test_target_languages:
      client.target_language = target_language
      output_file = params.output_po or get_outfile_name(client.params.model, params.input_po,
                                                         target_language, params.context_language)
      # Load input .po file
      assert params.input_po, "Input .po file not provided"
      assert Path(params.input_po).exists(), f"Input .po file {params.input_po} does not exist"
      po = polib.pofile(params.input_po)
      try:
        nb_translations = 0
        for entry in po:
          if entry.msgid and not entry.fuzzy:
            context_translation = entry.msgstr if entry.msgstr else entry.msgid
            original_phrase = entry.msgid
            translation, explanation = client.translate(original_phrase, context_translation)
            # Add explanation to comment
            if explanation:
              entry.comment = explanation
            # Update translation
            entry.msgstr = translation
            logger.info(f"""==================
  {params.original_language}: "{original_phrase}"
  {params.context_language}: "{context_translation}"
  {target_language}: "{translation}"
  Comment:{explanation if explanation else ''}
  """)
            sleep(1.0)  # Sleep for 1 second to avoid rate limiting
            nb_translations += 1
      except Exception as e:
        logger.error(f"Error: {e}")
      # Save the new .po file even if there was an error to not lose what was translated
      po.save(output_file)
      percent_translated = round(nb_translations / len(po) * 100, 2)
      logger.info(f"Saved {output_file}, translated {nb_translations} entries out "
                  f"of {len(po)} entries ({percent_translated}%)")


if __name__ == "__main__":
    main()
