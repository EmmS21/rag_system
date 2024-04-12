from pymongo import MongoClient
import os
from dotenv import load_dotenv
from transformers import pipeline, BertTokenizer, BertModel
import torch
from embeddings.generate_embeddings import generate_embedding

# from ..generate_embeddingsembeddings.generate_embeddings import generate_embedding

# Load environment variables
load_dotenv()

mongodb_uri = os.getenv('MONGODB_URI')
db_name = os.getenv('DB_NAME')
collection_name = os.getenv('COLLECTION_NAME')

client = MongoClient(mongodb_uri)
db = client[db_name]
collection = db[collection_name]

# # Translation pipeline initialization using a specific model for English to Spanish translation
# translation_pipeline = pipeline("translation_en_to_es", model="Helsinki-NLP/opus-mt-en-es")

# class TextToEmbeddings:
#     def __init__(self, model_name='bert-base-multilingual-cased'):
#         self.tokenizer = BertTokenizer.from_pretrained(model_name)
#         self.model = BertModel.from_pretrained(model_name)
#         self.model.eval()  # Ensure the model is in evaluation mode

#     def generate(self, text):
#         # Generate embeddings for the text
#         inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
#         with torch.no_grad():
#             outputs = self.model(**inputs)
#         # Use the pooler_output as the embedding representation
#         return outputs.last_hidden_state.mean(dim=1).squeeze().tolist()

# # Instantiate TextToEmbeddings
# text_to_embeddings = TextToEmbeddings()

# def translate_to_spanish(text):
#     # Translate English text to Spanish
#     translated_text = translation_pipeline(text)[0]['translation_text']
#     return translated_text

def retrieve_relevant_documents(query, top_n=5, num_candidates=50, min_similarity=0.1):
    # Translate the query to Spanish
    # query_in_spanish = translate_to_spanish(query)
    # print("Translated Query in Spanish:", query_in_spanish)


    # query_embedding = text_to_embeddings.generate(query_in_spanish)
    # print('Number of dimensions in query embedding:', len(query_embedding))

    # Perform a vector search in MongoDB
    results = collection.aggregate([
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "embeddings",
                "queryVector": generate_embedding(query),
                "numCandidates": num_candidates,
                "limit": top_n,
            }
        },
        {
            "$sort": {"similarity": -1}  # Sort by similarity score in descending order
        },
        {
            "$limit": top_n  # Limit the number of results
        }
    ])
    relevant_texts = []
    for result in results:
        similarity_score = result.get("similarity", 0)  # Get the similarity score
        relevant_text = result.get("full_text", "")
        # print("Similarity Score:", similarity_score)  # Print the similarity score
        relevant_texts.append(relevant_text)


    return relevant_texts

# Test query
# test_query = "What are the regulations for foreign exchange operations in Colombia?"
# relevant_texts = retrieve_relevant_documents(test_query)
# print("Relevant Texts:", relevant_texts)

