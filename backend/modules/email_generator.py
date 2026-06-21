# modules/email_generator.py
import os
from google import genai
from google.genai import types

def generate_email(candidate_name: str, final_score: float) -> str:
    """
    Generates a contextually accurate recruiter email based on rigid enterprise score tiers:
    - Score > 80: Shortlisted
    - Score 60 - 80: Under Review
    - Score < 60: Not Selected
    """
    # 1. Mathematically determine the true operational status
    if final_score > 80:
        status_tier = "Shortlisted / Moving to technical interview loop"
        tone_instruction = "highly encouraging, professional, welcoming, and clearly scheduling next steps."
    elif 60 <= final_score <= 80:
        status_tier = "Under Review / Hold position pipeline"
        tone_instruction = "neutral, encouraging but cautious, explaining that the application is undergoing final team review."
    else:
        status_tier = "Not Selected / Application Rejected"
        tone_instruction = "polite, respectful, empathetic, but definitive about not moving forward at this time."

    # 2. Construct the prompt with tight guardrails to prevent AI hallucinations
    prompt = f"""
    You are an automated corporate HR Recruiting Assistant. 
    Draft a professional email to the candidate based strictly on the parameters below. Do not deviate from the specified status tier.

    CANDIDATE NAME: {candidate_name}
    MATCH SCORE SUMMARY: {final_score}%
    OPERATIONAL STATUS TIER: {status_tier}

    TONE INSTRUCTIONS:
    {tone_instruction}

    REQUIREMENTS:
    - Return ONLY the final clean text email body (including Subject line).
    - Do not add any conversational meta-text before or after the email draft.
    - Use '[Recruiting Team / Company Name]' as the standard placeholder signature.
    """

    try:
        # Initialize your standard client signature wrapper
        client = genai.Client()
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text
        
    except Exception as e:
        print(f"[Email Engine Error]: {e}")
        # Secure static fallback template if the API drops under heavy load
        if final_score > 80:
            return f"Subject: Update on your application - Shortlisted\n\nDear {candidate_name},\n\nWe are pleased to inform you that your application has been shortlisted. Our team will contact you shortly regarding next steps.\n\nBest regards,\nRecruiting Team"
        elif 60 <= final_score <= 80:
            return f"Subject: Update on your application - Under Review\n\nDear {candidate_name},\n\nThank you for applying. Your profile is currently under review by our hiring team. We will update you shortly.\n\nBest regards,\nRecruiting Team"
        else:
            return f"Subject: Your application update\n\nDear {candidate_name},\n\nThank you for your interest. After careful consideration, we regret to inform you that we are not moving forward with your application at this time.\n\nBest regards,\nRecruiting Team"