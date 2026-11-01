#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv

load_dotenv()

from src.loaders import CivicPilotDocumentLoader
from src.vector_store import CivicPilotVectorStore

def main():
    print("="*70)
    print("  🚀 CivicPilot Vector Database Ingestion (ChromaDB + Gemini Embeddings)")
    print("="*70)

    loader = CivicPilotDocumentLoader()
    print("1. Loading authentic schemes from data/schemes/...")
    documents = loader.load_schemes()
    print(f"   Loaded {len(documents)} official government scheme documents.")

    print("\n2. Initializing Chroma Vector Store at data/vectorstore/chroma...")
    vs = CivicPilotVectorStore()
    print(f"   Current vector count in database: {vs.count}")

    print("\n3. Embedding and storing vectors into ChromaDB...")
    total_indexed = vs.index_documents(documents, batch_size=50)

    print("\n4. Verifying Vector Similarity Search...")
    test_queries = [
        "Farmer agriculture crop damage subsidy UP",
        "Solar rooftop free electricity subsidy",
        "Street vendor working capital loan"
    ]
    for q in test_queries:
        print(f"\n   Query: '{q}'")
        matches = vs.similarity_search(q, k=2)
        for i, m in enumerate(matches, 1):
            print(f"     [{i}] {m.metadata.get('scheme_name')} ({m.metadata.get('state_or_ministry')})")

    print("\n" + "="*70)
    print(f"  ✅ SUCCESS: {total_indexed} schemes successfully stored in ChromaDB!")
    print("="*70)

if __name__ == "__main__":
    main()

