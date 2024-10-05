#!/usr/bin/env python

import polib
from auto_po_lyglot import ParamsLoader, ClientBuilder
from auto_po_lyglot.getenv import get_language_code
from .settings import INPUT_DIRECTORY, OUTPUT_DIRECTORY, TEST_TRANSLATIONS
from pathlib import Path
import pytest


@pytest.fixture(scope="class")
def params():
  params = ParamsLoader().load_params_from_env()
  # force original language to English
  params.original_language = 'English'
  # force context language to French
  params.context_language = 'French'
  # force target language to Italian
  params.target_languages = ['Italian']
  # force LLM client to ollama
  params.llm_client = 'ollama'
  # force LLM model to qwen2.5:3b
  params.model = 'qwen2.5:3b'
  # force input file to tests/input/test-small.po
  params.input_po = 'tests/input/test-small.po'
  # force system prompt to None
  params.system_prompt = None
  # force temperature to 0
  params.temperature = 0.0
  # retain only one target language
  params.target_language = params.target_languages[0]
  del params.target_languages

  return params


@pytest.fixture(scope="class")
def llm_client(params):
    return ClientBuilder(params).get_client()


def output_model_file(llm_client, suffix=".po"):
  p = Path(OUTPUT_DIRECTORY)
  # print("Output directory:", p)
  if not p.is_dir():
    p.mkdir(parents=True, exist_ok=True)
  basefile_name = f"{llm_client.params.model.replace(':', '-')}_{llm_client.params.target_language}{suffix}"
  # i = 0
  # while True:
  #   outfile_name = p / (basefile_name % i)
  #   if not outfile_name.exists():
  #     print("Output file:", outfile_name)
  #     return outfile_name
  #   i += 1
  return p / basefile_name


def get_django_test_file(lang, file_name='test.po'):
  lang_code = get_language_code(lang)
  return Path(INPUT_DIRECTORY) / 'locale' / lang_code / 'LC_MESSAGES' / file_name


class TestTranspo:

  def translate(self, llm_client, output_file, gentestonly=False):
    with output_file.open('w', newline='', encoding='utf-8') as outfile:
      outfile.write('TEST_TRANSLATIONS = [\n')
      llm_client.target_language = llm_client.params.target_language
      for tr in TEST_TRANSLATIONS:
        out = f"""  {{
  "original_phrase": "{tr['original_phrase']}",  # {params.original_language}
  "context_translation": "{tr['context_translation']}",  # {params.context_language}
  "target_translation": """
        print(out, end='')
        translation, explanation = llm_client.translate(tr['original_phrase'], tr['context_translation'])
        comment = explanation.replace('\n', '\n# ')
        trans_exp = f"""{translation}  # {llm_client.params.target_language}
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
      outfile.write(']\n')
      outfile.close()
    # extract_csv_translations(output_file, params)

  @pytest.mark.gentestvalues
  def test_gentestvalues(self, llm_client):
    self.output_file = output_model_file(llm_client, ".py")
    self.translate(llm_client, self.output_file, gentestonly=True)

  @pytest.mark.asserts_llm_results
  def test_main(self, params, llm_client):
    print(f"Using model {llm_client.params.model} for {params.original_language} -> {params.context_language} -> "
          f"{params.target_languages} with an {params.llm_client} client")
    self.output_file = output_model_file(llm_client)
    self.translate(llm_client, self.output_file)

  def test_noforce(self, llm_client):
    llm_client.params.force = False
    self.output_file = output_model_file(llm_client)
    _, _, _, forced, _ = \
      llm_client.translate_pofile(llm_client.params.input_po, self.output_file)
    assert forced == 0, "There should be no forced translations"  # true whether output file exists or not

  def test_force(self, llm_client):
    llm_client.params.force = True
    self.output_file = output_model_file(llm_client)
    out_existed = self.output_file.exists()
    _, percent_translated, _, forced, _ = \
      llm_client.translate_pofile(llm_client.params.input_po, self.output_file)
    assert forced > 0, "There should be forced translations"
    if out_existed:
      assert percent_translated == 100, "The output file should be 100% translated when forced"

  def test_fuzzy(self, llm_client):
    llm_client.params.fuzzy = True
    self.output_file = output_model_file(llm_client)
    _, _, _, _, fuzzy = \
      llm_client.translate_pofile(llm_client.params.input_po, self.output_file)
    # fuzzy counts fuzzy entries not translated so fuzzy == 0 means all fuzzy entries were translated
    assert fuzzy == 0, "There should be fuzzy translations"

  def test_nofuzzy(self, llm_client):
    llm_client.params.fuzzy = False
    self.output_file = output_model_file(llm_client)
    _, _, _, _, fuzzy = \
      llm_client.translate_pofile(llm_client.params.input_po, self.output_file)
    # fuzzy counts fuzzy entries not translated so if params.fuzzy is False, we should 
    # not translate the only fuzzy entry in test file
    assert fuzzy == 1, "The fuzzy entry should not be translated"

  def test_django_getfiles(self, llm_client):
    from auto_po_lyglot import locate_django_translation_files
    django_files = locate_django_translation_files('./tests',
                                                   llm_client.params.context_language,
                                                   [llm_client.params.target_language])
    print(django_files)
    input_files = list(django_files.keys())
    assert len(input_files) == 1
    assert input_files[0] == str(get_django_test_file(llm_client.params.context_language))
    input_file = input_files[0]

    output_files = django_files[input_file]
    assert len(output_files) == 1
    output_lang_file = output_files[0]
    output_langs = list(output_lang_file.keys())
    assert len(output_langs) == 1
    assert output_langs[0] == llm_client.params.target_language
    output_file = output_lang_file[llm_client.params.target_language]
    assert output_file == str(get_django_test_file(llm_client.target_language))

  def test_django(self, llm_client):
    import shutil
    llm_client.params.django = True
    llm_client.params.input_po = get_django_test_file(llm_client.params.context_language)
    output_file = get_django_test_file(llm_client.target_language)
    output_file_exists = output_file.exists()
    if output_file_exists:
      # output_sha = sha256(output_file)
      out_copy = output_file.with_suffix('.copy' + output_file.suffix)
      shutil.copyfile(output_file, out_copy)
    llm_client.translate_pofile(llm_client.params.input_po, output_file)
    assert output_file.exists(), f"{output_file.name} should exist"
    out_po = polib.pofile(output_file)
    if not output_file_exists:
      in_po = polib.pofile(llm_client.params.input_po)
      assert len(out_po) == len(in_po), \
        f"{output_file} should contain the same number of entries as {llm_client.params.input_po}"
    else:
      try:
        copy_po = polib.pofile(out_copy)
        assert len(out_po) == len(copy_po), f"{output_file} should contain the same number of entries as {out_copy}"
        # check the entries one by one, but as LLMs are not deterministic, we can't assume the the translations are the same
        # so check only the count and that there is at least one translation
        for copy_entry in copy_po:
          if copy_entry.msgid_plural:
            out_entry = out_po.find(copy_entry.msgid_plural, by='msgid_plural')
            assert out_entry is not None, f"{copy_entry.msgid_plural} should exist in result"
            assert len(out_entry.msgstr_plural) == 2, f"{out_entry.msgid_plural} should have 2 translations: single and plural"
          else:
            out_entry = out_po.find(copy_entry.msgid)
            assert out_entry.msgstr != "", f"{out_entry.msgid} should be translated"
      finally:
        # reset original output file
        shutil.move(out_copy, output_file)

  def test_plurals(self, llm_client):
    self.output_file = output_model_file(llm_client)
    llm_client.translate_pofile(llm_client.params.input_po, self.output_file)
    in_po = polib.pofile(llm_client.params.input_po)
    out_po = polib.pofile(self.output_file)
    for entry in in_po:
      if not entry.msgid_plural:
        continue
      out_entry = out_po.find(entry.msgid)
      assert entry.msgid_plural == out_entry.msgid_plural, \
        f"{entry.msgid_plural} should be the same as {out_entry.msgid_plural}"
      if entry.msgstr_plural:
        assert 'msgstr_plural' in out_entry and out_entry.msgstr_plural != '', \
          f"{out_entry.msgid_plural} should not be empty"
      if isinstance(entry.msgstr, list):
        assert isinstance(out_entry.msgstr, list), \
          "{out_entry.msgid_plural} should be a list"
        assert len(entry.msgstr) == len(out_entry.msgstr), \
          "{out_entry.msgid_plural} should have the same number of entries as {entry.msgid_plural}"
