# RecruiteIQ.ai
AI Screening &amp; Pre-Assessment Engine for Recruitment Agencies

# 🚀 TalentAIQ.ai — AI-Assisted Resume Screening Engine

TalentAIQ.ai is an AI-powered candidate evaluation engine designed to intelligently score and rank resumes against job descriptions using semantic embeddings, structured scoring logic, and explainable AI principles.

Built with FastAPI and designed with production-grade architecture in mind.

---

## 🎯 Vision

TalentAIQ.ai aims to:

- Automate resume screening
- Improve hiring signal quality
- Reduce recruiter bias
- Provide explainable scoring outputs
- Enable enterprise-grade observability and scalability

---

## 🏗️ Architecture Overview

TalentAIQ follows a modular, scalable design:


RecruiteIQ.ai/
│
├── app/ # FastAPI API layer
├── core/ # Scoring engine, models, embeddings
├── llm/ # LLM integrations (if enabled)
├── observability.py # Logging + structured telemetry
├── config.py # Configuration management
├── requirements.txt # Dependencies
├── Dockerfile # Containerization
└── README.md


---

## ⚙️ Tech Stack

- **Python 3.10**
- **FastAPI**
- **Uvicorn**
- **Sentence Embeddings**
- **Structured Scoring Engine**
- **Explainability Layer**
- **Docker-ready**
- Git-optimized (no large artifacts)

---

## 🧠 Core Features

### ✅ Semantic Embedding Matching
- Uses vector similarity to compare resumes and job descriptions.

### ✅ Skill Match Scoring
- Keyword and structured skill comparison.

### ✅ Experience Weighting
- Experience-based boost scoring.

### ✅ Explainability Output
Returns:
- Matched skills
- Missing skills
- Embedding score
- Final weighted score
- Candidate category

### ✅ Observability
- Structured logging
- Correlation ID support
- Timed scoring stages

---

## 🔥 API Endpoint

### Analyze Candidates

**POST** `/analyze`

#### Request Body
```json
{
  "job_description": {...},
  "resumes": [...]
}
Response
[
  {
    "candidate_name": "John Doe",
    "skill_match_score": 0.85,
    "embedding_score": 0.91,
    "experience_score": 0.80,
    "final_score": 0.88,
    "category": "Strong Match",
    "matched_skills": ["python", "aws"],
    "missing_skills": ["kubernetes"]
  }
]
🛠️ Local Setup
1️⃣ Clone Repository
git clone https://github.com/rksalgotra/RecruiteIQ.ai.git
cd RecruiteIQ.ai
2️⃣ Create Virtual Environment
python -m venv .venv
source .venv/bin/activate
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ Run Server
uvicorn app.main:app --reload

Access API docs at:

http://127.0.0.1:8000/docs
🐳 Docker (Optional)
docker build -t recruiteiq .
docker run -p 8000:8000 recruiteiq
🔐 Environment Variables

Create .env file:

OPENAI_API_KEY=your_key_here

⚠️ .env is ignored by Git for security.

🧹 Git Hygiene

Large artifacts are excluded via .gitignore:

.venv/

model weights

FAISS indexes

logs

.env

Repository is optimized for clean CI/CD workflows.

🚀 Roadmap

 Persist FAISS index

 Resume chunking

 Metadata filtering

 Evaluation metrics dashboard

 CI/CD pipeline

 Cloud deployment

 Enterprise auth integration

🏢 Production Principles

TalentAIQ is designed with:

Clean separation of concerns

Observability-first mindset

Minimal Git footprint

Cloud-ready architecture

Extensible embedding layer

👨‍💻 Author

Rajesh Kumar
Lead Workflow Automation Specialist
AI Systems Architect


MIT License (Update as needed)