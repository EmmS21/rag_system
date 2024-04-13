from pymongo import MongoClient
import gridfs
import requests
from io import BytesIO
from dotenv import load_dotenv
import os
import numpy as np
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
fs = gridfs.GridFS(db)

def update_document_embeddings():
    for document in collection.find({}):
        full_text = document.get("full_text", "")
        if full_text:
            try:
                embeddings = generate_embedding(full_text)
                if isinstance(embeddings, list):
                    for embedding in embeddings:
                        embedding = np.array(embedding)
                        file_id = fs.put(embedding.tobytes(), metadata={
                            'document_id': str(document['_id']),
                            'tags': get_tags(document['_id'])
                        })
                        collection.update_one({'_id': document['_id']}, {'$push': {'embeddings_file_ids': file_id}})
                        print(f"Updated document {document['_id']} with embeddings file ID {file_id}")
                else:
                    embeddings = np.array([embeddings]) 
                    file_id = fs.put(embeddings.tobytes(), metadata={
                        'document_id': str(document['_id']),
                        'tags': get_tags(document['_id'])
                    })
                    collection.update_one({'_id': document['_id']}, {'$set': {'embeddings_file_id': file_id}})
                    print(f"Updated document {document['_id']} with embeddings file ID {file_id}")
            except ValueError as e:
                print(f"Error processing document {document['_id']}: {e}")
        else:
            print(f"No text found for document {document['_id']}")       

def get_tags(document_id):
    tags = []
    if str(document_id) == '661aa9bf198f319a3f0a8afa':
        tags.append('monetary_policy')
        tags.append('international_exchange_regime')
    elif str(document_id) == '661aa9c6198f319a3f0a8afb':
        tags.append('law_963_2005')
        tags.append('stability_contract')
    elif str(document_id) == '661aa9c6198f319a3f0a8afc':
        tags.append('tax_statute')
        tags.append('decree_624_1989')
    elif str(document_id) == '661aa9c6198f319a3f0a8afd':
        tags.append('law_1819_2016')
        tags.append('tax_reform')
        tags.append('evasion_avoidance')
    elif str(document_id) == '661aa9c6198f319a3f0a8afe':
        tags.append('decree_1625_2016')
        tags.append('tax_regulations')
    elif str(document_id) == '661aa9c7198f319a3f0a8aff':
        tags.append('law_160_1994')
        tags.append('agrarian_reform')
        tags.append('rural_development')
    elif str(document_id) == '661aa9c7198f319a3f0a8b00':
        tags.append('law_388_1997')
        tags.append('urban_development')
    elif str(document_id) == '661aa9c7198f319a3f0a8b01':
        tags.append('civil_code')
    elif str(document_id) == '661aa9c8198f319a3f0a8b02':
        tags.append('decree_1067_2015')
        tags.append('external_relations')
    elif str(document_id) == '661aa9c9198f319a3f0a8b03':
        tags.append('resolution_6045_2017')
        tags.append('foreign_affairs')
    return tags

# Execute the function
update_document_embeddings()