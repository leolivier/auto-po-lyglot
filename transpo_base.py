from abc import ABC, abstractmethod
import logging
from os import environ

logger = logging.getLogger(__name__)


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
    if format is None:
      raise TranspoException("SYSTEM_PROMPT environment variable not set")
    params = {
      "original_language": self.original_language,
      "context_language": self.context_language,
      "target_language": self.target_language,
    }
    return format.format(**params)

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
