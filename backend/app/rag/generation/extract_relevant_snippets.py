import spacy

nlp = spacy.load("xx_ent_wiki_sm")

if 'sentencizer' not in nlp.pipe_names:
    sentencizer = nlp.add_pipe('sentencizer')

nlp.max_length = 10000000  
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
        doc_text = doc
        
        # If document text exceeds Spacy's max_length, process it in smaller chunks
        if len(doc_text) > nlp.max_length:
            doc_text = doc_text[:nlp.max_length]
            
        doc_nlp = nlp(doc_text)

        similarities = []
        for sent in doc_nlp.sents:
            if sent.text.strip():
                similarities.append((sent, query_doc.similarity(sent)))
        # Sort sentences by similarity and select the top 10
        sorted_sents = sorted(similarities, key=lambda x: x[1], reverse=True)[:10]
        # print('sorted', sorted_sents)
        snippets.extend([sent[0].text for sent in sorted_sents])
        # print('snips', snippets)
    return snippets
