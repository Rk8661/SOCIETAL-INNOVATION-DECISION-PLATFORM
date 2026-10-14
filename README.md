
# Societal Innovation & Decision Platform

**From community problems to evidence-backed action.**

An AI-assisted platform that transforms scattered citizen-reported societal problems into structured community challenges, supports evidence-driven government decisions, connects universities and industry with real-world needs, and verifies whether implemented solutions actually work.

<p align="center">
  <strong>Detect · Decide · Allocate · Verify · Learn</strong>
</p>

---

## 🎥 Project Demo

**[▶ Watch the Working Prototype on YouTube](https://youtu.be/G0QIaDFIn7Q)**

The demonstration showcases the citizen reporting workflow, AI-assisted problem analysis, dossier consolidation, and government-facing views of community challenges.

---

## 📌 Problem Statement

**SIH26043 — Digital Platform to Crowdsource Societal Challenges and Facilitate Collaborative Problem Solving through Universities and Industry Partnerships**

Communities experience problems involving drinking water, sanitation, education, healthcare, infrastructure, agriculture, and other essential services. Meanwhile, universities, researchers, startups, and industries possess expertise and resources that could help address these challenges.

The difficulty is not simply collecting complaints. It is converting those reports into validated challenges, selecting appropriate interventions, coordinating institutional resources, and measuring real-world outcomes.

Our platform addresses this gap through an AI-assisted decision and coordination layer.

## 💡 Our Approach

Traditional complaint systems primarily focus on reporting and tracking issues. This platform extends the workflow by helping answer five important questions:

- **What is happening?** Classify citizen reports and consolidate related observations.
- **What requires attention?** Estimate preliminary priority and detect unusual reporting patterns.
- **What should be done?** Search existing innovation knowledge and recommend REUSE, ADAPT, or INVENT.
- **Who should act?** Support institutional matching and structured proposal comparison.
- **Did it work?** Collect impact evidence before considering a challenge resolved.

The governing principle is simple:

> AI recommends. Evidence and authorized humans decide.

---

## ✨ Key Features

### 1. Citizen Problem Reporting

A citizen-facing Streamlit interface allows users to describe local societal problems and provide location context.

Features include:
- Text-based problem submission.
- District, village/block, and pincode details.
- Optional Google Maps location link.
- Submission tracking and processing status.

The interface is designed to keep reporting straightforward, including for citizens who may find coordinate-based location entry difficult.

### 2. AI-Assisted Classification

The backend uses Hugging Face Transformers for zero-shot text classification.

The classification pipeline identifies a likely problem domain and subdomain from a controlled set of candidate categories.

The system stores classification scores alongside the results so that recommendations can be inspected rather than treated as unquestionable decisions.

### 3. Semantic Similarity and Dossier Consolidation

Similar reports can describe the same underlying problem using different words.

For example:

- "The primary school roof has collapsed."
- "The roof of our village school has caved in."

The platform uses sentence embeddings and vector similarity search to identify related submissions and group them under a shared community dossier.

**Technology:** Sentence Transformers, MiniLM, FAISS, NumPy, and SQLAlchemy.

Original submissions remain available as evidence. Consolidation is intended to reduce duplicate work records, not erase citizens' reports.

### 4. Explainable Priority Assessment

A lightweight heuristic engine combines urgency-related text signals with classified problem categories to estimate preliminary priority.

This design avoids requiring another large inference model for every priority assessment.

Priority is a decision-support signal, not a guarantee of severity or an autonomous emergency determination. Government review remains important.

### 5. Spatiotemporal Anomaly Detection

The anomaly layer analyses reporting activity across time and location to identify unusual increases in reports.

Rather than treating every frequently reported issue as an emergency, the system aims to distinguish persistent problems from potentially emerging situations by comparing current reporting activity against historical patterns.

An anomaly alert indicates a need for investigation; it does not independently declare an emergency.

### 6. Innovation Memory and Contextual Intervention

Before encouraging new research, the platform can consult an innovation memory of previously recorded interventions and their outcomes.

Its decision framework is:

| Decision | Meaning |
|---|---|
| **REUSE** | An existing validated intervention appears suitable for the new context. |
| **ADAPT** | A related intervention exists but requires local modification. |
| **INVENT** | No sufficiently applicable validated intervention has been identified, so new research may be justified. |

Similarity alone is insufficient. Contextual suitability should also consider local requirements, resources, infrastructure, deployment conditions, and previous outcomes.

### 7. Government Decision Support

The government-facing interface presents AI-grouped community challenges and relevant information in a consolidated view.

The intended workflow supports review of:
- Community problem summaries.
- Merged citizen reports.
- Classification and priority.
- Location and reporting activity.
- Intervention recommendations.
- Institutional proposals and allocation decisions.

AI provides recommendations; authorized officials retain responsibility for governance decisions.

### 8. Ground-Truth Evidence and Proof of Impact

The platform is designed to distinguish project completion from verified problem resolution.

Its intended lifecycle is:

`DEPLOYED → AWAITING IMPACT VERIFICATION → IMPACT VERIFIED → RESOLVED`

Citizen feedback, technical tests, field evidence, and measurable outcome indicators can contribute to the verification process.

Verified outcomes can then enrich innovation memory, helping future challenges benefit from previous successes and lessons learned.

---

## 🏗️ System Architecture

```text
                 STREAMLIT FRONTEND
          ┌─────────────┼─────────────┐
          │             │             │
       Citizen      Government    University
          │             │             │
          └─────────────┼─────────────┘
                        │
                   REST / JSON
                        │
                        ▼
                  FASTAPI BACKEND
          ┌─────────────┼─────────────┐
          │             │             │
       Submission    Dossier       Decision
       Management   Management      Engines
          │             │             │
          └─────────────┼─────────────┘
                        │
             ┌──────────┴──────────┐
             ▼                     ▼
       SQLAlchemy            AI / Intelligence
             │                     │
          SQLite              BART / MiniLM
             │                     │
       Persistent data            FAISS
                                   │
                          Classification, similarity,
                          priority and anomaly analysis
```

FastAPI acts as the backend authority. Streamlit communicates with the backend through HTTP requests instead of accessing the database directly.

The prototype uses SQLite for local development, with PostgreSQL as a potential production database.

---

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| Frontend | Streamlit |
| Backend API | FastAPI |
| API validation | Pydantic |
| Database ORM | SQLAlchemy |
| Prototype database | SQLite |
| Schema migrations | Alembic |
| Text classification | Hugging Face Transformers, BART-family model |
| Text embeddings | Sentence Transformers, MiniLM |
| Vector similarity search | FAISS |
| Data and numerical processing | Pandas, NumPy |
| Background processing | FastAPI BackgroundTasks |
| Version control | Git and GitHub |

---

## 📁 Project Structure

```text
SIH26043/
│
├── backend/
│   ├── alembic/
│   │   └── versions/           # Database migrations
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints/  # API endpoints
│   │   │       └── router.py
│   │   ├── core/               # Database and configuration
│   │   ├── models/             # SQLAlchemy models
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── services/
│   │   │   └── ai/             # AI pipeline and matching
│   │   └── main.py
│   ├── requirements.txt
│   ├── alembic.ini
│   └── seed_data.py
│
├── frontend/
│   ├── pages/
│   │   ├── 1_Officer_Dashboard.py
│   │   ├── 2_Citizen_Portal.py
│   │   └── 3_University_Portal.py
│   ├── utils/
│   │   └── api_client.py
│   └── app.py
│
├── .gitignore
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

Install the following before running the project:

- Python 3.9 or a compatible version supported by the dependencies.
- Git.
- A terminal and code editor.
- Internet connectivity for downloading AI models on first use.

### 1. Clone the Repository

Replace the placeholder with your GitHub repository URL.

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
```

### 2. Create and Activate a Virtual Environment

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Backend Dependencies

From the project root:

```bash
pip install -r backend/requirements.txt
```

### 4. Apply Database Migrations

```bash
cd backend
alembic upgrade head
```

This creates the database schema using the committed Alembic migration history.

### 5. Start the FastAPI Backend

Keep the terminal in the `backend/` directory:

```bash
uvicorn app.main:app --reload
```

The API should be available at:

- **API:** http://127.0.0.1:8000
- **Health check:** http://127.0.0.1:8000/health
- **Interactive API documentation:** http://127.0.0.1:8000/docs

The first startup may take longer while the AI models are loaded or downloaded.

### 6. Start the Streamlit Frontend

Open a second terminal and return to the repository root:

```bash
cd YOUR_REPOSITORY
source .venv/bin/activate
streamlit run frontend/app.py
```

Streamlit will display the local frontend URL, usually:

http://localhost:8501

Keep both the backend and frontend running while using the application.

---

## 🔌 API Overview

The FastAPI application exposes endpoints for the submission workflow.

| Endpoint | Purpose |
|---|---|
| `GET /health` | Check whether the API is running. |
| `POST /api/v1/submissions` | Submit a citizen problem. |
| `GET /api/v1/submissions/{submission_id}` | Retrieve a submission and its processing status. |
| `GET /api/v1/submissions/dossiers` | Retrieve grouped dossier summaries, where available in the current backend. |

Open `/docs` on the running backend to inspect the actual endpoint schemas and available operations.

### Example: Citizen Submission

A typical report includes problem text and location context:

```json
{
  "text": "Our village school does not have access to safe drinking water.",
  "district": "Example District",
  "village": "Example Village",
  "pincode": "000000",
  "google_maps_link": ""
}
```

Replace the example location values with valid information for your test. The accepted fields are determined by the current Pydantic submission schema.

---

## 🔄 AI Processing Workflow

The intended processing flow is:

```text
Citizen Submission
        │
        ▼
Persist Raw Submission
        │
        ▼
Background AI Processing
        │
        ▼
Domain / Subdomain Classification
        │
        ▼
MiniLM Embedding Generation
        │
        ▼
FAISS Similarity Search
        │
        ▼
Dossier Matching or Creation
        │
        ▼
Priority and Anomaly Analysis
        │
        ▼
Government Review
```

Background processing allows the API to acknowledge a new submission before the heavier analysis finishes.

The prototype uses a separate database session for background work. The database remains the source of truth for application records; FAISS acts as the vector search layer.

---

## 🔐 Security and Data Handling

This repository is a local development and hackathon prototype, not a production-ready government deployment.

Before production use, the application should be hardened with:
- Enforced authentication and role-based access control.
- Secure handling of personal information and uploaded evidence.
- Validated file uploads and controlled media access.
- Production database configuration, backups, and recovery.
- More robust job execution and failure recovery.
- Monitoring, logging, and auditable administrative actions.
- Validation of AI classifications, anomaly alerts, and similarity thresholds.

Never commit API keys, passwords, private citizen evidence, local databases, or environment-specific credentials.

---

## 🧭 Current Scope and Future Development

The project is designed as an extensible platform that can grow beyond basic complaint intake.

Further development can strengthen:
- Dynamic dossier-level priority and community evidence.
- Geographic validation and anomaly detection.
- Contextual reuse/adaptation of proven interventions.
- University capability matching and proposal comparison.
- Project milestones, funding, and collaboration workflows.
- Ground-truth evidence scoring and verified innovation memory.
- Authentication, deployment, and production operations.

AI scores and recommendations should be validated against representative cases before they are used for consequential decisions.

---

## 👥 Team

**Team Name:** Rogers
**Smart India Hackathon Problem Statement:** SIH26043
**Project:** AI-Assisted Societal Innovation & Decision Platform

---

## 📄 Disclaimer

This project is developed as a Smart India Hackathon prototype. AI-generated classifications, similarity matches, priority assessments, and intervention recommendations are decision-support outputs and should not replace authorized human review or independent evidence verification.
