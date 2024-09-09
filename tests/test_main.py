#!/usr/bin/env python
import os
from auto_po_lyglot import ParamsLoader
# from auto_po_lyglot import process_file
from .settings import OUTPUT_DIRECTORY, TEST_TRANSLATIONS
from pathlib import Path
import pytest


@pytest.fixture(scope="class")
def params():
  return ParamsLoader([
    {'arg': 'testdir', 'type': str, 'help': 'test directory'},
    {'arg': '-s', 'action': 'store_true', 'help': 'don\'t capture outputs'},
    ])


@pytest.fixture(scope="class")
def llm_client(params):
    return params.get_client()


@pytest.fixture(scope="class")
def output_file(llm_client):
  p = Path(OUTPUT_DIRECTORY)
  print("Output directory:", p)
  if not p.is_dir():
    p.mkdir(parents=True, exist_ok=True)
  basefile_name = f"{llm_client.params.model.replace(':', '-')}_output%i.md"
  i = 0
  while True:
    outfile_name = p / (basefile_name % i)
    if not outfile_name.exists():
      print("Output file:", outfile_name)
      return outfile_name
    i += 1


# def extract_csv_translations(output_file, params):
#   csv_file = PurePath(output_file).with_suffix('.csv')
#   if not output_file.exists():
#     print(f"Error: Input file '{output_file}' does not exist.")
#     sys.exit(1)
#   languages = [params.original_language, params.context_language] + params.test_target_languages
#   process_file(output_file, csv_file, languages)
#   print("CSV extracted to file:", csv_file)


class TestTranspo:
  @pytest.fixture(autouse=True, scope="class")
  def setup(self, params, llm_client, output_file):
    pass

  def test_main(self, params, llm_client, output_file):
    if 'GENTESTVALUES' in os.environ:
      print("Skipping test_main because GENTESTVALUES is set: only generating test values")
      gentestonly = True
    else:
      gentestonly = False

    print(f"Using model {llm_client.params.model} for {params.original_language} -> {params.context_language} -> "
          f"{params.test_target_languages} with an {params.llm_client} client")
    with output_file.open('w', newline='', encoding='utf-8') as outfile:
      for target_language in params.test_target_languages:
        llm_client.target_language = target_language
        for tr in TEST_TRANSLATIONS:
          out = f"""  {{
    "original_phrase": "{tr['original_phrase']}",  # {params.original_language}
    "context_translation": "{tr['context_translation']}",  # {params.context_language}
    "target_translation": """
          print(out, end='')
          translation, explanation = llm_client.translate(tr['original_phrase'], tr['context_translation'])
          comment = explanation.replace('\n', '\n# ')
          trans_exp = f"""{translation}  # {target_language}
  # {comment}
  }},
"""
          print(trans_exp)
          outfile.write(f'{out} {trans_exp}')
          outfile.flush()
          if gentestonly:  # no assert if gentestonly
            continue
          if type(tr['target_translation']) is str:
            assert translation == tr['target_translation']
          else:
            assert translation == tr['target_translation'][llm_client.params.model]
      outfile.close()
    # extract_csv_translations(output_file, params)
