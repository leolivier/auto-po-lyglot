from dotenv import load_dotenv
from os import environ
import json

load_dotenv()

# where tests results will be stored
output_dir = environ.get('OUTPUT_DIRECTORY', '.')
# .po file context:
# primary language (msgids)
original_language = environ.get('ORIGINAL_LANGUAGE', 'English')
# and translation language (msgstrs)
context_language = environ.get('CONTEXT_LANGUAGE', 'French')
# chose the LLM client and model
llm_client = environ.get('LLM_CLIENT', 'ollama')
model = environ.get('LLM_MODEL', None)
match llm_client:
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
    raise Exception(f"LLM_CLIENT must be one of 'ollama', 'openai', 'claude' or 'claude_cached', not '{llm_client}'")

# the target languages to test for translation
test_target_languages = environ.get('TARGET_LANGUAGES', 'Spanish').split(',')


# some ambiguous english sentences and their French translations for testing
translations_testset = json.loads(
  environ.get('TEST_TRANSLATIONS',
              """[{"original_phrase": "He gave her a ring.", "context_translation": "Il lui a donné une bague."}]"""))
# print(translations_testset)


def get_outfile_name(model_name):
    """
    Generates a unique output file name based on the given model name.

    Args:
        model_name (str): The name of the model.

    Returns:
        Path: A unique output file name in the format "{model_name}_output{i}.md".
    """
    from pathlib import Path
    p = Path(output_dir)
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


def extract_csv_translations(output_file):
  from output2csv import process_file
  from pathlib import PurePath
  import sys
  csv_file = PurePath(output_file).with_suffix('.csv')
  if not output_file.exists():
    print(f"Error: Input file '{output_file}' does not exist.")
    sys.exit(1)
  languages = [original_language, context_language] + test_target_languages
  process_file(output_file, csv_file, languages)
  print("CSV extracted to file:", csv_file)


def main():
    """
    This is the main function of the program. It generates a translation file for a given model.
    It iterates over a list of test translations and target languages, translating the English phrase
    into the target language using the provided client and prompt implementation.
    The translations are then written to an output file and printed to the console.

    Parameters:
        None

    Returns:
        None
    """
    client = LLMClient(original_language, context_language, "", model) if model else \
      LLMClient(original_language, context_language, "")

    print(f"Using model {client.model} for {original_language} -> {context_language} -> {test_target_languages} "
          f"with an {llm_client} client")
    outfile_name = get_outfile_name(client.model)
    with outfile_name.open('w', newline='', encoding='utf-8') as outfile:
      for tr in translations_testset:
        for target_language in test_target_languages:
          client.target_language = target_language
          out = f"""
=================
{original_language}: "{tr['original_phrase']}", {context_language}: "{tr['context_translation']}", {target_language}: """
          print(out, end='')
          translation = client.translate(tr['original_phrase'], tr['context_translation'])
          print(translation)
          outfile.write(out + translation)
      outfile.close()
    extract_csv_translations(outfile_name)


if __name__ == "__main__":
    main()
