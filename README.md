# Goal of this project
The goal of this project is to use various LLMs to help translate po files using a first already translated file to provide context for short pieces of text otherwise possibly very ambiguous.

For example, you have a .po file with msgids in English and msgstrs in French: using this file, you can ask the tool to translate the .po file into any other language. The first translation helps to disambiguate the very short sentences or parts of sentences that are usually found in .po files.

If you have an API key for the commercial LLMs, auto-po-lyglot can work with OpenAI, Anthropic Claude, Gemini and Grok.
Notes: 
1. Grok is implemented but not tested yet as the Grok API is not yet available in my country.
2. Claude is implemented in 2 flavors: cached (beta version on Anthropic) or non cached. The cached version uses a longer system prompt because caching only works if the system prompt is more than 1024 tokens long. The big advantage is that the cost of the cached version is much cheaper than the non-cached one.
It also works with Ollama: You can run your Ollama server locally and be able to use any model that Ollama can run - depending on your hardware capabilities, of course and for free!.

# Install

## Prerequisite
* You must have python>=3.10 installed 
* If you want to work with the source or fork the project, you should install and use [uv](https://docs.astral.sh/uv/) which is a lightning fast replacement for pip, poetry, ... :
  For installing:
  ```
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
  otherwise you'll have to install the dev dependencies  manually.
* While not required, it is highly recommended that you create a python virtual env, if you don't already have one, using pipenv or conda or whatever virtual env manager you prefer. e.g.:
  ```
  conda create -n auto_po_lyglot python=3.10 && conda activate auto_po_lyglot
  ```
  or
  ```
  python -m venv ~/auto_po_lyglot && source ~/auto_po_lyglot/bin/activate
  ```
  or, if you installed [uv](https://docs.astral.sh/uv/)
  ```
  uv venv
  source .venv/bin/activate
  ```

## Install from PyPi
* Install the module from PyPi:
   ```
    pip install --upgrade auto_po_lyglot
   ```

## Install from sources
1. Fork the repo:
   ```
   git clone https://github.com/leolivier/transpo.git auto_po_lyglot
   ```
1. cd to the auto_po_lyglot folder and install the package and its dependencies: 
   ```
   cd auto_po_lyglot && pip install .
   ```

# Configuration
auto_po_lyglot uses a mix of command line arguments and variables in a `.env` file to be as flexible as possible;

Most parameters can be given directly on the command line (if you don't use the UI version), but you can put all the parameters that don't change very often in a `.env` file and use the command line only to override their values when needed.

## The `.env` file
The `.env` file can be created by copying the `.env.example` file to `.env`:
```
cp .env.example .env
```
Then edit the `.env` file to suit your needs. Specifically:
* select your default LLM and if you do not want to use the predefined default models for the selected LLM, specify the model you want to use.
  Variables are:
    * `LLM_CLIENT`: possible values are 'ollama', 'openai', 'claude' or 'claude_cached' (claude_cached is advantageous for very big system prompts ie more than 1024 tokens with sonnet3.5)
    * `LLM_MODEL`: default models are GPT 4o (gpt-4o-latest) for OpenAI, Claude Sonnet 3.5 (claude-3-5-sonnet-20240620) for Anthropic (claude and claude_cached), Llama3.1-8B (llama3.1:8b) for Ollama.
    * `TEMPERATURE`: the temperature provided to the LLM. Default is 0.2
  If you choose OpenAI our Claude, you can also put in the .env file the API keys for the LLM:
    * `OPENAI_API_KEY` for OpenAI GPT
    * `ANTHROPIC_API_KEY` for Anthropic Claude
    * `GEMINI_API_KEY`for Google Gemini
    * `XAI_API_KEY` for X Grok
* Usually, the language of the msgids and the one for the initial translation of the msgstrs will always be the same based on your own language knowledge. Especially if your native language is not English, you will probably use English as your source language and your native language as your 1st translation. Variables are:
  * `ORIGINAL_LANGUAGE` for the language used in msgids
  * `CONTEXT_LANGUAGE` for the langauge used in the 1rst translation
  * `TARGET_LANGUAGES` is a comma separated list of languages in which the .po file must be translated. Usually provide by the command line
* This is also the place where you can tune the prompt for the LLM. The defaults provided work quite well, but if you can do better, please open a PR and provide your prompt with the LLM you tested it on and attach the original and translated .po files;
  Variables used are `SYSTEM_PROMPT` and `USER_PROMPT`.
* `FUZZY`: if set, will translate fuzzy entries of the PO file too. Default is False. Can be set on the command line with -f or --fuzzy
* `LOG_LEVEL` sets the log level (values are DEBUG, INFO, WARNING, ERROR, CRITICAL). This can be overriden on the command line (-v = INFO, -vv = DEBUG)
* `OLLAMA_BASE_URL`: the URL to access the Ollama server (if used). The default is `http://localhost:11434/v1` for using a local Ollama server. If your server uses a different URL, please specify it here. There is no command line argument to this parameter.

  **NOTE**: if you are using the Docker Streamlit image of auto-po-lyglot, please set up Ollama properly to be able to access it from inside the container. See [How do I configure Ollama server?](https://github.com/ollama/ollama/blob/main/docs/faq.md#how-do-i-configure-ollama-server)

### Only for the UI
* `MODELS_PER_LLM`: The list of models to show in the 'Model' select box per LMM. The format is a list of semi-colon separated strings, each string being formated like this \<llm\>|[\<llm|>...]\<comma separated list of models\>. The models must the technical name used in the APIs of the LLMs. Example (and default value):
  ```
  MODELS=ollama|llama3.1:8b,phi3,gemma2:2b;
  openai|gpt-4o-mini,chatgpt-4o-latest,gpt-4o,gpt-4-turbo,gpt-4-turbo-preview,gpt-4,gpt-3.5-turbo;
  claude|claude_cached|claude-3-5-sonnet-20240620,claude-3-opus-20240229,claude-3-sonnet-20240229,claude-3-haiku-20240307;
  gemini|gemini-1b,gemini-1.5b,gemini-2b,gemini-6b,gemini-12b;
  grok|grok-1b,grok-1.5b,grok-2b,grok-6b,grok-12b

  ```
  **NOTE**: The different LLM models can be set up each on separate lines.

### Only when translating a whole Django project
When translating a whole Django project (see below), you can set the folder where your Django project resides locally with:
```
PATH=<django project folder>
```

# Run it:
## Running with the UI
> As of version 1.3.0
### Running the UI from the command line
After installing auto_po_lyglot with pip, create a short Python script called `auto_po_lyglot_ui.py` that contains these 2 lines:
```
from auto_po_lyglot.po_streamlit import streamlit_main
streamlit_main()
```
And run `streamlit run auto_po_lyglot_ui.py`
Then you can go to http://localhost:8501 and provide the necessary parameters. Most of them can be initialized based on
* the contents of the .env file as described above
* the command line parameters as described below, after a special '--' param telling streamlit that the following parameters are for auto-po-lyglot, e.g. :
```
streamlit run auto_po_lyglot_ui.py -- -l ollama -m phi3 -t 0.5
```
**Note**: The `-o` and `-p` parameters are ignored.

In the UI, a help button (with a '?') explains which parameters to specify where.

## Running from the Command Line
**Usage:** `auto_po_lyglot [-h] [-p] [-l LLM] [-m MODEL] [-t TEMPERATURE] [--original_language ORIGINAL_LANGUAGE] [--context_language CONTEXT_LANGUAGE]
                     [--target_language TARGET_LANGUAGE] [-i INPUT_PO] [-o OUTPUT_PO] [-v] [-vv]`

| option                                 |           can be used to        | supersedes variable in the .env file |  default value |
|----------------------------------------|---------------------------------|--------------------------------------|----------------|
|  -h, --help                            | show this help message and exit |                                      |                |
|  -v, --verbose                         | verbose mode                    |       LOG_LEVEL=INFO                 | LOG_LEVEL=WARN |
|  -vv, --debug                          | debug mode                      |       LOG_LEVEL=DEBUG                | LOG_LEVEL=WARN |
|  -p, --show_prompts                    | show the prompts used for translation and exits |                      |                |
|  -f, --force                           | Forces translating already translated entries   | FORCE                | False (i.e; non blank entries in the output file won't be overwritten) |
|  --fuzzy                               | Translates fuzzy entries in the input po file   | FUZZY                | False (fuzzy entries are ignored) |
|  -i, --input_po INPUT_PO               | the .po file containing the msgids (phrases to be translated) and msgstrs (context translations) | INPUT_PO | |
|  -o, --output_po OUTPUT_PO             | is the .po file where the translated results will be written. If not specified, it will be created in the same directory as input_po unless the input po file has the specific format .../locale/<context language code>/LC_MESSAGES/\<input po file name>. In this case, the output po file will be created as .../locale/\<target language code>/LC_MESSAGES/\<input po file name>. | OUTPUT_PO | see doc |
|  -l, --llm LLM                         | the type of LLM you want to use. Can be openai, ollama, claude or claude_cached. For openai or claude[_cached], you need to set the proper api key in the environment or in the .env file | LLM_CLIENT | ollama |
|  -m, --model MODEL                     | the name of the model to use. If not specified, a default model will be used, based on the chosen client | LLM_MODEL | see doc |
|  -t, --temperature TEMPERATURE         | the temperature of the model. If not specified at all, a default value of 0.2 will be used | TEMPERATURE |  0.2  |
|  --original_language ORIGINAL_LANGUAGE | the language of the original phrase | ORIGINAL_LANGUAGE |  |
|  --context_language CONTEXT_LANGUAGE   | the language of the context translation | CONTEXT_LANGUAGE |  | 
|  --target_language TARGET_LANGUAGE     | the language into which the original phrase will be translated | TARGET_LANGUAGES (which is an array) |  |
| --owner OWNER | The owner of the project containing the po file. This is used only in the header of the translated file | OWNER | \<OWNER\> |
| --owner_mail | Email of the above owner. This is used only in the header of the translated file | OWNER_MAIL | \<OWNER EMAIL\> |

## Translate a whole Django project at once
If you use `auto_djangopo_lyglot` instead of `auto_po_lyglot`, you can translate a whole Django project in one run. 
Just set the variables or parameters as described above (except of course the -i and -o parameters which are ignored as well as their .env counterparts). 
The only optional additional parameter is --path (or the PATH variable in the .env file) which specifies the path to the Django project you want translate.
The tool will automatically detect all po files associated with the context language and use them to translate the original sentences into the target language(s), storing the resulting files in the right place in the Django structure. 
**NOTE**: If you use the -c or --compile option, the files will be compiled, so you don't need to run `python manage.py compilemessages`. 

# Using Docker
> As of version 1.4.0

You can run auto_po_lyglot via Docker. A pre-built up-to-date image can be used at ghcr.io/leolivier/auto_po_lyglot or you can build your own.
## Creating a Docker image
If you want to create your own Docker image, create a folder and cd to it then:
* create a small Python script called auto_po_lyglot_ui.py as described for running Streamlit from the command line:
```
from auto_po_lyglot.po_streamlit import streamlit_main
streamlit_main()
```
* create a file named Dockerfile that contains:
```
FROM python:3.10-slim
WORKDIR /app
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
RUN pip install auto-po-lyglot
COPY ./auto_po_lyglot_ui.py .
EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
ENTRYPOINT ["streamlit", "run", "auto_po_lyglot_ui.py", "--server.port=8501", "--server.address=0.0.0.0"]
```
Then run `docker build -t auto_po_lyglot .` to create your image locally

## Running the Docker image
If you built the image yourself, run:
```
docker run -p 8501:8501 -v ./.env:/app/.env --name auto_po_lyglot auto_po_lyglot:latest
```
If you want to use the pre-built image, run:
```
docker run -p 8501:8501 -v ./.env:/app/.env --name auto_po_lyglot ghcr.io/leolivier/auto_po_lyglot:latest
```
