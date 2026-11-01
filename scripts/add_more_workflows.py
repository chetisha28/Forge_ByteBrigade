import json

workflows = {
    "pm_awas_yojana_workflow": {
        "scheme_name": "Pradhan Mantri Awas Yojana - Gramin & Urban (PMAY)",
        "official_portals": {
            "pmay_gramin": "https://pmayg.nic.in/netiayHome/home.aspx",
            "pmay_urban": "https://pmay-urban.gov.in/"
        },
        "target_beneficiaries": "Homeless families and those living in kutcha/dilapidated houses in rural and urban areas.",
        "financial_subsidy": "Rural: ₹1,20,000 (Plains) / ₹1,30,000 (Hilly/NE/IAP districts) in 3 installments + ₹12,000 Swachh Bharat toilet grant + 90/95 days MGNREGS wage employment. Urban: Interest subsidy up to ₹2.67 Lakh under CLSS / ₹1.5 Lakh central assistance under BLC (Beneficiary-led Construction).",
        "application_process_steps": [
            {
                "step_number": 1,
                "step_name": "Gram Sabha / ULB Identification & Registration",
                "action": "Awaas+ survey registration / Urban demand survey through Urban Local Body (ULB) or online citizen assessment."
            },
            {
                "step_number": 2,
                "step_name": "AwaasSoft Beneficiary Registration",
                "fields": [
                    {"name": "aadhaar_number", "type": "string", "mandatory": True},
                    {"name": "bank_account_dbt", "type": "string", "mandatory": True},
                    {"name": "family_head_gender", "type": "string", "description": "Preference for female ownership or joint ownership", "mandatory": True},
                    {"name": "current_house_type", "type": "select", "options": ["Kutcha", "Zero-room", "One-room with kutcha roof"], "mandatory": True},
                    {"name": "land_ownership_document", "type": "file", "mandatory": True}
                ]
            },
            {
                "step_number": 3,
                "step_name": "Geo-Tagging & Stage-Wise Fund Release",
                "stages": [
                    "Stage 1 (Existing Site Geo-tag): Fund release for Foundation (Plinth level)",
                    "Stage 2 (Plinth Level Geo-tag): Fund release for Lintel / Roof level",
                    "Stage 3 (Roof Cast Geo-tag): Final finishing fund release",
                    "Stage 4 (Completed House with SBM Toilet Geo-tag): Handover & Completion Certificate"
                ]
            }
        ],
        "helpline": "1800-11-6446 (PMAY-G) / 1800-11-3116 (PMAY-U)"
    },
    "pm_surya_ghar_workflow": {
        "scheme_name": "PM Surya Ghar: Muft Bijli Yojana (Rooftop Solar)",
        "official_portal": "https://pmsuryaghar.gov.in/",
        "subsidy_structure": {
            "1_kw": "₹30,000 direct DBT subsidy",
            "2_kw": "₹60,000 direct DBT subsidy",
            "3_kw_and_above": "₹78,000 maximum central subsidy"
        },
        "step_by_step_workflow": [
            {
                "step_number": 1,
                "step_name": "Consumer Registration",
                "portal_action": "Select State -> Select Electricity Distribution Company (DISCOM) -> Enter Consumer Account Number -> Enter Mobile Number & Email"
            },
            {
                "step_number": 2,
                "step_name": "Feasibility Approval & Vendor Selection",
                "portal_action": "Apply for Rooftop Solar installation. DISCOM checks technical feasibility of grid transformer. Once approved, choose registered vendor from portal."
            },
            {
                "step_number": 3,
                "step_name": "Installation & Net Meter Commissioning",
                "portal_action": "Vendor installs solar modules and inverter. Apply for net meter. DISCOM inspects installation and commissions bidirectional net meter."
            },
            {
                "step_number": 4,
                "step_name": "Subsidy Claim Submission",
                "portal_action": "Submit bank details and upload cancelled cheque on portal. Central Government releases subsidy directly to bank account within 30 days."
            }
        ],
        "helpline": "15555"
    },
    "pm_svanidhi_workflow": {
        "scheme_name": "PM Street Vendor's AtmaNirbhar Nidhi (PM SVANidhi)",
        "official_portal": "https://pmsvanidhi.mohua.gov.in/",
        "target_beneficiaries": "Urban, semi-urban, and rural street vendors vending in urban areas.",
        "loan_slabs": {
            "first_loan": "₹10,000 (1 year repayment tenure)",
            "second_loan": "₹20,000 (Upon timely repayment of 1st loan)",
            "third_loan": "₹50,000 (Upon timely repayment of 2nd loan)"
        },
        "interest_subsidy": "7% interest subsidy credited directly to vendor's bank account quarterly.",
        "digital_cashback": "Up to ₹1,200 per year (₹100/month) for receiving payments via QR code.",
        "step_by_step_workflow": [
            {
                "step_number": 1,
                "step_name": "Vendor Vending Status Check",
                "options": [
                    "Category A: Vendors possessing Certificate of Vending / ID Card issued by ULB",
                    "Category B: Vendors identified in ULB survey but not issued ID card",
                    "Category C: Vendors left out of ULB survey (Requires Letter of Recommendation - LoR from ULB/Town Vending Committee)",
                    "Category D: Vendors from surrounding rural/peri-urban areas"
                ]
            },
            {
                "step_number": 2,
                "step_name": "Loan Application Submission",
                "portal_action": "Log in with Aadhaar OTP on PM SVANidhi portal or through Lending Institution / CSC. Select preferred lending bank."
            },
            {
                "step_number": 3,
                "step_name": "Disbursement & Digital QR Onboarding",
                "action": "Bank sanctions and disburses loan. UPI QR code (BHIM/Paytm/PhonePe/GPay) linked for cashback."
            }
        ],
        "helpline": "1800-11-1979"
    }
}

for name, data in workflows.items():
    path = f"data/application_forms_and_workflows/{name}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved {path}")

