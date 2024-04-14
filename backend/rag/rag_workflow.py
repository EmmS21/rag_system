from .mongo_retrieval import retrieve_relevant_documents
from .generation.generate_response import ResponseGenerator
from .generation.extract_relevant_snippets import extract_relevant_snippets


async def rag_workflow(query):
    documents = retrieve_relevant_documents(query, top_n=5)
    relevant_snippets = extract_relevant_snippets(documents, query)
    combined_texts = " ".join(relevant_snippets)
    generator = ResponseGenerator(model="gpt-3.5-turbo")  
    response_generator = generator.generate(combined_texts, query)
    async for chunk in response_generator:
        yield chunk
    # return response

