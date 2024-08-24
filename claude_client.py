import anthropic

from base import TranspoClient, TranspoException


class ClaudeClient(TranspoClient):
  def __init__(self,
               original_language,
               context_language,
               target_language,
               api_key=None,  # ANTHROPIC_API_KEY to be provided in the environment if None here
               model="claude-3-5-sonnet-20240620"  # default model if not provided
               ):
    super().__init__(original_language, context_language, target_language, api_key, model)
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
      print("claude cached usage", response.usage)
      return response.content[0].text
    except Exception as e:
      raise TranspoException(str(e))
