from .client_base import TranspoClient, TranspoException
from openai import OpenAI


class OpenAIAPICompatibleClient(TranspoClient):
  def get_translation(self, system_prompt, user_prompt):
    """
    Retrieves a translation from any OpenAI API compatible client based on the provided system and user prompts.

    Args:
        system_prompt (str): The system prompt to be used for the translation.
        user_prompt (str): The user prompt containing the text to be translated and its context translation.

    Returns:
        str: The translated text

    Raises TranspoException with an error message if the translation fails.
    """

    try:
        response = self.client.chat.completions.create(
            model=self.params.model,
            messages=[
              {"role": "system", "content": system_prompt},
              {"role": "user", "content": user_prompt},
            ],
            # max_tokens=2000,
            temperature=self.params.temperature,
            stream=False
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise TranspoException(str(e))


class OpenAIClient(OpenAIAPICompatibleClient):
    def __init__(self, params, target_language=None):
        params.model = params.model or "gpt-4o-2024-08-06"  # default model if not provided
        super().__init__(params, target_language)
        self.client = OpenAI(api_key=params.open_api_key) if hasattr(params, 'open_api_key') else OpenAI()

# TODO: implement a batch openai client


class OllamaClient(OpenAIAPICompatibleClient):
    def __init__(self, params, target_language=None):
        params.model = params.model or "llama3.1:8b"  # default model if not provided
        params.ollama_base_url = params.ollama_base_url or 'http://localhost:11434/v1'  # default Ollama local server URL
        super().__init__(params, target_language)
        self.client = OpenAI(api_key='Ollama_Key_Unused_But_Required', base_url=self.params.ollama_base_url)
