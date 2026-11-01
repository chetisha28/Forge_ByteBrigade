import os
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from src.loaders import CivicPilotDocumentLoader
from src.vector_store import CivicPilotVectorStore

class LangChainSchemeRetriever:
    """
    Official Hybrid LangChain Scheme Retriever for CivicPilot:
    1. ChromaDB Vector Store (Dense Semantic Vectors persisted in data/vectorstore/chroma)
    2. BM25Retriever (Sparse Lexical Token Matching)
    Combines both for state-of-the-art accuracy on Indian civic queries.
    """
    def __init__(self,
                 csv_path: str = "data/schemes/myscheme_central_state_schemes.csv",
                 k: int = 5):
        self.loader = CivicPilotDocumentLoader(csv_path=csv_path)
        self.k = k
        self.documents: List[Document] = []
        self.retriever: Optional[BM25Retriever] = None
        self.vector_store: Optional[CivicPilotVectorStore] = None
        self._initialize_retriever()

    def _initialize_retriever(self):
        # 1. Load authentic scheme documents via LangChain CSVLoader
        self.documents = self.loader.load_schemes()

        # 2. Primary Fast Lexical Retriever (BM25 In-Memory)
        self.retriever = BM25Retriever.from_documents(self.documents, k=self.k)
        print(f"Loaded {len(self.documents)} authentic schemes into LangChain BM25Retriever.")

        # 3. Persistent ChromaDB Vector Store
        if os.getenv("GEMINI_API_KEY"):
            try:
                self.vector_store = CivicPilotVectorStore()
                print(f"Connected to ChromaDB Vector Store ({self.vector_store.count} vectors in data/vectorstore/chroma).")
            except Exception as e:
                print(f"Info: VectorStore initialization notice: {e}")

    def invoke(self, query: str, k: Optional[int] = None) -> List[Document]:
        """LangChain standard retrieval method."""
        if k is not None:
            self.retriever.k = k
        return self.retriever.invoke(query)

    def search_with_filters(self,
                            query: str,
                            top_k: int = 5,
                            state_filter: Optional[str] = None,
                            category_filter: Optional[str] = None) -> List[Document]:
        """
        Executes Hybrid Retrieval (Chroma Vector DB + BM25) and applies demographic filters.
        """
        candidates: List[Document] = []
        seen_slugs = set()

        # Step 1: Semantic search in ChromaDB Vector Database
        if self.vector_store and self.vector_store.count > 0:
            try:
                vector_docs = self.vector_store.similarity_search_with_filters(
                    query=query,
                    top_k=top_k * 2,
                    state_filter=state_filter,
                    category_filter=category_filter
                )
                for doc in vector_docs:
                    slug = doc.metadata.get("scheme_slug") or doc.metadata.get("scheme_name")
                    if slug and slug not in seen_slugs:
                        seen_slugs.add(slug)
                        candidates.append(doc)
            except Exception as e:
                print(f"Info: Vector search fallback ({e})")

        # Step 2: Lexical search in LangChain BM25Retriever
        bm25_docs = self.invoke(query, k=top_k * 3)
        for doc in bm25_docs:
            meta = doc.metadata
            level = meta.get("level", "")
            state_min = (meta.get("state_or_ministry") or "").lower()
            tags = (meta.get("tags") or "").lower()

            if state_filter and level == "State / UT Government" and state_filter.lower() not in state_min:
                continue
            if category_filter and category_filter.lower() not in tags:
                continue

            slug = meta.get("scheme_slug") or meta.get("scheme_name")
            if slug and slug not in seen_slugs:
                seen_slugs.add(slug)
                candidates.append(doc)

        return candidates[:top_k] if candidates else self.documents[:top_k]
