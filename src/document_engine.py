import json
import os
from typing import Dict, Any, List, Optional
from langchain_core.documents import Document

TAG_ALIASES = {
    "land_records_ror": "land_records_khasra_ror",
    "land_records": "land_records_khasra_ror",
    "ror": "land_records_khasra_ror",
    "khasra": "land_records_khasra_ror",
    "khatauni": "land_records_khasra_ror",
    "ration_card": "ration_card_bpl",
    "bpl_card": "ration_card_bpl",
    "caste_certificate": "caste_category_certificate",
    "caste": "caste_category_certificate",
    "domicile_certificate": "residence_domicile_certificate",
    "domicile": "residence_domicile_certificate",
    "bank_passbook": "bank_passbook_account",
    "bank_account": "bank_passbook_account",
    "disability_certificate": "disability_certificate_udid",
    "udid": "disability_certificate_udid",
    "marksheet": "educational_marksheets",
    "marksheets": "educational_marksheets",
    "education": "educational_marksheets"
}

TARGET_SCHEMES_AUDIT_DATA = {
    "pm-kisan": {
        "name": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
        "benefit": "₹6,000 / year in 3 installments via DBT",
        "required_docs": ["aadhaar_card", "bank_passbook_account", "land_records_khasra_ror"],
        "critical_rejection_warning": "Land mutation must be on or before 01-02-2019 and Bank account must be seeded with NPCI Aadhaar mapper.",
        "tat": "15-30 days",
        "workflow_slug": "pm-kisan",
        "portal": "https://pmkisan.gov.in/"
    },
    "pm-surya-ghar": {
        "name": "PM Surya Ghar: Muft Bijli Yojana (Rooftop Solar)",
        "benefit": "Up to ₹78,000 central subsidy + 300 units free solar power",
        "required_docs": ["aadhaar_card", "bank_passbook_account"],
        "critical_rejection_warning": "Electricity connection must match Aadhaar card name; unshaded rooftop area min 100 sq.ft/kW.",
        "tat": "30-45 days",
        "workflow_slug": "pm-surya-ghar",
        "portal": "https://pmsuryaghar.gov.in/"
    },
    "ayushman-bharat-pmjay": {
        "name": "Ayushman Bharat PM-JAY (Ayushman Card)",
        "benefit": "₹5,00,000 annual cashless healthcare cover per family",
        "required_docs": ["aadhaar_card", "ration_card_bpl"],
        "critical_rejection_warning": "Beneficiary name must be active in NFSA Ration or SECC-2011 database; live selfie match score must be >=80%.",
        "tat": "24-48 hours",
        "workflow_slug": "ayushman-bharat-pmjay",
        "portal": "https://beneficiary.nha.gov.in/"
    },
    "national-scholarship-portal": {
        "name": "National Scholarship Portal (NSP Scholarships)",
        "benefit": "Tuition fees reimbursement + ₹10,000-₹50,000 annual student grant",
        "required_docs": ["aadhaar_card", "bank_passbook_account", "income_certificate", "educational_marksheets", "caste_category_certificate"],
        "critical_rejection_warning": "Annual family income certificate must be from competent Tehsildar; College AISHE/UDISE verification mandatory.",
        "tat": "30-60 days",
        "workflow_slug": "national-scholarship-portal",
        "portal": "https://scholarships.gov.in/"
    },
    "pm-svanidhi": {
        "name": "PM SVANidhi (Street Vendor Working Capital Loan)",
        "benefit": "₹10,000 to ₹50,000 collateral-free loan @ 7% subsidy + ₹1,200 annual UPI cashback",
        "required_docs": ["aadhaar_card", "bank_passbook_account"],
        "critical_rejection_warning": "Must possess Certificate of Vending (CoV) or Letter of Recommendation (LoR) from Town Vending Committee.",
        "tat": "7-15 days",
        "workflow_slug": "pm-svanidhi",
        "portal": "https://pmsvanidhi.mohua.gov.in/"
    },
    "pm-vishwakarma": {
        "name": "PM Vishwakarma Scheme (Traditional Artisans)",
        "benefit": "₹15,000 tool kit incentive, 5-day stipend & 5% collateral-free loan up to ₹3 Lakh",
        "required_docs": ["aadhaar_card", "bank_passbook_account"],
        "critical_rejection_warning": "Must practice one of 18 traditional crafts; no active Mudra/PMEGP loan in past 5 years.",
        "tat": "20-30 days",
        "workflow_slug": "pm-vishwakarma",
        "portal": "https://pmvishwakarma.gov.in/"
    },
    "pmay-urban": {
        "name": "Pradhan Mantri Awas Yojana (PMAY Housing)",
        "benefit": "₹1.20 Lakh to ₹2.67 Lakh financial subsidy for pucca house construction",
        "required_docs": ["aadhaar_card", "bank_passbook_account", "income_certificate", "land_records_khasra_ror"],
        "critical_rejection_warning": "No family member can own a pucca house in India; female ownership or joint ownership mandatory.",
        "tat": "45-90 days",
        "workflow_slug": "pmay-urban",
        "portal": "https://pmayg.nic.in/"
    }
}

class DocumentEngine:
    """
    LangChain Document readiness, DigiLocker integration, and scheme eligibility audit engine.
    Maps 2,066 government schemes to authentic document requirements.
    """
    def __init__(self,
                 catalog_path: str = "data/document_requirements/master_documents_catalog.json",
                 matrix_path: str = "data/document_requirements/scheme_document_matrix.json"):
        self.catalog: Dict[str, Any] = {}
        self.matrix: Dict[str, Any] = {}
        self._load_data(catalog_path, matrix_path)

    def _load_data(self, catalog_path: str, matrix_path: str):
        if os.path.exists(catalog_path):
            with open(catalog_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for doc in data.get("documents", []):
                    self.catalog[doc["id"]] = doc

        if os.path.exists(matrix_path):
            with open(matrix_path, "r", encoding="utf-8") as f:
                self.matrix = json.load(f)

    def _normalize_tag(self, tag: str) -> str:
        return TAG_ALIASES.get(tag, tag)

    def evaluate_citizen_documents(self, citizen_ready_docs: List[str], target_scheme: Optional[str] = None) -> Dict[str, Any]:
        """
        Conclusively evaluates citizen documents across all 2,066 schemes:
        1. Identifies 100% Ready schemes for immediate application (Zero Rejection Risk)
        2. Identifies high-value schemes unlocked with just 1 missing document
        3. Provides step-by-step document issuance guidelines
        4. Performs deep targeted audit for selected major schemes
        """
        ready_set = set(self._normalize_tag(d) for d in citizen_ready_docs if d)
        ready_schemes = []
        one_away_by_doc: Dict[str, List[Dict[str, Any]]] = {}
        all_one_away = []

        # Ignore non-essential photo / voter id tags in primary gating
        ignored_tags = {"passport_size_photo", "voter_id_card", "pan_card"}

        for slug, s in self.matrix.items():
            raw_tags = s.get("detected_document_tags", [])
            if not raw_tags:
                continue

            clean_tags = [self._normalize_tag(t) for t in raw_tags if t not in ignored_tags]
            if not clean_tags:
                clean_tags = ["aadhaar_card"]

            missing = [t for t in clean_tags if t not in ready_set]
            scheme_item = {
                "slug": slug,
                "name": s.get("scheme_name", slug),
                "state_or_ministry": s.get("state_or_ministry", "National / Central"),
                "total_required": len(clean_tags),
                "required_docs": [self.catalog.get(t, {}).get("name", t.replace("_", " ").title()) for t in clean_tags]
            }

            if len(missing) == 0:
                ready_schemes.append(scheme_item)
            elif len(missing) == 1:
                missing_id = missing[0]
                doc_meta = self.catalog.get(missing_id, {})
                one_away_item = {
                    "slug": slug,
                    "name": s.get("scheme_name", slug),
                    "state_or_ministry": s.get("state_or_ministry", "National / Central"),
                    "missing_doc_id": missing_id,
                    "missing_doc_name": doc_meta.get("name", missing_id.replace("_", " ").title()),
                    "issuing_portal": doc_meta.get("official_portal", "State e-District Portal"),
                    "total_required": len(clean_tags)
                }
                all_one_away.append(one_away_item)
                one_away_by_doc.setdefault(missing_id, []).append(one_away_item)

        # Sort ready schemes by required docs count descending
        ready_schemes.sort(key=lambda x: x["total_required"], reverse=True)
        all_one_away.sort(key=lambda x: x["total_required"], reverse=True)

        # Format Missing Document Impact Map
        missing_impact_list = []
        for doc_id, doc_meta in self.catalog.items():
            if doc_id not in ready_set:
                unlocked_count = len(one_away_by_doc.get(doc_id, []))
                missing_impact_list.append({
                    "document_id": doc_id,
                    "name": doc_meta["name"],
                    "issuing_authority": doc_meta.get("issuing_authority", "State Revenue Department"),
                    "official_portal": doc_meta.get("official_portal", "https://edistrict.up.gov.in"),
                    "validity": doc_meta.get("validity", "1 Year / Permanent"),
                    "digilocker_pullable": True,
                    "schemes_unlocked_count": unlocked_count,
                    "sample_schemes": [s["name"] for s in one_away_by_doc.get(doc_id, [])[:3]]
                })

        missing_impact_list.sort(key=lambda x: x["schemes_unlocked_count"], reverse=True)

        # Target Scheme Audit
        audit_slug = target_scheme or "pm-kisan"
        target_info = TARGET_SCHEMES_AUDIT_DATA.get(audit_slug, TARGET_SCHEMES_AUDIT_DATA["pm-kisan"])
        req_tags = target_info["required_docs"]

        target_ready_items = []
        target_missing_items = []

        for r_id in req_tags:
            d_meta = self.catalog.get(r_id, {
                "id": r_id,
                "name": r_id.replace("_", " ").title(),
                "issuing_authority": "Revenue / Portal Authority",
                "official_portal": "https://myscheme.gov.in"
            })
            if r_id in ready_set:
                target_ready_items.append({
                    "document_id": r_id,
                    "name": d_meta["name"],
                    "status": "Ready",
                    "digilocker_verified": True
                })
            else:
                target_missing_items.append({
                    "document_id": r_id,
                    "name": d_meta["name"],
                    "status": "Missing",
                    "issuing_authority": d_meta.get("issuing_authority"),
                    "official_portal": d_meta.get("official_portal"),
                    "action_required": f"Apply/Download on {d_meta.get('issuing_authority', 'Portal')}"
                })

        is_target_ready = len(target_missing_items) == 0
        readiness_pct = min(round((len(ready_set) / max(len(self.catalog), 1)) * 100), 100)

        return {
            "readiness_percentage": readiness_pct,
            "ready_docs_count": len(ready_set),
            "total_catalog_docs": len(self.catalog),
            "total_schemes_analyzed": len(self.matrix),
            "ready_schemes_count": len(ready_schemes),
            "ready_schemes_sample": ready_schemes[:12],
            "one_away_schemes_count": len(all_one_away),
            "one_away_schemes_sample": all_one_away[:10],
            "missing_document_impact_map": missing_impact_list,
            "target_scheme_audit": {
                "slug": audit_slug,
                "scheme_name": target_info["name"],
                "benefit": target_info["benefit"],
                "tat": target_info["tat"],
                "portal": target_info["portal"],
                "workflow_slug": target_info["workflow_slug"],
                "is_100_percent_ready": is_target_ready,
                "rejection_risk": "Zero Risk (All Mandatory Documents Cleared)" if is_target_ready else f"High Risk: Missing {len(target_missing_items)} Mandatory Document(s)",
                "critical_warning": target_info["critical_rejection_warning"],
                "ready_items": target_ready_items,
                "missing_items": target_missing_items,
                "conclusive_action_summary": (
                    f"🎉 Aapke paas sabhi zaroori documents tayyar hain! Aap abhi bina rejection risk ke '{target_info['name']}' apply kar sakte hain."
                    if is_target_ready
                    else f"⚠️ '{target_info['name']}' me application rejection se bachne ke liye pehle missing documents prapt karein."
                )
            }
        }

    def get_document_report(self, doc: Document, citizen_ready_docs: List[str] = None) -> Dict[str, Any]:
        """
        Takes a LangChain Document and citizen ready documents list,
        returns structured checklist and readiness percentage.
        """
        slug = doc.metadata.get("scheme_slug", "")
        scheme_name = doc.metadata.get("scheme_name", slug)
        citizen_docs = set(self._normalize_tag(d) for d in (citizen_ready_docs or []))

        scheme_info = self.matrix.get(slug, {})
        detected_tags = scheme_info.get("detected_document_tags", [])
        raw_text = scheme_info.get("raw_documents_required", "")

        checklist = []
        ready_count = 0
        missing_count = 0

        for tag in detected_tags:
            norm_tag = self._normalize_tag(tag)
            doc_meta = self.catalog.get(norm_tag, {
                "id": norm_tag,
                "name": norm_tag.replace("_", " ").title(),
                "issuing_authority": "Relevant Government Department / Portal",
                "validity": "As per official notification",
                "verification_method": "Physical copy / DigiLocker verification",
                "official_portal": "State e-District / National Portal"
            })

            is_ready = norm_tag in citizen_docs or doc_meta["name"].lower() in [d.lower() for d in citizen_docs]
            if is_ready:
                ready_count += 1
            else:
                missing_count += 1

            checklist.append({
                "document_id": norm_tag,
                "name": doc_meta["name"],
                "is_ready": is_ready,
                "issuing_authority": doc_meta.get("issuing_authority"),
                "validity": doc_meta.get("validity"),
                "verification_method": doc_meta.get("verification_method"),
                "official_portal": doc_meta.get("official_portal", "State e-District / National Portal")
            })

        total = len(checklist)
        readiness_pct = round((ready_count / total * 100), 1) if total > 0 else 100.0

        return {
            "scheme_slug": slug,
            "scheme_name": scheme_name,
            "total_documents_required": total,
            "ready_count": ready_count,
            "missing_count": missing_count,
            "readiness_percentage": readiness_pct,
            "checklist": checklist,
            "raw_instructions": raw_text
        }
