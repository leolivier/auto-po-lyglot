import openai
# from dotenv import load_dotenv
# load_dotenv()

# English sentence to translate
text_to_translate = "She made a call."

# Context provided in French
context_translation = "Elle a pris une décision."

# Prompt for GPT-4
prompt = (
    f"Translate the following English sentence into Spanish, considering the provided French context for disambiguation:\n"
    f"English: '{text_to_translate}'\n"
    f"French context: '{context_translation}'\n"
    f"Provide only the Spanish translation."
)

# Call the OpenAI API to generate the response
client = openai.OpenAI()


response = client.chat.completions.create(
    model="gpt-4o-2024-08-06",
    messages=[
        {"role": "system", "content": "You are a helpful assistant that translates text."},
        {"role": "user", "content": prompt}
    ],
    max_tokens=60,
    n=1,
    stop=None,
    temperature=0.3
)

# Display Spanish translation
spanish_translation = response.choices[0].message.content.strip()
print(spanish_translation)
