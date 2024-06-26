from pymongo import MongoClient
import requests
from io import BytesIO
from dotenv import load_dotenv
import os
from embeddings.generate_embeddings import generate_embeddings

load_dotenv()
username = os.getenv('MONGODB_USERNAME')
password = os.getenv('MONGODB_PASSWORD')
cluster = os.getenv('MONGODB_CLUSTER')
mongodb_uri = f"mongodb+srv://{username}:{password}@{cluster}/?retryWrites=true&w=majority&appName=LATAMLaws"
db_name = os.getenv('DB_NAME')
collection_name = os.getenv('COLLECTION_NAME')

client = MongoClient(mongodb_uri)
db = client[db_name]
collection = db[collection_name]
embeddings_collection = db["embeddings"]

def update_document_embeddings():
    for document in collection.find({}):
        full_text = document.get("full_text", "")
        if full_text:
            try:
                # First, delete any existing embeddings for this document
                embeddings_collection.delete_many({"document_id": document["_id"]})

                # Generate and store hierarchical embeddings for the document
                embeddings = generate_embeddings(full_text)
                for segment_id, segment_embedding in embeddings.items():
                    embedding_document = {
                        "document_id": document["_id"],
                        "segment_id": segment_id,
                        "embedding": segment_embedding
                    }
                    embeddings_collection.insert_one(embedding_document)
                print(f"Embeddings updated for document {document['_id']}")
            except Exception as e:
                print(f"Error processing document {document['_id']}: {e}")
        else:
            print(f"No text found for document {document['_id']}")

# Execute the function
update_document_embeddings()