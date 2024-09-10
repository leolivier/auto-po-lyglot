#!/usr/bin/env python
import logging
from dotenv import load_dotenv
from os import environ
import argparse
import sys

logger = logging.getLogger(__name__)


def set_all_loggers_level(level):
    logger.info(f"Setting all loggers to level {logging.getLevelName(level)}")

    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)
    formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    for name in logging.root.manager.loggerDict:
      if not name.startswith('auto_po_lyglot.'):
        continue
      nlogger = logging.getLogger(name)
      nlogger.handlers = []
      nlogger.addHandler(handler)
      nlogger.setLevel(level)
      nlogger.propagate = False

    root = logging.getLogger()
    root.handlers = []
    root.addHandler(handler)
    root.setLevel(level)


# def inspect_logger(logger):
#     print(f"Logger: {logger.name}")
#     print(f"  Level: {logging.getLevelName(logger.level)}")
#     print(f"  Propagate: {logger.propagate}")
#     print("  Handlers:")
#     for idx, handler in enumerate(logger.handlers):
#         print(f"    Handler {idx}: {type(handler).__name__}")
#         print(f"      Level: {logging.getLevelName(handler.level)}")


class ParamsLoader:
  description = """
Creates a .po translation file based on an existing one using a given model and llm type.
It reads the parameters from the command line and completes them if necessary from the .env in the same directory.
It iterates over the provided target languages, and for each language iterates over the entries of the input po file and,
using the provided client, model and prompt, translates the original phrase into the target language with the help of
the context translation."""

  def parse_args(self, additional_args=None):
    parser = argparse.ArgumentParser(description=self.description)
    # Add arguments
    parser.add_argument('-p', '--show_prompts',
                        action='store_true',
                        help='show the prompts used for translation and exits')
    parser.add_argument('-l', '--llm',
                        type=str,
                        help='Le type of LLM you want to use. Can be openai, ollama, claude or claude_cached. '
                             'For openai or claude[_cached], you need to set the api key in the environment. '
                             'Supersedes LLM_CLIENT in .env. Default is ollama',
                        choices=['openai', 'ollama', 'claude', 'claude_cached', 'gemini', 'grok'])
    parser.add_argument('-m', '--model',
                        type=str,
                        help='the name of the model to use. Supersedes LLM_MODEL in .env. If not provided at all, '
                             'a default model will be used, based on the chosen client')
    parser.add_argument('-t', '--temperature',
                        type=float,
                        help='the temperature of the model. Supersedes TEMPERATURE in .env. If not provided at all, '
                             'a default value of 0.2 will be used')
    parser.add_argument('--original_language',
                        type=str,
                        help='the language of the original phrase. Supersedes ORIGINAL_LANGUAGE in .env. ')
    parser.add_argument('--context_language',
                        type=str,
                        help='the language of the context translation. Supersedes CONTEXT_LANGUAGE in .env. ')
    parser.add_argument('--target_language',
                        type=str,
                        help='the language into which the original phrase will be translated. Supersedes '
                             'TARGET_LANGUAGE in .env. ')
    parser.add_argument('-i', '--input_po',
                        type=str,
                        help='the .po file containing the msgids (phrases to be translated) '
                              'and msgstrs (context translations). Supersedes INPUT_PO in .env.')
    parser.add_argument('-o', '--output_po',
                        type=str,
                        help='the .po file where the translated results will be written. If not provided, '
                             'it will be created in the same directory as the input_po except if the input po file has '
                             'the specific format .../locale/<context language code>/LC_MESSAGES/<input po file name>. '
                             'In this case, the output po file will be created as '
                             '.../locale/<target language code>/LC_MESSAGES/<input po file name>. Supersedes '
                             'OUTPUT_PO in .env.')

    parser.add_argument('-v', '--verbose', action='store_true', help='verbose mode. Equivalent to LOG_LEVEL=INFO in .env')
    parser.add_argument('-vv', '--debug', action='store_true', help='debug mode. Equivalent to LOG_LEVEL=DEBUG in .env')
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
    self._client = None

    args = self.parse_args(additional_args)

    if args.show_prompts:
      self.show_prompts = True
      return  # will exit just after showing prompts, no need to continue
    else:
      self.show_prompts = False

    load_dotenv(override=True)

    if args.debug or (not args.verbose and environ.get('LOG_LEVEL', None) == 'DEBUG'):
      self.log_level = logging.DEBUG
    elif args.verbose or environ.get('LOG_LEVEL', None) == 'INFO':
      self.log_level = logging.INFO
    else:
      self.log_level = logging.WARNING
    set_all_loggers_level(self.log_level)

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

    self.system_prompt = environ.get('SYSTEM_PROMPT', None)
    if self.system_prompt:
      logger.debug(f"SYSTEM_PROMPT environment variable is set to '{self.system_prompt}'")

    self.user_prompt = environ.get('USER_PROMPT', None)
    if self.user_prompt:
      logger.debug(f"USER_PROMPT environment variable is set to '{self.user_prompt}'")

    self.temperature = args.temperature or float(environ.get('TEMPERATURE', 0.2))

    self.input_po = args.input_po or environ.get('INPUT_PO', None)
    self.output_po = args.output_po or environ.get('OUTPUT_PO', None)

    # generic processing of additional arguments
    if additional_args:
      for argument in additional_args:
        arg = argument.get('arg')
        while arg.startswith('-'):
          arg = arg[1:]
        val = getattr(args, arg) or environ.get(argument.get('env', 'UNDEFINED_VARIABLE'), argument.get('default', None))
        setattr(self, arg, val)

    logger.info(f"Loaded Params: {self.__dict__}")

  def get_client(self):
    if not self._client:

      match self.llm_client:
        case 'ollama':
          from .clients.openai_ollama_client import OllamaClient as LLMClient
        case 'openai':
          # uses OpenAI GPT-4o by default
          from .clients.openai_ollama_client import OpenAIClient as LLMClient
        case 'claude':
          # uses Claude Sonnet 3.5 by default
          from .clients.claude_client import ClaudeClient as LLMClient
        case 'claude_cached':
          # uses Claude Sonnet 3.5, cached mode for long system prompts
          from .clients.claude_client import CachedClaudeClient as LLMClient
        case 'gemini':
          from .clients.gemini_client import GeminiClient as LLMClient
        case 'grok':
          from .clients.grok_client import GrokClient as LLMClient
        case _:
          raise Exception(
            f"LLM_CLIENT must be one of 'ollama', 'openai', 'claude' or 'claude_cached', not '{self.llm_client}'"
            )
      self._client = LLMClient(self, "")

    return self._client
