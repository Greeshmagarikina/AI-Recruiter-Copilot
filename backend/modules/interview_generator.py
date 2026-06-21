from groq import Groq
import os
from dotenv import load_dotenv

# =====================================================
# ================= LOAD ENV ==========================
# =====================================================

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# =====================================================
# ============ INTERVIEW QUESTION GENERATOR ===========
# =====================================================

def generate_interview_questions(

    skills,
    role="AI Engineer"

):

    # Convert skills list to readable text
    if isinstance(skills, list):

        skills_text = ", ".join(skills)

    else:

        skills_text = str(skills)

    # =================================================
    # ================= PROMPT ========================
    # =================================================

    prompt = f"""

You are an expert AI technical interviewer.

Generate exactly 6 interview questions.

Candidate Role:
{role}

Candidate Skills:
{skills_text}

Instructions:

1. Create:
   - 3 easy questions
   - 2 intermediate questions
   - 1 advanced project-based question

2. Questions must match ONLY the candidate's skills.

3. Each question should start with a bullet point (•) and be on a new line.

4. Keep questions:
   - concise
   - realistic
   - interview-friendly
   - beginner-to-intermediate level

5. Include:
   - theory questions
   - practical coding questions
   - project discussion questions

6. Avoid:
   - research-level questions
   - extremely difficult algorithm questions
   - unrelated topics
   - repeated skills

7. Make questions similar to:
   - internship interviews
   - fresher AI engineer interviews
   - ML developer interviews

8. Return ONLY bullet point questions.

Example Format:

• What is overfitting in machine learning?

• Explain the difference between a list and tuple in Python.

"""

    # =================================================
    # ================= GROQ API ======================
    # =================================================

    response = client.chat.completions.create(

        model="llama-3.1-8b-instant",

        messages=[

            {
                "role": "system",

                "content":
                "You are an expert technical interviewer."
            },

            {
                "role": "user",

                "content": prompt
            }
        ],

        temperature=0.7,

        max_tokens=400
    )

    # =================================================
    # ================= RETURN ========================
    # =================================================

    return response.choices[0].message.content