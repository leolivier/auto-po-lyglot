import xai_sdk
import asyncio
from .client_base import TranspoClient
import logging

logger = logging.getLogger(__name__)


class GrokClient(TranspoClient):
  def __init__(self, params, target_language=None):
    params.model = params.model or ""  # default model given by Grok itself if not provided
    super().__init__(params, target_language)
    self.client = xai_sdk.Client(api_key=params.xai_api_key) if hasattr(params, 'xai_api_key') else xai_sdk.Client()

  async def async_get_translation(self, system_prompt, user_prompt):
    conversation = self.client.chat.create_conversation()
    response = await conversation.add_response_no_stream(f'{system_prompt}\n{user_prompt}\n')
    return response.message

  def get_translation(self, system_prompt, user_prompt):
    return asyncio.run(self.async_get_translation(system_prompt, user_prompt))
