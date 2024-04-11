from pymongo import MongoClient
import requests
import fitz  
from io import BytesIO
from dotenv import load_dotenv
from embeddings.text_to_embeddings import TextToEmbeddings
import os

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

# BERT setup
tokenizer = BertTokenizer.from_pretrained('google-bert/bert-base-multilingual-uncased')
model = BertModel.from_pretrained('google-bert/bert-base-multilingual-uncased')

def fetch_and_extract_text_from_pdf(url):
    response = requests.get(url)
    if response.status_code == 200:
        with fitz.open(stream=BytesIO(response.content), filetype="pdf") as doc:
            text = ""
            for page in doc:
                text += page.get_text()
            return text
    else:
        print(f"Failed to fetch PDF from {url}")
        return ""

def update_document_embeddings():
    for document in collection.find({}):
        texts = []
        for url in document.get("urls", []):
            text = fetch_and_extract_text_from_pdf(url)
            if text:
                texts.append(text)
        if texts:
            full_text = " ".join(texts)
            embeddings = text_to_embeddings.generate(full_text)
            collection.update_one({'_id': document['_id']}, {'$set': {'embeddings': embeddings}})
        else:
            print(f"No text found for document {document['_id']}")

# Execute the function
update_document_embeddings()
