#!/usr/bin/env python
from getenv import TranspoParams


def get_outfile_name(model_name, params):
    """
    Generates a unique output file name based on the given model name.

    Args:
        model_name (str): The name of the model.

    Returns:
        Path: A unique output file name in the format "{model_name}_output{i}.md".
    """
    from pathlib import Path
    p = Path(params.output_dir)
    print("Output directory:", p)
    if not p.is_dir():
      raise ValueError(f"Output directory {p} does not exist.")
    basefile_name = f"{model_name.replace(':', '-')}_output%i.md"
    i = 0
    while True:
      outfile_name = p / (basefile_name % i)
      if not outfile_name.exists():
        print("Output file:", outfile_name)
        return outfile_name
      i += 1


def extract_csv_translations(output_file, params):
  from csv_extractor import process_file
  from pathlib import PurePath
  import sys
  csv_file = PurePath(output_file).with_suffix('.csv')
  if not output_file.exists():
    print(f"Error: Input file '{output_file}' does not exist.")
    sys.exit(1)
  languages = [params.original_language, params.context_language] + params.test_target_languages
  process_file(output_file, csv_file, languages)
  print("CSV extracted to file:", csv_file)


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
         'arg': '--output_dir',
         'type': str,
         'help': 'the directory where the output files will be stored'
      },
      {
        'arg': '--original_phrase',
        'type': str,
        'help': 'the sentence to be translated (otherwise, taken from .env). '
                'If this is provided, context_translation is required'
      },
      {
        'arg': '--context_translation',
        'type': str,
        'help': 'the context translation related to the original phrase (otherwise, taken from .env)'
      }
    ]

    params = TranspoParams(additional_args)

    client = params.get_client()

    print(f"Using model {client.model} for {params.original_language} -> {params.context_language} -> {params.test_target_languages} "  # noqa
          f"with an {params.llm_client} client")
    outfile_name = get_outfile_name(client.model, params)
    with outfile_name.open('w', newline='', encoding='utf-8') as outfile:
      for tr in params.translations_testset:
        for target_language in params.test_target_languages:
          client.target_language = target_language
          out = f"""
=================
{params.original_language}: "{tr['original_phrase']}", {params.context_language}: "{tr['context_translation']}", {target_language}: """  # noqa
          print(out, end='')
          translation = client.translate(tr['original_phrase'], tr['context_translation'])
          print(translation)
          outfile.write(out + translation)
      outfile.close()
    extract_csv_translations(outfile_name, params)


if __name__ == "__main__":
    main()
