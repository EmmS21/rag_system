from transformers import AutoTokenizer, AutoModel
import torch

def generate_embeddings(text: str):
    """
    Generate hierarchical embeddings for the given text using a multilingual BERT model.

    Args:
        text (str): The text to generate embeddings for.

    Returns:
        dict: A dictionary mapping segment IDs to their corresponding embeddings.
    """
    # Load the tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained("bert-base-multilingual-cased")
    model = AutoModel.from_pretrained("bert-base-multilingual-cased")

    # Tokenize the text
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)

    # Generate embeddings
    with torch.no_grad():
        outputs = model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

    # Split embeddings into segments (e.g., paragraphs)
    segment_embeddings = {}
    for i, start in enumerate(range(0, len(embeddings), 384)):
        end = start + 384
        segment_id = f"segment_{i}"
        segment_embeddings[segment_id] = embeddings[start:end].tolist()

    return segment_embeddings