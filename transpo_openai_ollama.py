from transpo_abc import TranspoClient, TranspoException
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
            model=self.model,
            messages=[
              {"role": "system", "content": system_prompt},
              {"role": "user", "content": user_prompt},
            ],
            # max_tokens=2000,
            temperature=0.2,
            stream=False
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise TranspoException(str(e))


class OpenAIClient(OpenAIAPICompatibleClient):
    def __init__(self,
                 original_language,
                 context_language,
                 target_language,
                 api_key=None,  # OPEN_API_KEY to be provided in the environment if None here
                 model="gpt-4o-2024-08-06"  # default model if not provided
                 ):
        super().__init__(original_language, context_language, target_language, api_key, model)
        self.client = OpenAI(api_key=api_key) if api_key else OpenAI()


class OllamaClient(OpenAIAPICompatibleClient):
    def __init__(self,
                 original_language,
                 context_language,
                 target_language,
                 model="llama3.1:8b",  # default model if not provided
                 base_url='http://localhost:11434/v1'  # default Ollama local server URL
                 ):
        super().__init__(original_language, context_language, target_language,
                         api_key='Ollama_Key_Unused_But_Required', model=model)
        self.client = OpenAI(api_key=self.api_key, base_url=base_url)
