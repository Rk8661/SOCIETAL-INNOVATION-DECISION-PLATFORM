import os
# Prevent Apple Silicon Mac crashes in background threads
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"

import logging
import re
import uuid
from sqlalchemy.orm import Session
from transformers import pipeline
from sentence_transformers import SentenceTransformer

from app.core.database import SessionLocal
from app.models.submission import Submission, ProcessingStatus
from app.services.ai.matcher import search_similar_submissions, add_single_vector_to_index

logger = logging.getLogger(__name__)

logger.info("Loading Zero-Shot AI Model (valhalla/distilbart-mnli-12-3)...")
classifier = pipeline(
    "zero-shot-classification",
    model="valhalla/distilbart-mnli-12-3"
)

logger.info("Loading Embedding Model (all-MiniLM-L6-v2)...")
embedder = SentenceTransformer("all-MiniLM-L6-v2")
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384

DOMAIN_LABELS = [
    "schools and education", "hospitals and healthcare", "farming and agriculture",
    "water supply and sanitation", "environment and pollution", "electricity and power",
    "employment and microfinance", "roads and transport infrastructure",
    "disability accessibility", "civic administration", "urban planning",
]

SUBDOMAIN_MAP = {
    "schools and education": ["school building repair", "teacher shortage", "digital learning", "mid-day meals"],
    "hospitals and healthcare": ["primary health centers", "medicine shortage", "maternal health", "ambulance services"],
    "farming and agriculture": ["irrigation and water", "crop disease", "market access", "fertilizer supply"],
    "water supply and sanitation": ["drinking water shortage", "drainage and sewage", "public toilets", "waste management"],
    "environment and pollution": ["air pollution", "deforestation", "wildlife conservation"],
    "electricity and power": ["power outages", "solar power", "street lighting", "tariff issues"],
    "employment and microfinance": ["skill development", "microfinance", "employment schemes", "handicrafts"],
    "roads and transport infrastructure": ["road potholes", "bridge repairs", "public transport", "broadband connectivity"],
    "disability accessibility": ["wheelchair access", "sign language resources", "disability pensions", "inclusive education"],
    "civic administration": ["corruption", "document issuance", "grievance redressal", "welfare distribution"],
    "urban planning": ["traffic management", "slum rehabilitation", "zoning violations", "public parks"],
}

def contains_keyword(text: str, keywords: list[str]) -> bool:
    """Checks for whole-word keyword matches to avoid accidental substring matches."""
    text_lower = text.lower()
    return any(
        re.search(rf"\b{re.escape(keyword)}\b", text_lower)
        for keyword in keywords
    )

def calculate_priority(subdomain: str, text: str) -> str:
    """Calculates preliminary submission priority using deterministic heuristic logic."""
    subdomain_lower = subdomain.lower().strip()

    # 1. Severe emergency signals
    emergency_keywords = [
        "death", "casualty", "fatal", "collapse", "collapsed",
        "emergency", "life threatening", "major accident",
        "bridge collapse", "building collapse",
    ]
    if contains_keyword(text, emergency_keywords):
        return "High"

    # 2. Serious health / safety signals
    serious_keywords = [
        "disease outbreak", "contaminated", "poisoned",
        "mass illness", "severe shortage", "no drinking water",
        "hospital emergency", "ambulance unavailable", "no essential medicines"
    ]
    urgency_signal = contains_keyword(text, serious_keywords)

    # 3. Critical subdomains
    high_priority_subdomains = {
        "drinking water shortage", "primary health centers", "medicine shortage",
        "power outages", "bridge repairs", "maternal health", "ambulance services",
    }
    critical_subdomain = subdomain_lower in {item.lower() for item in high_priority_subdomains}

    if urgency_signal and critical_subdomain:
        return "High"
    if urgency_signal or critical_subdomain:
        return "Medium"

    # 4. Standard civic issues
    medium_priority_subdomains = {
        "school building repair", "irrigation and water", "road potholes",
        "drainage and sewage", "waste management", "teacher shortage",
        "public transport", "street lighting"
    }
    if subdomain_lower in {item.lower() for item in medium_priority_subdomains}:
        return "Medium"

    # 5. Default
    return "Low"

def process_submission_background(submission_id: int):
    """Background worker executing the domain cascade, priority heuristics, and vector embeddings."""
    db: Session = SessionLocal()

    try:
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        if not submission:
            return

        # 1. State: PROCESSING
        submission.processing_status = ProcessingStatus.PROCESSING
        db.commit()

        # 2a. RUN DOMAIN INFERENCE
        domain_result = classifier(submission.text, DOMAIN_LABELS)
        top_domain = domain_result["labels"][0]
        submission.domain = top_domain
        submission.classification_score = float(domain_result["scores"][0])

        # 2b. RUN DYNAMIC SUBDOMAIN INFERENCE
        candidate_subdomains = SUBDOMAIN_MAP.get(top_domain)
        if candidate_subdomains:
            sub_result = classifier(submission.text, candidate_subdomains)
            submission.subdomain = sub_result["labels"][0]
            submission.subdomain_score = float(sub_result["scores"][0])

        # 2c. RUN PRIORITY CALCULATION
        calculated_priority = calculate_priority(
            subdomain=submission.subdomain or "",
            text=submission.text
        )
        submission.priority = calculated_priority

        # 2d. GENERATE VECTOR EMBEDDING
        raw_embedding = embedder.encode(submission.text, normalize_embeddings=True)
        submission.embedding = raw_embedding.tolist()
        submission.embedding_model = EMBEDDING_MODEL_NAME
        submission.embedding_dimension = EMBEDDING_DIMENSION

        # 2e. FAISS DOSSIER MATCHING
        matched_id = search_similar_submissions(submission.embedding, threshold=0.85)

        if matched_id:
            existing_sub = db.query(Submission).filter(Submission.id == matched_id).first()
            submission.dossier_id = existing_sub.dossier_id if existing_sub.dossier_id else f"DOS-{uuid.uuid4().hex[:8].upper()}"
        else:
            submission.dossier_id = f"DOS-{uuid.uuid4().hex[:8].upper()}"

        # 3. Save AI results and transition state
        submission.processing_status = ProcessingStatus.READY_FOR_REVIEW
        db.commit()

        # 4. Add the new vector to the live FAISS index
        add_single_vector_to_index(submission.id, submission.embedding)

    except Exception as e:
        logger.error(f"Pipeline failed for submission {submission_id}: {e}")
        db.rollback()
    finally:
        db.close()