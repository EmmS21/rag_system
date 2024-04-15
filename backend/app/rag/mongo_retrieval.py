import cProfile
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import numpy as np
from .embeddings.generate_embeddings import generate_embeddings

# Load environment variables
load_dotenv()
mongodb_uri = os.getenv('MONGODB_URI')
db_name = os.getenv('DB_NAME')
collection_name = os.getenv('COLLECTION_NAME')

# Connect to MongoDB
client = MongoClient(mongodb_uri)
db = client[db_name]
collection = db[collection_name]
embeddings_collection = db["embeddings"]

def fetch_embeddings():
    """Fetch all embeddings from MongoDB."""
    embeddings = {}
    for embedding_doc in embeddings_collection.find():
        document_id = embedding_doc["document_id"]
        segment_id = embedding_doc["segment_id"]
        embedding = embedding_doc["embedding"]
        if document_id not in embeddings:
            embeddings[document_id] = {}
        embeddings[document_id][segment_id] = embedding
    return embeddings

def process_document(document, embeddings, query_embedding, min_similarity):
    document_id = document["_id"]
    if document_id in embeddings:
        segment_similarities = []
        for segment_id, segment_embedding in embeddings[document_id].items():
            similarity = np.dot(segment_embedding, query_embedding) / (np.linalg.norm(segment_embedding) * np.linalg.norm(query_embedding))
            segment_similarities.append((segment_id, similarity))
        segment_similarities.sort(key=lambda x: x[1], reverse=True)
        relevant_segments = [segment_id for segment_id, similarity in segment_similarities if similarity >= min_similarity]
        # print(f"Relevant segments for Document ID {document_id} with similarities: {[(s[0], round(s[1], 4)) for s in segment_similarities if s[1] >= min_similarity]}")  # Debug relevant segments
        if relevant_segments:
            return document, relevant_segments, max(similarity for _, similarity in segment_similarities if similarity >= min_similarity)
    return None

def retrieve_relevant_documents(query, top_n=5, num_candidates=50, min_similarity=0.1):
    query_embedding_0 = generate_embeddings(query)["segment_0"]  
    query_embedding_1 = generate_embeddings(query)["segment_1"]  
    query_embedding_np_0 = np.array(query_embedding_0)
    query_embedding_np_1 = np.array(query_embedding_1)

    # Fetch candidate documents and prefetch all embeddings
    candidates = list(collection.find({}, {"full_text": 1}))
    embeddings = fetch_embeddings()

    relevant_documents = []
    for candidate in candidates[:num_candidates]:
        result_0 = process_document(candidate, embeddings, query_embedding_np_0, min_similarity)
        result_1 = process_document(candidate, embeddings, query_embedding_np_1, min_similarity)
        if result_0:
            relevant_documents.append(result_0)
        if result_1:
            relevant_documents.append(result_1)


    # Sort documents by the highest similarity score of their most relevant segment
    relevant_documents.sort(key=lambda x: x[2], reverse=True)

    relevant_texts = []
    for doc, relevant_segments, _ in relevant_documents[:top_n]:
        full_text = doc["full_text"]
        segment_texts = []
        for segment_id in relevant_segments:
            start_idx = sum(len(part) for part in full_text.split(segment_id)[:-1])
            end_idx = start_idx + len(embeddings[doc["_id"]][segment_id]) * 384
            segment_text = full_text[start_idx:end_idx]
            segment_texts.append(segment_text)
        relevant_texts.append("\n".join(segment_texts))

    return relevant_texts

# def main():
#     test_query = "What are the regulations for foreign exchange operations in Colombia?"
#     relevant_texts = retrieve_relevant_documents(test_query)
#     # print("Relevant Texts:", relevant_texts)

# if __name__ == '__main__':
#     cProfile.run('main()', 'profile_output')
