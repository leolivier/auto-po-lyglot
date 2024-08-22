from transpo_base import TranspoPrompts


class TranspoPromptsImpl1(TranspoPrompts):

  def get_system_prompt(self):
    return f"""
You are a helpful, smart translation assistant. You will be given an {self.original_language} sentence
to be translated to {self.target_language}. You will also be given a {self.context_language} translation
for this {self.original_language} sentence that you will consider for desambiguating the meaning of the
{self.original_language} sentence. Your {self.target_language} translation must be consistent with the
{self.context_language} translation.
Please respond with the best translation you find for the {self.context_language} sentence. If you need to provide
an explanation of the translation, please do so but only after giving the best translation and on another line."""

  def get_user_prompt(self, phrase, context_translation):
    return (f"""{self.original_language} sentence: "{phrase}", {self.context_language} translation:"""
            f""" "{context_translation}", {self.target_language}:""")


class TranspoPromptsImpl2(TranspoPrompts):

  def get_system_prompt(self):
    return "You are a helpful assistant that translates text."

  def get_user_prompt(self, phrase, context_translation):
    return (
      f"Translate the following {self.original_language} sentence into {self.target_language},"
      f"considering the provided {self.context_language} context for disambiguation:\n"
      f"{self.original_language}: '{phrase}'\n"
      f"{self.context_language} context: '{context_translation}'\n"
      f"Provide only the {self.target_language} translation."
    )
