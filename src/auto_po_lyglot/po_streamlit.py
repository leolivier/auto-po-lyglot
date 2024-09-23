# pyright: reportAttributeAccessIssue=false
from io import StringIO
import logging
import os
from time import sleep
import polib
import streamlit as st
from auto_po_lyglot import ClientBuilder, ParamsLoader, system_prompt, user_prompt, get_outfile_name

logger = logging.getLogger(__name__)

supported_llms = ["openai", "ollama", "claude", "claude_cached", "gemini", "grok"]
MODELS_PER_LLM = """ollama|llama3.1:8b,phi3,gemma2:2b;
  openai|gpt-4o-mini,chatgpt-4o-latest,gpt-4o,gpt-4-turbo,gpt-4-turbo-preview,gpt-4,gpt-3.5-turbo;
  claude|claude_cached|claude-3-5-sonnet-20240620,claude-3-opus-20240229,claude-3-sonnet-20240229,claude-3-haiku-20240307;
  gemini|gemini-1b,gemini-1.5b,gemini-2b,gemini-6b,gemini-12b;
  grok|grok-1b,grok-1.5b,grok-2b,grok-6b,grok-12b"""

# The right order is important. The first one is the original language, the second one is the context
# language supported in examples
supported_languages = ["English", "French", "Spanish", "Italian", "Portuguese", "German"]


class StParams:
  pass


@st.cache_data
def get_params():
  """Loads the parameters from the command line and .env file"""
  params = ParamsLoader().load()
  return params


@st.cache_data
def get_models():
  models = {}
  models_string = os.environ['MODELS_PER_LLM'] if 'MODELS_PER_LLM' in os.environ else MODELS_PER_LLM
  for model_per_llm in models_string.split(';'):
    lst = model_per_llm.split('|')
    llms = lst[:-1]  # all but last elements are llms
    models_string = lst[-1].split(',')  # last element is a comma separated list of models
    for llm in llms:
      llm = llm.strip('\n \t')
      models[llm] = models_string
  # print(models)
  return models


def update_models():
  # print(f'Updating models for "{st.session_state.llm_client}"')
  try:
    st.session_state.client_models = st.session_state.models_per_llm[st.session_state.llm_client]
  except KeyError as e:
    st.exception(e)
    st.error(f"Available keys: {st.session_state.models_per_llm}")


def init_session_state(params):

  if 'llm_client' in st.session_state:
    return  # already initialized

  for key in [
    'llm_client', 'model', 'temperature',
    'original_language', 'context_language', 'target_languages'
  ]:
    if key not in st.session_state:
      st.session_state[key] = getattr(params, key)

  st.session_state.models_per_llm = get_models()
  st.session_state.model = st.session_state.model or st.session_state.models_per_llm[st.session_state.llm_client][0]
  update_models()
  for api_key in ["open_api_key", "anthropic_api_key", "xai_api_key", "gemini_api_key"]:
    envvar = api_key.upper()
    api_key_value = os.environ.get(envvar, "")
    # print(f"api_key: {api_key}, envvar {envvar} = {api_key_value}")
    setattr(st.session_state, api_key, api_key_value)


def st_help():
  with st.container():
    col1, col2 = st.columns([0.9, 0.1])
    with col1:
      st.write("This tool allows you to translate a PO file using a given large language model (LLM).")
    with col2:
      with st.popover("?"):
        """
* You must provide an existing PO file with a first translation that will be used as context.
* The original language is the language of the msgids, the context language is the language of the
first translation that will be used as context for translating to the target language.
Please select those languages in the Languages tab below.
* You can chose the LLM you want to use in the select box below then the models supported by that LLM
will be updated. Chose one of the models from the list below. The first one in the list will be the default model.
* You can select the temperature in the slider below. The higher the temperature, the more likely the
translation will be "creative" (ie random 🙂).
* Click on the "Browse file" button below to upload the .po file to be translated (or drag and drop a file to the upload area).
* In the Secrets tab, you can provide the API keys for the commercial APIs. No API key is required for the Ollama models.
* The Prompts tab contains the default prompts that will be used to translate from one language to another.
You can try to tune these prompts in the text area if you want.
"""


def build_ui(params):

  st.title("Auto PO Lyglot")
  st_help()
  st_params = StParams()
  st_params.llm_client = st.selectbox("LLM Client:",
                                      options=supported_llms,
                                      key="llm_client",
                                      # will update the list of proposed models based on the chosen client
                                      on_change=update_models)

  st_params.model = st.selectbox('Models:',
                                 options=st.session_state.client_models)

  with st.form("Parameters"):
    tab_basic, tab_languages, tab_prompts, tab_secrets = st.tabs(["Basic", "Languages", "Prompts", "Secrets"])

    with tab_basic:
      st_params.temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, step=0.05, key="temperature")
      st_params.input_po = st.file_uploader("Input .po file", type="po", key="input_po")

    with tab_languages:
      st_params.original_language = st.selectbox("Original language:",
                                                 options=supported_languages,
                                                 index=0,
                                                 key="original_language")
      st_params.context_language = st.selectbox("Context language:",
                                                options=supported_languages,
                                                index=1,
                                                key="context_language")
      st_params.target_language = st.selectbox("Target languages:",
                                               options=supported_languages,
                                               index=2,
                                               key="target_language")
    with tab_prompts:
      st_params.system_prompt = st.text_area("System prompt:", value=system_prompt, key="system_prompt")
      st_params.user_prompt = st.text_area("User prompt:", value=user_prompt, key="user_prompt")

    with tab_secrets:
      st_params.openai_api_key = st.text_input("OpenAI API key:", type="password", key="openai_api_key")
      st_params.anthropic_api_key = st.text_input("Anthropic API key:", type="password", key="anthropic_api_key")
      st_params.gemini_api_key = st.text_input("Gemini API key:", type="password", key="gemini_api_key")
      st_params.xai_api_key = st.text_input("XAI (Grok) API key:", type="password", key="xai_api_key")

    st_params.submitted = st.form_submit_button("Run")

  # complete st_params with params that are not in the form
  for key in params.__dict__:
    if not hasattr(st_params, key):
      setattr(st_params, key, params.__dict__[key])
  return st_params


def streamlit_main():
    params = get_params()

    init_session_state(params)

    # build ui form to allow changing or filling in missing params
    st_params = build_ui(params)

    if st_params.submitted:
      if not st_params.input_po:
        st.error("No .po file provided!", icon="🔥")
      else:
        data = run_llm(st_params)
        output_file = get_outfile_name(st_params.model, st_params.input_po.name,
                                       st_params.target_language, st_params.context_language)
        st.download_button(label="Download translated .po", data=data, file_name=output_file.name, mime="text/plain")


def run_llm(st_params):
    client = ClientBuilder(st_params).get_client()
    st.info(f"> Using model `{st_params.model}` to translate `{st_params.input_po.name}` "
            f"from `{st_params.original_language}` -> `{st_params.context_language}` -> "
            f"`{st_params.target_language}` with an `{st_params.llm_client}` client...")
    percent_translated = 0
    with st.status("# Start of translation...") as status:
      # read and decode .po file content
      po_data = StringIO(st_params.input_po.getvalue().decode("utf-8")).read()
      # create a POfile instance
      po = polib.pofile(po_data)
      nb_translations = 0
      try:
        for entry in po:
          if entry.msgid and not entry.fuzzy:
            context_translation = entry.msgstr if entry.msgstr else entry.msgid
            original_phrase = entry.msgid
            status.update(label=f"{percent_translated}%: translating '{original_phrase}' ...")
            translation, explanation = client.translate(original_phrase, context_translation)
            # Add explanation to comment
            if explanation:
              entry.comment = explanation
            # Update translation
            entry.msgstr = translation
            st.divider()
            st.write(f'{st_params.original_language}: `{original_phrase}`')
            st.write(f'{st_params.context_language}: `{context_translation}`')
            st.write(f'{st_params.target_language}: `{translation}`')
            if explanation:
              st.write(f'{explanation}')  # some llms generate explanation in MD so no backquotes

            sleep(1.0)  # Sleep for 1 second to avoid rate limiting
            nb_translations += 1
            percent_translated = round(nb_translations / len(po) * 100, 2)
      except Exception as e:
        st.error(f"> Error: {e}", icon="🚨")

      status.update(label=f"Translated `{nb_translations}` entries out "
                          f"of `{len(po)}` entries (`{percent_translated}%`)")

    return po.__unicode__()


if __name__ == "__main__":
  streamlit_main()
