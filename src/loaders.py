import os
import csv
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import CSVLoader, DirectoryLoader, TextLoader

class CivicPilotDocumentLoader:
    """
    Official LangChain Document Loader for CivicPilot.
    Loads authentic government schemes, guidelines, and catalogs
    into first-class LangChain Document objects.
    """
    def __init__(self,
                 csv_path: str = "data/schemes/myscheme_central_state_schemes.csv",
                 guidelines_dir: str = "data/official_policy_guidelines"):
        self.csv_path = csv_path
        self.guidelines_dir = guidelines_dir

    def load_schemes(self) -> List[Document]:
        """
        Loads 2,066 authentic government schemes using LangChain's official CSVLoader.
        Extracts key columns into Document metadata and page_content.
        """
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"Schemes CSV not found at: {self.csv_path}")

        # Extract header names from CSV
        with open(self.csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader)

        title_col = headers[0] # Handles UTF-8 BOM if present
        metadata_cols = [
            title_col,
            "Scheme Slug",
            "Level",
            "State / UT / Ministry",
            "Application Mode",
            "Tags / Categories",
            "Official Link",
            "MyScheme URL"
        ]

        # Use official LangChain CSVLoader with metadata columns
        loader = CSVLoader(
            file_path=self.csv_path,
            metadata_columns=metadata_cols,
            encoding="utf-8"
        )
        documents = loader.load()

        # Normalize title key in metadata for consistency
        for doc in documents:
            if title_col in doc.metadata:
                doc.metadata["scheme_name"] = doc.metadata.pop(title_col)
            doc.metadata["scheme_slug"] = doc.metadata.get("Scheme Slug", "")
            doc.metadata["level"] = doc.metadata.get("Level", "")
            doc.metadata["state_or_ministry"] = doc.metadata.get("State / UT / Ministry", "")
            doc.metadata["application_mode"] = doc.metadata.get("Application Mode", "")
            doc.metadata["tags"] = doc.metadata.get("Tags / Categories", "")
            doc.metadata["official_url"] = doc.metadata.get("Official Link") or doc.metadata.get("MyScheme URL", "")

        return documents

    def load_guidelines(self) -> List[Document]:
        """
        Loads authentic Ministry Operational Guidelines using LangChain's DirectoryLoader.
        """
        if not os.path.exists(self.guidelines_dir):
            return []

        loader = DirectoryLoader(
            self.guidelines_dir,
            glob="*.md",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"}
        )
        return loader.load()

