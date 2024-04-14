import cProfile
from pymongo import MongoClient
import gridfs
import os
from dotenv import load_dotenv
import numpy as np
from embeddings.generate_embeddings import generate_embedding

# Load environment variables
load_dotenv()

mongodb_uri = os.getenv('MONGODB_URI')
db_name = os.getenv('DB_NAME')
collection_name = os.getenv('COLLECTION_NAME')

# Connect to MongoDB
client = MongoClient(mongodb_uri)
db = client[db_name]
collection = db[collection_name]
fs = gridfs.GridFS(db)

def fetch_embeddings(embeddings_file_ids):
    """Fetch all embeddings once and store them in a dictionary."""
    embeddings = {}
    for file_id in embeddings_file_ids:
        embedding_bytes = fs.get(file_id).read()
        embeddings[file_id] = np.frombuffer(embedding_bytes, dtype=np.float32)
    return embeddings

def process_document(document, embeddings, query_embedding, query_embedding_dim, min_similarity):
    embeddings_file_ids = document.get("embeddings_file_ids", [])
    embeddings_chunks = [embeddings[file_id] for file_id in embeddings_file_ids if file_id in embeddings]

    if embeddings_chunks:
        combined_embedding = np.concatenate(embeddings_chunks)
        combined_embedding = combined_embedding.reshape(-1, query_embedding_dim)
        combined_embedding = np.mean(combined_embedding, axis=0)
        combined_embedding = np.array(combined_embedding)

        query_embedding_np = np.array(query_embedding)

        similarity = np.dot(combined_embedding, query_embedding_np) / (np.linalg.norm(combined_embedding) * np.linalg.norm(query_embedding_np))

        if similarity >= min_similarity:
            return document, similarity
    return None

def retrieve_relevant_documents(query, top_n=5, num_candidates=50, min_similarity=0.1):
    query_embedding = generate_embedding(query)
    query_embedding_dim = len(query_embedding)

    # Fetch candidate documents and prefetch all embeddings
    candidates = list(collection.find({}, {"embeddings_file_ids": 1, "full_text": 1}).limit(num_candidates))
    all_file_ids = {file_id for candidate in candidates for file_id in candidate.get("embeddings_file_ids", [])}
    embeddings = fetch_embeddings(all_file_ids)

    relevant_documents = []
    for candidate in candidates:
        result = process_document(candidate, embeddings, query_embedding, query_embedding_dim, min_similarity)
        if result:
            relevant_documents.append(result)

    relevant_documents.sort(key=lambda x: x[1], reverse=True)
    relevant_texts = [doc[0]["full_text"] for doc in relevant_documents[:top_n]]

    return relevant_texts

def main():
    test_query = "What are the regulations for foreign exchange operations in Colombia?"
    relevant_texts = retrieve_relevant_documents(test_query)
    print("Relevant Texts:", relevant_texts)

if __name__ == '__main__':
    cProfile.run('main()', 'profile_output')
