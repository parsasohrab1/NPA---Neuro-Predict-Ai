"""
Longitudinal Tracking Schemas
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from ..models.longitudinal import (
    LongitudinalEpisodeStatus,
    LongitudinalVisitType,
    MetricCategory,
    AlertSeverity,
    AlertType,
)


class LongitudinalEpisodeCreate(BaseModel):
    title: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class LongitudinalEpisodeSummary(BaseModel):
    id: int
    patient_id: int
    title: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    status: LongitudinalEpisodeStatus
    visit_count: int

    class Config:
        from_attributes = True


class LongitudinalVisitCreate(BaseModel):
    medical_record_id: Optional[int] = None
    imaging_study_id: Optional[int] = None
    prediction_id: Optional[int] = None
    visit_date: Optional[datetime] = None
    visit_type: LongitudinalVisitType = LongitudinalVisitType.FOLLOWUP
    notes: Optional[str] = None
    progression_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class LongitudinalMetricCreate(BaseModel):
    metric_type: MetricCategory
    metric_key: str
    metric_value: Optional[float] = None
    metric_payload: Optional[dict] = None
    unit: Optional[str] = None
    z_score: Optional[float] = None


class LongitudinalMetricResponse(BaseModel):
    id: int
    metric_type: MetricCategory
    metric_key: str
    metric_value: Optional[float]
    metric_payload: Optional[dict]
    unit: Optional[str]
    z_score: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class LongitudinalVisitResponse(BaseModel):
    id: int
    episode_id: int
    visit_date: datetime
    visit_type: LongitudinalVisitType
    notes: Optional[str]
    progression_score: Optional[float]
    medical_record_id: Optional[int]
    imaging_study_id: Optional[int]
    prediction_id: Optional[int]
    metrics: List[LongitudinalMetricResponse]

    class Config:
        from_attributes = True


class LongitudinalEpisodeDetail(BaseModel):
    id: int
    patient_id: int
    title: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    status: LongitudinalEpisodeStatus
    visits: List[LongitudinalVisitResponse]

    class Config:
        from_attributes = True


class TimelineEvent(BaseModel):
    visit_id: int
    visit_date: datetime
    visit_type: LongitudinalVisitType
    label: str
    metrics: List[LongitudinalMetricResponse]
    progression_score: Optional[float]
    imaging_available: bool


class TrendPoint(BaseModel):
    visit_id: int
    visit_date: datetime
    metric_value: Optional[float]
    z_score: Optional[float]


class ImagingComparisonResponse(BaseModel):
    episode_id: int
    visit_a_id: int
    visit_b_id: int
    visit_a_date: datetime
    visit_b_date: datetime
    mean_absolute_difference: float
    max_absolute_difference: float
    heatmap: str
    metadata: dict


class LongitudinalAlertResponse(BaseModel):
    id: int
    episode_id: int
    visit_id: Optional[int]
    metric_key: Optional[str]
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    created_at: datetime
    acknowledged_at: Optional[datetime]

    class Config:
        from_attributes = True


class ProgressionMetricSummary(BaseModel):
    slope: Optional[float]
    latest_value: Optional[float]
    latest_recorded_at: Optional[datetime]


class LongitudinalProgressionSummary(BaseModel):
    metrics: dict[str, ProgressionMetricSummary]



class ImagingComparisonResponse(BaseModel):
    episode_id: int
    visit_a_id: int
    visit_b_id: int
    overlay_image_a: str
    overlay_image_b: str
    diff_heatmap: str
    diff_mask: str
    metadata_a: Optional[dict] = None
    metadata_b: Optional[dict] = None


