import anthropic

from transpo_base import TranspoClient, TranspoException


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

  def __init__(self, original_language, context_language, target_language, api_key, model=None):
    super().__init__(original_language, context_language, target_language, api_key, model)
    self.cached_system_prompt = None

  def get_system_prompt(self):
    """
    Returns the system prompt for the translation task, caching the result to avoid repeated computation.

    Parameters:
    None

    Returns:
    str: The system prompt for the translation task, or None if the prompt has not changed since the last call.
    """
    super_prompt = super().get_system_prompt()
    if self.cached_system_prompt is None:
      self.cached_system_prompt = super_prompt
      return super_prompt
    elif self.cached_system_prompt != super_prompt:
      self.cached_system_prompt = super_prompt
    return None

  def get_translation(self, system_prompt, user_prompt):
    # TODO: This works only for ttl of the cache ==> can be improved
    if system_prompt is not None:  # Means the system prompt has changed since last call and must be cached
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
        return response.content[0].text
      except Exception as e:
        raise TranspoException(str(e))
    else:  # system prompt has not changed
      return super().get_translation(system_prompt, user_prompt)
