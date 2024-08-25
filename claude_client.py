import anthropic
from base import TranspoClient, TranspoException, Logger

logger = Logger(__name__)


class ClaudeClient(TranspoClient):
  def __init__(self, params, target_language=None):
    params.model = params.model or "claude-3-5-sonnet-20240620"  # default model if not provided
    super().__init__(params, target_language)
    self.client = anthropic.Anthropic(api_key=self.api_key)

  def get_translation(self, system_prompt, user_prompt):
    try:
      message = self.client.messages.create(
        model=self.model,
        max_tokens=1000,
        temperature=0.2,
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

  def get_translation(self, system_prompt, user_prompt):
    try:
      # uses a beta endpoint, changes in the future
      response = self.client.beta.prompt_caching.messages.create(
        model=self.model,
        max_tokens=1024,
        temperature=0.2,
        system=[
          {
            "type": "text",
            "text": system_prompt,
            "cache_control": {"type": "ephemeral"}
          }
        ],
        messages=[{"role": "user", "content": user_prompt}],
      )
      logger.info("claude cached usage", response.usage)
      return response.content[0].text
    except Exception as e:
      raise TranspoException(str(e))
