from pymongo import MongoClient
import requests
from io import BytesIO
from dotenv import load_dotenv
# from embeddings.text_to_embedding import TextToEmbeddings
import os
from embeddings.generate_embeddings import generate_embedding


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

def update_document_embeddings():
    for document in collection.find({}):
        texts = []
        for text in document.get("full_text", []):
            if text:
                texts.append(text)
        if texts:
            full_text = " ".join(texts)
            try:
                embeddings = generate_embedding(full_text)
                collection.update_one({'_id': document['_id']}, {'$set': {'embeddings': embeddings}})
            except ValueError as e:
                print(f"Error processing document {document['_id']}: {e}")
        else:
            print(f"No text found for document {document['_id']}")

# Execute the function
update_document_embeddings()
