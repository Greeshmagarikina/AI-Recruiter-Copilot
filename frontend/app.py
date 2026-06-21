import streamlit as st
import fitz
import pandas as pd
import plotly.express as px
import requests
import os

BACKEND_URL = "http://localhost:8000/api"

if "user_authenticated" not in st.session_state:
    st.session_state.user_authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "all_candidates_cached" not in st.session_state:
    st.session_state.all_candidates_cached = []

st.set_page_config(page_title="AI Resume Screening Assistant", layout="wide")

# =========================================================
# RECRUITER AUTHENTICATION UI GATEWAY (Routed via API)
# =========================================================
st.sidebar.header("Recruiter Authentication Suite")

if not st.session_state.user_authenticated:
    auth_action = st.sidebar.radio("Choose Action", ["Login", "Register New Account"])
    email_input = st.sidebar.text_input("Corporate Email Address")
    password_input = st.sidebar.text_input("Password Secure Access Key", type="password")
    
    auth_payload = {"email": email_input, "password": password_input}
    
    if auth_action == "Register New Account":
        if st.sidebar.button("Create Account"):
            response = requests.post(f"{BACKEND_URL}/auth/signup", json=auth_payload)
            if response.status_code == 200:
                st.sidebar.success("Registration Success! Check email verification channels.")
            else:
                st.sidebar.error(response.json().get("detail", "Registration Error"))
                
    elif auth_action == "Login":
        if st.sidebar.button("Sign In"):
            response = requests.post(f"{BACKEND_URL}/auth/signin", json=auth_payload)
            if response.status_code == 200:
                user_data = response.json()
                st.session_state.user_authenticated = True
                st.session_state.user_email = user_data["email"]
                st.session_state.user_id = user_data["user_id"]
                st.rerun()
            else:
                st.sidebar.error(response.json().get("detail", "Authentication Failed"))

    st.warning("Please sign in using verified recruiter credentials to unlock system processing clusters.")
    st.stop()

st.sidebar.success(f"Active Account: {st.session_state.user_email}")
if st.sidebar.button("Log Out Session"):
    requests.post(f"{BACKEND_URL}/auth/signout")
    st.session_state.user_authenticated = False
    st.session_state.user_id = None
    st.session_state.all_candidates_cached = []
    st.rerun()

# =========================================================
# APPLICATION WORKSPACE MAIN SURFACE
# =========================================================
st.title("AI Resume Screening Assistant")

def extract_pdf_text(file_path):
    text = ""
    pdf = fitz.open(file_path)
    for page in pdf:
        text += page.get_text()
    pdf.close()
    return text

uploaded_files = st.file_uploader("Upload Resumes", accept_multiple_files=True, type=["pdf"])
jd_text = st.text_area("Paste Job Description Requirements")

# 🧠 LAYER 6 RAG COPILOT CONFIGURATION
st.markdown("### 🤖 Live AI Recruiter Copilot ")
copilot_query = st.text_input(
    "Ask a question..", 
)

st.divider()

os.makedirs("frontend_resumes", exist_ok=True)

# Main Multi-Layer Evaluation and Retrieval Pipeline Trigger
if st.button("Analyze Resumes"):
    if uploaded_files and jd_text:
        
        # --- PIPELINE PHASE 1: INDIVIDUAL RESUME PARSING & VECTOR INGESTION ---
        for uploaded_file in uploaded_files:
            st.header(f"🔍 Auditing: {uploaded_file.name}")
            
            file_path = f"frontend_resumes/{uploaded_file.name}"
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            resume_text = extract_pdf_text(file_path)
            
            payload = {
                "user_id": st.session_state.user_id,
                "file_name": uploaded_file.name,
                "resume_text": resume_text,
                "jd_text": jd_text
            }
            
            with st.spinner(f"Executing deep audit analysis loops for {uploaded_file.name}..."):
                try:
                    response = requests.post(f"{BACKEND_URL}/analyze", json=payload)
                    if response.status_code == 200:
                        data = response.json()
                        
                        if data.get("quota_exhausted"):
                            st.error(f"🛑 API Quota Exhausted while parsing: {data['file_name']}")
                            continue

                        # --- HEADER VERDICT BARS ---
                        st.subheader(f"Candidate Evaluation Profile: {data['candidate_name']}")
                        rec = data['recommendation']
                        if rec == "Highly Recommended": st.success(f"Vetting Status Verdict: {rec}")
                        elif rec == "Recommended": st.info(f"Vetting Status Verdict: {rec}")
                        elif rec == "Consider": st.warning(f"Vetting Status Verdict: {rec}")
                        else: st.error(f"Vetting Status Verdict: {rec}")
                        
                        # --- STRENGTHS & RISKS PANEL ---
                        col_s, col_r = st.columns(2)
                        with col_s:
                            st.markdown("### 🟢 Candidate Core Strengths")
                            for strength in data['strengths']:
                                st.markdown(f"- {strength}")
                        with col_r:
                            st.markdown("### 🔴 Candidate Core Risks & Voids")
                            for risk in data['risks']:
                                st.markdown(f"- **{risk}**")

                        # --- DETAILED SUITABILITY BREAKDOWN METRICS ---
                        st.markdown("### 📊 Audited Suitability Score Breakdown")
                        c1, c2, c3, c4, c5, c6 = st.columns(6)
                        with c1: st.metric("TOTAL SCORE", f"{data['final_suitability_score']}/100")
                        with c2: st.metric("Skills Match", f"{data['skills_breakdown']}/35")
                        with c3: st.metric("Projects Match", f"{data['projects_breakdown']}/45")
                        with c4: st.metric("Experience Proof", f"{data['experience_breakdown']}/10")
                        with c5: st.metric("Education Score", f"{data['education_breakdown']}/5")
                        with c6: st.metric("Certifications Weight", f"{data['certifications_breakdown']}/5")

                        # --- STRATEGIC SKILL TRACKING TABS ---
                        tab1, tab2, tab3 = st.tabs(["Explicit Skills Listed", "Potentially Inferred Capabilities", "Detected Skill Gaps"])
                        
                        with tab1:
                            st.write(", ".join(data['explicit_skills']))
                        
                        with tab2:
                            for inf in data['inferred_skills']:
                                st.markdown(f"• **{inf['name']}** — *Confidence Level: {inf['conf']}%*")
                                st.caption(f"Justification: {inf['just']}")
                        
                        with tab3:
                            st.markdown("#### ⚠️ Missing Core System Requirements")
                            st.write(", ".join(data['missing_skills']) if data['missing_skills'] else "No critical missing gaps identified.")
                            st.markdown("#### 📈 Recommended Upskilling Paths")
                            for up in data['recommended_upskilling']:
                                st.markdown(f"- {up}")

                        # --- ARCHITECTURAL PROJECT VERIFICATION LOGS (REWRITTEN TAXONOMY) ---
                        st.markdown("### 📂 Project Architecture Verification Logs")
                        for proj in data['projects']:
                            relevance = proj.get('industry_relevance', 'Medium')
                            
                            # Build color-coded badges based on explicit technical merit rankings
                            if relevance == "High":
                                rel_badge = "🔥 HIGH INDUSTRY RELEVANCE"
                            elif relevance == "Medium":
                                rel_badge = "⚡ MEDIUM INDUSTRY RELEVANCE"
                            else:
                                rel_badge = "💤 LOW INDUSTRY RELEVANCE"
                                
                            st.markdown(f"#### {proj['name']} — `{proj.get('category', 'Applied AI')}`")
                            st.markdown(f"**Relevance Standing:** `{rel_badge}`")
                            st.write(proj['desc'])
                            st.caption(f"Configured Stack: {', '.join(proj['tech'])}")
                            st.divider()

                        with st.expander("View Recruiter Engagement Email Blueprint"):
                            st.info(data['email_draft'])
                        
                        st.markdown("### �� Advanced Core Technical Interview Loops")
                        st.write(data['interview_questions'])

                        # Append candidate metadata data frames to structural UI state cache
                        skills_matrix_string = ", ".join(data['explicit_skills'])
                        candidate_row = {
                            "Name": data['candidate_name'],
                            "Final Suitability Score": data['final_suitability_score'],
                            "Recommendation": rec,
                            "Skills Match (/35)": data['skills_breakdown'],
                            "Projects Match (/45)": data['projects_breakdown'],
                            "Experience Proof (/10)": data['experience_breakdown'],
                            "Skills Matrix": skills_matrix_string
                        }
                        st.session_state.all_candidates_cached = [c for c in st.session_state.all_candidates_cached if c["Name"] != data['candidate_name']]
                        st.session_state.all_candidates_cached.append(candidate_row)
                    else:
                        st.error(f"FastAPI Server Error: {response.text}")
                except Exception as e:
                    st.error(f"Could not connect to API Gateway Service layer: {e}")
        
        # --- PIPELINE PHASE 2: AUTOMATED SEQUENTIAL LAYER 6 RAG COPILOT COUPLING ---
        if copilot_query:
            st.divider()
            st.subheader("💡 Automated AI Recruiter Copilot Insights")
            with st.spinner("Retrieving semantic vector contexts and synthesizing response..."):
                try:
                    copilot_res = requests.post(f"{BACKEND_URL}/copilot", json={"query": copilot_query})
                    if copilot_res.status_code == 200:
                        answer_data = copilot_res.json()
                        st.info(f"🔮 **Copilot Synthesis Verdict:**\n\n{answer_data.get('answer', 'No response returned.')}")
                    else:
                        st.error(f"Copilot API Layer Error: {copilot_res.text}")
                except Exception as e:
                    st.error(f"Could not reach Copilot vector routing gateway: {e}")
        
        st.success("✅ Complete vetting loops and semantic database analysis finished successfully!")

# =====================================================
# ================= DASHBOARD ANALYTICS PANEL =========
# =====================================================
if st.session_state.all_candidates_cached:
    st.divider()
    st.header("📈 Recruiter Suite Dashboard Analytics")
    
    df = pd.DataFrame(st.session_state.all_candidates_cached)
    df = df.sort_values(by="Final Suitability Score", ascending=False).reset_index(drop=True)
    
    st.dataframe(df, use_container_width=True)
    
    melt_cols = ["Skills Match (/35)", "Projects Match (/45)", "Experience Proof (/10)"]
    available_melt = [c for c in melt_cols if c in df.columns]
    
    if available_melt:
        chart_df = df.melt(id_vars=["Name"], value_vars=available_melt, var_name="Evaluation Metric Vector", value_name="Points Earned")
        fig_metrics = px.bar(chart_df, x="Name", y="Points Earned", color="Evaluation Metric Vector", barmode="group", color_discrete_sequence=px.colors.qualitative.G10)
        st.subheader("Dynamic Multi-Criteria Analysis Plots")
        st.plotly_chart(fig_metrics)
    
    fig_rank = px.bar(
        df, x="Name", y="Final Suitability Score", 
        title="Comprehensive Standings Matrix (Total Score Overview)", 
        color="Final Suitability Score", color_continuous_scale="Viridis"
    )
    st.plotly_chart(fig_rank)
