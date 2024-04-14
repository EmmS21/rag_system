import fitz  # PyMuPDF
import requests
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

mongodb_uri = os.getenv('MONGODB_URI')
db_name = os.getenv('DB_NAME')
collection_name = os.getenv('COLLECTION_NAME')

client = MongoClient(mongodb_uri)
db = client[db_name]
collection = db[collection_name]

def extract_text_from_pdf(content):
    """
    Try to extract text from PDF content, checking for common encoding or compression issues.
    """
    text = ""
    try:
        with fitz.open(stream=content, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text("text")
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    return text

def extract_text_from_url(url):
    """
    Extract text from a given URL, handling PDFs specifically to check for encoding issues.
    """
    response = requests.get(url)
    if response.status_code == 200:
        if url.lower().endswith('.pdf'):
            text = extract_text_from_pdf(response.content)
        else:
            # Handle other document types if necessary
            text = response.text
    else:
        print(f"Failed to fetch content from {url}")
        text = ""
    return text

def update_documents_with_text():
    for document in collection.find({"full_text": {"$exists": False}}):
        url = document.get("url")
        text = extract_text_from_url(url)
        if text:
            try:
                # Ensure the text is stored correctly
                collection.update_one({'_id': document['_id']}, {'$set': {'full_text': text}})
                print(f"Updated document {document['_id']} with text from {url}")
            except Exception as e:
                print(f"Failed to update document {document['_id']}: {e}")
        else:
            print(f"No text found for document {document['_id']}")

if __name__ == "__main__":
    update_documents_with_text()
