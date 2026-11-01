import os
import re
import uuid
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from backend.app.config import settings
from backend.app.schemas.assistant import AssistantQueryRequest, AssistantQueryResponse, SourceCitation
from backend.app.services.scheme_service import scheme_service

logger = logging.getLogger("civicpilot.rag")

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
GUIDELINES_DIR = BASE_DIR / "data" / "official_policy_guidelines"


class DocumentChunk:
    def __init__(self, doc_title: str, section_title: str, content: str, scheme_slug: str, source_url: str):
        self.doc_title = doc_title
        self.section_title = section_title
        self.content = content
        self.scheme_slug = scheme_slug
        self.source_url = source_url


class RAGAssistantService:
    def __init__(self):
        self._chunks: List[DocumentChunk] = []
        self._load_knowledge_base()

    def _load_knowledge_base(self):
        """Chunk all official policy markdown documents and index them."""
        if not GUIDELINES_DIR.exists():
            logger.warning(f"Guidelines directory not found at {GUIDELINES_DIR}")
            return

        for md_path in GUIDELINES_DIR.glob("*.md"):
            try:
                with open(md_path, "r", encoding="utf-8") as f:
                    text = f.read()

                # Extract title from first H1
                lines = text.split("\n")
                doc_title = md_path.stem.replace("_", " ").title()
                for line in lines:
                    if line.startswith("# "):
                        doc_title = line.replace("# ", "").strip()
                        break

                # Extract portal URL if present
                source_url = "https://www.myscheme.gov.in/"
                for line in lines:
                    if "scholarships.gov.in" in line:
                        source_url = "https://scholarships.gov.in/"
                        break
                    elif "pmkisan.gov.in" in line:
                        source_url = "https://pmkisan.gov.in/"
                        break
                    elif "pmsuryaghar.gov.in" in line:
                        source_url = "https://pmsuryaghar.gov.in/"
                        break

                # Determine associated scheme slug
                scheme_slug = md_path.stem.replace("_guidelines", "").replace("_operational_guidelines", "")
                if "scholarship" in scheme_slug:
                    scheme_slug = "national-scholarship-post-matric"
                elif "kisan" in scheme_slug:
                    scheme_slug = "pm-kisan"
                elif "ayushman" in scheme_slug:
                    scheme_slug = "ayushman-bharat-pmjay"
                elif "surya" in scheme_slug:
                    scheme_slug = "pm-surya-ghar-muft-bijli"
                elif "svanidhi" in scheme_slug:
                    scheme_slug = "pm-svanidhi"
                elif "vishwakarma" in scheme_slug:
                    scheme_slug = "pm-vishwakarma"
                elif "housing" in scheme_slug or "pmay" in scheme_slug:
                    scheme_slug = "pm-awas-yojana"

                # Split by Markdown sections (H2 / ##)
                sections = re.split(r'\n(?=##\s+)', text)
                for sec in sections:
                    sec_clean = sec.strip()
                    if not sec_clean:
                        continue
                    first_line = sec_clean.split("\n")[0].replace("##", "").strip()
                    section_title = first_line if first_line else "General Guidelines"

                    self._chunks.append(DocumentChunk(
                        doc_title=doc_title,
                        section_title=section_title,
                        content=sec_clean,
                        scheme_slug=scheme_slug,
                        source_url=source_url
                    ))

            except Exception as e:
                logger.error(f"Error chunking {md_path}: {e}")

        logger.info(f"RAG Knowledge Base initialized with {len(self._chunks)} official policy chunks.")

    def _retrieve_relevant_chunks(self, question: str, scheme_slug: Optional[str] = None, top_k: int = 3) -> List[Tuple[DocumentChunk, float]]:
        """
        Deterministic retrieval scoring based on query terms and scheme association.
        """
        tokens = set(re.findall(r'\b[a-zA-Z0-9]{3,}\b', question.lower()))
        # Remove common English stop words
        stop_words = {
            "what", "when", "where", "which", "who", "whom", "this", "that", "there",
            "have", "from", "with", "does", "about", "tell", "the", "for", "and", "are",
            "can", "how", "any", "you", "your", "per", "all", "not", "but", "why"
        }
        tokens = tokens - stop_words


        scored = []

        for chunk in self._chunks:
            chunk_text = chunk.content.lower()
            score = 0.0
            matched_token_count = 0

            # Match keyword tokens
            for token in tokens:
                count = chunk_text.count(token)
                if count > 0:
                    matched_token_count += 1
                    score += 2.0 + min(count, 5) * 0.5

            # High-value domain concept matching
            domain_concepts = {
                "income": ["income", "ceiling", "2,50,000", "4,50,000", "financial", "means"],
                "eligibility": ["eligible", "criteria", "percentile", "marks", "cutoff", "regular"],
                "documents": ["document", "aadhaar", "marksheet", "bonafide", "certificate", "aishe"],
                "benefits": ["benefit", "stipend", "allowance", "reimbursement", "12,000", "20,000", "6,000"],
                "apply": ["otr", "registration", "portal", "step", "verify", "nodal"]
            }

            matched_concepts = 0
            for concept, synonyms in domain_concepts.items():
                if concept in tokens or any(s in question.lower() for s in synonyms):
                    matched_synonyms = sum(1 for s in synonyms if s in chunk_text)
                    if matched_synonyms > 0:
                        matched_concepts += 1
                        score += matched_synonyms * 1.5

            # Only grant scheme slug boost if at least one query token or domain concept matched
            if matched_token_count > 0 or matched_concepts > 0:
                if scheme_slug and chunk.scheme_slug == scheme_slug:
                    score += 10.0

            if score > 0:
                scored.append((chunk, score))

        # Also search scheme catalog FAQs / Eligibility if query mentions a specific scheme
        if scheme_slug:
            scheme = scheme_service.get_scheme_by_slug(scheme_slug)
            if scheme:
                scheme_text = f"{scheme.name}\n{scheme.eligibility_criteria_text}\n{scheme.benefit_summary}\n{scheme.documents_required_text}\n{scheme.faqs}"
                score = 0.0
                matched_in_scheme = False
                for token in tokens:
                    if token in scheme_text.lower():
                        score += 3.0
                        matched_in_scheme = True
                if matched_in_scheme and score > 0:
                    scored.append((
                        DocumentChunk(
                            doc_title=scheme.name,
                            section_title="Official Portal Guidelines & FAQs",
                            content=scheme_text[:1200],
                            scheme_slug=scheme_slug,
                            source_url=scheme.official_url
                        ),
                        score + 5.0
                    ))


        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    def _call_gemini_api(self, prompt: str) -> Optional[str]:
        """Call official Google GenAI API if valid GEMINI_API_KEY is configured."""
        api_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not api_key or "your_" in api_key.lower() or "placeholder" in api_key.lower():
            return None

        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model=settings.gemini_generation_model,
                contents=prompt,
            )
            return response.text
        except Exception as e:
            logger.warning(f"Gemini API call failed or unavailable ({e}); falling back to local grounded synthesis.")
            return None


    def answer_query(self, request: AssistantQueryRequest) -> AssistantQueryResponse:
        """
        Generate a verifiable answer strictly grounded in authentic government documents.
        Never hallucinate dates, income caps, or eligibility rules.
        """
        question = request.question.strip()
        scheme_slug = request.scheme_id

        # 1. Retrieve relevant chunks
        top_chunks = self._retrieve_relevant_chunks(question, scheme_slug=scheme_slug, top_k=3)

        # 2. Check for insufficient evidence threshold
        if not top_chunks or top_chunks[0][1] < 3.0:
            return AssistantQueryResponse(
                answer="I could not find verified facts regarding this in the official government scheme guidelines. "
                       "To ensure complete accuracy, CivicPilot only provides information directly stated in official government notifications.",
                citations=[],
                insufficient_evidence=True,
                conversation_id=request.conversation_id or str(uuid.uuid4())
            )

        # 3. Build citations list
        citations = []
        context_parts = []

        for chunk, score in top_chunks:
            # Extract first 2-3 sentences as representative excerpt
            clean_content = re.sub(r'#+\s*', '', chunk.content)
            clean_content = ' '.join(clean_content.split())
            excerpt = clean_content[:240] + ("..." if len(clean_content) > 240 else "")

            citations.append(SourceCitation(
                source_title=chunk.doc_title,
                source_url=chunk.source_url,
                section_title=chunk.section_title,
                page_number=1,
                excerpt=excerpt
            ))

            context_parts.append(f"[{chunk.doc_title} | Section: {chunk.section_title}]\n{chunk.content}")

        context_str = "\n\n---\n\n".join(context_parts)

        # 4. Attempt Gemini generation with strict grounding constraints
        system_prompt = (
            "You are CivicPilot, an authentic Government of India welfare scheme assistant. "
            "Follow these rules strictly:\n"
            "1. Answer ONLY using the official excerpts provided below.\n"
            "2. Never fabricate income ceilings, deadlines, or eligibility conditions.\n"
            "3. If the context does not explicitly answer the question, state: "
            "'The official guidelines do not specify this information.'\n"
            "4. Keep the answer concise, respectful, and easy for students or citizens to understand.\n\n"
            f"OFFICIAL CONTEXT:\n{context_str}\n\n"
            f"CITIZEN QUESTION:\n{question}\n\n"
            "GROUNDED ANSWER:"
        )

        llm_response = self._call_gemini_api(system_prompt)

        if llm_response and len(llm_response.strip()) > 10:
            final_answer = llm_response.strip()
        else:
            # Deterministic, grounded local synthesis
            top_chunk, _ = top_chunks[0]
            paragraphs = [p.strip() for p in top_chunk.content.split("\n\n") if p.strip() and not p.strip().startswith("#")]
            relevant_p = paragraphs[0] if paragraphs else top_chunk.content[:400]
            
            final_answer = (
                f"According to the official {top_chunk.doc_title} ({top_chunk.section_title}):\n\n"
                f"{relevant_p}\n\n"
                f"Please refer to the verified citation below for the original policy text."
            )

        return AssistantQueryResponse(
            answer=final_answer,
            citations=citations,
            insufficient_evidence=False,
            conversation_id=request.conversation_id or str(uuid.uuid4())
        )


rag_service = RAGAssistantService()
