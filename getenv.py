#!/usr/bin/env python
import sys
from dotenv import load_dotenv
from os import environ
import json
import argparse


class TranspoParams:
  description = """
Generates a translation file using a given model and llm type. It reads the parameters from the command line,
and completes them when necessary from the content of .env in the same directory.
It iterates over a list of test translations containing the original phrase and its translation
within a context language, and for each target language, translates the original phrase
into the target language helped with the context translation, by using the provided client and
prompt implementation."""

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
    for arg in additional_args:
      parser.add_argument(arg.get('arg'), type=arg.get('type'), help=arg.get('help'))

    # Analyze the arguments
    return parser.parse_args()

  def __init__(self, additional_args=None):
    "looks at args and returns an object with attributes of these args completed by the environ variables where needed"
    args = self.parse_args(additional_args)

    load_dotenv(override=True)

    # original language
    self.original_language = args.original_language or environ.get('ORIGINAL_LANGUAGE', 'English')
    # context translation language
    self.context_language = args.context_language or environ.get('CONTEXT_LANGUAGE', 'French')
    # LLM client and model
    self.llm_client = args.llm or environ.get('LLM_CLIENT', 'ollama')
    self.model = args.model or environ.get('LLM_MODEL', None)

    # the target languages to test for translation
    if args.target_language:
      self.test_target_languages = [args.target_language]
    else:
      self.test_target_languages = environ.get('TARGET_LANGUAGES', 'Spanish').split(',')

    # semi specific management for testing and for po files
    for argument in additional_args:
      arg = argument.get('arg')[2:]
      # some ambiguous original sentences and their context translations for testing
      if arg == 'original_phrase':
        if args.original_phrase:
          if not hasattr(args, 'context_translation'):
            print("context_translation must be set when original_phrase is set")
            sys.exit(1)

          self.translations_testset = [{"original_phrase": args.original_phrase,
                                        "context_translation": args.context_translation}]
        else:
          TEST_TRANSLATIONS = environ.get(
            'TEST_TRANSLATIONS',
            """[{"original_phrase": "He gave her a ring.", "context_translation": "Il lui a donné une bague."}]""")
          try:
            self.translations_testset = json.loads(TEST_TRANSLATIONS)
          except json.decoder.JSONDecodeError:
            print("TEST_TRANSLATIONS must be a valid JSON array\n", TEST_TRANSLATIONS)
            sys.exit(1)
        # print(self.translations_testset)
      elif arg == 'context_translation':
        continue  # already processed with original_phrase
      else:
        # for all other arguments, generic processing
        val = getattr(args, arg) or environ.get(argument.get('env'), argument.get('default', None))
        setattr(self, arg, val)

  def get_client(self):
    match self.llm_client:
      case 'ollama':
        from openai_ollama_client import OllamaClient as LLMClient
      case 'openai':
        # uses OpenAI GPT-4o by default
        from openai_ollama_client import OpenAIClient as LLMClient
      case 'claude':
        # uses Claude Sonnet 3.5 by default
        from claude_client import ClaudeClient as LLMClient
      case 'claude_cached':
        # uses Claude Sonnet 3.5, cached mode for long system prompts
        from claude_client import CachedClaudeClient as LLMClient
      case _:
        raise Exception(
          f"LLM_CLIENT must be one of 'ollama', 'openai', 'claude' or 'claude_cached', not '{self.llm_client}'"
          )
    return LLMClient(self.original_language, self.context_language, "", model=self.model) if self.model \
      else LLMClient(self.original_language, self.context_language, "")
