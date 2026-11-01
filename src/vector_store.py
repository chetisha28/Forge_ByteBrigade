import os
import time
import pandas as pd
from typing import List, Dict, Any, Optional

from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

VECTOR_STORE_DIR = os.path.join("data", "vectorstore", "chroma")
COLLECTION_NAME = "civicpilot_authentic_schemes"

class CivicPilotVectorStore:
    """
    Official Persistent ChromaDB Vector Store for CivicPilot:
    - Stores 3072-dimensional dense semantic vectors using Google Gemini Embeddings.
    - Persisted locally on disk in data/vectorstore/chroma/.
    - Provides semantic similarity search and metadata filtering.
    """
    def __init__(self,
                 persist_directory: str = VECTOR_STORE_DIR,
                 collection_name: str = COLLECTION_NAME,
                 embedding_model: str = "models/gemini-embedding-001"):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.embedding_model = embedding_model

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required for ChromaDB Vector Store.")

        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=self.embedding_model,
            google_api_key=api_key
        )
        os.makedirs(self.persist_directory, exist_ok=True)
        self.vectorstore = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )

    @property
    def count(self) -> int:
        """Returns the total number of vector embeddings stored in ChromaDB."""
        try:
            return self.vectorstore._collection.count()
        except Exception:
            return 0

    def ingest_csv(self,
                   csv_path: str = "data/schemes/myscheme_central_state_schemes.csv",
                   batch_size: int = 40,
                   limit: Optional[int] = None) -> int:
        """
        Embeds authentic schemes from CSV into persistent ChromaDB.
        Skips indexing if vectors are already populated.
        """
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV not found at: {csv_path}")

        current = self.count
        if current > 0 and (limit is None or current >= limit):
            print(f"ChromaDB already has {current} vector embeddings in '{self.collection_name}'. Skipping re-indexing.")
            return current

        df = pd.read_csv(csv_path)
        if limit:
            df = df.head(limit)

        print(f"Ingesting {len(df)} authentic schemes into Chroma Vector DB (Batch size: {batch_size})...")

        docs = []
        for _, row in df.iterrows():
            name = str(row.get("Scheme Name", "")).strip()
            slug = str(row.get("Scheme Slug", "")).strip()
            level = str(row.get("Level", "")).strip()
            ministry = str(row.get("State / UT / Ministry", "")).strip()
            tags = str(row.get("Tags / Categories", "")).strip()
            desc = str(row.get("Description", ""))[:250].strip()
            benefits = str(row.get("Benefits", ""))[:250].strip()
            eligibility = str(row.get("Eligibility Criteria", ""))[:200].strip()
            url = str(row.get("Official Link", row.get("MyScheme URL", ""))).strip()

            content = (
                f"Scheme: {name} ({level} - {ministry})\n"
                f"Categories: {tags}\n"
                f"Summary: {desc}\n"
                f"Benefits: {benefits}\n"
                f"Eligibility: {eligibility}"
            )
            meta = {
                "scheme_name": name,
                "scheme_slug": slug,
                "level": level,
                "state_or_ministry": ministry,
                "tags": tags,
                "official_url": url
            }
            docs.append(Document(page_content=content, metadata=meta))

        # Batch ingestion with rate-limit protection
        total_batches = (len(docs) + batch_size - 1) // batch_size
        for i in range(0, len(docs), batch_size):
            batch = docs[i:i + batch_size]
            b_idx = (i // batch_size) + 1
            t0 = time.time()
            try:
                self.vectorstore.add_documents(batch)
                t1 = time.time()
                print(f"  [Chroma Ingestion {b_idx}/{total_batches}] Indexed {len(batch)} schemes ({t1-t0:.2f}s) | Total DB vectors: {self.count}")
                time.sleep(1.0) # Respect rate limits
            except Exception as e:
                print(f"  Rate-limit pause on batch {b_idx} ({e}). Sleeping 20s...")
                time.sleep(20.0)
                try:
                    self.vectorstore.add_documents(batch)
                except Exception as retry_err:
                    print(f"  Failed batch {b_idx}: {retry_err}")

        print(f"✅ ChromaDB Ingestion complete! Total stored vectors: {self.count}")
        return self.count

    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """Runs standard cosine vector similarity search in ChromaDB."""
        return self.vectorstore.similarity_search(query, k=k)

    def similarity_search_with_filters(self,
                                        query: str,
                                        top_k: int = 5,
                                        state_filter: Optional[str] = None,
                                        category_filter: Optional[str] = None) -> List[Document]:
        """
        Runs vector similarity search with demographic and state filtering.
        Safely falls back if network or embedding service is unreachable.
        """
        try:
            candidates = self.vectorstore.similarity_search(query, k=top_k * 3)
        except Exception as e:
            print(f"Info: Chroma vector similarity search notice ({e}). Using BM25.")
            return []

        filtered: List[Document] = []

        for doc in candidates:
            meta = doc.metadata
            level = meta.get("level", "")
            state_min = (meta.get("state_or_ministry") or "").lower()
            tags = (meta.get("tags") or "").lower()

            if state_filter:
                sf = state_filter.lower()
                if level == "State / UT Government" and sf not in state_min:
                    continue

            if category_filter:
                cf = category_filter.lower()
                if cf not in tags:
                    continue

            filtered.append(doc)
            if len(filtered) >= top_k:
                break

        if not filtered and candidates:
            filtered = candidates[:top_k]

        return filtered
