from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from core.structured_resume_parser import parse_resume_semantically, RecruiterCopilotEngine

app = FastAPI(title="AI Recruiter Intelligence Gateway Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    user_id: Optional[str] = None
    file_name: str
    resume_text: str
    jd_text: str

class CopilotRequest(BaseModel):
    query: str

@app.get("/api/health")
def health_check():
    return {"status": "operational", "engine": "Gemini-2.5-Flash"}

@app.post("/api/auth/signup")
def signup(payload: dict):
    return {"status": "success", "message": "Account initialized secure routing spaces."}

@app.post("/api/auth/signin")
def signin(payload: dict):
    return {"email": payload.get("email", "recruiter@enterprise.com"), "user_id": "usr_dev_state_99"}

@app.post("/api/auth/signout")
def signout():
    return {"status": "terminated"}

@app.post("/api/analyze")
def analyze_resume_pipeline(payload: AnalysisRequest):
    if not payload.resume_text.strip():
        return {"file_name": payload.file_name, "quota_exhausted": True}
        
    try:
        assessment = parse_resume_semantically(payload.resume_text, payload.jd_text)
        score = assessment.final_suitability_index
        name = assessment.candidate_name
        
        # =========================================================
        # 📧 ENTERPRISE SCORE-DRIVEN EMAIL BLUEPRINT GENERATOR
        # =========================================================
        if score >= 90:
            email_status = "Offer Extended"
            email_body = (
                f"Subject: Congratulations! Executive Offer Extended - {name}\n\n"
                f"Dear {name},\n\n"
                f"Following the rigorous architectural audit of your application, our engineering leadership group "
                f"is thrilled to formally extend an offer to join our AI Systems division. Your elite technical portfolio "
                f"scored at the top of our alignment index ({score}/100).\n\n"
                f"Our talent acquisition leads will reach out within 24 hours with package documents and start schedules.\n\n"
                f"Welcome to the team,\nHR Operations Group"
            )
        elif score >= 75:
            email_status = "Interview Scheduled"
            email_body = (
                f"Subject: Interview Technical Loop Scheduled - {name}\n\n"
                f"Dear {name},\n\n"
                f"Thank you for your patience during our technical screening process. Your profile has demonstrated exceptional "
                f"alignment with our technical parameters, scoring a high-tier matching index of {score}/100.\n\n"
                f"We have officially advanced your profile to our live core loop. A calendar link has been dispatched to coordinate "
                f"your technical system panel interviews with our AI engineering architects.\n\n"
                f"Best regards,\nTechnical Sourcing Team"
            )
        elif score >= 60:
            email_status = "Shortlisted"
            email_body = (
                f"Subject: Application Update: Shortlisted - {name}\n\n"
                f"Dear {name},\n\n"
                f"We are pleased to inform you that your profile has successfully passed our automated structural validation filters, "
                f"ranking at a strong suitability standing of {score}/100.\n\n"
                f"Your engineering record has been actively shortlisted for this technical track. We are consolidating our top candidate "
                f"matrices and will reach out with primary technical discussion dates shortly.\n\n"
                f"Sincerely,\nTalent Acquisition Group"
            )
        elif score >= 40:
            email_status = "Under Review"
            email_body = (
                f"Subject: Processing Status Notice: Under Review - {name}\n\n"
                f"Dear {name},\n\n"
                f"Thank you for submitting your engineering credentials for our open AI position. Your application profile has generated a "
                f"suitability baseline score of {score}/100.\n\n"
                f"Your background is currently undergoing deep manual cross-matching by our sourcing managers against auxiliary team balances. "
                f"We appreciate your patience while we complete this review sequence.\n\n"
                f"Best regards,\nRecruitment Review Board"
            )
        else:
            email_status = "Rejected"
            email_body = (
                f"Subject: Regarding Your Application - {name}\n\n"
                f"Dear {name},\n\n"
                f"Thank you for your interest in our open AI positions and for taking the time to share your technical timeline with us. "
                f"Your application profile registered a final alignment score of {score}/100.\n\n"
                f"After executing a complete review of our pipeline dependencies, we have decided not to advance your candidacy further at "
                f"this time. The candidate pool was highly competitive, and we had to make complex selections.\n\n"
                f"We wish you the best in your career pursuits,\nAI Recruitment Team"
            )

        formatted_projects = []
        for p in assessment.projects:
            formatted_projects.append({
                "name": p.name,
                "desc": p.description,
                "tech": p.technologies,
                "category": getattr(p, "category", "Applied NLP"),
                "industry_relevance": getattr(p, "industry_relevance", "Medium")
            })

        document_context = f"Candidate Profile: {name}\nSkills Matrix: {', '.join(assessment.explicit_skills)}\nResume Raw: {payload.resume_text}"
        RecruiterCopilotEngine.add_documents_to_pool(
            documents=[document_context],
            metadatas=[{"file_name": payload.file_name, "candidate_name": name}],
            ids=[f"id_{payload.file_name.replace('.', '_')}"]
        )

        return {
            "candidate_name": name,
            "file_name": payload.file_name,
            "recommendation": "Recommended" if score >= 65 else ("Consider" if score >= 40 else "Not Recommended"),
            "final_suitability_score": score,
            "skills_breakdown": assessment.scores.skills_match,
            "projects_breakdown": assessment.scores.projects_match,
            "experience_breakdown": assessment.scores.experience_match,
            "education_breakdown": assessment.scores.education_match,
            "certifications_breakdown": assessment.scores.certifications_match,
            "explicit_skills": assessment.explicit_skills,
            "inferred_skills": [{"name": i.capability_name, "conf": i.confidence_percentage, "just": i.justification} for i in assessment.inferred_skills],
            "missing_skills": assessment.skill_gap.missing_skills,
            "recommended_upskilling": assessment.skill_gap.recommended_upskilling,
            "strengths": assessment.strengths,
            "risks": assessment.risks,
            "projects": formatted_projects,
            "email_status": email_status,
            "email_draft": email_body,
            "interview_questions": assessment.interview_questions if hasattr(assessment, 'interview_questions') else "• Review core technical concepts in NLP."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/copilot")
def query_talent_rag_engine(payload: CopilotRequest):
    try:
        answer_text = RecruiterCopilotEngine.query_candidate_pool(payload.query)
        return {"answer": answer_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
