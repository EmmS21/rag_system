# main.py
from retrieval.mongo_retrieval import retrieve_relevant_documents

def main():
    # Example query
    query = "Compare the minimum wage laws in Colombia and Brazil"
    documents = retrieve_relevant_documents(query)
    for doc in documents:
        print(doc)

if __name__ == "__main__":
    main()
