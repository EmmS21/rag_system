from pymongo import MongoClient
import os
from dotenv import load_dotenv
# Assuming text_to_embeddings.py is in the embeddings folder
from embeddings.text_to_embedding import TextToEmbeddings

load_dotenv()

mongodb_uri = os.getenv('MONGODB_URI')
db_name = os.getenv('DB_NAME')
collection_name = os.getenv('COLLECTION_NAME')

client = MongoClient(mongodb_uri)
db = client[db_name]
collection = db[collection_name]

# Instantiate TextToEmbeddings
text_to_embeddings = TextToEmbeddings()

def retrieve_relevant_documents(query, top_n=5, num_candidates=50):
    query_embedding = text_to_embeddings.generate(query)
    
    results = collection.aggregate([
        {
            "$vectorSearch": {
                "index": "lawsRegVector", 
                "path": "embeddings",  
                "queryVector": query_embedding, 
                "numCandidates": num_candidates,  
                "limit": top_n 
            }
        }
    ])
    return list(results)

