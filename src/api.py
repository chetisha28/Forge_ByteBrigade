import os
import json
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from src.langgraph_pipeline import CivicPilotLangGraph
from src.loaders import CivicPilotDocumentLoader
from src.retriever import LangChainSchemeRetriever
from src.eligibility_engine import EligibilityEngine
from src.document_engine import DocumentEngine
from src.workflow_engine import WorkflowEngine
from src.form_filler import CivicPilotFormFiller
from src.digilocker_engine import DigiLockerEngine

# ---------------------------------------------------------
# Pydantic Schemas for Request & Response Validation
# ---------------------------------------------------------

class CitizenProfile(BaseModel):
    full_name: Optional[str] = Field(None, example="Ramesh Kumar")
    age: Optional[int] = Field(None, ge=0, le=120, example=42)
    gender: Optional[str] = Field(None, example="Male")
    marital_status: Optional[str] = Field(None, example="Married")
    state_residence: Optional[str] = Field(None, example="Uttar Pradesh")
    district: Optional[str] = Field(None, example="Varanasi")
    annual_household_income: Optional[float] = Field(None, ge=0, example=120000.0)
    caste_category: Optional[str] = Field(None, example="OBC")
    occupation: Optional[str] = Field(None, example="Farmer (Cultivator / Landowner)")
    is_landowner: Optional[bool] = Field(False, example=True)
    land_holding_acres: Optional[float] = Field(0.0, example=2.0)
    is_pwd: Optional[bool] = Field(False, example=False)
    ration_card_type: Optional[str] = Field(None, example="BPL / Priority Household (PHH)")
    documents_ready: List[str] = Field(default_factory=list, example=["aadhaar_card", "bank_passbook_account"])

class ChatRequest(BaseModel):
    query: str = Field(..., example="Main UP se chhota kisan hu, 2 acre jamin hai, kaunsi yojana milegi?")
    profile: Optional[CitizenProfile] = None
    top_k: int = Field(3, ge=1, le=10, example=3)
    language: str = Field("Hinglish", example="Hinglish")

class SearchRequest(BaseModel):
    query: str = Field(..., example="solar rooftop")
    state: Optional[str] = Field(None, example="Uttar Pradesh")
    category: Optional[str] = Field(None, example="Agriculture")
    limit: int = Field(5, ge=1, le=20)

class EligibilityEvaluateRequest(BaseModel):
    profile: CitizenProfile
    scheme_slug: str = Field(..., example="pm-kisan")

class FormFillRequest(BaseModel):
    scheme_identifier: str = Field(..., example="pm-kisan")
    citizen_details: str = Field("", example="Mera naam Ramesh Kumar hai, UP Varanasi se hu, mobile 9876543210, 2 acre jamin Khasra no 452/1, bank account 1234567890 IFSC BARB0VARANA")
    profile: Optional[CitizenProfile] = None

class FormSubmitRequest(BaseModel):
    scheme_identifier: str = Field(..., example="pm-kisan")
    form_data: Dict[str, Any] = Field(..., example={"full_name": "Ramesh Kumar Verma", "mobile_number": "9876543210"})

class DigiLockerInitiateRequest(BaseModel):
    identifier: str = Field(default="2345 6789 1234", description="12-digit Aadhaar or 10-digit mobile number")

class DigiLockerVerifyRequest(BaseModel):
    txn_id: str = Field(description="Transaction ID from initiate endpoint")
    otp: str = Field(default="123456", description="6-digit verification OTP")
    profile: Optional[Dict[str, Any]] = None

class DigiLockerPullRequest(BaseModel):
    access_token: str = Field(description="DigiLocker session access token")
    profile: Optional[Dict[str, Any]] = None

# ---------------------------------------------------------
# FastAPI App Initialization
# ---------------------------------------------------------

app = FastAPI(
    title="CivicPilot – AI-Powered Digital Governance API",
    description="Official Backend API for Government Scheme Discovery, Eligibility Evaluation, Document Preparation, and Application Workflows.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for React, Next.js, Vue, mobile apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Engines (Loaded Once at Startup)
print("🚀 Initializing CivicPilot Backend Engines...")
langgraph_pipeline = CivicPilotLangGraph(llm_provider="auto")
retriever = langgraph_pipeline.retriever
eligibility_engine = langgraph_pipeline.eligibility_engine
document_engine = langgraph_pipeline.document_engine
workflow_engine = langgraph_pipeline.workflow_engine
digilocker_engine = DigiLockerEngine()
form_filler = CivicPilotFormFiller(workflow_engine=workflow_engine, retriever=retriever, llm=langgraph_pipeline.llm)
print("✅ CivicPilot Backend Ready!")

# ---------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------

@app.get("/health", tags=["System"])
@app.get("/api/health", tags=["System"])
def health_check():
    """Health status and metadata of the indexed authentic schemes."""
    return {
        "status": "healthy",
        "service": "CivicPilot AI Backend",
        "version": "1.0.0",
        "indexed_schemes_count": len(retriever.documents),
        "llm_backend": langgraph_pipeline.llm_provider,
        "docs_url": "/docs"
    }

@app.post("/api/chat", tags=["AI Assistant (LangGraph RAG)"])
@app.post("/api/query", tags=["AI Assistant (LangGraph RAG)"])
def chat_assistant(req: ChatRequest):
    """
    Master RAG Endpoint powered by LangGraph StateGraph.
    - Evaluates query + citizen profile
    - Performs Hybrid BM25 Search across 2,066 authentic schemes
    - Calculates eligibility scores & reasons
    - Prepares document checklists
    - Generates grounded multilingual explanation
    """
    profile_dict = req.profile.model_dump() if req.profile else {}
    result = langgraph_pipeline.run(
        query=req.query,
        citizen_profile=profile_dict,
        top_k=req.top_k,
        language=req.language
    )
    return result

@app.post("/api/schemes/search", tags=["Scheme Discovery"])
def search_schemes(req: SearchRequest):
    """
    Fast scheme search with state jurisdiction and category filtering.
    """
    docs = retriever.search_with_filters(
        query=req.query,
        top_k=req.limit,
        state_filter=req.state,
        category_filter=req.category
    )
    results = []
    for doc in docs:
        meta = dict(doc.metadata)
        results.append({
            "scheme_name": meta.get("scheme_name"),
            "scheme_slug": meta.get("scheme_slug"),
            "level": meta.get("level"),
            "state_or_ministry": meta.get("state_or_ministry"),
            "application_mode": meta.get("application_mode"),
            "tags": meta.get("tags"),
            "official_url": meta.get("official_url"),
            "benefits": meta.get("benefits", "")[:200] + "..." if meta.get("benefits") else ""
        })
    return {
        "query": req.query,
        "total_results": len(results),
        "schemes": results,
        "results": results
    }

@app.get("/api/schemes/categories", tags=["Scheme Discovery"])
def list_categories():
    """Returns the 8 curated category subsets with scheme counts."""
    cat_dir = "data/schemes/by_category"
    if not os.path.exists(cat_dir):
        raise HTTPException(status_code=500, detail="Categories directory not found")

    categories = []
    for fname in sorted(os.listdir(cat_dir)):
        if fname.endswith(".json"):
            cat_key = fname.replace(".json", "")
            fpath = os.path.join(cat_dir, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
                categories.append({
                    "id": cat_key,
                    "title": cat_key.replace("_", " ").title(),
                    "schemes_count": data.get("count", 0),
                    "endpoint": f"/api/schemes/categories/{cat_key}"
                })
    return {"total_categories": len(categories), "categories": categories}

@app.get("/api/schemes/categories/{category_id}", tags=["Scheme Discovery"])
def get_category_schemes(category_id: str, limit: int = Query(20, ge=1, le=100)):
    """Returns schemes inside a specific category."""
    fpath = f"data/schemes/by_category/{category_id}.json"
    if not os.path.exists(fpath):
        raise HTTPException(status_code=404, detail=f"Category '{category_id}' not found")

    with open(fpath, "r", encoding="utf-8") as f:
        data = json.load(f)

    schemes = data.get("schemes", [])[:limit]
    return {
        "category": category_id,
        "total_available": data.get("count", 0),
        "returned": len(schemes),
        "schemes": schemes
    }

@app.post("/api/eligibility/evaluate", tags=["Eligibility Evaluation"])
def evaluate_eligibility(req: EligibilityEvaluateRequest):
    """
    Evaluates citizen profile against a specific scheme.
    Returns Score (0-100), Status (Eligible/Ineligible), and specific reasons.
    """
    # Find scheme document
    matching_doc = next(
        (doc for doc in retriever.documents if doc.metadata.get("scheme_slug") == req.scheme_slug),
        None
    )
    if not matching_doc:
        raise HTTPException(status_code=404, detail=f"Scheme '{req.scheme_slug}' not found")

    profile_dict = req.profile.model_dump()
    eval_result = eligibility_engine.evaluate_doc(profile_dict, matching_doc)
    return eval_result

@app.get("/api/documents/catalog", tags=["Document Preparation"])
def get_documents_catalog():
    """
    Official registry of 15+ government documents with authorities, validity, and DigiLocker APIs.
    """
    return {
        "total_documents": len(document_engine.catalog),
        "documents": list(document_engine.catalog.values())
    }

@app.get("/api/documents/evaluate", tags=["Document Preparation"])
def evaluate_citizen_documents(
    ready_docs: Optional[str] = Query(None, description="Comma-separated document IDs citizen already has"),
    target_scheme: Optional[str] = Query(None, description="Target scheme to audit e.g. pm-kisan, ayushman-bharat-pmjay")
):
    """
    Evaluates citizen documents across all 2,066 schemes,
    returning:
    - 100% Ready schemes for immediate application
    - Schemes unlocked with just 1 missing document
    - Targeted audit for selected scheme
    - Missing document issuing authority & portals
    """
    citizen_docs = [d.strip() for d in ready_docs.split(",")] if ready_docs else []
    return document_engine.evaluate_citizen_documents(citizen_docs, target_scheme)

@app.get("/api/documents/scheme/{scheme_slug}", tags=["Document Preparation"])
def get_scheme_document_checklist(
    scheme_slug: str,
    ready_docs: Optional[str] = Query(None, description="Comma-separated document IDs citizen already has")
):
    """
    Returns exact required document checklist for a scheme and readiness assessment.
    """
    matching_doc = next(
        (doc for doc in retriever.documents if doc.metadata.get("scheme_slug") == scheme_slug),
        None
    )
    if not matching_doc:
        raise HTTPException(status_code=404, detail=f"Scheme '{scheme_slug}' not found")

    citizen_docs = [d.strip() for d in ready_docs.split(",")] if ready_docs else []
    report = document_engine.get_document_report(matching_doc, citizen_docs)
    return report

# ---------------------------------------------------------
# DigiLocker & MeriPehchan Integration Endpoints
# ---------------------------------------------------------

@app.post("/api/digilocker/auth/initiate", tags=["DigiLocker Integration"])
def digilocker_initiate_auth(req: DigiLockerInitiateRequest):
    """
    Initiates DigiLocker / MeriPehchan authentication challenge and sends OTP to linked mobile.
    """
    return digilocker_engine.initiate_auth(req.identifier)

@app.post("/api/digilocker/auth/verify", tags=["DigiLocker Integration"])
def digilocker_verify_otp(req: DigiLockerVerifyRequest):
    """
    Verifies OTP challenge and generates authenticated DigiLocker session access token.
    """
    res = digilocker_engine.verify_otp(req.txn_id, req.otp, req.profile)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error", "OTP Verification Failed"))
    return res

@app.post("/api/digilocker/documents/pull", tags=["DigiLocker Integration"])
def digilocker_pull_documents(req: DigiLockerPullRequest):
    """
    Pulls digitally signed issued government documents from DigiLocker repository (Aadhaar, NPCI, Ration, Marksheet).
    """
    return digilocker_engine.get_issued_documents(req.access_token, req.profile)

@app.get("/api/digilocker/document/{doc_id}", tags=["DigiLocker Integration"])
def digilocker_get_document(doc_id: str, access_token: str = Query("demo_token")):
    """
    Retrieves individual cryptographic verification envelope and issuer details.
    """
    res = digilocker_engine.pull_document_file(doc_id, access_token)
    if not res.get("success"):
        raise HTTPException(status_code=404, detail=res.get("error", "Document not found"))
    return res

@app.get("/api/workflows", tags=["Application Workflows"])
def list_workflows():
    """Lists all available official step-by-step portal workflows."""
    return {
        "available_workflows_count": len(workflow_engine.workflows),
        "workflows": workflow_engine.list_available_workflows()
    }

@app.get("/api/workflows/{scheme_slug}", tags=["Application Workflows"])
def get_application_workflow(scheme_slug: str):
    """
    Returns step-by-step application form schemas, required uploads, and official portal URLs.
    """
    wf = workflow_engine.get_workflow(scheme_slug)
    if not wf:
        raise HTTPException(status_code=404, detail=f"Application workflow for '{scheme_slug}' not found")
    return wf

@app.post("/api/form-fill/generate", tags=["Form Auto-Fill Assistant"])
@app.post("/api/form-filler/generate", tags=["Form Auto-Fill Assistant"])
def generate_form_answers(req: FormFillRequest):
    """
    Form Auto-Fill Assistant:
    Takes citizen details (notes or profile) and generates exact field-by-field copy-paste answers
    structured according to the official government portal's application form.
    """
    profile_dict = req.profile.model_dump() if req.profile else {}
    result = form_filler.generate_form_answers(
        scheme_identifier=req.scheme_identifier,
        citizen_details=req.citizen_details,
        profile=profile_dict
    )
    return result

@app.post("/api/form-fill/submit", tags=["Direct Government Application Form"])
@app.post("/api/form-filler/submit", tags=["Direct Government Application Form"])
def submit_form(req: FormSubmitRequest):
    """
    Submits direct online application for the scheme and generates official registration receipt.
    """
    receipt = form_filler.submit_application(
        scheme_identifier=req.scheme_identifier,
        form_data=req.form_data
    )
    return receipt

# ---------------------------------------------------------
# Static Frontend Mounting (Live at http://localhost:8080)
# ---------------------------------------------------------
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

