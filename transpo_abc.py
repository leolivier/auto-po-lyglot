from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class TranspoException(Exception):
  pass


class TranspoPrompts(ABC):

  def __init__(self, client):
    self.original_language = client.original_language
    self.context_language = client.context_language
    self.target_language = client.target_language

  @abstractmethod
  def get_system_prompt(self):
    ...

  @abstractmethod
  def get_user_prompt(self, phrase, contextual_translation):
    ...


class TranspoClient(ABC):
  def __init__(self, original_language, context_language, target_language, api_key, model=None):
    self.original_language = original_language
    self.context_language = context_language
    self.target_language = target_language
    self.api_key = api_key
    self.model = model
    logger.info(f"TranspoClient using model {self.model}")

  @abstractmethod
  def get_translation(self, phrase, contextual_translation):
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

  def translate(self, prompter, phrase, contextual_translation):
      prompt = prompter(self)
      system_prompt = prompt.get_system_prompt()
      user_prompt = prompt.get_user_prompt(phrase, contextual_translation)
      return self.get_translation(system_prompt, user_prompt)
