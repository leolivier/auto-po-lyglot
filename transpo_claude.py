import anthropic

from transpo_abc import TranspoClient, TranspoException


class ClaudeClient(TranspoClient):
  def __init__(self, original_language, context_language, target_language, api_key, model=None):
    super().__init__(original_language, context_language, target_language, api_key, model)
    self.client = anthropic.Client(self.api_key)

  def get_translation(self, system_prompt, user_prompt):
    try:
      message = self.client.messages.create(
        model=self.model,
        max_tokens=1000,
        temperature=0,
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
      return message.content
    except Exception as e:
      raise TranspoException(str(e))
