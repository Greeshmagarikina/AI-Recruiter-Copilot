from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from groq import Groq
from dotenv import load_dotenv
import numpy as np
import os

load_dotenv()

# ======================================================
# ================= LOAD GROQ CLIENT ===================
# ======================================================

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# ======================================================
# ============== LOAD EMBEDDING MODEL ==================
# ======================================================

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

# ======================================================
# ================= CHATBOT FUNCTION ===================
# ======================================================

def recruiter_chatbot(
    question,
    resume_text,
    ats_score=None,
    semantic_score=None,
    final_score=None,
    mode="single",
):

    # ==================================================
    # ============== BETTER TEXT CHUNKING ==============
    # ==================================================

    # Split using paragraphs instead of lines
    chunks = resume_text.split("\n\n")

    # Remove small/useless chunks
    chunks = [
        chunk.strip()
        for chunk in chunks
        if len(chunk.strip()) > 40
    ]

    # ==================================================
    # ================= EMPTY CHECK ====================
    # ==================================================

    if len(chunks) == 0:
        return (
            "No meaningful content found "
            "in resume."
        )

    # ==================================================
    # ============== QUESTION EMBEDDING ================
    # ==================================================

    question_embedding = model.encode(
        [question]
    )

    # ==================================================
    # ============== CHUNK EMBEDDINGS ==================
    # ==================================================

    chunk_embeddings = model.encode(
        chunks
    )

    # ==================================================
    # ============== COSINE SIMILARITY =================
    # ==================================================

    similarities = cosine_similarity(
        question_embedding,
        chunk_embeddings
    )[0]

    # ==================================================
    # ============== TOP MATCHES =======================
    # ==================================================

    top_indices = similarities.argsort()[-8:][::-1]

    # ==================================================
    # ============== CONTEXT CREATION ==================
    # ==================================================

    context = ""

    for index in top_indices:
        similarity_score = similarities[index]

        # Higher threshold = better accuracy
        if similarity_score > 0.35:
            context += f"""

Similarity Score:
{round(float(similarity_score), 2)}

Resume Section:
{chunks[index]}

----------------------------------------
"""

    # ==================================================
    # ============== FALLBACK ==========================
    # ==================================================

    if context.strip() == "":
        context = "\n".join(
            chunks[:5]
        )

    # ==================================================
    # ============== SCORE CONTEXT =====================
    # ==================================================

    score_context = f"""
ATS Score:
{ats_score if ats_score is not None else "Not provided"}

Semantic Score:
{semantic_score if semantic_score is not None else "Not provided"}

Final Score:
{final_score if final_score is not None else "Not provided"}
"""

    # ==================================================
    # ============== SINGLE MODE =======================
    # ==================================================

    if mode == "single":

        prompt = f"""

You are an expert AI recruiter.

Your task is to evaluate ONLY ONE candidate.

Use ONLY the provided resume information.

==================================================

Resume Information:
{context}

==================================================

Scores:
{score_context}

==================================================

Recruiter Question:
{question}

==================================================

STRICT RULES:

1. Evaluate ONLY this candidate.

2. NEVER invent skills, projects, or experience.

3. Mention only explicitly available skills.

4. Missing skills must be stated ONLY if they are explicitly absent in the resume and explicitly required by the question.


5. Keep answer concise and professional.

6. Maximum 8 lines.

7. Do not exaggerate candidate strengths.

8. If information is unavailable,
   clearly say so.

9. Prefer factual evaluation over
   generic praise.

10. Mention strengths and weaknesses
    separately.

11. NEVER change numerical scores.

12. Use ONLY provided ATS and Final Scores.

13. NEVER invent ratings like
    8/10 or 90/100.

14. If scores are provided,
    repeat them exactly.

15. If no projects were found, say:
    Projects not mentioned in the extracted resume data.
16. Also include skills present in the resume that are relevant to the question, even if they are not explicitly required.

"""

    # ==================================================
    # ============== MULTIPLE MODE =====================
    # ==================================================

    else:

        prompt = f"""

You are an expert AI recruiter.

Your task is to compare candidates fairly.

IMPORTANT:
Final Score and ATS data are VERY IMPORTANT.

Higher Final Score means stronger candidate fit.

==================================================

Candidate Information:
{context}

==================================================

Scores:
{score_context}

==================================================

Recruiter Question:
{question}

==================================================

STRICT RULES:

1. Rank candidates using:
   - Final Score
   - ATS Score
   - Semantic Similarity
   - Technical Skills
   - Project Relevance

2. NEVER ignore Final Score.

3. Candidate with highest Final Score
   should usually rank first unless
   resume quality is extremely poor.

4. NEVER invent fake projects, skills, or experience.

5. Mention:
   - strengths
   - weaknesses
   - missing skills ONLY if explicitly absent in the resume and explicitly required by the question

6. Keep response professional.

7. Give final hiring recommendation.

8. Use bullet points.

9. Be consistent with provided scores.

10. Do not hallucinate information.

11. NEVER change numerical scores.

12. Use ONLY provided ATS and Final Scores.

13. NEVER invent ratings like
    8/10 or 90/100.

14. If scores are provided,
    repeat them exactly.

15. If no projects were found, say:
    Projects not mentioned in the extracted resume data.

"""

    # ==================================================
    # ============== LLM CALL ==========================
    # ==================================================

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict "
                    "technical recruiter."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    # ==================================================
    # ============== RETURN RESPONSE ===================
    # ==================================================

    return response.choices[0].message.content