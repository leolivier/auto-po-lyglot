#!/usr/bin/env python
from getenv import TranspoParams
from pathlib import PurePath
import polib


def get_outfile_name(model_name, input_po, target_language):
    """
    Generates a unique output file name based on the given model name and the parameters.

    Args:
        model_name (str): The name of the model.
        params (TranspoParams): The parameters for the translation.
    Returns:
        Path: A unique output po file name in the format "{input_po}_{target_language}_{i}.po".
    """
    p = PurePath(input_po)
    basefile_name = f'{p.name}_{target_language}_%i.po'
    basefile_name = f"{model_name.replace(':', '-')}_output%i.md"
    i = 0
    while True:
      outfile_name = p.with_name(basefile_name % i)
      if not outfile_name.exists():
        print("Output file:", outfile_name)
        return outfile_name
      i += 1


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
         'type': str,
         'help': 'the .po file containing the msgids (phrases to be translated) and msgstrs (context translations)'
      },
    ]

    params = TranspoParams(additional_args)

    client = params.get_client()

    print(f"Using model {client.model} to translate {params.input_po} from {params.original_language} -> {params.context_language} "
          f"-> {params.test_target_languages} with an {params.llm_client} client")
    for target_language in params.test_target_languages:
      client.target_language = target_language
      output_file = get_outfile_name(client.model, params.input_po, target_language)
      # Load input .po file
      po = polib.pofile(params.input_po)
      for entry in po:
        if entry.msgid and not entry.fuzzy:
          context_translation = entry.msgstr if entry.msgstr else entry.msgid
          original_phrase = entry.msgid
          translation = client.translate(original_phrase, context_translation)
          # Update translation
          entry.msgstr = translation
          # print(translation)
    # Save the new .po file
    po.save(output_file)


if __name__ == "__main__":
    main()
