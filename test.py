import torch

from sentence_transformers import SentenceTransformer

embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Corpus with example sentences
corpus = [
    "**Text**: Aleksandr Solzhenitsyn , the Russian Nobel Prize in Literature -winning anti-Communist author of The Gulag Archipelago , argued that Soviet communism needed enslavement and forced labour to survive , and that this had been ... foreseen as far back as Thomas More , in his Utopia .",
    "**Text**: 59 , pp. 2547-2553 , Oct. 2011 In one dimensional polynomial-based memory ( or memoryless ) DPD , in order to solve for the digital pre-distorter polynomials coefficients and minimize the mean squared error ( MSE ) , the distorted output of the nonlinear system must be over-sampled at a rate that enables the capture of the nonlinear products of the order of the digital pre-distorter .",
]
# Use "convert_to_tensor=True" to keep the tensors on GPU (if available)
corpus_embeddings = embedder.encode(corpus, convert_to_tensor=True)

# Query sentences:
queries = [
    "Carmilla is an 1872 Gothic novel la by Irish author Sheridan Le Fanu and one of the early works of vampire fiction , predating Bram Stoker ' s Dracula ( 1897 ) by 26 years .",
]

# Find the closest 5 sentences of the corpus for each query sentence based on cosine similarity
top_k = min(5, len(corpus))
for query in queries:
    query_embedding = embedder.encode(query, convert_to_tensor=True)

    # We use cosine-similarity and torch.topk to find the highest 5 scores
    similarity_scores = embedder.similarity(query_embedding, corpus_embeddings)[0]
    scores, indices = torch.topk(similarity_scores, k=top_k)

    print("\nQuery:", query)
    print("Top 5 most similar sentences in corpus:")

    for score, idx in zip(scores, indices):
        print(corpus[idx], "(Score: {:.4f})".format(score))
