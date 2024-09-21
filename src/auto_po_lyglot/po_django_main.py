#!/usr/bin/env python

import logging

from . import ClientBuilder, ParamsLoader, system_prompt, user_prompt, locate_django_translation_files

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

    params = ParamsLoader([
      {'arg': '--path',
       'type': str,
       'help': 'Path to the Django project directory. Default is the current directory',
       'env': 'PATH',
       'default': '.'},
      {'arg': '--owner',
       'type': str,
       'help': 'Owner of the project. Supersersedes OWNER in .env. Default is <OWNER>',
       'env': 'OWNER',
       'default': '<OWNER>'},
      {'arg': '--owner_mail',
       'type': str,
       'help': 'Email of the owner. Supersersedes OWNER_MAIL in .env. Default is <OWNER EMAIL>',
       'env': 'OWNER_MAIL',
       'default': '<OWNER EMAIL>'},
    ]).load()

    if params.show_prompts:
        print(f">>>>>>>>>>System prompt:\n{system_prompt}\n\n>>>>>>>>>>>>User prompt:\n{user_prompt}")
        exit(0)

    client = ClientBuilder(params).get_client()

    logger.info(f"Using model {client.params.model} to translate Django project located at {params.path} "
                f"from {params.original_language} -> {params.context_language} -> {params.target_languages} "
                f"with an {params.llm_client} client")
    po_list = locate_django_translation_files(params.path, params.context_language, params.target_languages)
    for input_file, output_files in po_list.items():
      for tlg_output_file in output_files:
        client.target_language, output_file = list(tlg_output_file.items())[0]
        client.translate_pofile(input_file, output_file)


if __name__ == "__main__":
    main()
