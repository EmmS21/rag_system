from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

mongodb_uri = os.getenv('MONGODB_URI')
db_name = os.getenv('DB_NAME')
collection_name = os.getenv('COLLECTION_NAME')

client = MongoClient(mongodb_uri)
db = client[db_name]
collection = db[collection_name]

# Function to get embeddings for the single document
def get_embeddings():
    try:
        # Fetch the single document
        document = collection.find_one()
        if document is None:
            print("No documents found in the collection.")
            return None
        
        # Check if the document belongs to the 'Legal_Docs' group
        document_group = document.get("document_group")
        if document_group != "Legal_Docs":
            print("The document is not in the 'Legal_Docs' group.")
            return None
        
        # Fetch embeddings from the document
        embeddings = document.get("embeddings")
        
        if embeddings:
            return embeddings
        else:
            print("Embeddings not found in the document.")
            return None
    except Exception as e:
        print("An error occurred:", e)
        return None

# Example usage
embeddings = get_embeddings()
if embeddings:
    print("Embeddings:", embeddings)
else:
    print("Failed to retrieve embeddings.")
