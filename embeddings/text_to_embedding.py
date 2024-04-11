from transformers import BertModel, BertTokenizer
import torch

class TextToEmbeddings:
    def __init__(self, model_name='google-bert/bert-base-multilingual-uncased'):
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertModel.from_pretrained(model_name)

    def generate(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.pooler_output[0].numpy().tolist()

