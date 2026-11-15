import os
import json
import numpy as np
from typing import List, Dict, Optional, Tuple
import config

class VectorStore:
    def __init__(self):
        self._stores: Dict[str, Dict] = {}
        self._mode = None

    def create_index(self, index_id: str, chunks: List[Dict[str, str]]) -> bool:
        if not chunks:
            return False
        
        texts = [c["text"] for c in chunks]

        # Try FAISS + SentenceTransformers first if available
        try:
            import faiss
            from sentence_transformers import SentenceTransformer
            embedder = SentenceTransformer('all-MiniLM-L6-v2')
            embeddings = embedder.encode(texts, show_progress_bar=False)
            embeddings = np.array(embeddings).astype('float32')
            
            dimension = embeddings.shape[1]
            index = faiss.IndexFlatIP(dimension)
            faiss.normalize_L2(embeddings)
            index.add(embeddings)
            
            self._stores[index_id] = {
                "type": "faiss",
                "index": index,
                "embedder": embedder,
                "chunks": chunks,
                "embeddings": embeddings,
            }
            return True
        except Exception:
            pass

        # Robust High-Performance Sklearn / TF-IDF Vector Space Retrieval
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            
            vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
            tfidf_matrix = vectorizer.fit_transform(texts)

            self._stores[index_id] = {
                "type": "tfidf",
                "vectorizer": vectorizer,
                "matrix": tfidf_matrix,
                "chunks": chunks,
            }
            return True
        except Exception as e:
            print(f"Fallback vector index creation error: {e}")
            # Final fallback: keyword / substring scoring
            self._stores[index_id] = {
                "type": "keyword",
                "chunks": chunks,
            }
            return True

    def search(self, index_id: str, query: str, top_k: int = 5) -> List[Dict]:
        if index_id not in self._stores:
            return []
        
        store = self._stores[index_id]
        store_type = store.get("type")

        try:
            if store_type == "faiss":
                import faiss
                embedder = store["embedder"]
                query_embedding = embedder.encode([query])
                query_embedding = np.array(query_embedding).astype('float32')
                faiss.normalize_L2(query_embedding)
                
                scores, indices = store["index"].search(query_embedding, min(top_k, len(store["chunks"])))
                results = []
                for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                    if idx < len(store["chunks"]) and idx >= 0:
                        chunk = store["chunks"][idx].copy()
                        chunk["score"] = float(score)
                        chunk["rank"] = i + 1
                        results.append(chunk)
                return results

            elif store_type == "tfidf":
                from sklearn.metrics.pairwise import cosine_similarity
                vectorizer = store["vectorizer"]
                matrix = store["matrix"]
                query_vec = vectorizer.transform([query])
                similarities = cosine_similarity(query_vec, matrix).flatten()
                
                top_indices = np.argsort(similarities)[::-1][:top_k]
                results = []
                for rank, idx in enumerate(top_indices):
                    if similarities[idx] > 0 or rank == 0:
                        chunk = store["chunks"][idx].copy()
                        chunk["score"] = float(similarities[idx])
                        chunk["rank"] = rank + 1
                        results.append(chunk)
                return results

            else:
                # Simple keyword relevance
                q_words = set(query.lower().split())
                scored = []
                for idx, c in enumerate(store["chunks"]):
                    score = sum(1 for w in q_words if w in c["text"].lower())
                    scored.append((score, idx))
                scored.sort(key=lambda x: x[0], reverse=True)
                
                results = []
                for rank, (score, idx) in enumerate(scored[:top_k]):
                    chunk = store["chunks"][idx].copy()
                    chunk["score"] = float(score)
                    chunk["rank"] = rank + 1
                    results.append(chunk)
                return results

        except Exception as e:
            print(f"Vector search error: {e}")
            return store["chunks"][:top_k]

    def delete_index(self, index_id: str) -> bool:
        if index_id in self._stores:
            del self._stores[index_id]
            return True
        return False

    def has_index(self, index_id: str) -> bool:
        return index_id in self._stores

# Singleton instance
vector_store = VectorStore()
