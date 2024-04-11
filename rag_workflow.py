from retrieval.mongo_retrieval import retrieve_relevant_documents
from generation.generate_response import ResponseGenerator

def rag_workflow(query):
    # Retrieve relevant documents based on the query
    documents = retrieve_relevant_documents(query, top_n=5)
    print('docs', documents)
    
    # Prepare the context for the generative model
    # This example simply concatenates the text of each document. Adjust as needed.
    combined_texts = " ".join([doc['text'] for doc in documents])  # Adjust 'text' based on your document schema
    
    # Generate a response based on the combined texts
    generator = ResponseGenerator(model="gpt-3.5-turbo")  # Specify the model
    response = generator.generate(combined_texts)
    
    return response

if __name__ == "__main__":
    query = "Compare and contrast tax laws in Colombia and Brazil?"
    response = rag_workflow(query)
    print("Response:", response)
