#!/usr/bin/env python
from dotenv import load_dotenv
from os import environ
import argparse
from .base import Logger

logger = Logger(__name__)


class TranspoParams:
  description = """
Creates a .po translation file based on an existing one using a given model and llm type.
It reads the parameters from the command line and completes them if necessary from the .env in the same directory.
It iterates over the provided target languages, and for each language iterates over the entries of the input po file and,
using the provided client, model and prompt, translates the original phrase into the target language with the help of
the context translation."""

  def parse_args(self, additional_args=None):
    parser = argparse.ArgumentParser(description=self.description)
    # Add arguments
    parser.add_argument('--llm',
                        type=str,
                        help='Le type of LLM you want to use. Can be openai, ollama, claude or claude_cached. '
                             'For openai or claude[_cached], you need to set the api key in the environment')
    parser.add_argument('--model',
                        type=str,
                        help='the name of the model to use. If not provided, a default model '
                             'will be used, based on the chosen client')
    parser.add_argument('--original_language',
                        type=str,
                        help='the language of the original phrase')
    parser.add_argument('--context_language',
                        type=str,
                        help='the language of the context translation')
    parser.add_argument('--target_language',
                        type=str,
                        help='the language into which the original phrase will be translated')
    parser.add_argument('--verbose', action='store_true', help='verbose mode')
    if additional_args:
      for arg in additional_args:
        if arg.get('action'):
          parser.add_argument(arg.get('arg'), action=arg.get('action'), help=arg.get('help'))
        else:
          parser.add_argument(arg.get('arg'), type=arg.get('type'), help=arg.get('help'))

    # Analyze the arguments
    return parser.parse_args()

  def __init__(self, additional_args=None):
    "looks at args and returns an object with attributes of these args completed by the environ variables where needed"
    args = self.parse_args(additional_args)

    load_dotenv(override=True)

    self.verbose = args.verbose or bool(environ.get('VERBOSE', False))
    logger.set_verbose(self.verbose)

    # original language
    self.original_language = args.original_language or environ.get('ORIGINAL_LANGUAGE', 'English')
    # context translation language
    self.context_language = args.context_language or environ.get('CONTEXT_LANGUAGE', 'French')
    # LLM client and model
    self.llm_client = args.llm or environ.get('LLM_CLIENT', 'ollama')
    self.model = args.model or environ.get('LLM_MODEL', None)

    # ollama base url if needed
    self.ollama_base_url = environ.get('OLLAMA_BASE_URL', 'http://localhost:11434/v1')

    # the target languages to test for translation
    if args.target_language:
      self.test_target_languages = [args.target_language]
    else:
      self.test_target_languages = environ.get('TARGET_LANGUAGES', 'Spanish').split(',')

    # generic processing of additional arguments
    if additional_args:
      for argument in additional_args:
        arg = argument.get('arg')
        while arg.startswith('-'):
          arg = arg[1:]
        val = getattr(args, arg) or environ.get(argument.get('env'), argument.get('default', None))
        setattr(self, arg, val)

  def get_client(self):
    match self.llm_client:
      case 'ollama':
        from .openai_ollama_client import OllamaClient as LLMClient
      case 'openai':
        # uses OpenAI GPT-4o by default
        from .openai_ollama_client import OpenAIClient as LLMClient
      case 'claude':
        # uses Claude Sonnet 3.5 by default
        from .claude_client import ClaudeClient as LLMClient
      case 'claude_cached':
        # uses Claude Sonnet 3.5, cached mode for long system prompts
        from .claude_client import CachedClaudeClient as LLMClient
      case _:
        raise Exception(
          f"LLM_CLIENT must be one of 'ollama', 'openai', 'claude' or 'claude_cached', not '{self.llm_client}'"
          )
    return LLMClient(self, "")