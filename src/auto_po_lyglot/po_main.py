#!/usr/bin/env python
# pyright: reportAttributeAccessIssue=false

import logging
from pathlib import Path

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
      client.translate_pofile(params.input_po, output_file)

    logger.info("Done!")


if __name__ == "__main__":
    main()
