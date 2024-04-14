import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Instantiate the OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class ResponseGenerator:
    def __init__(self, model="gpt-3.5-turbo"):
        self.model = model

    def generate(self, input_text, query):
        """
        Generate a response based on the input text using OpenAI's GPT-3.5.
        Note: The max_tokens, temperature, and n parameters have been removed
        to align with the updated API. Adjustments may be needed based on available options.
        """
        prompt = (f"Given the following detailed context and other information you have access to, "
                f"answer the question: '{query}'. Explain things back to me simply, assuming I do not have "
                f"a legal background.\n\nContext:\n{input_text}")
        # instruction = "Translate the following text to English if needed and explain it in simple terms:"
        # formatted_input = f"{prompt}\n\n{input_text}"
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=self.model,
        )
        return response.choices[0].message.content.strip()
        
