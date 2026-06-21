import os
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from google import genai
from google.genai import types
import chromadb
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")
chroma_client = chromadb.PersistentClient(path=DB_PATH)
vector_collection = chroma_client.get_or_create_collection(name="talent_pool")

allow_extra_config = ConfigDict(extra="allow")

class InferredCapability(BaseModel):
    model_config = allow_extra_config
    capability_name: str = Field(description="The technology or domain skill inferred from context.")
    confidence_percentage: int = Field(description="Strict confidence score (0-100%).")
    justification: str = Field(description="Direct text evidence from the resume.")

class ProjectDetail(BaseModel):
    model_config = allow_extra_config
    name: str
    description: str
    technologies: List[str]
    category: str = Field(description="Technical classification (e.g., 'Applied NLP', 'NLP Application', 'Local LLM Integration').")
    industry_relevance: str = Field(description="Must be exactly 'High', 'Medium', or 'Low'.")

class ScoreBreakdown(BaseModel):
    model_config = allow_extra_config
    skills_match: float = Field(ge=0, le=35, description="Score between 0.0 and 35.0 maximum.")
    projects_match: float = Field(ge=0, le=45, description="Score between 0.0 and 45.0 maximum.")
    experience_match: float = Field(ge=0, le=10, description="Score between 0.0 and 10.0 maximum.")
    education_match: float = Field(ge=0, le=5, description="Score between 0.0 and 5.0 maximum. NEVER go above 5.0.")
    certifications_match: float = Field(ge=0, le=5, description="Score between 0.0 and 5.0 maximum. NEVER go above 5.0.")

class SkillGapAnalysis(BaseModel):
    model_config = allow_extra_config
    missing_skills: List[str]
    recommended_upskilling: List[str]

class RecruiterAssessment(BaseModel):
    model_config = allow_extra_config
    candidate_name: str
    final_suitability_index: float = Field(description="The exact mathematical sum of the broken down scores. Maximum limit 100.")
    scores: ScoreBreakdown
    explicit_skills: List[str]
    inferred_skills: List[InferredCapability]
    skill_gap: SkillGapAnalysis
    strengths: List[str] = Field(description="Top 3-4 professional, technical, or architecture highlights.")
    risks: List[str] = Field(description="Crucial gaps or warnings matching the specific role requirement scope.")
    projects: List[ProjectDetail]
    education: List[dict]
    experience: List[dict]
    certifications: Optional[str]
    # ⚡ STRICT FORMATTING MANDATE: Changed description to force strict markdown line breaks in output string
    interview_questions: str = Field(description="6 separate technical interview questions. Crucial: Use double line breaks between questions so that every single question renders strictly on its own fresh line (e.g., '• Question 1\n\n• Question 2').")

def _get_genai_client() -> genai.Client:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Missing GOOGLE_API_KEY environment variable.")
    return genai.Client(api_key=api_key)

class RecruiterCopilotEngine:
    @staticmethod
    def _generate_embedding(text: str) -> List[float]:
        client = _get_genai_client()
        try:
            response = client.models.embed_content(
                model="gemini-embedding-2",
                contents=text
            )
            if hasattr(response, 'embeddings') and response.embeddings:
                return response.embeddings[0].values
            if hasattr(response, 'embedding') and response.embedding:
                return response.embedding.values
            if isinstance(response, dict) and "embeddings" in response and response["embeddings"]:
                return response["embeddings"][0].get("values")
            raise ValueError("Could not extract embeddings structural data values.")
        except Exception as e:
            raise RuntimeError(f"Embedding request failed: {e}")

    @staticmethod
    def add_documents_to_pool(documents: List[str], metadatas: List[dict], ids: List[str]):
        embeddings = [RecruiterCopilotEngine._generate_embedding(doc) for doc in documents]
        vector_collection.upsert(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

    @staticmethod
    def query_candidate_pool(query: str) -> str:
        query_vector = RecruiterCopilotEngine._generate_embedding(query)
        results = vector_collection.query(query_embeddings=[query_vector], n_results=3)
        retrieved_docs = results.get("documents", [[]])[0]
        if not retrieved_docs:
            return "No matching profiles or credentials located inside database records."
            
        context_block = "\n---\n".join(retrieved_docs)
        client = _get_genai_client()
        prompt = f"Answer the recruiter's query based strictly on this resume context:\n{context_block}\n\nQuery: {query}"
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.2)
        )
        return response.text

def fix_schema_dict(schema: dict) -> dict:
    if isinstance(schema, dict):
        schema.pop("additionalProperties", None)
        for key, value in schema.items():
            fix_schema_dict(value)
    elif isinstance(schema, list):
        for item in schema:
            fix_schema_dict(item)
    return schema

def parse_resume_semantically(resume_text: str, jd_text: str) -> RecruiterAssessment:
    client = _get_genai_client()

    # 🚀 REWRITTEN LINE-BREAK RULES FOR INTERVIEW LOOPS
    system_instruction = """
    You are an expert Senior Technical Recruiter and AI Systems Architect screening candidates for technical positions.
    Your primary goal is to evaluate applicants with high realism, mapping their verified skills and projects objectively against requirements.

    Execute a strict vetting audit of the candidate based on these mandates:
    1. EXPLICIT VS INFERRED: List skills as explicit ONLY if written textually. Provide strict confidence levels and rigid text justifications.
    2. DYNAMIC & CONDITIONAL EXPERIENCE SCOUTING: Scan the provided Job Description for explicit required timelines (e.g., '3+ years experience'). IF and ONLY IF the Job Description demands full professional years of tenure and the candidate is a student/intern, apply a heavy experience penalty (1 or 2 out of 10). Otherwise, score fairly based on internship/project complexity.
    3. ACCURATE TECHNICAL TAXONOMY: Evaluate and categorize every project accurately. Foundational tasks like grammatical parsing systems or local text translators are core NLP/computational linguistic implementations. Use professional tags for the 'category' field (e.g., 'Applied NLP', 'NLP Application', 'Local LLM Integration', 'Autonomous Robotics').
    4. GRANULAR RELEVANCE RANKING: Populate 'industry_relevance' with 'High', 'Medium', or 'Low' based on complexity and alignment with modern AI engineering needs.
    5. INTERVIEW PROMPTING: For the 'interview_questions' string, generate exactly 6 high-level architectural follow-up technical interview questions. You MUST put a blank line between every single question using double newlines (\\n\\n) so they print beautifully on their own lines without clumping together. Never combine multiple questions on the same row.
    6. COMPLIANCE: Ensure final_suitability_index is EXACTLY the mathematical sum of the broken down scores. Do not let scores spill over their configured maxima definitions.
    """

    raw_schema = RecruiterAssessment.model_json_schema()
    clean_schema = fix_schema_dict(raw_schema)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[f"JOB DESCRIPTION:\n{jd_text}\n\n", f"CANDIDATE RESUME TEXT:\n{resume_text}"],
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=clean_schema,
            temperature=0.1
        )
    )
    return RecruiterAssessment.model_validate_json(response.text)
