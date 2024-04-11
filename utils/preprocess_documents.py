from pymongo import MongoClient
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup  # For HTML parsing
import fitz  # PyMuPDF, for PDF processing

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
    """
    if url.lower().endswith('.pdf'):
        response = requests.get(url)
        if response.status_code == 200:
            with fitz.open(stream=response.content, filetype="pdf") as doc:
                text = ""
                for page in doc:
                    text += page.get_text()
        else:
            print(f"Failed to fetch PDF from {url}")
            return ""
    else:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text()
        else:
            print(f"Failed to fetch content from {url}")
            return ""
    return text

def update_documents_with_text():
    for document in collection.find({}):
        texts = []
        for url in document.get("urls", []):
            text = extract_text_from_url(url)
            if text:
                texts.append(text)
        full_text = " ".join(texts)
        if full_text:
            collection.update_one({'_id': document['_id']}, {'$set': {'text': full_text}})
        else:
            print(f"No text found for document {document['_id']}")

if __name__ == "__main__":
    update_documents_with_text()
