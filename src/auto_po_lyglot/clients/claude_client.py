from time import sleep
from anthropic import Anthropic
from .client_base import TranspoClient, TranspoException
import logging

logger = logging.getLogger(__name__)


class ClaudeClient(TranspoClient):
  def __init__(self, params, target_language=None):
    params.model = params.model or "claude-3-5-sonnet-20240620"  # default model if not provided
    super().__init__(params, target_language)
    self.client = Anthropic(api_key=params.anthropic_api_key) if hasattr(params, 'anthropic_api_key') else Anthropic()

  def get_translation(self, system_prompt, user_prompt):
    try:
      message = self.client.messages.create(
        model=self.params.model,
        max_tokens=1000,
        temperature=self.params.temperature,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_prompt
                    }
                ]
            }
        ]
      )
      return message.content[0].text
    except Exception as e:
      raise TranspoException(str(e))


class CachedClaudeClient(ClaudeClient):
  use_large_system_prompt = True  # claude cached system prompt must be at least 1024 tokens
  first = True

  def get_translation(self, system_prompt, user_prompt):
    retries = 0
    next_retry_in = 1
    max_retries = 5
    while retries < max_retries:
      try:
        # uses a beta endpoint, changes in the future
        response = self.client.beta.prompt_caching.messages.create(
          model=self.params.model,
          max_tokens=1024,
          temperature=self.params.temperature,
          system=[
            {
              "type": "text",
              "text": system_prompt,
              "cache_control": {"type": "ephemeral"}
            }
          ],
          messages=[{"role": "user", "content": user_prompt}],
        )
        if self.first:
          self.first = False
          logger.info(f"claude cached usage: {response.usage}")
        else:
          logger.debug(f"claude cached usage: {response.usage}")
        return response.content[0].text
      except Exception as e:
        if "overloaded_error" in str(e):
          logger.info(f"claude cached overloaded error, next retry in {next_retry_in} seconds")
          next_retry_in = 2 ** retries
          if next_retry_in > 60:  # should never happen with max_retries = 5
            next_retry_in = 60
          sleep(next_retry_in)
          retries += 1
          continue
        raise TranspoException(str(e))
