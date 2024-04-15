import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ResponseGenerator:
    def __init__(self, model="gpt-3.5-turbo"):
        self.model = model
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    async def generate(self, input_text, query):
        prompt = (f"Given the following detailed context and other information you have access to, "
                  f"'{query}'. Explain things back to me simply, assuming I do not have "
                  f"a legal background.\n\nContext:\n{input_text}")
        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.model,
            stream=True
        )
        try:
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    yield f"data: {chunk.choices[0].delta.content}\n\n"
        finally:
            yield "event: end-of-stream\ndata: end\n\n"  # Signal the end of the stream