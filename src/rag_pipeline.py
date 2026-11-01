import json
import os
import urllib.request
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.retriever import LangChainSchemeRetriever
from src.eligibility_engine import EligibilityEngine
from src.document_engine import DocumentEngine
from src.workflow_engine import WorkflowEngine
from src.nlp_processor import CivicPilotNLPProcessor

class CivicPilotLangChainRAG:
    """
    Unified RAG Pipeline for CivicPilot built entirely on LangChain components:
    - Loader: LangChain CSVLoader & DirectoryLoader
    - Documents: langchain_core.documents.Document
    - Retriever: langchain_community.retrievers.BM25Retriever
    - Prompts: langchain_core.prompts.ChatPromptTemplate
    - Models: langchain_google_genai / langchain_groq / langchain_community
    - Parser: langchain_core.output_parsers.StrOutputParser
    - LCEL Execution: prompt | llm | StrOutputParser()
    """
    def __init__(self, llm_provider: str = "auto", api_key: Optional[str] = None):
        self.retriever = LangChainSchemeRetriever()
        self.eligibility_engine = EligibilityEngine()
        self.document_engine = DocumentEngine()
        self.workflow_engine = WorkflowEngine()

        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GROQ_API_KEY")
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
        self.llm_provider = self._resolve_provider(llm_provider)
        self.llm = self._init_langchain_llm()
        self.nlp_processor = CivicPilotNLPProcessor(llm=self.llm)
        self.prompt = self._build_prompt_template()

    def _is_ollama_alive(self, base_url: str) -> bool:
        try:
            req = urllib.request.Request(f"{base_url.rstrip('/')}/api/tags", headers={"User-Agent": "CivicPilot"})
            with urllib.request.urlopen(req, timeout=0.6) as resp:
                return resp.status == 200
        except Exception:
            return False

    def _resolve_provider(self, provider: str) -> str:
        env_provider = os.getenv("CIVICPILOT_LLM_PROVIDER", "").strip().lower()
        if provider == "auto":
            if env_provider in ["ollama", "gemini", "groq", "extractive"]:
                return env_provider
            elif self._is_ollama_alive(self.ollama_base_url):
                print(f"Detected local Ollama instance running at {self.ollama_base_url}. Using Ollama model: {self.ollama_model}")
                return "ollama"
            elif os.getenv("GEMINI_API_KEY"):
                return "gemini"
            elif os.getenv("GROQ_API_KEY"):
                return "groq"
            else:
                return "extractive"
        return provider

    def _init_langchain_llm(self):
        if self.llm_provider == "ollama":
            try:
                from langchain_ollama import ChatOllama
                
                print(f"Connecting to Ollama model '{self.ollama_model}' at {self.ollama_base_url} via LangChain ChatOllama...")
                return ChatOllama(
                    model=self.ollama_model,
                    base_url=self.ollama_base_url,
                    temperature=0.2
                )
            except Exception as e:
                print(f"Warning: Failed to load ChatOllama ({e}).")
                return None

        elif self.llm_provider == "gemini":
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                key = self.api_key or os.getenv("GEMINI_API_KEY")
                model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
                print(f"Connecting to Google Gemini model '{model}' via LangChain ChatGoogleGenerativeAI...")
                return ChatGoogleGenerativeAI(
                    model=model,
                    google_api_key=key,
                    temperature=0.2
                )
            except Exception as e:
                print(f"Warning: Failed to load ChatGoogleGenerativeAI ({e}).")
                return None

        elif self.llm_provider == "groq":
            try:
                from langchain_groq import ChatGroq
                key = self.api_key or os.getenv("GROQ_API_KEY")
                return ChatGroq(
                    model_name="llama-3.1-8b-instant",
                    groq_api_key=key,
                    temperature=0.2
                )
            except Exception as e:
                print(f"Warning: Failed to load ChatGroq ({e}).")
                return None

        return None

    def _build_prompt_template(self) -> ChatPromptTemplate:
        system_instruction = (
            "You are CivicPilot, an authoritative AI Government Scheme and Application Assistant for Indian citizens.\n"
            "You must respond in {language}.\n"
            "Strict Instructions:\n"
            "1. Base your answer EXCLUSIVELY on the authentic government context provided below. Never invent or hallucinate schemes.\n"
            "2. State clearly whether the citizen is eligible and why.\n"
            "3. Mention the exact benefit or financial assistance amounts.\n"
            "4. Provide a bulleted checklist of mandatory documents they need to prepare.\n"
            "5. Walk through the application steps and cite the official government URL.\n\n"
            "--- VERIFIED GOVERNMENT DATA CONTEXT ---\n"
            "{context}\n"
        )
        user_instruction = (
            "Citizen Profile:\n{profile}\n\n"
            "Citizen Query:\n\"{query}\"\n\n"
            "Please provide a structured, polite, and actionable guide for the citizen:"
        )

        return ChatPromptTemplate.from_messages([
            ("system", system_instruction),
            ("human", user_instruction)
        ])

    def run(self,
            query: str,
            citizen_profile: Optional[Dict[str, Any]] = None,
            top_k: int = 3,
            language: str = "Hinglish") -> Dict[str, Any]:
        """
        Executes LangChain retrieval, eligibility evaluation, and LCEL generation.
        """
        profile = dict(citizen_profile or {})

        # NLP NLU: Extract demographics and detect language
        detected_lang = self.nlp_processor.detect_language(query)
        extracted = self.nlp_processor.extract_demographics(query, llm=self.llm)
        for k, v in extracted.items():
            if k not in profile or profile[k] is None:
                profile[k] = v

        if not language or language == "Hinglish":
            language = detected_lang

        state_filter = profile.get("state_residence")
        category_filter = profile.get("occupation")

        # NLP Query Expansion
        expanded_query = self.nlp_processor.expand_query(query, profile)

        # 1. Retrieve LangChain Document objects
        retrieved_docs: List[Document] = self.retriever.search_with_filters(
            query=expanded_query,
            top_k=top_k,
            state_filter=state_filter,
            category_filter=category_filter
        )

        if not retrieved_docs:
            return {
                "query": query,
                "answer": "Maaf kijiye, aapki query ke anusaar koi relevant government scheme nahi mili.",
                "matched_schemes": [],
                "document_checklists": {},
                "workflows": {}
            }

        # 2. Evaluate Eligibility & Documents across LangChain Documents
        evaluated_schemes = []
        doc_checklists = {}
        workflows = {}
        context_blocks = []

        ready_docs = profile.get("documents_ready", [])

        for idx, doc in enumerate(retrieved_docs, 1):
            meta = doc.metadata
            slug = meta.get("scheme_slug", "")

            # Eligibility evaluation
            eval_res = self.eligibility_engine.evaluate_doc(profile, doc)
            meta["eligibility_assessment"] = eval_res

            # Document report
            doc_report = self.document_engine.get_document_report(doc, ready_docs)
            doc_checklists[slug] = doc_report

            # Workflow schema
            wf = self.workflow_engine.get_workflow(slug)
            if wf:
                workflows[slug] = wf

            evaluated_schemes.append(meta)

            # Build context block
            key_docs = [d["name"] for d in doc_report["checklist"][:5]]
            block = (
                f"### Scheme {idx}: {meta.get('scheme_name')} ({meta.get('level')} - {meta.get('state_or_ministry')})\n"
                f"- Official Link: {meta.get('official_url')}\n"
                f"- Assessment: {eval_res['status']} (Score: {eval_res['score']}/100)\n"
                f"- Reasons: {', '.join(eval_res['matched_reasons']) or 'General'}\n"
                f"- Key Documents: {', '.join(key_docs)}\n"
                f"- Details: {doc.page_content[:300]}...\n"
            )
            context_blocks.append(block)

        context_str = "\n".join(context_blocks)

        # 3. LangChain LCEL Chain Execution
        if self.llm is not None:
            chain = self.prompt | self.llm | StrOutputParser()
            try:
                answer = chain.invoke({
                    "context": context_str,
                    "profile": json.dumps(profile, ensure_ascii=False, indent=2),
                    "query": query,
                    "language": language
                })
            except Exception:
                answer = self.nlp_processor.synthesize_hinglish_response(
                    query=query,
                    profile=profile,
                    schemes=evaluated_schemes,
                    checklists=doc_checklists,
                    workflows=workflows
                )
        else:
            if language in ["Hinglish", "Hindi"]:
                answer = self.nlp_processor.synthesize_hinglish_response(
                    query=query,
                    profile=profile,
                    schemes=evaluated_schemes,
                    checklists=doc_checklists,
                    workflows=workflows
                )
            else:
                answer = f"CivicPilot Grounded Summary (myScheme.gov.in):\n\n{context_str}"

        return {
            "query": query,
            "answer": answer,
            "matched_schemes": evaluated_schemes,
            "document_checklists": doc_checklists,
            "application_workflows": workflows,
            "backend_used": f"LangChain [{self.llm_provider.upper()}]"
        }

# Alias for backwards compatibility
CivicPilotRAG = CivicPilotLangChainRAG
