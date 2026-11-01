#!/usr/bin/env python3
import sys
import json
from dotenv import load_dotenv

load_dotenv()

from src.rag_pipeline import CivicPilotRAG

def print_separator(title=""):
    print("\n" + "="*70)
    if title:
        print(f"  {title}")
        print("="*70)

def main():
    print_separator("🇮🇳 Welcome to CivicPilot – RAG Pipeline CLI Test")
    print("AI-powered Government Scheme Discovery and Application Assistant")
    print("Backend ready: 2,066 Authentic Government Schemes Indexed")
    print_separator()

    rag = CivicPilotRAG(llm_provider="auto")

    # Sample citizen test profiles
    test_scenarios = [
        {
            "name": "1. Small Farmer in Uttar Pradesh (PM-KISAN query)",
            "query": "Main UP se ek chhota kisan hu, mere paas 2 acre kheti ki jamin hai. Mujhe kaunsi sarkari yojana ka labh mil sakta hai aur apply kaise karein?",
            "profile": {
                "full_name": "Ramesh Kumar",
                "age": 42,
                "gender": "Male",
                "state_residence": "Uttar Pradesh",
                "annual_household_income": 120000,
                "occupation": "Farmer (Cultivator / Landowner)",
                "is_landowner": True,
                "land_holding_acres": 2.0,
                "caste_category": "OBC",
                "documents_ready": ["aadhaar_card", "land_records_khasra_ror", "bank_passbook_account"]
            }
        },
        {
            "name": "2. College Student from Bihar (Scholarship query)",
            "query": "Main Bihar ka student hu aur graduation kar raha hu. Family income 1.5 lakh hai. Scholarship ke liye kaunse documents chahiye?",
            "profile": {
                "full_name": "Pooja Kumari",
                "age": 20,
                "gender": "Female",
                "state_residence": "Bihar",
                "annual_household_income": 150000,
                "occupation": "Student",
                "caste_category": "SC",
                "highest_qualification": "12th Passed",
                "documents_ready": ["aadhaar_card", "income_certificate", "caste_category_certificate"]
            }
        },
        {
            "name": "3. Traditional Carpenter / Artisan (PM Vishwakarma query)",
            "query": "Main lakdi ka kaam karta hu (carpenter). Mujhe naye tools khareedne ke liye sarkari help chahiye.",
            "profile": {
                "full_name": "Mohan Mistry",
                "age": 35,
                "gender": "Male",
                "state_residence": "Madhya Pradesh",
                "annual_household_income": 180000,
                "occupation": "Traditional Artisan / Craftsman",
                "documents_ready": ["aadhaar_card", "bank_passbook_account"]
            }
        }
    ]

    print("Choose a test scenario to run, or type 'custom':")
    for s in test_scenarios:
        print(f"  [{s['name']}]")
    print("  [4. Custom query]")
    print()

    choice = input("Enter choice (1/2/3/4) [Default: 1]: ").strip() or "1"

    if choice in ["1", "2", "3"]:
        idx = int(choice) - 1
        scenario = test_scenarios[idx]
        query = scenario["query"]
        profile = scenario["profile"]
    else:
        query = input("\nEnter your query for CivicPilot: ").strip()
        state = input("Enter your State (e.g. Uttar Pradesh, Maharashtra, Delhi) [Optional]: ").strip()
        occ = input("Enter your Occupation (e.g. Farmer, Student, Artisan) [Optional]: ").strip()
        income = input("Enter family annual income in INR (e.g. 150000) [Optional]: ").strip()
        profile = {}
        if state: profile["state_residence"] = state
        if occ: profile["occupation"] = occ
        if income and income.isdigit(): profile["annual_household_income"] = float(income)

    print_separator(f"Running RAG Query: '{query}'")
    result = rag.run(query=query, citizen_profile=profile, top_k=2)

    print("\n--- [1] CIVICPILOT AI ANSWER ---")
    print(result["answer"])

    print("\n--- [2] TOP MATCHED SCHEMES ---")
    for s in result["matched_schemes"]:
        ea = s["eligibility_assessment"]
        print(f"• {s['scheme_name']} ({s['level']} - {s['state_or_ministry']})")
        print(f"  - Status: {ea['status']} (Score: {ea['score']}/100)")
        print(f"  - Official Link: {s['official_url']}")
        print(f"  - Benefits: {s['benefits'][:140]}...")

    print("\n--- [3] REQUIRED DOCUMENTS CHECKLIST ---")
    for slug, doc_rep in result["document_checklists"].items():
        print(f"For '{doc_rep['scheme_name']}':")
        for item in doc_rep["checklist"][:5]:
            status_symbol = "✅" if item["is_ready"] else "❌ (Needs preparation)"
            print(f"  {status_symbol} {item['name']} -> Authority: {item['issuing_authority']}")

    if result.get("application_workflows"):
        print("\n--- [4] APPLICATION WORKFLOW STEPS ---")
        for slug, wf in result["application_workflows"].items():
            print(f"Workflow: {wf.get('scheme_name')}")
            for step in wf.get("application_steps", []):
                print(f"  Step {step['step_number']}: {step['step_name']}")

    print_separator("Execution Complete!")

if __name__ == "__main__":
    main()

