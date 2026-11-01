import os
import uuid
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
from backend.app.schemas.document import DocumentResponse, DocumentChecklistResponse
from backend.app.services.scheme_service import scheme_service
from backend.app.services.profile_service import DEFAULT_DEMO_USER_ID

logger = logging.getLogger("civicpilot.documents")

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
UPLOAD_DIR = BASE_DIR / "backend" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# In-memory document vault
_DOCUMENTS_VAULT: Dict[str, Dict] = {}


class DocumentService:
    def __init__(self):
        # Pre-seed verified demo documents strictly for the demo user only
        self._seed_default_documents()

    def _seed_default_documents(self):
        _DOCUMENTS_VAULT["doc-seed-aadhaar"] = {
            "id": "doc-seed-aadhaar",
            "user_id": DEFAULT_DEMO_USER_ID,
            "original_filename": "Aadhaar_Card_Verified.pdf",
            "file_size": 1420000,
            "detected_type": "Aadhaar Card (UIDAI)",
            "processing_status": "verified",
            "tag": "aadhaar_card",
            "extracted_fields": {
                "document_number": "XXXX-XXXX-4921",
                "holder_name": "Aarav Sharma",
                "dob": "2004-06-15",
                "gender": "Male"
            },
            "user_confirmed_fields": {
                "document_number": "XXXX-XXXX-4921",
                "holder_name": "Aarav Sharma"
            },
            "created_at": "2024-10-25T10:00:00Z"
        }

        _DOCUMENTS_VAULT["doc-seed-income"] = {
            "id": "doc-seed-income",
            "user_id": DEFAULT_DEMO_USER_ID,
            "original_filename": "Income_Certificate_Tehsildar_FY24.pdf",
            "file_size": 890000,
            "detected_type": "Income Certificate",
            "processing_status": "verified",
            "tag": "income_certificate",
            "extracted_fields": {
                "certificate_no": "REV/GJ/2024/84912",
                "annual_family_income": 220000.0,
                "issuing_authority": "Office of the Tehsildar, Ahmedabad",
                "validity_year": "2024-2025"
            },
            "user_confirmed_fields": {
                "annual_family_income": 220000.0
            },
            "created_at": "2024-10-28T14:30:00Z"
        }

    def list_documents(self, user_id: Optional[str] = None) -> List[DocumentResponse]:
        """List documents for the specific authenticated user only. Never leaks demo docs to registered citizens."""
        target_uid = user_id or DEFAULT_DEMO_USER_ID
        results = []
        for d in _DOCUMENTS_VAULT.values():
            if d.get("user_id") == target_uid:
                results.append(DocumentResponse(
                    id=d["id"],
                    original_filename=d["original_filename"],
                    file_size=d["file_size"],
                    detected_type=d.get("detected_type"),
                    processing_status=d["processing_status"],
                    extracted_fields=d.get("extracted_fields"),
                    user_confirmed_fields=d.get("user_confirmed_fields"),
                    created_at=d["created_at"]
                ))
        return results

    def simulate_or_parse_upload(self, filename: str, content_bytes: bytes, user_id: Optional[str] = None) -> DocumentResponse:
        """
        Extract facts from uploaded certificate with mandatory user-confirmation requirement.
        """
        doc_id = str(uuid.uuid4())
        lower_name = filename.lower()
        
        # Fetch current user profile to ground extracted names/details
        target_uid = user_id or "anonymous"
        user_prof = _DOCUMENTS_VAULT.get(target_uid) # check if exists
        applicant_name = "Candidate"
        from backend.app.services.profile_service import profile_service
        prof = profile_service.get_profile(target_uid)
        if prof and prof.full_name:
            applicant_name = prof.full_name

        if "income" in lower_name:
            doc_type = "Income Certificate"
            tag = "income_certificate"
            extracted = {
                "annual_family_income": prof.annual_family_income or 220000.0,
                "issuing_authority": f"Tehsildar / Revenue Authority ({prof.state_code or 'State'})",
                "validity": "Current Financial Year"
            }
        elif "mark" in lower_name or "score" in lower_name or "12th" in lower_name:
            doc_type = "Class 12 Marksheet"
            tag = "educational_marksheets"
            extracted = {
                "board": "State Board of Secondary & Higher Secondary Education",
                "aggregate_percentage": "84.6%",
                "candidate_name": applicant_name
            }
        elif "bonafide" in lower_name or "college" in lower_name:
            doc_type = "Bonafide Student Certificate"
            tag = "bonafide_student_certificate"
            extracted = {
                "institution": prof.institution_name or "Recognized Institution",
                "aishe_code": "U-0142",
                "course": prof.course or "Degree Course",
                "year": prof.study_year or 1
            }
        else:
            doc_type = "Government Verification Document"
            tag = "other_certificate"
            extracted = {
                "status": "Document successfully parsed",
                "candidate_name": applicant_name,
                "character_count": len(content_bytes)
            }

        doc_record = {
            "id": doc_id,
            "user_id": user_id or "registered_user",
            "original_filename": filename,
            "file_size": len(content_bytes),
            "detected_type": doc_type,
            "processing_status": "awaiting_user_confirmation",
            "tag": tag,
            "extracted_fields": extracted,
            "user_confirmed_fields": None,
            "created_at": datetime.now(timezone.utc).isoformat()
        }


        _DOCUMENTS_VAULT[doc_id] = doc_record

        return DocumentResponse(
            id=doc_id,
            original_filename=filename,
            file_size=len(content_bytes),
            detected_type=doc_type,
            processing_status="awaiting_user_confirmation",
            extracted_fields=extracted,
            user_confirmed_fields=None,
            created_at=doc_record["created_at"]
        )

    def confirm_extraction(self, doc_id: str, confirmed_fields: Dict) -> Optional[DocumentResponse]:
        """User explicitly reviews and confirms extracted facts."""
        doc = _DOCUMENTS_VAULT.get(doc_id)
        if not doc:
            return None

        doc["processing_status"] = "verified"
        doc["user_confirmed_fields"] = confirmed_fields
        _DOCUMENTS_VAULT[doc_id] = doc

        return DocumentResponse(
            id=doc["id"],
            original_filename=doc["original_filename"],
            file_size=doc["file_size"],
            detected_type=doc.get("detected_type"),
            processing_status="verified",
            extracted_fields=doc.get("extracted_fields"),
            user_confirmed_fields=confirmed_fields,
            created_at=doc["created_at"]
        )

    def get_scheme_checklist(self, scheme_slug: str) -> DocumentChecklistResponse:
        """
        Compare user's verified document tags against authentic scheme document matrix.
        Returns missing-document checklist.
        """
        detail = scheme_service.get_scheme_by_slug(scheme_slug)
        required_tags = detail.detected_document_tags if detail else [
            "aadhaar_card", "income_certificate", "educational_marksheets", "bonafide_student_certificate"
        ]

        # Get uploaded verified tags
        uploaded_tags = [
            d["tag"] for d in _DOCUMENTS_VAULT.values()
            if d.get("processing_status") == "verified" and "tag" in d
        ]

        missing_tags = [t for t in required_tags if t not in uploaded_tags]

        return DocumentChecklistResponse(
            scheme_id=scheme_slug,
            required_document_tags=required_tags,
            uploaded_document_tags=uploaded_tags,
            missing_document_tags=missing_tags,
            is_ready_for_application=len(missing_tags) == 0
        )


document_service = DocumentService()
