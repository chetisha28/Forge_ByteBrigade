import os
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

# Standard NLP Libraries
from langdetect import detect
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class CitizenDemographicEntity(BaseModel):
    """
    Standard Pydantic Schema for LangChain NLU Information Extraction.
    """
    state_residence: Optional[str] = Field(None, description="Citizen state of residence in India (e.g. Uttar Pradesh, Bihar, Maharashtra, etc.)")
    occupation: Optional[str] = Field(None, description="Primary occupation or category (e.g. Farmer, Street Vendor, Artisan, Student, Construction Laborer)")
    land_holding_acres: Optional[float] = Field(None, description="Agricultural land owned in acres, if mentioned")
    annual_household_income: Optional[float] = Field(None, description="Annual household income in INR, if mentioned")
    age: Optional[int] = Field(None, description="Citizen age in years, if mentioned")
    gender: Optional[str] = Field(None, description="Gender (Male, Female, Other), if mentioned")
    is_landowner: Optional[bool] = Field(None, description="True if citizen owns agricultural or residential land")
    ration_card_type: Optional[str] = Field(None, description="BPL, AAY, Priority Household, or APL, if mentioned")

class CivicPilotNLPProcessor:
    """
    NLP Processor built with standard industry libraries:
    - Language Detection: langdetect standard library
    - NLU & Entity Extraction: LangChain JsonOutputParser + Pydantic schema
    - Text Vectorization & Matching: scikit-learn TfidfVectorizer
    """

    def __init__(self, llm=None):
        self.llm = llm
        self.parser = JsonOutputParser(pydantic_object=CitizenDemographicEntity)
        self.extraction_prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are an expert NLP Information Extraction assistant for Indian public administration.\n"
                "Extract citizen demographic attributes and eligibility criteria from their query text (which may be in English, Hindi, or Hinglish).\n"
                "Normalize state names to official Title Case (e.g. 'UP' -> 'Uttar Pradesh', 'MP' -> 'Madhya Pradesh').\n"
                "Normalize occupation to categories like: 'Farmer (Cultivator / Landowner)', 'Street Vendor / Urban Self-Employed', 'Traditional Artisan / Craftsman', 'Student / Youth', etc.\n"
                "{format_instructions}"
            )),
            ("human", "Citizen Query: \"{query}\"")
        ])

    def detect_language(self, text: str) -> str:
        """
        Uses standard langdetect library with Devanagari script detection.
        """
        if not text or not text.strip():
            return "English"

        # Check for Devanagari Unicode range
        if any('\u0900' <= char <= '\u097f' for char in text):
            return "Hindi"

        try:
            detected = detect(text)
            if detected == "hi":
                return "Hindi"
        except Exception:
            pass

        # Standard Hinglish detection heuristic (Latin script with Hindi romanized vocabulary)
        text_lower = text.lower().split()
        hinglish_tokens = {"kisan", "yojana", "milegi", "milega", "kheti", "jamin", "zameen", "chahiye", "ghar", "bijli", "mera", "meri", "hum", "hain"}
        if any(token in hinglish_tokens for token in text_lower):
            return "Hinglish"

        return "English"

    def extract_demographics(self, text: str, llm=None) -> Dict[str, Any]:
        """
        Executes LangChain standard NLU extraction chain:
        Prompt | LLM | JsonOutputParser()
        """
        active_llm = llm or self.llm
        if active_llm is not None:
            try:
                chain = self.extraction_prompt | active_llm | self.parser
                result = chain.invoke({
                    "query": text,
                    "format_instructions": self.parser.get_format_instructions()
                })
                # Clean up None values
                return {k: v for k, v in result.items() if v is not None}
            except Exception as e:
                print(f"Info: Standard LangChain NLU extraction fallback: {e}")

        # Standard fallback using basic string extraction when LLM is unavailable
        extracted = {}
        text_lower = text.lower()
        if "up" in text_lower or "uttar pradesh" in text_lower:
            extracted["state_residence"] = "Uttar Pradesh"
        elif "bihar" in text_lower:
            extracted["state_residence"] = "Bihar"
        elif "mp" in text_lower or "madhya pradesh" in text_lower:
            extracted["state_residence"] = "Madhya Pradesh"

        if any(w in text_lower for w in ["kisan", "farmer", "kheti"]):
            extracted["occupation"] = "Farmer (Cultivator / Landowner)"
            extracted["is_landowner"] = True
        elif any(w in text_lower for w in ["thela", "vendor", "rehri"]):
            extracted["occupation"] = "Street Vendor / Urban Self-Employed"
        elif any(w in text_lower for w in ["karigar", "artisan", "vishwakarma"]):
            extracted["occupation"] = "Traditional Artisan / Craftsman"

        return extracted

    def expand_query(self, query: str, demographics: Dict[str, Any]) -> str:
        """
        Standard NLP Query Expansion:
        Combines original query with extracted demographic entities.
        """
        tokens = [query]
        if "state_residence" in demographics:
            tokens.append(demographics["state_residence"])
        if "occupation" in demographics:
            tokens.append(demographics["occupation"])
        if demographics.get("is_landowner"):
            tokens.append("landowner agriculture pm-kisan")
        return " ".join(tokens)

    def calculate_text_similarity(self, query: str, documents: List[str]) -> List[float]:
        """
        Calculates standard TF-IDF Cosine Similarity using scikit-learn.
        """
        if not documents:
            return []
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform([query] + documents)
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        return similarities.tolist()

    def synthesize_hinglish_response(self,
                                      query: str,
                                      profile: Dict[str, Any],
                                      schemes: List[Dict[str, Any]],
                                      checklists: Dict[str, Any],
                                      workflows: Dict[str, Any]) -> str:
        """
        Structured Hinglish response generator when LLM is offline.
        """
        if not schemes:
            return "Namaste! Aapke profile ke anusaar abhi koi specific scheme match nahi hui hai."

        greeting = f"Namaste {profile.get('full_name', '')}!".strip()
        lines = [f"{greeting} Aapke query aur profile ke anusaar verified official government data se khoji gayi schemes:\n"]

        for idx, scheme in enumerate(schemes, 1):
            s_name = scheme.get("scheme_name", "Yojana")
            ministry = scheme.get("state_or_ministry", "Central Government")
            url = scheme.get("official_url", "https://myscheme.gov.in")
            ea = scheme.get("eligibility_assessment", {})
            status = "✅ Eligible" if ea.get("status") == "Eligible" else "⚠️ Partially Eligible"
            score = ea.get("score", 70)
            slug = scheme.get("scheme_slug", "")

            lines.append(f"### {idx}. {s_name}")
            lines.append(f"🏛️ **Vibhag/Rajya**: {ministry}")
            lines.append(f"🎯 **Yogyata**: {status} (Match Score: {score}/100)")
            
            docs = checklists.get(slug, {}).get("checklist", [])
            if docs:
                lines.append(f"📄 **Zaroori Dastavez**: {', '.join(d['name'] for d in docs[:3])}")

            lines.append(f"🔗 **Official Portal**: [{url}]({url})\n")

        return "\n".join(lines)
