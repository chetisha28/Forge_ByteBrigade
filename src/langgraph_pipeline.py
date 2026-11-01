import os
import json
import urllib.request
from typing import TypedDict, List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

from langgraph.graph import StateGraph, END
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.retriever import LangChainSchemeRetriever
from src.eligibility_engine import EligibilityEngine
from src.document_engine import DocumentEngine
from src.workflow_engine import WorkflowEngine
from src.nlp_processor import CivicPilotNLPProcessor

# StateGraph TypedDict using LangChain Document objects
class CivicPilotState(TypedDict):
    query: str
    citizen_profile: Dict[str, Any]
    retrieved_docs: List[Document]
    evaluated_schemes: List[Dict[str, Any]]
    document_checklists: Dict[str, Any]
    application_workflows: Dict[str, Any]
    final_answer: str
    language: str
    top_k: int
    llm_provider: str

class CivicPilotLangGraph:
    """
    Official LangGraph Agentic Pipeline for CivicPilot.
    Orchestrates LangChain DocumentLoaders, BM25Retrievers,
    Eligibility Evaluation, Document Readiness, and LCEL Synthesis.
    """
    def __init__(self, llm_provider: str = "auto", api_key: Optional[str] = None):
        print("Initializing CivicPilot LangGraph Pipeline...")
        self.retriever = LangChainSchemeRetriever()
        self.eligibility_engine = EligibilityEngine()
        self.document_engine = DocumentEngine()
        self.workflow_engine = WorkflowEngine()

        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GROQ_API_KEY")
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

        env_provider = os.getenv("CIVICPILOT_LLM_PROVIDER", "").strip().lower()
        if llm_provider == "auto":
            if env_provider in ["ollama", "gemini", "groq", "extractive"]:
                self.llm_provider = env_provider
            elif self._is_ollama_alive(self.ollama_base_url):
                print(f"Detected local Ollama instance running at {self.ollama_base_url}. Using Ollama model: {self.ollama_model}")
                self.llm_provider = "ollama"
            elif os.getenv("GEMINI_API_KEY"):
                self.llm_provider = "gemini"
            elif os.getenv("GROQ_API_KEY"):
                self.llm_provider = "groq"
            else:
                self.llm_provider = "extractive"
        else:
            self.llm_provider = llm_provider

        self.llm = self._init_llm()
        self.nlp_processor = CivicPilotNLPProcessor(llm=self.llm)
        self.prompt = self._build_prompt()
        self.graph = self._build_graph()

    def _is_ollama_alive(self, base_url: str) -> bool:
        try:
            req = urllib.request.Request(f"{base_url.rstrip('/')}/api/tags", headers={"User-Agent": "CivicPilot"})
            with urllib.request.urlopen(req, timeout=0.6) as resp:
                return resp.status == 200
        except Exception:
            return False

    def _init_llm(self):
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
                print(f"Warning: Failed to load ChatOllama ({e}). Falling back to extractive engine.")
                return None
        elif self.llm_provider == "gemini":
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                key = self.api_key or os.getenv("GEMINI_API_KEY")
                model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
                print(f"Connecting to Google Gemini model '{model}' via LangChain ChatGoogleGenerativeAI...")
                return ChatGoogleGenerativeAI(model=model, google_api_key=key, temperature=0.2)
            except Exception as e:
                print(f"Warning: Failed to load ChatGoogleGenerativeAI ({e}).")
                return None
        elif self.llm_provider == "groq":
            try:
                from langchain_groq import ChatGroq
                key = self.api_key or os.getenv("GROQ_API_KEY")
                return ChatGroq(model_name="llama-3.1-8b-instant", groq_api_key=key, temperature=0.2)
            except Exception:
                return None
        return None

    def _build_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", (
                "You are CivicPilot, an authoritative AI Indian Government Scheme Assistant for Indian citizens.\n"
                "CRITICAL LANGUAGE RULE:\n"
                "- If {language} is 'Hinglish', you MUST formulate your entire response in natural, empathetic, conversational Hinglish (Hindi written in Roman English script, e.g., 'Namaste! Aapke profile ke anusaar aap PM-KISAN ke liye eligible hain...'). Never respond in pure English!\n"
                "- If {language} is 'Hindi', respond in Devanagari Hindi.\n"
                "- If {language} is 'English', respond in English.\n\n"
                "GROUNDING RULE:\n"
                "Ground your answer strictly on this authentic government data context:\n{context}"
            )),
            ("human", (
                "Citizen Profile:\n{profile}\n\n"
                "Citizen Query:\n\"{query}\"\n\n"
                "Please give a warm, structured response with:\n"
                "1. Eligibility status (Eligible/Not Eligible) with reasons\n"
                "2. Specific financial benefits/assistance\n"
                "3. Checklist of mandatory documents\n"
                "4. Step-by-step application guidance with official link"
            ))
        ])

    def _build_graph(self):
        workflow = StateGraph(CivicPilotState)
        workflow.add_node("extract_profile", self._extract_profile_node)
        workflow.add_node("retrieve_docs", self._retrieve_docs_node)
        workflow.add_node("evaluate_eligibility", self._evaluate_eligibility_node)
        workflow.add_node("assemble_documents", self._assemble_documents_node)
        workflow.add_node("attach_workflows", self._attach_workflows_node)
        workflow.add_node("generate_response", self._generate_response_node)

        workflow.set_entry_point("extract_profile")
        workflow.add_edge("extract_profile", "retrieve_docs")
        workflow.add_edge("retrieve_docs", "evaluate_eligibility")
        workflow.add_edge("evaluate_eligibility", "assemble_documents")
        workflow.add_edge("assemble_documents", "attach_workflows")
        workflow.add_edge("attach_workflows", "generate_response")
        workflow.add_edge("generate_response", END)

        return workflow.compile()

    def _extract_profile_node(self, state: CivicPilotState) -> Dict[str, Any]:
        query = state["query"]
        profile = dict(state.get("citizen_profile") or {})

        # Standard NLP Stage 1: Detect Language and Extract Entities with LangChain NLU
        detected_lang = self.nlp_processor.detect_language(query)
        extracted = self.nlp_processor.extract_demographics(query, llm=self.llm)

        for k, v in extracted.items():
            if k not in profile or profile[k] is None:
                profile[k] = v

        profile.setdefault("documents_ready", [])
        return {"citizen_profile": profile, "language": detected_lang}

    def _retrieve_docs_node(self, state: CivicPilotState) -> Dict[str, Any]:
        query = state["query"]
        top_k = state.get("top_k", 3)
        profile = state.get("citizen_profile", {})

        # Standard NLP Stage 2: Query Expansion
        expanded_query = self.nlp_processor.expand_query(query, profile)

        docs = self.retriever.search_with_filters(
            query=expanded_query,
            top_k=top_k,
            state_filter=profile.get("state_residence"),
            category_filter=profile.get("occupation")
        )
        return {"retrieved_docs": docs}

    def _evaluate_eligibility_node(self, state: CivicPilotState) -> Dict[str, Any]:
        docs = state.get("retrieved_docs", [])
        profile = state.get("citizen_profile", {})
        evaluated = []
        for doc in docs:
            eval_res = self.eligibility_engine.evaluate_doc(profile, doc)
            meta = dict(doc.metadata)
            meta["eligibility_assessment"] = eval_res
            meta["page_content"] = doc.page_content
            evaluated.append(meta)
        evaluated = sorted(evaluated, key=lambda x: x["eligibility_assessment"]["score"], reverse=True)
        return {"evaluated_schemes": evaluated}

    def _assemble_documents_node(self, state: CivicPilotState) -> Dict[str, Any]:
        docs = state.get("retrieved_docs", [])
        profile = state.get("citizen_profile", {})
        ready_docs = profile.get("documents_ready", [])
        doc_checklists = {}
        for doc in docs:
            slug = doc.metadata.get("scheme_slug", "")
            doc_report = self.document_engine.get_document_report(doc, ready_docs)
            doc_checklists[slug] = doc_report
        return {"document_checklists": doc_checklists}

    def _attach_workflows_node(self, state: CivicPilotState) -> Dict[str, Any]:
        schemes = state.get("evaluated_schemes", [])
        workflows = {}
        for s in schemes:
            slug = s.get("scheme_slug", "")
            wf = self.workflow_engine.get_workflow(slug)
            if wf:
                workflows[slug] = wf
        return {"application_workflows": workflows}

    def _generate_response_node(self, state: CivicPilotState) -> Dict[str, Any]:
        schemes = state.get("evaluated_schemes", [])
        query = state["query"]
        profile = state.get("citizen_profile", {})
        doc_checklists = state.get("document_checklists", {})
        workflows = state.get("application_workflows", {})
        language = state.get("language", "Hinglish")

        if not schemes:
            return {"final_answer": "Aapki query ke anusaar koi government scheme nahi mili."}

        context_parts = []
        for idx, s in enumerate(schemes, 1):
            ea = s["eligibility_assessment"]
            slug = s.get("scheme_slug", "")
            docs = [d["name"] for d in doc_checklists.get(slug, {}).get("checklist", [])[:5]]
            context_parts.append(
                f"### Scheme {idx}: {s.get('scheme_name')} ({s.get('level')} - {s.get('state_or_ministry')})\n"
                f"- Official Portal: {s.get('official_url')}\n"
                f"- Assessment: {ea['status']} (Score: {ea['score']}/100)\n"
                f"- Matched: {', '.join(ea['matched_reasons']) or 'General'}\n"
                f"- Key Documents: {', '.join(docs)}\n"
                f"- Summary: {s.get('page_content', '')[:250]}...\n"
            )

        context_str = "\n".join(context_parts)

        if self.llm is not None:
            chain = self.prompt | self.llm | StrOutputParser()
            try:
                answer = chain.invoke({
                    "context": context_str,
                    "profile": json.dumps(profile, ensure_ascii=False, indent=2),
                    "query": query,
                    "language": language
                })
            except Exception as e:
                print(f"Info: LLM chain generation fallback ({e}). Synthesizing Hinglish response...")
                answer = self.nlp_processor.synthesize_hinglish_response(
                    query=query,
                    profile=profile,
                    schemes=schemes,
                    checklists=doc_checklists,
                    workflows=workflows
                )
        else:
            # NLP Stage 3: Structured Hinglish response generation when offline
            if language in ["Hinglish", "Hindi"]:
                answer = self.nlp_processor.synthesize_hinglish_response(
                    query=query,
                    profile=profile,
                    schemes=schemes,
                    checklists=doc_checklists,
                    workflows=workflows
                )
            else:
                answer = f"CivicPilot Grounded Summary (myScheme.gov.in):\n\n{context_str}"

        return {"final_answer": answer}

    def run(self,
            query: str,
            citizen_profile: Optional[Dict[str, Any]] = None,
            top_k: int = 3,
            language: str = "Hinglish") -> Dict[str, Any]:
        initial_state: CivicPilotState = {
            "query": query,
            "citizen_profile": citizen_profile or {},
            "retrieved_docs": [],
            "evaluated_schemes": [],
            "document_checklists": {},
            "application_workflows": {},
            "final_answer": "",
            "language": language,
            "top_k": top_k,
            "llm_provider": self.llm_provider
        }
        final_state = self.graph.invoke(initial_state)
        return {
            "query": final_state["query"],
            "answer": final_state["final_answer"],
            "matched_schemes": final_state["evaluated_schemes"],
            "document_checklists": final_state["document_checklists"],
            "application_workflows": final_state["application_workflows"],
            "framework": "LangGraph + LangChain"
        }
