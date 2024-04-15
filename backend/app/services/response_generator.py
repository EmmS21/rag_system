import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ResponseGenerator:
    def __init__(self, model="gpt-3.5-turbo"):
        self.model = model
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    # async def generate(self, input_text, query):
    async def generate(self, rag_context, curr_query, chat_history):
        prompt = (
            f"Given the following detailed context and other information you have access to, "
            f"'{curr_query}'. Explain back to me in detail using the context and chat history, assuming I do not have a legal background.\n\n"
            f"Chat History:\n{chat_history}\n\n"  
            f"Context:\n{rag_context}"
        )
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
            yield "event: end-of-stream\ndata: end\n\n" 

