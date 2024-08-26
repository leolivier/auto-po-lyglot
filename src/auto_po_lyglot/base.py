from abc import ABC, abstractmethod
import logging
from os import environ
import sys


class TranspoException(Exception):
  pass


class TranspoClient(ABC):
  def __init__(self, params, target_language=None):
    self.params = params
    # target language can be set later but before any translation.
    # it can also be changed by the user at any time, the prompt will be updated automatically
    self.target_language = target_language
    logger.info(f"TranspoClient using model {self.params.model}")
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
    format = self.params.system_prompt if hasattr(self.params, 'system_prompt') else None
    if format is None:
      raise TranspoException("SYSTEM_PROMPT environment variable not set")
    logger.debug("system prompt format: ", format)
    prompt_params = {
      "original_language": self.params.original_language,
      "context_language": self.params.context_language,
      "target_language": self.target_language,
    }
    system_prompt = format.format(**prompt_params)
    if self.first:
      logger.info("system prompt:\n", system_prompt)
      self.first = False
    else:
      logger.debug("system prompt:\n", system_prompt)
    return system_prompt

  def get_user_prompt(self, phrase, context_translation):
    format = environ.get("USER_PROMPT", None)
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
    explanation = 'Not provided'
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


class Logger():
  verbose_mode = False

  def __init__(self, name):
    self.logger = logging.getLogger(name)

  def vprint(self, *args, **kwargs):
    """Print only if verbose is set"""
    if self.verbose_mode:
      print(*args, **kwargs)
      sys.stdout.flush()

  def info(self, *args, **kwargs):
    self.logger.info(*args, **kwargs)

  def debug(self, *args, **kwargs):
    self.logger.debug(*args, **kwargs)

  def error(self, *args, **kwargs):
    self.logger.error(*args, **kwargs)

  def warning(self, *args, **kwargs):
    self.logger.warning(*args, **kwargs)

  def critical(self, *args, **kwargs):
    self.logger.critical(*args, **kwargs)

  def exception(self, *args, **kwargs):
    self.logger.exception(*args, **kwargs)

  @classmethod
  def set_verbose(cls, verbose):
    cls.verbose_mode = verbose

  def set_level(self, level):
    self.logger.setLevel(level)

  def get_level(self):
    return self.logger.getEffectiveLevel()

  def set_format(self, format):
    self.logger.handlers[0].setFormatter(logging.Formatter(format))

  def get_format(self):
    return self.logger.handlers[0].formatter

  def set_file(self, filename):
    self.logger.addHandler(logging.FileHandler(filename))

  def get_file(self):
    return self.logger.handlers[0]

  def remove_file(self):
    self.logger.removeHandler(self.logger.handlers[0])

  def remove_console(self):
    self.logger.removeHandler(self.logger.handlers[1])

  def remove_all(self):
    self.logger.removeHandler(self.logger.handlers[0])
    self.logger.removeHandler(self.logger.handlers[1])


logger = Logger(__name__)
