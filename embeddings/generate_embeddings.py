import requests
import numpy as np

def generate_embedding(text: str) -> list[float]:
    hf_token = "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"
    embedding_url = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
    max_length = 50000  # Adjust based on trial to avoid payload limit

    parts = [text[i:i + max_length] for i in range(0, len(text), max_length)]
    embeddings = []

    for part in parts:
        response = requests.post(
            embedding_url,
            headers={"Authorization": f"Bearer {hf_token}"},
            json={"inputs": part}
        )
        if response.status_code == 200:
            part_embedding = response.json()
            if isinstance(part_embedding, list) and len(part_embedding) == 384:
                embeddings.append(part_embedding)
            else:
                print(f"Malformed embedding data: {part_embedding}")  # More detailed error information
                raise ValueError("Received malformed embedding data")
        else:
            raise ValueError(f"Request failed with status code {response.status_code}: {response.text}")

    if embeddings:
        # If multiple embeddings are received, average them
        if len(embeddings) > 1:
            embedding_arrays = [np.array(embed) for embed in embeddings]
            avg_embedding = np.mean(embedding_arrays, axis=0).tolist()
            return avg_embedding
        else:
            # If only one embedding, return it directly
            return embeddings[0]

    return []
