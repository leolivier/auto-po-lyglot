import google.generativeai as genai
import os
from .client_base import TranspoClient
import logging

logger = logging.getLogger(__name__)


class GeminiClient(TranspoClient):
  cached_system_prompt = None

  def __init__(self, params, target_language=None):
    params.model = params.model or 'gemini-1.5-flash'  # default model if not provided
    super().__init__(params, target_language)
    api_key = params.gemini_api_key if hasattr(params, 'gemini_api_key') else os.environ["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    # self.client = genai.GenerativeModel(params.model) # must be regenerated every time the system prompt changes

  def get_translation(self, system_prompt, user_prompt):
    if not self.cached_system_prompt or self.cached_system_prompt != system_prompt:
      self.cached_system_prompt = system_prompt
      self.client = genai.GenerativeModel(self.params.model, system_instruction=system_prompt)

    response = self.client.generate_content(user_prompt)
    return response.text
