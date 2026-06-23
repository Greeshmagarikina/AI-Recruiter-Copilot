# 🚀 AI Recruiter Copilot

An enterprise-grade AI-powered recruitment platform that automates resume screening, candidate evaluation, and recruiter workflows using Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), and vector search.

The platform enables recruiters to securely authenticate, upload resumes, evaluate candidates against custom job descriptions, and query a semantic AI Copilot for cross-candidate insights.

---

## 🌐 Live Demo

### Frontend

https://ai-recruiter-copilot-vvatkfdcyliacg8o8e5vqg.streamlit.app/

### Backend API

https://ai-recruiter-copilot.onrender.com/api

---

# ⭐ Key Features

* 🔐 **Secure Authentication** – User Sign Up and Login system.
* 📄 **AI Resume Screening** – Automated resume analysis against job descriptions.
* 🎯 **Dynamic Candidate Scoring** – Adaptive evaluation for different experience levels.
* 🧠 **Layer 6 RAG Copilot** – Semantic search and cross-candidate comparisons.
* 🏷️ **Project Classification** – Automatic categorization of technical projects.
* 📧 **Recruiter Email Generation** – AI-generated hiring communication templates.
* 📊 **Recruiter Dashboard** – Candidate rankings, scorecards, and insights.
* 🗄️ **Persistent Vector Database** – ChromaDB-powered semantic candidate retrieval.
* ☁️ **Cloud Deployment** – Frontend deployed on Streamlit Community Cloud and Backend deployed on Render.
* 🛡️ **Enterprise Validation** – Strict schema-based scoring and evaluation controls.

---

## 🧠 About The Project

Recruiting technical talent is often slowed by manual resume reviews, inconsistent evaluations, and keyword-stuffed applications.

This platform addresses these challenges by combining AI-powered candidate assessment with Retrieval-Augmented Generation (RAG) to create an intelligent recruiter workspace.

### Workflow

1. Recruiter creates an account or logs in.
2. Upload one or more candidate resumes (PDF).
3. Paste the target job description.
4. AI evaluates candidates using structured scoring criteria.
5. Resume content is embedded and stored in ChromaDB.
6. Recruiters can query the Layer 6 RAG Copilot.
7. The system generates candidate insights, rankings, and recommendations.

---

## 🏗️ System Architecture

```text
Recruiter Login / Signup
            │
            ▼
      Streamlit Frontend
            │
            ▼
       FastAPI Backend
            │
            ▼
      Resume Upload
            │
            ▼
      PDF Extraction
        (PyMuPDF)
            │
            ▼
   Structured Parsing
            │
            ▼
      Gemini 2.5 Flash
            │
            ├── Candidate Scoring
            ├── Skill Analysis
            ├── Project Classification
            ├── Interview Suggestions
            └── Email Generation
            │
            ▼
    gemini-embedding-2
            │
            ▼
   ChromaDB Vector Store
            │
            ▼
    Layer 6 RAG Copilot
            │
            ▼
 Candidate Insights & Search
```

---

## 📦 Tech Stack

| Component            | Technology           |
| -------------------- | -------------------- |
| Frontend             | Streamlit            |
| Backend              | FastAPI              |
| Server               | Uvicorn              |
| Authentication       | User Login & Sign Up |
| LLM                  | Gemini 2.5 Flash     |
| AI SDK               | Google GenAI SDK     |
| Embeddings           | gemini-embedding-2   |
| Vector Database      | ChromaDB             |
| PDF Processing       | PyMuPDF (fitz)       |
| Data Analysis        | Pandas               |
| Visualization        | Plotly Express       |
| Deployment           | Render+Streamlit Community Cloud|
| Programming Language | Python               |

---

## 🚀 Installation

### Clone Repository

```bash
git clone https://github.com/Greeshmagarikina/AI-Recruiter-Copilot.git
cd AI-Recruiter-Copilot
```

### Create Virtual Environment

```bash
python -m venv venv
```

#### Linux / macOS

```bash
source venv/bin/activate
```

#### Windows

```bash
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

### Configure Environment Variables

Create a `.env` file inside the backend directory:

```env
GOOGLE_API_KEY=your_gemini_api_key
```

---

## ▶️ Running Locally

### Terminal 1 — Backend

```bash
cd backend
source ../venv/bin/activate

uvicorn main:app --reload --port 8000
```

Expected Output:

```text
INFO: Uvicorn running on http://127.0.0.1:8000
```

---

### Terminal 2 — Frontend

```bash
cd frontend
source ../venv/bin/activate

streamlit run app.py --server.port 8501
```

Open:

```text
http://localhost:8501
```

---

## 📖 Usage

### Step 1

Create a new account or log in.

### Step 2

Upload candidate resumes in PDF format.

### Step 3

Paste the target job description.

### Step 4

(Optional) Enter a recruiter question for the AI Copilot.

Examples:

```text
Who is the strongest NLP candidate?

Compare Python skills across all applicants.

Which candidate best matches the job description?

Who has production-level AI project experience?
```

### Step 5

Click **Analyze Resume**.

### Step 6

Review:

* Candidate Scores
* Skill Analysis
* Project Classifications
* Recruiter Email Drafts
* Interview Recommendations
* RAG Copilot Insights

---

## 🗑️ Reset Vector Database

To start with a fresh candidate pool, stop the backend service and delete the ChromaDB storage directory.

### Linux / macOS

```bash
rm -rf chroma_db/
```

### Windows PowerShell

```powershell
Remove-Item -Recurse -Force chroma_db
```

After restarting the application, a new vector database will be created automatically.

> ⚠️ This action permanently removes all stored candidate embeddings.

---

## 📂 Project Structure

```text
AI-Recruiter-Copilot/
│
├── backend/
│   ├── core/
│   │   └── structured_resume_parser.py
│   ├── main.py
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── .streamlit/
│   │   └── config.toml
│   ├── app.py
│   ├── frontend_resumes/
│   └── requirements.txt
│
├── chroma_db/
│
├── README.md
```

---

 
## 🔮 Future Enhancements & Roadmap
 * **Multi-User Support & Recruiter Collaboration**
 * **OCR & Vision-Language Model Integration**
 * **STT / TTS Voice Interfaces**
 * **Automated CI/CD Pipelines**
 * **Production Testing Frameworks**
 * **Load Balancing & Horizontal Scaling**
 * **Cloud Vector Database Migration**
 * **Multi-LLM Integration Orchestration**


---

## 🙏 Acknowledgements

* Google Gemini Team
* ChromaDB Community
* FastAPI Framework
* Streamlit Team
* Open Source AI Community

---

## 👨‍💻 Author

### GREESHMA GARIKINA

**AI & ML Engineer | Generative AI | NLP | LLM Applications | RAG Systems | System Design**

⭐ If you found this project useful, consider giving it a star on GitHub.
