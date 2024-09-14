#!/usr/bin/env python

import logging
import polib
from pathlib import Path
from time import sleep

from . import ClientBuilder, ParamsLoader, get_outfile_name, system_prompt, user_prompt

logger = logging.getLogger(__name__)


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

    params = ParamsLoader().load()

    if params.show_prompts:
        print(f">>>>>>>>>>System prompt:\n{system_prompt}\n\n>>>>>>>>>>>>User prompt:\n{user_prompt}")
        exit(0)

    client = ClientBuilder(params).get_client()

    logger.info(f"Using model {client.params.model} to translate {params.input_po} from {params.original_language} -> "
                f"{params.context_language} -> {params.target_languages} with an {params.llm_client} client")
    for target_language in params.target_languages:
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
