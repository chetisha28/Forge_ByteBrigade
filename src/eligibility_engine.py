import json
import os
import re
from typing import Dict, Any, List, Optional
from langchain_core.documents import Document

class EligibilityEngine:
    """
    Evaluates citizen profiles against LangChain Document objects.
    Extracts eligibility rules from document metadata & page content.
    """
    def __init__(self, rules_path: str = "data/eligibility_rules/eligibility_rule_engine.json"):
        self.rules_path = rules_path
        self.flagship_rules = {}
        self._load_rules()

    def _load_rules(self):
        if os.path.exists(self.rules_path):
            with open(self.rules_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for r in data.get("flagship_scheme_rules", []):
                    self.flagship_rules[r["scheme_slug"]] = r

    def evaluate_doc(self, profile: Dict[str, Any], doc: Document) -> Dict[str, Any]:
        """
        Evaluates a LangChain Document object against the citizen profile.
        """
        meta = doc.metadata
        content = doc.page_content.lower()
        slug = meta.get("scheme_slug", "")
        reasons = []
        disqualifications = []
        score = 80 # Baseline match score

        # 1. State Jurisdiction Check
        state_rule = meta.get("state_or_ministry", "")
        level = meta.get("level", "")
        citizen_state = profile.get("state_residence", "").strip().lower()

        if level == "State / UT Government" and state_rule:
            if citizen_state and citizen_state not in state_rule.lower():
                disqualifications.append(f"Restricted to residents of {state_rule}.")
                score = 0
            else:
                reasons.append(f"Eligible for state jurisdiction: {state_rule}")

        # 2. Flagship Scheme Deterministic Check
        if slug in self.flagship_rules:
            rule = self.flagship_rules[slug]
            conds = rule.get("eligibility_conditions", {})

            # Landowner check
            if conds.get("is_landowner") is True:
                if not profile.get("is_landowner"):
                    disqualifications.append("Requires cultivable agricultural land ownership.")
                    score -= 50
                else:
                    reasons.append("Citizen is a verified agricultural landholder.")
                    score += 10

            # Income Ceiling Check
            income_max = conds.get("annual_household_income_max")
            citizen_income = profile.get("annual_household_income")
            if income_max is not None and citizen_income is not None:
                if citizen_income > income_max:
                    disqualifications.append(f"Income ₹{citizen_income:,.0f} exceeds max ceiling ₹{income_max:,.0f}.")
                    score -= 60
                else:
                    reasons.append(f"Income within eligible limit (<= ₹{income_max:,.0f}).")

            # Occupation Check
            occ_list = conds.get("occupation_in")
            citizen_occ = profile.get("occupation")
            if occ_list and citizen_occ:
                if citizen_occ not in occ_list:
                    disqualifications.append(f"Occupation '{citizen_occ}' not in target list: {', '.join(occ_list)}.")
                    score -= 40
                else:
                    reasons.append(f"Occupation matches: {citizen_occ}")

            # Caste Check
            caste_list = conds.get("caste_category_in")
            citizen_caste = profile.get("caste_category")
            if caste_list and citizen_caste:
                if citizen_caste not in caste_list and "General" not in caste_list:
                    disqualifications.append(f"Reserved for: {', '.join(caste_list)}.")
                    score -= 40
                else:
                    reasons.append(f"Caste criteria satisfied: {citizen_caste}")

        # 3. Dynamic Text-Based Evaluation on Document page_content
        else:
            age = profile.get("age")
            if age is not None:
                age_matches = re.findall(r'(\d{1,2})\s*(?:years|yrs)\s*(?:of\s*age|and\s*above|or\s*above|minimum)', content)
                for am in age_matches:
                    min_age = int(am)
                    if min_age > 10 and age < min_age:
                        disqualifications.append(f"Requires minimum age of {min_age} years.")
                        score -= 30

            citizen_income = profile.get("annual_household_income")
            if citizen_income is not None:
                if "bpl" in content or "below poverty line" in content:
                    if citizen_income > 150000 and profile.get("ration_card_type") not in ["BPL / Priority Household (PHH)", "Antyodaya (AAY)"]:
                        disqualifications.append("Requires BPL status or income under ₹1.5 Lakh.")
                        score -= 30
                    else:
                        reasons.append("Eligible under BPL / Low-income criterion.")

        is_eligible = len(disqualifications) == 0 and score >= 50
        status = "Eligible" if is_eligible else ("Partially Eligible" if score > 30 else "Ineligible")

        return {
            "scheme_slug": slug,
            "scheme_name": meta.get("scheme_name", slug),
            "status": status,
            "score": max(0, min(100, score)),
            "is_eligible": is_eligible,
            "matched_reasons": reasons,
            "disqualifications": disqualifications
        }
