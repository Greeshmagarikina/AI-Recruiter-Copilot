# vector_store.py

import os
import chromadb

from google import genai

from typing import List, Dict, Any

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .structured_resume_parser import FullStructuredResume

class CandidateVectorStore:

    def __init__(self):

        # Local ChromaDB storage
        self.chroma_client = chromadb.PersistentClient(
            path="chroma_db"
        )

        self.collection = self.chroma_client.get_or_create_collection(
            name="talent_pool"
        )
        # Gemini Client
        self.ai_client = genai.Client(
            api_key=os.getenv("GOOGLE_API_KEY")
        )

    # vector_store.py (Line 16 onwards)

    def _get_embedding(self, text: str) -> List[float]:
        """Generates embedding vector utilizing Google's native gemini-embedding-2."""
        try:
            # ⚡ THE PRODUCTION FIX: Set model explicitly to "gemini-embedding-2"
            response = self.ai_client.models.embed_content(
                model="gemini-embedding-2",
                contents=text
            )
            return response.embeddings[0].values
        except Exception as e:
            print(f"[RAG Database Error] Embedding calculation failed: {e}")
            raise e  

    def upsert_candidate(
        self,
        file_name: str,
        parsed_resume: "FullStructuredResume",
        suitability_index: float
    ):

        print(
            f"[RAG Registry] Archiving candidate records: "
            f"{parsed_resume.candidate_name}"
        )

        # Projects
        project_text = " ".join(
            [
                f"Project: {p.name}. "
                f"Description: {p.description}. "
                f"Technologies: {', '.join(p.technologies)}."
                for p in parsed_resume.projects
            ]
        )

        # Experience
        experience_text = " ".join(
            [
                f"Job Role: {exp.job_title} "
                f"at {exp.company}. "
                f"Details: {exp.description}."
                for exp in parsed_resume.experience
            ]
        )

        # Skills
        skills_text = (
            f"Skills listed: "
            f"{', '.join(parsed_resume.explicit_skills)}."
        )

        # Education
        education_text = " ".join(
            [
                f"Degree: {edu.degree} "
                f"in {edu.field_of_study} "
                f"from {edu.institution}."
                for edu in parsed_resume.education
            ]
        )

        composite_document = (
            f"Candidate Profile: "
            f"{parsed_resume.candidate_name}. "
            f"{skills_text} "
            f"{project_text} "
            f"{experience_text} "
            f"{education_text}"
        )

        # Create embedding
        vector = self._get_embedding(composite_document)

        # Store in ChromaDB
        self.collection.upsert(
            ids=[file_name],
            embeddings=[vector],
            documents=[composite_document],
            metadatas=[
                {
                    "candidate_name": parsed_resume.candidate_name,
                    "file_name": file_name,
                    "suitability_score": float(
                        suitability_index
                    ),
                    "skills_summary": ", ".join(
                        parsed_resume.explicit_skills[:6]
                    )
                }
            ]
        )

        print(
            "[RAG Registry] Successfully indexed vector payload."
        )

    def query_talent_pool(
        self,
        natural_language_query: str,
        top_n: int = 3
    ) -> List[Dict[str, Any]]:

        print(
            f"[RAG Search Engine] "
            f"Retrieving closest matches for: "
            f"'{natural_language_query}'"
        )

        query_vector = self._get_embedding(
            natural_language_query
        )

        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=top_n
        )

        formatted_matches = []

        if (
            results
            and results.get("ids")
            and results["ids"][0]
        ):

            for i in range(
                len(results["ids"][0])
            ):

                formatted_matches.append(
                    {
                        "id":
                            results["ids"][0][i],

                        "document":
                            results["documents"][0][i],

                        "metadata":
                            results["metadatas"][0][i],

                        "distance":
                            results["distances"][0][i]
                            if "distances" in results
                            else 0.0
                    }
                )

        return formatted_matches