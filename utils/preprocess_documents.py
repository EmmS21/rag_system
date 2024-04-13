from pymongo import MongoClient
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup  
import fitz  

load_dotenv()

mongodb_uri = os.getenv('MONGODB_URI')
db_name = os.getenv('DB_NAME')
collection_name = os.getenv('COLLECTION_NAME')

client = MongoClient(mongodb_uri)
db = client[db_name]
collection = db[collection_name]

def extract_text_from_url(url):
    """
    Extract text from a given URL. Adjust this function to handle different document types.
    For PDFs, this function will attempt to download and extract all text as a single block.
    """
    text = ""
    if url.lower().endswith('.pdf'):
        response = requests.get(url)
        if response.status_code == 200:
            try:
                with fitz.open(stream=response.content, filetype="pdf") as doc:
                    for page in doc:
                        text += page.get_text()
            except Exception as e:
                print(f"Failed to parse PDF from {url}: {e}")
        else:
            print(f"Failed to fetch PDF from {url}")
    else:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text()
        else:
            print(f"Failed to fetch content from {url}")

    return text

def update_documents_with_text():
    """ Update documents with the entire text from the corresponding URL. """
    for document in collection.find({"full_text": {"$exists": False}}):
        url = document.get("url")
        text = extract_text_from_url(url)
        if text:
            try:
                collection.update_one({'_id': document['_id']}, {'$set': {'full_text': text}})
                print(f"Updated document {document['_id']} with text from {url}")
            except Exception as e:
                print(f"Failed to update document {document['_id']}: {e}")
        else:
            print(f"No text found for document {document['_id']}")

if __name__ == "__main__":
    update_documents_with_text()
