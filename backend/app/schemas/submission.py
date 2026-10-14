from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class SubmissionBase(BaseModel):
    text: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    district: Optional[str] = None
    village: Optional[str] = None
    pincode: Optional[str] = None
    domain: Optional[str] = None
    classification_score: Optional[float] = None
    subdomain: Optional[str] = None
    subdomain_score: Optional[float] = None
    priority: Optional[str] = None
    embedding_model: Optional[str] = None
    embedding_dimension: Optional[int] = None

class SubmissionCreate(SubmissionBase):
    pass

class SubmissionResponse(SubmissionBase):
    id: int
    processing_status: str
    created_at: datetime
    dossier_id: Optional[str] = None

    class Config:
        from_attributes = True

class AnomalyData(BaseModel):
    is_anomaly: bool
    reports_24h: int = 0
    baseline_24h: int = 0
    spike_multiplier: float = 0.0
    temporal_signal: str = "NORMAL"
    geographic_concentration: str = "NORMAL"

class DossierSummary(BaseModel):
    dossier_id: str
    title: str
    domain: str
    subdomain: str
    priority: str
    report_count: int
    district: str
    pincode: str
    latest_report: datetime
    status: str
    anomaly: Optional[AnomalyData] = None

    class Config:
        from_attributes = True

class ReportSummary(BaseModel):
    id: int
    text: str
    created_at: datetime

    class Config:
        from_attributes = True

class ContextualRecommendation(BaseModel):
    decision: str
    reference_project: Optional[str] = None
    reason: str
    match_score: int

class DossierDetail(DossierSummary):
    reports: List[ReportSummary]
    contextual_intervention: Optional[ContextualRecommendation] = None