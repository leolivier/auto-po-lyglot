import logging
from pathlib import Path, PurePath
from auto_po_lyglot.getenv import get_language_code

logger = logging.getLogger(__name__)


def locate_django_translation_files(django_path, context_language, target_languages):
  """
  Locates all the Django translation files for the context language in the given path and returns a list of their paths.

  Parameters:
    django_path (str): The path to the Django project directory. If None, the current directory is used.
    context_language (str): The context language of the translations.
    target_languages (List[str]): The target languages of the translations.

  Returns:
    List[str]: A dictionary of the form
      { "paths to a context translation files": [
          {"target_language": "path of translated file"},
          {"target_language": "path of translated file"},
         ...
        ],
        "paths another context translation files": [
          {"target_language": "path of translated file"},
          {"target_language": "path of translated file"},
         ...
        ],
        ...
      }. One for each Django application that contains a context translation file.
  """

  path = Path(django_path or '.')
  context_lang_code = get_language_code(context_language) or 'xx'
  context_lang_path = Path('locale') / context_lang_code / 'LC_MESSAGES'
  input_po_files = [p for p in path.glob(f'*/{context_lang_path}/*.po')]
  logger.debug(f"Input PO files: {input_po_files}")
  translation_files = {}
  for input_po_file in input_po_files:
    output_po_files = []
    outfile_parts = PurePath(input_po_file).parts
    for target_language in target_languages:
      # replace the context language code with the target language code in the file name
      target_code = get_language_code(target_language) or 'xx'
      target_path = PurePath(target_code)
      outfile = Path(*outfile_parts[:-3]).joinpath(target_path, *outfile_parts[-2:])
      # create the directory if it doesn't exist
      dir = outfile.parent
      dir.mkdir(parents=True, exist_ok=True)

      output_po_files.append({target_language: str(outfile)})
    translation_files[str(input_po_file)] = output_po_files
  logger.info(f"Translation files: {translation_files}")
  return translation_files
