import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
from typing import List, Dict, Any

class RAGSystem:
    def __init__(self, model_name='sentence-transformers/LaBSE'):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.documents = []
        self.bm25 = None

    def create_index(self, documents: List[Dict[str, Any]]):
        self.documents = documents
        texts = [doc["full_text"] for doc in self.documents]

        # Indexation sémantique (FAISS)
        print("Encoding documents for semantic search...")
        embeddings = self.model.encode(texts, convert_to_tensor=False, show_progress_bar=True)
        
        d = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(d)
        self.index.add(embeddings)
        print("FAISS index created.")

        # Indexation lexicale (BM25)
        print("Creating BM25 index for lexical search...")
        tokenized_corpus = [doc.split(" ") for doc in texts]
        self.bm25 = BM25Okapi(tokenized_corpus)
        print("BM25 index created.")

    def search(self, query: str, k: int = 5, alpha: float = 0.5) -> List[Dict[str, Any]]:
        # Recherche sémantique
        query_embedding = self.model.encode([query])
        distances, indices = self.index.search(query_embedding, k * 2)

        semantic_results = [self.documents[i] for i in indices[0]]

        # Recherche lexicale
        tokenized_query = query.split(" ")
        bm25_scores = self.bm25.get_scores(tokenized_query)
        top_n_bm25 = np.argsort(bm25_scores)[::-1][:k*2]
        lexical_results = [self.documents[i] for i in top_n_bm25]

        # Fusion et re-ranking
        combined_results = {doc["id"]: doc for doc in semantic_results}
        for doc in lexical_results:
            if doc["id"] not in combined_results:
                combined_results[doc["id"]] = doc
        
        final_results = list(combined_results.values())
        
        return final_results[:k]

    def save_index(self, path: str):
        print(f"Saving FAISS index to {path}...")
        faiss.write_index(self.index, path)
        print("Index saved.")

    def load_index(self, path: str):
        print(f"Loading FAISS index from {path}...")
        self.index = faiss.read_index(path)
        print("Index loaded.")

if __name__ == '__main__':
    print("Loading processed articles...")
    with open('/home/achraf-bouyalloul/Desktop/chatha9i/data/processed_articles.json', 'r', encoding='utf-8') as f:
        articles = json.load(f)
    print(f"Loaded {len(articles)} articles.")

    rag_system = RAGSystem()
    rag_system.create_index(articles)
    rag_system.save_index('/home/achraf-bouyalloul/Desktop/chatha9i/data/legal_index.faiss')

    print("\n--- Testing Search ---")
    results = rag_system.search("ما هي حرية الفكر؟", k=3)
    print(f"Found {len(results)} results.")
    for res in results:
        print(f"Source: {res['source']}, Title: {res['title']}")
        print(f"Text: {res['text'][:150]}...")
        print("---")

