from abc import ABC, abstractmethod
import logging
from ..default_prompts import (
  system_prompt as default_system_prompt,
  additional_system_prompt,
  user_prompt as default_user_prompt,
  po_placeholder_examples,
  basic_examples,
  ambiguous_examples,
  additional_system_prompt_examples,
)

logger = logging.getLogger(__name__)


class TranspoException(Exception):
  pass


class TranspoClient(ABC):
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

  def get_system_prompt(self):
    format = self.params.system_prompt or default_system_prompt
    if self.use_large_system_prompt:
      format += '\n\nAdditional system prompt examples:\n'
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
        format += f'Example #{i}:\n{additional_system_prompt.format(**params)}\n'
        i += 1
    logger.debug("system prompt format: ", format)
    # print("default system prompt format: ", default_system_prompt)
    try:
      basic_exemple = basic_examples[0]
      assert self.params.original_language in basic_exemple
      assert self.params.context_language in basic_exemple
      assert self.target_language in basic_exemple
      simple_original_phrase = basic_exemple[self.params.original_language]
      simple_context_translation = basic_exemple[self.params.context_language]
      simple_target_translation = basic_exemple[self.target_language]
      for ambiguous_example in ambiguous_examples:
        if ambiguous_example['original_language'] == self.params.original_language and \
           ambiguous_example['context_language'] == self.params.context_language:
          assert self.params.original_language in ambiguous_example
          assert self.params.context_language in ambiguous_example
          assert self.target_language in ambiguous_example
          ambiguous_original_phrase = ambiguous_example[self.params.original_language]
          ambiguous_context_translation = ambiguous_example[self.params.context_language]
          ambiguous_target_translation = ambiguous_example[self.target_language]
          ambiguous_explanation = ambiguous_example['explanation']
          ambiguous_target_translation = ambiguous_example[self.target_language]
          break
      if ambiguous_original_phrase is None:
        raise TranspoException("ambiguous_examples.py does not contain an ambiguous example for these languages")

      # PO placeholders
      assert len(po_placeholder_examples) == 3
      for po_placeholder_example in po_placeholder_examples:
        assert self.params.original_language in po_placeholder_example
        assert self.params.context_language in po_placeholder_example
        assert self.target_language in po_placeholder_example

      prompt_params = {
        "original_language": self.params.original_language,
        "context_language": self.params.context_language,
        "target_language": self.target_language,
        "simple_original_phrase": simple_original_phrase,
        "simple_context_translation": simple_context_translation,
        "simple_target_translation": simple_target_translation,
        "ambiguous_original_phrase": ambiguous_original_phrase,
        "ambiguous_context_translation": ambiguous_context_translation,
        "ambiguous_target_translation": ambiguous_target_translation,
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
    except KeyError as e:
      raise TranspoException(f"examples.py does not contain an example for these piece: {str(e)}")

    # first format the explanation then add it to the params before formatting the prompt
    explanation_params = prompt_params.copy()
    explanation_params["target_translation"] = ambiguous_target_translation
    prompt_params["ambiguous_explanation"] = ambiguous_explanation.format(**explanation_params)
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
      raise TranspoException("USER_PROMPT environment variable not set")
    params = {
      "original_language": self.params.original_language,
      "context_language": self.params.context_language,
      "target_language": self.target_language,
      "original_phrase": phrase,
      "context_translation": context_translation
    }
    return format.format(**params)

  def process_translation(self, raw_result):
    translation_result = raw_result.split('\n')
    translation = translation_result[0].strip(' "')
    explanation = None
    if len(translation_result) > 1:
      translation_result.pop(0)
      translation_result = [line for line in translation_result if line]
      explanation = '\n'.join(translation_result)

    return translation, explanation

  def translate(self, phrase, context_translation):
      if self.target_language is None:
        raise TranspoException("Error:target_language must be set before trying to translate anything")
      system_prompt = self.get_system_prompt()
      user_prompt = self.get_user_prompt(phrase, context_translation)
      raw_result = self.get_translation(system_prompt, user_prompt)
      return self.process_translation(raw_result)
