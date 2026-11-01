import os
import json
from typing import Dict, Any, Optional, List
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_core.documents import Document

# Authoritative Operational & Rejection Pitfalls Metadata
SCHEME_OPERATIONAL_METADATA: Dict[str, Dict[str, Any]] = {
    "pm_kisan": {
        "tat": "15-30 days",
        "benefit": "₹6,000 annually in 3 equal installments of ₹2,000 via DBT directly to Aadhaar-seeded bank account",
        "beneficiary": "Small and marginal farmer families owning cultivable agricultural land",
        "prerequisites": [
            "Active 12-digit Aadhaar linked with operational mobile for OTP verification",
            "Cultivable Land Record (Khatauni / Khasra / Dag number) in applicant's name",
            "DBT-enabled Bank Account seeded with NPCI Aadhaar mapper",
            "Scanned PDF of Land Record Document (strictly under 200 KB)"
        ],
        "rejection_pitfalls": [
            "❌ Bank Account NPCI DBT Inactive: Normal savings account without NPCI Aadhaar mapping causes PFMS transfer failure.",
            "❌ Land Mutation Cutoff: Land acquired after 01-02-2019 requires succession/inheritance certificate; direct purchases post-cutoff are ineligible.",
            "❌ Name Mismatch: Spelling discrepancy between Aadhaar card and State Land Revenue (Bhulekh) records leads to Level-1 rejection.",
            "❌ Oversized Land PDF: Uploading file over 200 KB or unreadable scan halts Patwari verification."
        ],
        "approval_flow": {
            "level_1": "Village Level: Physical & Revenue verification by Patwari / Lekhpal",
            "level_2": "Block / Tehsil: Scrutiny by Sub-Divisional Officer (SDO / Tehsildar)",
            "level_3": "District: Approval by District Agriculture Officer (DAO)",
            "level_4": "State & PFMS: Validation on DBT Bharat portal and electronic fund transfer",
            "tracking_url": "https://pmkisan.gov.in/BeneficiaryStatus_New.aspx",
            "helpline": "155261 / 1800-115-526"
        }
    },
    "pm_surya_ghar": {
        "tat": "30-45 days",
        "benefit": "Up to ₹78,000 central subsidy + state subsidy for 1kW-3kW+ rooftop solar",
        "beneficiary": "Residential domestic electricity consumers with owned unshaded roof space",
        "prerequisites": [
            "Electricity Consumer Account Number with latest paid electricity bill",
            "Ownership of residential roof with shadow-free area (min 10 sq.m / 100 sq.ft per kW)",
            "Aadhaar card of the electricity consumer",
            "Active savings bank account with cancelled cheque for DBT subsidy release"
        ],
        "rejection_pitfalls": [
            "❌ Name Mismatch on Electricity Bill: Consumer connection must match applicant's Aadhaar name; otherwise DISCOM cancels feasibility.",
            "❌ Capacity Exceeding Sanctioned Load: Applying for kW capacity higher than existing sanctioned load requires prior load enhancement.",
            "❌ Non-Empaneled Vendor: Solar installation must be done through DISCOM-registered vendors using ALMM-listed solar PV modules.",
            "❌ Blurred Cancelled Cheque: Unclear bank details or mismatched IFSC halts ₹30,000–₹78,000 DBT transfer."
        ],
        "approval_flow": {
            "level_1": "DISCOM Technical Feasibility Approval (Transformer & grid capacity check)",
            "level_2": "Installation by Registered Solar Vendor & ALMM module validation",
            "level_3": "DISCOM Field Inspection & Bi-directional Net Meter Commissioning",
            "level_4": "Central Subsidy Release to Bank Account via DBT within 30 days",
            "tracking_url": "https://pmsuryaghar.gov.in/",
            "helpline": "15555"
        }
    },
    "ayushman_bharat_pmjay": {
        "tat": "24-48 hours (Instant at Hospital)",
        "benefit": "₹5,00,000 annual cashless healthcare cover per family across empanelled hospitals nationwide",
        "beneficiary": "Vulnerable rural and urban families identified under SECC-2011 / NFSA Ration Card",
        "prerequisites": [
            "Ration Card / Family ID / SECC 2011 registration",
            "Aadhaar Card linked to active mobile for OTP, or biometric access",
            "Smartphone with camera for Ayushman Face-Auth App (or visit CSC/Hospital)"
        ],
        "rejection_pitfalls": [
            "❌ Face Auth Low Match Score: Live camera selfie match below 80% against Aadhaar photo causes auto-rejection. Visit hospital Ayushman Mitra for fingerprint scan.",
            "❌ Family Member Not Linked in Ration Database: New family members must first be added to the State NFSA / Food Department portal.",
            "❌ Non-Empanelled Hospital: Treatment must be taken strictly at PMJAY empanelled private or government hospitals."
        ],
        "approval_flow": {
            "level_1": "Beneficiary e-KYC Verification (Aadhaar OTP / Face / Fingerprint)",
            "level_2": "State Health Agency (SHA) automated database verification",
            "level_3": "Ayushman PVC Golden Card Approval & Immediate Digital PDF Download",
            "level_4": "Cashless Hospitalization Assistance at Help Desk (Ayushman Mitra)",
            "tracking_url": "https://beneficiary.nha.gov.in/",
            "helpline": "14555"
        }
    },
    "pm_svanidhi": {
        "tat": "7-15 days",
        "benefit": "Collateral-free working capital loan: ₹10k (1st tranche) -> ₹20k -> ₹50k with 7% interest subsidy and ₹1,200 annual UPI cashback",
        "beneficiary": "Urban, peri-urban, and rural street vendors vending within urban local body limits",
        "prerequisites": [
            "Certificate of Vending (CoV) / Identity Card or LoR (Letter of Recommendation) from ULB",
            "Aadhaar card linked with active mobile number",
            "Savings Bank Account with IFSC code for loan credit",
            "Smartphone capable of UPI QR code operations"
        ],
        "rejection_pitfalls": [
            "❌ Vendor Category Misidentification: Vendors missing ULB survey must obtain Letter of Recommendation (LoR) from Town Vending Committee first.",
            "❌ Active Commercial Default: CIBIL default or unpaid non-performing loan at a commercial bank halts lending partner sanction.",
            "❌ QR Code Inactivity: Failure to adopt digital payments forfeits ₹100/month cashback and 7% interest rebate."
        ],
        "approval_flow": {
            "level_1": "Urban Local Body (ULB) / Town Vending Committee verification",
            "level_2": "Lending Institution (PSU Bank / MFI) credit scoring and sanction",
            "level_3": "Direct Loan Disbursement into vendor bank account",
            "level_4": "Digital QR Onboarding & Interest Subsidy Direct Transfer",
            "tracking_url": "https://pmsvanidhi.mohua.gov.in/",
            "helpline": "1800-11-1979"
        }
    },
    "pm_vishwakarma": {
        "tat": "20-30 days",
        "benefit": "PM Vishwakarma Certificate & ID, ₹15,000 tool kit incentive, 5-day training with ₹500/day stipend, and collateral-free loan up to ₹3 Lakh at 5%",
        "beneficiary": "Artisans and craftspersons engaged in 18 traditional family-based trades",
        "prerequisites": [
            "Self-declaration of practicing one of 18 recognized traditional crafts",
            "Minimum age of 18 years at date of registration",
            "Aadhaar card linked with active mobile number",
            "Bank account details (for stipend & tool kit voucher)",
            "No active loan under PMEGP, PM SVANidhi, or Mudra in past 5 years"
        ],
        "rejection_pitfalls": [
            "❌ Multiple Household Claims: Only one member per family (husband/wife/unmarried children) can register.",
            "❌ Existing Government Micro-Loan: Having an active Mudra or PMEGP loan in past 5 years disqualifies the applicant.",
            "❌ Trade Outside 18 Notified Trades: Applicant must strictly belong to recognized artisanal crafts (Carpenter, Blacksmith, Potter, Tailor, Cobbler, etc.)."
        ],
        "approval_flow": {
            "level_1": "Gram Panchayat Head (Rural) / ULB Executive Officer (Urban) Trade Verification",
            "level_2": "District Implementation Committee (headed by District Collector / MSME DFO)",
            "level_3": "National Steering Committee Approval & PM Vishwakarma Certificate Issuance",
            "level_4": "Skill Training Onboarding, ₹15,000 E-Voucher & Collateral-Free Loan Sanction",
            "tracking_url": "https://pmvishwakarma.gov.in/",
            "helpline": "1800-267-7777 / 011-23061500"
        }
    },
    "pm_awas_yojana": {
        "tat": "45-90 days",
        "benefit": "Gramin: ₹1,20,000 (Plains) / ₹1,30,000 (Hilly) + ₹12,000 SBM toilet + 90 days MGNREGS wages. Urban: Interest subsidy up to ₹2.67 Lakh under CLSS / ₹1.5 Lakh grant.",
        "beneficiary": "Homeless families and households living in kutcha/dilapidated homes with no pucca house",
        "prerequisites": [
            "Aadhaar numbers of all family members",
            "Clear land possession deed / Gram Panchayat residential patta",
            "MGNREGA Job Card (for rural wage labor component)",
            "DBT-enabled Bank Account solely or jointly with female head of household"
        ],
        "rejection_pitfalls": [
            "❌ Pucca House Ownership: If any family member owns a registered pucca house anywhere in India, application is disqualified.",
            "❌ Non-Geo-Tagged Construction: Next installment is strictly released only after mobile geo-tag inspection of completed stage (Plinth, Lintel, Roof).",
            "❌ Male-Only Title: Scheme guidelines mandate house registration in the name of the female head or joint ownership."
        ],
        "approval_flow": {
            "level_1": "Gram Sabha Priority List / Awaas+ Beneficiary Verification",
            "level_2": "Block Development Officer (BDO) / ULB Inspection & Sanction Order",
            "level_3": "Stage-wise Geo-Tagging by Mobile Inspector (Plinth -> Lintel -> Roof)",
            "level_4": "Direct FTO (Fund Transfer Order) into beneficiary bank account via PFMS",
            "tracking_url": "https://pmayg.nic.in/netiayHome/home.aspx",
            "helpline": "1800-11-6446 (PMAY-G) / 1800-11-3116 (PMAY-U)"
        }
    },
    "national_scholarship_portal": {
        "tat": "30-60 days",
        "benefit": "Direct scholarship credit of tuition fees, maintenance allowance, and book grant directly into student's bank account",
        "beneficiary": "Students from minority, SC, ST, OBC, EWS families studying in Class 1 to Post-Doctoral courses",
        "prerequisites": [
            "14-digit One-Time Registration (OTR) number generated via NSP OTR App",
            "Previous qualifying exam mark sheet (min 50% marks)",
            "Annual Family Income Certificate issued by competent revenue authority (Tehsildar/SDM)",
            "Valid Bonafide Student Certificate with AISHE / UDISE code of institution",
            "Student's personal bank account seeded with NPCI Aadhaar mapper"
        ],
        "rejection_pitfalls": [
            "❌ Missing Institute Verification: Application is auto-rejected if College Nodal Officer (CNO) fails to verify before state deadline.",
            "❌ Bank Account DBT Not Active: Scholarship will bounce at PFMS stage if bank account is inactive on NPCI mapper or minor account without joint sign.",
            "❌ Duplicate Scholarship Application: Applying for both State and Central scholarships for same academic course leads to blacklisting."
        ],
        "approval_flow": {
            "level_1": "Institute Level: College / School Nodal Officer (CNO / INO) verification",
            "level_2": "District Level: District Nodal Officer (DNO / District Welfare Officer)",
            "level_3": "State Level: State Nodal Officer (SNO) merit list generation",
            "level_4": "Ministry & PFMS: Central DBT release directly into student's bank account",
            "tracking_url": "https://scholarships.gov.in/",
            "helpline": "0120-6619540"
        }
    }
}

class WorkflowEngine:
    """
    Manages authentic application form schemas and step-by-step portal workflows.
    Loaded via LangChain TextLoader / DirectoryLoader with rich operational normalization.
    """
    def __init__(self, workflows_dir: str = "data/application_forms_and_workflows"):
        self.workflows_dir = workflows_dir
        self.workflows: Dict[str, Any] = {}
        self.documents: List[Document] = []
        self._load_workflows()

    def _load_workflows(self):
        if not os.path.exists(self.workflows_dir):
            return

        # Load workflow JSONs via LangChain DirectoryLoader
        loader = DirectoryLoader(
            self.workflows_dir,
            glob="*.json",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"}
        )
        self.documents = loader.load()

        for doc in self.documents:
            fname = os.path.basename(doc.metadata.get("source", ""))
            key = fname.replace(".json", "").replace("_workflow", "")
            try:
                self.workflows[key] = json.loads(doc.page_content)
            except Exception:
                pass

    def _normalize_workflow(self, raw: Dict[str, Any], key: str) -> Dict[str, Any]:
        """Normalizes and enriches raw workflow data with standardized schema, rejection pitfalls, and field copy-paste helper."""
        meta = SCHEME_OPERATIONAL_METADATA.get(key, {})

        # 1. Scheme name & portal
        scheme_name = raw.get("scheme_name") or "Government Scheme Application Procedure"
        portal = raw.get("official_portal")
        if not portal and isinstance(raw.get("official_portals"), dict):
            portal = raw.get("official_portals", {}).get("pmay_gramin") or "https://pmayg.nic.in/"
        if not portal:
            portal = "https://myscheme.gov.in"

        tat = meta.get("tat") or raw.get("turnaround_time_days") or "15-30 days"
        benefit = meta.get("benefit") or raw.get("financial_benefit") or raw.get("benefit_summary") or raw.get("financial_subsidy") or "Direct Government Benefit / Subsidy via DBT"
        beneficiary = meta.get("beneficiary") or raw.get("target_beneficiary") or raw.get("target_beneficiaries") or "Eligible Indian Citizens"

        # 2. Prerequisites
        prereqs = meta.get("prerequisites") or raw.get("prerequisites") or [
            "Aadhaar Number linked with active mobile for OTP authentication",
            "DBT-enabled Bank Account seeded with NPCI Aadhaar mapper",
            "Relevant category / income / domicile certificate"
        ]

        # 3. Rejection pitfalls
        pitfalls = meta.get("rejection_pitfalls") or [
            "❌ Aadhaar Name Mismatch: Ensure spelling matches identity and bank records.",
            "❌ Bank Account Seeding: Bank account must be seeded with NPCI mapper for DBT credit.",
            "❌ Document Format: Scanned uploads must be crisp, legible, and within portal size limits."
        ]

        # 4. Extract raw steps from various possible keys
        raw_steps = (
            raw.get("application_steps") or
            raw.get("step_by_step_workflow") or
            raw.get("application_process_steps") or
            []
        )

        normalized_steps: List[Dict[str, Any]] = []
        for idx, s in enumerate(raw_steps):
            if not isinstance(s, dict):
                continue

            step_num = s.get("step_number") or (idx + 1)
            step_name = s.get("step_name") or s.get("step_title") or s.get("title") or s.get("name") or f"Step {step_num}"
            portal_action = s.get("portal_action") or s.get("action") or s.get("description") or ""

            # Fields extraction
            fields_raw = s.get("input_fields") or s.get("fields") or s.get("search_criteria") or []
            normalized_fields: List[Dict[str, Any]] = []
            if isinstance(fields_raw, list):
                for f in fields_raw:
                    if isinstance(f, dict):
                        f_name = f.get("name") or f.get("field") or "field"
                        f_label = f_name.replace("_", " ").title()
                        f_type = f.get("type") or "text"
                        f_desc = f.get("description") or ""
                        f_opts = f.get("options") or []
                        f_mandatory = f.get("mandatory", True)
                        normalized_fields.append({
                            "name": f_name,
                            "label": f_label,
                            "type": f_type,
                            "mandatory": f_mandatory,
                            "description": f_desc,
                            "options": f_opts
                        })
                    elif isinstance(f, str):
                        normalized_fields.append({
                            "name": f.lower().replace(" ", "_"),
                            "label": f,
                            "type": "text",
                            "mandatory": True,
                            "description": "",
                            "options": []
                        })

            # Verification / Additional options
            verification = s.get("verification") or ""
            if not verification and "modes" in s:
                verification = "Supported Verification Modes: " + ", ".join(s["modes"])
            if not verification and "stages" in s:
                verification = "Stages: " + " | ".join(s["stages"])
            if not verification and "options" in s and isinstance(s["options"], list):
                verification = "Eligible Categories: " + "; ".join(s["options"][:2])

            output_artifact = s.get("output_artifact") or ""

            normalized_steps.append({
                "step_number": step_num,
                "step_name": step_name,
                "portal_action": portal_action,
                "verification": verification,
                "fields": normalized_fields,
                "output_artifact": output_artifact
            })

        # 5. Approval & Redressal Flow
        approval_flow = meta.get("approval_flow") or raw.get("approval_and_redressal_flow") or {}
        tracking_url = approval_flow.get("tracking_url") or raw.get("tracking_url") or portal
        helpline = approval_flow.get("helpline") or raw.get("helpline") or "1800-11-5555"

        return {
            "key": key,
            "scheme_name": scheme_name,
            "official_portal": portal,
            "processing_tat": tat,
            "financial_benefit": benefit,
            "target_beneficiary": beneficiary,
            "prerequisites": prereqs,
            "rejection_pitfalls": pitfalls,
            "steps": normalized_steps,
            "approval_and_redressal_flow": {
                "level_1": approval_flow.get("level_1", "Verification by Village / Local Authority"),
                "level_2": approval_flow.get("level_2", "Block / Tehsil Level Scrutiny"),
                "level_3": approval_flow.get("level_3", "District Level Sanction"),
                "level_4": approval_flow.get("level_4", "State / PFMS DBT Fund Release"),
                "tracking_url": tracking_url,
                "helpline": helpline
            },
            "helpline": helpline,
            "tracking_url": tracking_url
        }

    def get_workflow(self, scheme_slug: str) -> Optional[Dict[str, Any]]:
        slug_clean = scheme_slug.replace("-", "_").lower()

        # Handle common aliases
        if "pmay" in slug_clean or "awas" in slug_clean:
            target_key = "pm_awas_yojana"
        elif "kisan" in slug_clean:
            target_key = "pm_kisan"
        elif "surya" in slug_clean or "solar" in slug_clean:
            target_key = "pm_surya_ghar"
        elif "ayushman" in slug_clean or "pmjay" in slug_clean:
            target_key = "ayushman_bharat_pmjay"
        elif "svanidhi" in slug_clean or "vendor" in slug_clean:
            target_key = "pm_svanidhi"
        elif "vishwakarma" in slug_clean:
            target_key = "pm_vishwakarma"
        elif "scholarship" in slug_clean or "nsp" in slug_clean:
            target_key = "national_scholarship_portal"
        else:
            target_key = None

        if target_key and target_key in self.workflows:
            return self._normalize_workflow(self.workflows[target_key], target_key)

        for key in self.workflows:
            if key in slug_clean or slug_clean in key:
                return self._normalize_workflow(self.workflows[key], key)

        return None

    def list_available_workflows(self) -> List[str]:
        return list(self.workflows.keys())
