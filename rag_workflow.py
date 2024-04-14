from mongo_retrieval import retrieve_relevant_documents
from generation.generate_response import ResponseGenerator
from generation.extract_relevant_snippets import extract_relevant_snippets


def rag_workflow(query):
    # Retrieve relevant documents based on the query
    documents = retrieve_relevant_documents(query, top_n=5)
    relevant_snippets = extract_relevant_snippets(documents, query)
    combined_texts = " ".join(relevant_snippets)
    generator = ResponseGenerator(model="gpt-3.5-turbo")  
    response = generator.generate(combined_texts, query)
    
    return response

if __name__ == "__main__":
    query = "What are the regulations for foreign exchange operations in Colombia?"
    response = rag_workflow(query)
    print("Response:", response)
