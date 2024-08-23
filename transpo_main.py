import sys
from dotenv import load_dotenv
from os import environ
import json
import argparse


def get_params(args):
  "looks at args and returns an object with attributes of these args completed by the environ variables where needed"
  params_dict = {}
  # where tests results will be stored
  params_dict['output_dir'] = args.output_dir or environ.get('OUTPUT_DIRECTORY', '.')
  # .po file context:
  # primary language (msgids)
  params_dict['original_language'] = args.original_language or environ.get('ORIGINAL_LANGUAGE', 'English')
  # and translation language (msgstrs)
  params_dict['context_language'] = args.context_language or environ.get('CONTEXT_LANGUAGE', 'French')
  # chose the LLM client and model
  params_dict['llm_client'] = args.llm or environ.get('LLM_CLIENT', 'ollama')
  params_dict['model'] = args.model or environ.get('LLM_MODEL', None)

  # the target languages to test for translation
  if args.target_language:
    params_dict['test_target_languages'] = [args.target_language]
  else:
    params_dict['test_target_languages'] = environ.get('TARGET_LANGUAGES', 'Spanish').split(',')

  # some ambiguous original sentences and their context translations for testing
  if args.original_phrase:
    if not args.context_translation:
      print("context_translation must be set when origin_phrase is set")
      sys.exit(1)

    params_dict['translations_testset'] = [{"original_phrase": args.original_phrase,
                                            "context_translation": args.context_translation}]
  else:
    params_dict['translations_testset'] = json.loads(
      environ.get('TEST_TRANSLATIONS',
                  """[{"original_phrase": "He gave her a ring.", "context_translation": "Il lui a donné une bague."}]"""))
  # print(translations_testset)

  class Params:
    def __init__(self, **entries):
        self.__dict__.update(entries)
  return Params(**params_dict)


def get_client(params):
  match params.llm_client:
    case 'ollama':
      from transpo_openai_ollama import OllamaClient as LLMClient
    case 'openai':
      # uses OpenAI GPT-4o by default
      from transpo_openai_ollama import OpenAIClient as LLMClient
    case 'claude':
      # uses Claude Sonnet 3.5 by default
      from transpo_claude import ClaudeClient as LLMClient
    case 'claude_cached':
      # uses Claude Sonnet 3.5, cached mode for long system prompts
      from transpo_claude import CachedClaudeClient as LLMClient
    case _:
      raise Exception(
        f"LLM_CLIENT must be one of 'ollama', 'openai', 'claude' or 'claude_cached', not '{params.llm_client}'"
        )
  return LLMClient(params.original_language, params.context_language, "", params.model) if params.model \
    else LLMClient(params.original_language, params.context_language, "")


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
  from output2csv import process_file
  from pathlib import PurePath
  import sys
  csv_file = PurePath(output_file).with_suffix('.csv')
  if not output_file.exists():
    print(f"Error: Input file '{output_file}' does not exist.")
    sys.exit(1)
  languages = [params.original_language, params.context_language] + params.test_target_languages
  process_file(output_file, csv_file, languages)
  print("CSV extracted to file:", csv_file)


help = """
Generates a translation file using a given model and llm type. It reads the parameters from the command line,
and completes them when necessary from the content of .env in the same directory.
It iterates over a list of test translations containing the original phrase and its translation
within a context language, and for each target language, translates the original phrase
into the target language helped with the context translation, by using the provided client and
prompt implementation."""


def parse_args():
  parser = argparse.ArgumentParser(description=help)
  # Add arguments
  parser.add_argument('--llm',
                      type=str,
                      help='Le type of LLM you want to use. Can be openai, ollama, claude or claude_cached. '
                           'For openai or claude[_cached], you need to set the api key in the environment')
  parser.add_argument('--model',
                      type=str,
                      help='the name of the model to use. If not provided, a default model '
                           'will be used, based on the chosen client')
  parser.add_argument('--output_dir',
                      type=str,
                      help='the directory where the output files will be stored')
  parser.add_argument('--original_language',
                      type=str,
                      help='the language of the original phrase')
  parser.add_argument('--context_language',
                      type=str,
                      help='the language of the context translation')
  parser.add_argument('--target_language',
                      type=str,
                      help='the language into which the original phrase will be translated')
  parser.add_argument('--original_phrase',
                      type=str,
                      help='the sentence to be translated (otherwise, taken from .env). '
                           'If this is provided, context_translation is required')
  parser.add_argument('--context_translation',
                      type=str,
                      help='the context translation related to the original phrase (otherwise, taken from .env)')
  parser.add_argument('--verbose', action='store_true', help='verbose mode')

  # Analyze the arguments
  return parser.parse_args()


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

    load_dotenv()

    args = parse_args()
    params = get_params(args)

    client = get_client(params)

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
