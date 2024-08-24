# Goal of this project
This project aims at using different LLMs to help translating po files using a first already translated file.

For instance, you have a .po file containing msgids in English and msgstrs in French: using this file, you can ask the tool to tranlate the .po file to any other language. The first translation helps at disambiguating the very short sentences or part of sentences usually found in .po files.

This can work with OpenAI (provided you have an OpenAI API key) or Anthropic Claude (provided you have an Anthropic AIP key) or Ollama (here, you'll run your Ollama server locally and be able to use any model that Ollama can run - depending obviously on your hardware capabilities, and that for free!).

# Install
1. Create a python virtual env using pipenv or conda or whatever virtual env manager you prefer. eg:
   
   `conda create -n transpo python=3.10 && conda activate transpo`
1. Fork the repo:
   
   `git clone https://github.com/leolivier/transpo.git`
1. cd to the transpo folder:
 
   `cd transpo`
1. Install the dependencies: 

   `pip install -r requirements`
1. Configure the parameters: see next chapter

# Configuration
## `.env` file
Transpo uses a mix of command line arguments and `.env` file to be as flexible as possible;
Put in the `.env` file all parameters that don't change very often and use the command line to override their values when needed.

The `.env` file can be created by copying the `.env.example` file to `.env`:
`cp .env.example .env`
Then edit the `.env` file and adapt it to your needs. Specifically:
* choose your default LLM and if you dont want to use the predefined default models for the chosen LLM, specify the model you want to use.
  Variables are:
    * `LLM_CLIENT`: possible values are 'ollama', 'openai', 'claude' or 'claude_cached' (claude_cached is advantageous for very big system prompts ie more than 1024 tokens with sonnet)
    * `LLM_MODEL`: default models are gpt-4o-2024-08-06 for OpenAI, claude-3-5-sonnet-20240620 for claude and claude_cached, llama3.1:8b for ollama.
  If you choose OpenAI our Claude, you can also put in the .env file the API keys for the LLM:
    * `OPENAI_API_KEY` for OpenAI
    * `ANTHROPIC_API_KEY` for Claude
* usually, the language of the msgids and the one for the initial translation of the msgstrs will always be the same based on your own language knowledge. Especially if your native language is not English, you will probably use English as your source language and your native language as your 1st translation. Variables are:
  * `ORIGINAL_LANGUAGE` for the language used in msgids
  * `CONTEXT_LANGUAGE` for the langauge used in the 1rst translation
  * `TARGET_LANGUAGES` is a comma separated list of languages in which the .po file must be translated. Usually provide by the command line
* also, this is the place where you can tune the prompt for the LLM. The ones provided work quite well, but if you can do better, please open a PR and provide your prompt with the LLM on which you tested it and attach the original and translated .po files;
  Variables used are `SYSTEM_PROMPT` and `USER_PROMPT` but you can create several ones and at the end of the file select of on them as in the .env.example file.
* `VERBOSE`=True or False drives verbose mode
* Other possible variables are more for testing with hardcode value and test_main.py...

## Tool arguments
usage: `po_main.py [-h] [--llm LLM] [--model MODEL] [--original_language ORIGINAL_LANGUAGE] [--context_language CONTEXT_LANGUAGE]
                  [--target_language TARGET_LANGUAGE] [--verbose] [--input_po INPUT_PO]`

Creates a .po translation file based on an existing one using a given model and llm type. It reads the parameters from the command line and completes
them if necessary from the .env in the same directory. It iterates over the provided target languages, and for each language iterates over the entries
of the input po file and, using the provided client, model and prompt, translates the original phrase into the target language with the help of the
context translation.

| option                                 |           can be used to        | supersedes variable in the .env file |
|----------------------------------------|---------------------------------|--------------------------------------|
|  -h, --help                            | show this help message and exit |                                      |
|  --verbose                             | verbose mode (not yet implemented)|     VERBOSE=True or False          |
|  --input_po INPUT_PO                   | the .po file containing the msgids (phrases to be translated) and msgstrs (context translations) | INPUT_PO |
|  --llm LLM                             | Le type of LLM you want to use. Can be openai, ollama, claude or claude_cached. For openai or claude[_cached], you need to set the proper api key in the environment or in the .env file | LLM_CLIENT |
|  --model MODEL                         | the name of the model to use. If not provided, a default model will be used, based on the chosen client | LLM_MODEL |
|  --original_language ORIGINAL_LANGUAGE | the language of the original phrase | ORIGINAL_LANGUAGE |
|  --context_language CONTEXT_LANGUAGE   | the language of the context translation | CONTEXT_LANGUAGE | 
|  --target_language TARGET_LANGUAGE     | the language into which the original phrase will be translated | TARGET_LANGUAGES (which is an array) |
