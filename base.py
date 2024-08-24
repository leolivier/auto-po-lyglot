from abc import ABC, abstractmethod
import logging
from os import environ


class TranspoException(Exception):
  pass


class TranspoClient(ABC):
  def __init__(self, original_language, context_language, target_language, api_key, model=None):
    self.original_language = original_language
    self.context_language = context_language
    self.target_language = target_language
    self.api_key = api_key
    self.model = model
    logger.info(f"TranspoClient using model {self.model}")
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
    format = environ.get("SYSTEM_PROMPT", None)
    logger.debug("system prompt format: ", format)
    if format is None:
      raise TranspoException("SYSTEM_PROMPT environment variable not set")
    params = {
      "original_language": self.original_language,
      "context_language": self.context_language,
      "target_language": self.target_language,
    }
    system_prompt = format.format(**params)
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
      "original_language": self.original_language,
      "context_language": self.context_language,
      "target_language": self.target_language,
      "original_phrase": phrase,
      "context_translation": context_translation
    }
    return format.format(**params)

  def translate(self, phrase, context_translation):
      system_prompt = self.get_system_prompt()
      user_prompt = self.get_user_prompt(phrase, context_translation)
      return self.get_translation(system_prompt, user_prompt)


class Logger():
  verbose_mode = False

  def __init__(self, name):
    self.logger = logging.getLogger(name)

  def vprint(self, *args, **kwargs):
    """Print only if verbose is set"""
    if self.verbose_mode:
      print(*args, **kwargs)
      # sys.stdout.flush()

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
