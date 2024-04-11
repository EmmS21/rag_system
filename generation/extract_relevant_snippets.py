import spacy

# Load the multilingual model
nlp = spacy.load("xx_ent_wiki_sm")

# Add the sentencizer component to the pipeline
if 'sentencizer' not in nlp.pipe_names:
    sentencizer = nlp.add_pipe('sentencizer')

# Increase the max_length to accommodate larger texts
nlp.max_length = 10000000  # Setting to 10 million characters

def extract_relevant_snippets(docs, query):
    """
    Extracts relevant snippets from the document texts based on the query.
    
    :param docs: List of documents retrieved from MongoDB.
    :param query: Query string used to generate response.
    :return: List of relevant snippets from the documents.
    """
    query_doc = nlp(query)
    snippets = []

    for doc in docs:
        # Assuming 'text' contains the full document text
        doc_text = doc['text']
        
        # If document text exceeds Spacy's max_length, process it in smaller chunks
        if len(doc_text) > nlp.max_length:
            doc_text = doc_text[:nlp.max_length]
            
        doc_nlp = nlp(doc_text)
        
        # Ensure sentence boundaries are set
        if not doc_nlp.has_annotation("SENT_START"):
            doc_nlp = sentencizer(doc_text)
        
        similarities = []
        for sent in doc_nlp.sents:
            # Avoid calculating similarity for empty sentences
            if sent.text.strip():
                similarities.append((sent, query_doc.similarity(sent)))

        # Sort sentences by similarity and select the top 3
        sorted_sents = sorted(similarities, key=lambda x: x[1], reverse=True)[:3]
        snippets.extend([sent[0].text for sent in sorted_sents])

    return snippets
