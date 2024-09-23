from abc import ABC, abstractmethod
import logging
from pathlib import Path
import polib
from time import sleep
from datetime import datetime

from auto_po_lyglot.getenv import get_language_code
from ..default_prompts import (
  system_prompt as default_system_prompt,
  additional_system_prompt,
  user_prompt as default_user_prompt,
  po_placeholder_examples,
  basic_examples,
  ambiguous_examples,
  html_markers_examples,
  additional_system_prompt_examples,
)

logger = logging.getLogger(__name__)


class PoLyglotException(Exception):
  pass


class AutoPoLyglotClient(ABC):
  """
  Base class for all LLM clients.
  """
  # set to True in client sub classes to use a large system prompt. Useful for claude_cached 
  # where the system prompt must at least be 1024 tokens
  use_large_system_prompt = False

  def __init__(self, params, target_language=None):
    self.params = params
    # target language can be set later but before any translation.
    # it can also be changed by the user at any time, the prompt will be updated automatically
    self.target_language = target_language
    logger.debug(f"TranspoClient using model {self.params.model}")
    self.first = True

  @abstractmethod
  def get_translation(self, phrase, context_translation):
    """
    Retrieves a translation from an LLM client based on the provided system and user prompts.

    Args:
        system_prompt (str): The system prompt to be used for the translation.
        user_prompt (str): The user prompt containing the text to be translated and its context translation.

    Returns:
        str: The translated text

    Raises TranspoException with an error message if the translation fails.
    """
    ...

  def _get_languages(self):
    return {
        "original_language": self.params.original_language,
        "context_language": self.params.context_language,
        "target_language": self.target_language,
    }

  def _get_additional_system_prompt(self):
    additional_format = '\n\nAdditional system prompt examples:\n'
    i = 1
    for example in additional_system_prompt_examples:
      params = {
        'original_language': self.params.original_language,
        'context_language': self.params.context_language,
        'target_language': self.target_language,
        'original_phrase': example[self.params.original_language],
        'context_translation': example[self.params.context_language],
        'target_translation': example[self.target_language],
      }
      additional_format += f'Example #{i}:\n{additional_system_prompt.format(**params)}\n'
      i += 1
    return additional_format

  def _get_basic_examples(self):
    basic_exemple = basic_examples[0]
    assert self.params.original_language in basic_exemple
    assert self.params.context_language in basic_exemple
    assert self.target_language in basic_exemple
    return {
      "simple_original_phrase": basic_exemple[self.params.original_language],
      "simple_context_translation": basic_exemple[self.params.context_language],
      "simple_target_translation": basic_exemple[self.target_language],
    }

  def _get_ambiguous_examples(self):
    for ambiguous_example in ambiguous_examples:
      if ambiguous_example['original_language'] == self.params.original_language and \
          ambiguous_example['context_language'] == self.params.context_language:
        assert self.params.original_language in ambiguous_example
        assert self.params.context_language in ambiguous_example
        assert self.target_language in ambiguous_example
        ambiguous_original_phrase = ambiguous_example[self.params.original_language]
        ambiguous_context_translation = ambiguous_example[self.params.context_language]
        ambiguous_target_translation = ambiguous_example[self.target_language]
        ambiguous_target_translation = ambiguous_example[self.target_language]
        ambiguous_explanation = ambiguous_example['explanation']
        break
    if ambiguous_original_phrase is None:
      raise PoLyglotException("ambiguous_examples.py does not contain an ambiguous example for these languages")

    return {
      "ambiguous_original_phrase": ambiguous_original_phrase,
      "ambiguous_context_translation": ambiguous_context_translation,
      "ambiguous_target_translation": ambiguous_target_translation,
      "ambiguous_explanation": ambiguous_explanation
    }

  def _get_po_placeholder_examples(self):
    assert len(po_placeholder_examples) == 3
    for po_placeholder_example in po_placeholder_examples:
      assert self.params.original_language in po_placeholder_example
      assert self.params.context_language in po_placeholder_example
      assert self.target_language in po_placeholder_example
    return {
      "po_placeholder_original_phrase_1": po_placeholder_examples[0][self.params.original_language],
      "po_placeholder_context_translation_1": po_placeholder_examples[0][self.params.context_language],
      "po_placeholder_target_translation_1": po_placeholder_examples[0][self.target_language],
      "po_placeholder_original_phrase_2": po_placeholder_examples[1][self.params.original_language],
      "po_placeholder_context_translation_2": po_placeholder_examples[1][self.params.context_language],
      "po_placeholder_target_translation_2": po_placeholder_examples[1][self.target_language],
      "po_placeholder_original_phrase_3": po_placeholder_examples[2][self.params.original_language],
      "po_placeholder_context_translation_3": po_placeholder_examples[2][self.params.context_language],
      "po_placeholder_target_translation_3": po_placeholder_examples[2][self.target_language],

    }

  def _get_html_markers_examples(self):
    assert len(html_markers_examples) == 2
    for html_markers_example in html_markers_examples:
      assert self.params.original_language in html_markers_example
      assert self.params.context_language in html_markers_example
      assert self.target_language in html_markers_example
    return {
      "html_original_phrase_1": html_markers_examples[0][self.params.original_language],
      "html_context_translation_1": html_markers_examples[0][self.params.context_language],
      "html_target_translation_1": html_markers_examples[0][self.target_language],
      "html_original_phrase_2": html_markers_examples[1][self.params.original_language],
      "html_context_translation_2": html_markers_examples[1][self.params.context_language],
      "html_target_translation_2": html_markers_examples[1][self.target_language],
    }

  def _get_ambiguous_explanation(self, params):
    # format the explanation using the already defined parameters
    explanation_params = params.copy()
    explanation_params["target_translation"] = params['ambiguous_target_translation']
    return {"ambiguous_explanation": params['ambiguous_explanation'].format(**explanation_params)}

  def get_system_prompt(self):
    format = self.params.system_prompt or default_system_prompt
    if self.use_large_system_prompt:
      format += self._get_additional_system_prompt()
    logger.debug("system prompt format: ", format)
    # print("default system prompt format: ", default_system_prompt)
    try:
      prompt_params = self._get_languages()
      prompt_params.update(self._get_basic_examples())
      prompt_params.update(self._get_ambiguous_examples())
      prompt_params.update(self._get_po_placeholder_examples())
      prompt_params.update(self._get_html_markers_examples())
      prompt_params.update(self._get_ambiguous_explanation(prompt_params))
    except KeyError as e:
      raise PoLyglotException(f"examples.py does not contain an example for these piece: {str(e)}")

    system_prompt = format.format(**prompt_params)
    if self.first:
      logger.info(f"First system prompt:\n{system_prompt}")
      self.first = False
    else:
      logger.debug(f"System prompt:\n{system_prompt}")
    return system_prompt

  def get_user_prompt(self, phrase, context_translation):
    format = self.params.user_prompt or default_user_prompt
    if format is None:
      raise PoLyglotException("USER_PROMPT environment variable not set")
    params = {
      "original_language": self.params.original_language,
      "context_language": self.params.context_language,
      "target_language": self.target_language,
      "original_phrase": phrase,
      "context_translation": context_translation
    }
    return format.format(**params)

  def process_translation(self, raw_result):
    """
    Process the raw translation result
    Args:
        raw_result (str): The raw translation result
    Returns:
        tuple(str,str): The translation and its explanation
    """
    translation_result = raw_result.split('\n')
    translation = translation_result[0].strip(' "')
    explanation = None
    if len(translation_result) > 1:
      translation_result.pop(0)
      translation_result = [line for line in translation_result if line]
      explanation = '\n'.join(translation_result)

    return translation, explanation

  def translate(self, phrase, context_translation):
      """
      Translate a single phrase using the given context translation
      Args:
          phrase (str): The phrase to translate
          context_translation (str): The context translation
      Returns:
          str: The translated phrase and its explanation
      """
      if self.target_language is None:
        raise PoLyglotException("Error:target_language must be set before trying to translate anything")
      system_prompt = self.get_system_prompt()
      user_prompt = self.get_user_prompt(phrase, context_translation)
      raw_result = self.get_translation(system_prompt, user_prompt)
      return self.process_translation(raw_result)

  def set_po_header_and_metadata(self, po, input_file):
    input_path = Path(input_file)
    if str(input_path.parents[1]) == 'LC_MESSAGES':
      app_name = input_path.parents[4].name.capitalize()
      wr_input_file = '/'.join(input_path.parts[-6:])  # don't keep the beginning of the file name to put in the header
    else:
      app_name = "NO NAME FOUND"
      wr_input_file = input_file
    po.header = f"""{self.target_language} Translations for {app_name} app.
Copyright (C) {datetime.now().year} {self.params.owner}
This file is distributed under the same license as the application.
This file was generated from {wr_input_file} by [Auto-po-lyglot](https://github.com/leolivier/auto-po-lyglot)
using the {self.params.model} model. Depending on the model, it may contain some errors and should be reviewed
by a human translator. Also depending on the model, each translation can be preceded by an explanation provided
by the model.
{self.params.owner} {self.params.owner_mail}, {datetime.now().year}.
"""
    po.metadata['Last-Translator'] = f'Auto-po-lyglot using {self.params.model} (https://github.com/leolivier/auto-po-lyglot)'
    po.metadata['Language'] = get_language_code(self.target_language).upper()
    po.metadata['PO-Revision-Date'] = f"{datetime.now():%Y-%m-%d %H:%M+00:00}\n"  # "2024-08-07 20:09+0200""

  def _copy_entry(self, to_entry, from_entry):
    for attr in ["msgid", "msgstr", "msgid_plural", "fuzzy",
                 "obsolete", "comment", "msgctxt", "encoding",
                 "occurrences", "tcomment", "flags"
                 "previous_msgctxt", "previous_msgid",
                 "previous_msgid_plural", "linenum"]:
      setattr(to_entry, attr, getattr(from_entry, attr))
    if from_entry.msgstr_plural:  # entry with plural management. Deep copy the plural case
      to_entry.msgstr_plural = from_entry.msgstr_plural.copy()

  def translate_entry(self, entry, out_po=None):
    """
    Translate a single entry
    Args:
        entry (polib.POEntry): The entry to translate
        out_po (polib.POFile): The output po file if already existing
    Returns:
        nothing (the entry is updated in-place)
    """
    forced = False
    if entry.msgid:
      # dont translate fuzzy entries except if forced by params
      if entry.fuzzy and not self.params.fuzzy:
        return {"status": 'Fuzzy', "forced": forced}
      if out_po:
        out_entry = out_po.find(entry.msgid)
        # don't translate again the existing translations except if forced by params
        if out_entry:
          if out_entry.msgstr != "" and not self.params.force:
            self._copy_entry(entry, out_entry)
            return {"status": 'Already', "forced": forced}
          else:
            forced = "True"
      original_phrase = entry.msgid
      if entry.msgid_plural:  # entry with plural management. First manage the singular case
        context_translation = entry.msgstr_plural[0] if entry.msgstr_plural else entry.msgid_plural
      else:
        context_translation = entry.msgstr if entry.msgstr else entry.msgid
      translation, explanation = self.translate(original_phrase, context_translation)
      # Add explanation to comment
      if explanation:
        entry.comment = explanation
      # Update translation
      if entry.msgid_plural:  # entry with plural management. Update the singular case
        entry.msgstr_plural[0] = translation
      else:
        entry.msgstr = translation
      logger.info(f"""==================
{self.params.original_language}: "{original_phrase}"
{self.params.context_language}: "{context_translation}"
{self.target_language}: "{translation}"
Comment:{explanation if explanation else ''}
""")

      if entry.msgid_plural:  # entry with plural management. Now manage the plural case
        original_phrase = entry.msgid_plural
        context_translation = entry.msgstr_plural[1] if entry.msgstr_plural else entry.msgid_plural
        translation, explanation = self.translate(original_phrase, context_translation)
        # Update translation
        entry.msgstr_plural[1] = translation
        # Note: the plural explanation is **not** stored in the out po file.
        logger.info(f"""================== PLURAL CASE ==================
{self.params.original_language}: "{original_phrase}"
{self.params.context_language}: "{context_translation}"
{self.target_language}: "{translation}"
Comment:{explanation if explanation else ''}
""")
        return {"status": 'Plural', "forced": forced}
    return {"status": 'Singular', "forced": forced}

  def translate_pofile(self, input_file, output_file):
    logger.info(f"Translating {input_file} to {self.target_language} in {output_file}")
    po = polib.pofile(input_file)
    out_po = polib.pofile(output_file) if Path(output_file).exists() else None
    self.set_po_header_and_metadata(po, input_file)
    try:
      nb_translations = 0
      already_translated = 0
      forced = 0
      fuzzy = 0
      for entry in po:
        res = self.translate_entry(entry, out_po)
        if res['status'] == 'Already':
          already_translated += 1
        elif res['status'] == 'Fuzzy':
          fuzzy += 1
        elif res['forced'] == 'True':
          forced += 1
        sleep(0.5)  # Sleep for 1/2 second to avoid rate limiting
        nb_translations += 1
    except Exception as e:
      logger.error(f"Error: {e}")
    # Save the new .po file even if there was an error to not lose what was translated
    po.save(output_file)
    if self.params.compile:
      logger.info(f"Compiling {output_file}")
      mo_output_file = Path(output_file).with_suffix('.mo')
      po.save_as_mofile(mo_output_file)
    percent_translated = round(nb_translations / (len(po)-already_translated) * 100, 2)
    logger.info(f"Saved {output_file}, translated {nb_translations} entries out "
                f"of {len(po)} entries, with {already_translated} entries already translated and not taken into account "
                f"({percent_translated}%)")
    if forced > 0:
      logger.info(f"Forced {forced} entries")
    return nb_translations, percent_translated, already_translated, forced, fuzzy
