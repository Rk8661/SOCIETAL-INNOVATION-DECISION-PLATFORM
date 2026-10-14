from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from collections import defaultdict
from typing import List
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.core.database import get_db
from app.models.submission import Submission
from app.schemas.submission import SubmissionCreate, SubmissionResponse, DossierSummary, DossierDetail
from app.services.ai.pipeline import process_submission_background

router = APIRouter()

def calculate_anomaly(subs) -> dict:
    """Calculates temporal spikes and geographic concentration."""
    if not subs:
        return {"is_anomaly": False}

    now = datetime.utcnow()
    last_24h = [s for s in subs if now - s.created_at <= timedelta(hours=24)]
    older_than_24h = [s for s in subs if now - s.created_at > timedelta(hours=24)]

    # Hackathon fallback: If no older data exists, assume a normal baseline of 1-2 reports
    baseline_24h = len(older_than_24h) if older_than_24h else 1
    recent_count = len(last_24h)

    if recent_count == 0:
        return {
            "is_anomaly": False,
            "reports_24h": 0,
            "baseline_24h": baseline_24h,
            "spike_multiplier": 0.0
        }

    spike_multiplier = recent_count / baseline_24h

    # Anomaly Trigger: Sudden burst of 3+ reports with a 3x or greater spike
    if recent_count >= 3 and spike_multiplier >= 3.0:
        # Check geographic concentration using pincode
        unique_pincodes = len(set([s.pincode for s in last_24h if s.pincode]))
        geo_signal = "HIGH" if unique_pincodes == 1 else "MEDIUM"

        return {
            "is_anomaly": True,
            "reports_24h": recent_count,
            "baseline_24h": baseline_24h,
            "spike_multiplier": round(spike_multiplier, 1),
            "temporal_signal": "HIGH",
            "geographic_concentration": geo_signal
        }

    return {
        "is_anomaly": False,
        "reports_24h": recent_count,
        "baseline_24h": baseline_24h,
        "spike_multiplier": round(spike_multiplier, 1)
    }

def get_contextual_recommendation(domain: str) -> dict:
    """Simulates searching 'Innovation Memory' for past solutions."""
    domain_lower = str(domain).lower() if domain else ""

    if "water" in domain_lower:
        return {
            "decision": "ADAPT",
            "reference_project": "Low-Cost Gravity Iron Filter (Dumka Pilot)",
            "reason": "High problem similarity, but local terrain differences require adaptation.",
            "match_score": 87
        }
    elif "infrastructure" in domain_lower or "school" in domain_lower:
        return {
            "decision": "INVENT",
            "reference_project": None,
            "reason": "No sufficiently validated intervention exists in Innovation Memory for this structural failure.",
            "match_score": 12
        }
    else:
        return {
            "decision": "REUSE",
            "reference_project": "Standardized Civic Response Protocol v2",
            "reason": "High contextual compatibility. Solution is validated and ready for immediate deployment.",
            "match_score": 94
        }


class StatusUpdateRequest(BaseModel):
    status: str


@router.post("", response_model=SubmissionResponse)
def create_submission(
    submission_in: SubmissionCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    db_submission = Submission(**submission_in.model_dump())

    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)

    background_tasks.add_task(process_submission_background, db_submission.id)

    return db_submission


@router.get("/dossiers", response_model=List[DossierSummary])
def get_dossiers(db: Session = Depends(get_db)):
    submissions = db.query(Submission).filter(Submission.dossier_id.isnot(None)).all()

    dossiers_map = defaultdict(list)
    for sub in submissions:
        dossiers_map[sub.dossier_id].append(sub)

    result = []
    for d_id, subs in dossiers_map.items():
        subs.sort(key=lambda x: x.created_at, reverse=True)
        latest = subs[0]

        priorities = [s.priority for s in subs if s.priority]
        if "High" in priorities:
            agg_priority = "High"
        elif "Medium" in priorities:
            agg_priority = "Medium"
        else:
            agg_priority = "Low"

        subdomain_str = str(latest.subdomain) if latest.subdomain else "N/A"

        anomaly_data = calculate_anomaly(subs)

        result.append({
            "dossier_id": d_id,
            "title": f"{subdomain_str.title()} issue in {latest.village or latest.district or 'Unknown'}",
            "domain": latest.domain or "Uncategorized",
            "subdomain": subdomain_str,
            "priority": agg_priority,
            "report_count": len(subs),
            "district": latest.district or "Unknown",
            "pincode": latest.pincode or "Unknown",
            "latest_report": latest.created_at,
            "status": latest.processing_status,
            "anomaly": anomaly_data
        })

    priority_weight = {"High": 1, "Medium": 2, "Low": 3}
    result.sort(key=lambda x: (priority_weight.get(x["priority"], 4), x["latest_report"]), reverse=False)

    return result


@router.get("/dossiers/{dossier_id}", response_model=DossierDetail)
def get_dossier_detail(dossier_id: str, db: Session = Depends(get_db)):
    subs = db.query(Submission).filter(Submission.dossier_id == dossier_id).order_by(Submission.created_at.desc()).all()

    if not subs:
        raise HTTPException(status_code=404, detail="Dossier not found")

    latest = subs[0]
    priorities = [s.priority for s in subs if s.priority]

    if "High" in priorities:
        agg_priority = "High"
    elif "Medium" in priorities:
        agg_priority = "Medium"
    else:
        agg_priority = "Low"

    subdomain_str = str(latest.subdomain) if latest.subdomain else "N/A"

    anomaly_data = calculate_anomaly(subs)
    context_data = get_contextual_recommendation(latest.domain)

    return {
        "dossier_id": dossier_id,
        "title": f"{subdomain_str.title()} issue in {latest.village or latest.district or 'Unknown'}",
        "domain": latest.domain or "Uncategorized",
        "subdomain": subdomain_str,
        "priority": agg_priority,
        "report_count": len(subs),
        "district": latest.district or "Unknown",
        "pincode": latest.pincode or "Unknown",
        "latest_report": latest.created_at,
        "status": latest.processing_status,
        "anomaly": anomaly_data,
        "contextual_intervention": context_data,
        "reports": [{"id": s.id, "text": s.text, "created_at": s.created_at} for s in subs]
    }


@router.patch("/dossiers/{dossier_id}/status")
def update_dossier_status(
    dossier_id: str,
    status_update: StatusUpdateRequest,
    db: Session = Depends(get_db)
):
    subs = db.query(Submission).filter(Submission.dossier_id == dossier_id).all()
    if not subs:
        raise HTTPException(status_code=404, detail="Dossier not found")

    for sub in subs:
        sub.processing_status = status_update.status

    db.commit()
    return {"message": "Status updated successfully", "dossier_id": dossier_id, "new_status": status_update.status}


@router.get("/{submission_id}", response_model=SubmissionResponse)
def get_submission(
    submission_id: int,
    db: Session = Depends(get_db)
):
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    return submission