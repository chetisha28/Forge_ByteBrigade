import os

guidelines = {
    "pm_surya_ghar_guidelines.md": """# PM Surya Ghar: Muft Bijli Yojana - Operational Guidelines

**Issuing Authority**: Ministry of New and Renewable Energy (MNRE), Government of India  
**Official Portal**: [pmsuryaghar.gov.in](https://pmsuryaghar.gov.in/)  
**Scheme Outlay**: ₹75,021 Crore

## 1. Scheme Objective
To install rooftop solar plants in 1 Crore households across India, providing up to 300 units of free electricity every month and generating income by selling surplus electricity back to the grid.

## 2. Subsidy Structure (Central Financial Assistance - CFA)
- **1 kW System**: ₹30,000 direct subsidy.
- **2 kW System**: ₹60,000 direct subsidy.
- **3 kW and above System**: ₹78,000 maximum direct subsidy.
- **Group Housing Societies / Residential Welfare Associations (GHS/RWA)**: ₹18,000 per kW for common facilities (up to 500 kW).

## 3. Implementation Mechanism
1. National Portal for single-window registration, feasibility check, vendor selection, net-metering application, and subsidy claim.
2. Low-interest collateral-free bank loans (approx. 7% interest rate) available via national portal integration.
3. DBT subsidy released directly into applicant's bank account within 30 days of installation commissioning.
""",
    "pmay_housing_guidelines.md": """# Pradhan Mantri Awas Yojana (PMAY) - Operational Guidelines

**Issuing Authority**: Ministry of Housing and Urban Affairs (MoHUA) & Ministry of Rural Development (MoRD), Government of India  
**Official Portals**: [pmayg.nic.in](https://pmayg.nic.in/) / [pmay-urban.gov.in](https://pmay-urban.gov.in/)

## 1. Core Principles
- Provision of pucca houses with basic amenities (water, sanitation, electricity, LPG) to all eligible houseless and families living in kutcha or dilapidated houses.
- Mandatory ownership or co-ownership of the house in the name of the female head of household.

## 2. Financial Assistance Norms
### PMAY-Gramin (Rural):
- **Unit Assistance**: ₹1,20,000 in plain areas; ₹1,30,000 in hilly/difficult/IAP areas.
- **Toilet Construction**: Additional ₹12,000 assistance under Swachh Bharat Mission (Gramin).
- **Unskilled Labour Support**: 90 person-days (plain) / 95 person-days (hilly) of unskilled wage labour under MGNREGS (approx. ₹20,000+).

### PMAY-Urban:
- **Beneficiary Led Construction (BLC)**: Central assistance of ₹1.50 Lakh per house.
- **Affordable Housing in Partnership (AHP)**: ₹1.50 Lakh per EWS house.
- **Credit Linked Subsidy Scheme (CLSS)**: Up to ₹2.67 Lakh upfront interest subsidy on home loans.
""",
    "pm_svanidhi_guidelines.md": """# PM Street Vendor's AtmaNirbhar Nidhi (PM SVANidhi) - Guidelines

**Issuing Authority**: Ministry of Housing and Urban Affairs (MoHUA), Government of India  
**Official Portal**: [pmsvanidhi.mohua.gov.in](https://pmsvanidhi.mohua.gov.in/)

## 1. Objectives
- Facilitate collateral-free working capital micro-loans to street vendors to resume livelihoods.
- Incentivize regular repayment through interest subsidy.
- Reward digital transactions via monthly cashbacks.
- Integrate vendors into institutional social security safety nets.

## 2. Loan Hierarchy
- **1st Loan**: ₹10,000 with 1-year tenure.
- **2nd Loan**: ₹20,000 with 18-month tenure (eligible on timely repayment of 1st loan).
- **3rd Loan**: ₹50,000 with 36-month tenure (eligible on timely repayment of 2nd loan).

## 3. Financial Subsidies
- **Interest Subsidy**: 7% per annum credited quarterly directly into the vendor's bank account through DBT.
- **Digital Incentive**: ₹100 per month (up to ₹1,200 per year) cashback based on volume of QR code transactions.
"""
}

for fname, content in guidelines.items():
    path = f"data/official_policy_guidelines/{fname}"
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Saved {path}")

