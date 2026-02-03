"""
Longitudinal Tracking API Endpoints
"""
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_db
from ..models.longitudinal import MetricCategory, LongitudinalReportScheduleStatus
from ..schemas.longitudinal import (
    LongitudinalEpisodeCreate,
    LongitudinalEpisodeDetail,
    LongitudinalEpisodeSummary,
    LongitudinalMetricCreate,
    LongitudinalVisitCreate,
    LongitudinalVisitResponse,
    ImagingComparisonResponse,
    TimelineEvent,
    TrendPoint,
    LongitudinalAlertResponse,
    LongitudinalProgressionSummary,
    ProgressionMetricSummary,
    LongitudinalReportCreate,
    LongitudinalReportResponse,
    ReportScheduleCreate,
    ReportScheduleResponse,
    ReportRunResponse,
    ReportScheduleUpdate,
)
from ..services.longitudinal_service import longitudinal_service

router = APIRouter(prefix="/longitudinal", tags=["Longitudinal Tracking"])


@router.get(
    "/{patient_id}/episodes",
    response_model=List[LongitudinalEpisodeSummary],
)
async def list_episodes(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
):
    episodes = await longitudinal_service.list_episodes(db, patient_id)
    summaries: List[LongitudinalEpisodeSummary] = []
    for episode in episodes:
        visit_count = await longitudinal_service.get_episode_visit_count(db, episode.id)
        summaries.append(
            LongitudinalEpisodeSummary(
                id=episode.id,
                patient_id=episode.patient_id,
                title=episode.title,
                start_date=episode.start_date,
                end_date=episode.end_date,
                status=episode.status,
                visit_count=visit_count,
            )
        )
    return summaries


@router.post(
    "/{patient_id}/episodes",
    response_model=LongitudinalEpisodeDetail,
    status_code=status.HTTP_201_CREATED,
)
async def create_episode(
    patient_id: int,
    payload: LongitudinalEpisodeCreate,
    db: AsyncSession = Depends(get_db),
):
    episode = await longitudinal_service.create_episode(db, patient_id, payload)
    detailed = await longitudinal_service.get_episode(db, episode.id, patient_id)
    if detailed is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Episode creation failed")
    return detailed


@router.get(
    "/episodes/{episode_id}",
    response_model=LongitudinalEpisodeDetail,
)
async def get_episode(
    episode_id: int,
    patient_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    episode = await longitudinal_service.get_episode(db, episode_id, patient_id)
    if episode is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Episode not found")
    return episode


@router.post(
    "/episodes/{episode_id}/visits",
    response_model=LongitudinalVisitResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_visit(
    episode_id: int,
    payload: LongitudinalVisitCreate,
    db: AsyncSession = Depends(get_db),
):
    visit = await longitudinal_service.add_visit(db, episode_id, payload)
    visit_with_metrics = await longitudinal_service.get_timeline(db, episode_id)
    for candidate in visit_with_metrics:
        if candidate.id == visit.id:
            return candidate
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Visit creation failed")


@router.post(
    "/visits/{visit_id}/metrics",
    response_model=List[TrendPoint],
    status_code=status.HTTP_201_CREATED,
)
async def add_metrics(
    visit_id: int,
    metrics: List[LongitudinalMetricCreate],
    episode_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    saved_metrics = await longitudinal_service.add_metrics(db, visit_id, metrics)
    if episode_id is None:
        if saved_metrics:
            episode_id = saved_metrics[0].visit.episode_id
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Episode id required")

    trend_points: List[TrendPoint] = []
    for metric in saved_metrics:
        trend_points.append(
            TrendPoint(
                visit_id=metric.visit_id,
                visit_date=metric.visit.visit_date,
                metric_value=metric.metric_value,
                z_score=metric.z_score,
            )
        )
    return trend_points


@router.get(
    "/episodes/{episode_id}/timeline",
    response_model=List[TimelineEvent],
)
async def get_timeline(
    episode_id: int,
    db: AsyncSession = Depends(get_db),
):
    visits = await longitudinal_service.get_timeline(db, episode_id)
    events: List[TimelineEvent] = []
    for visit in visits:
        label = f"{visit.visit_type.value.title()} visit"
        events.append(
            TimelineEvent(
                visit_id=visit.id,
                visit_date=visit.visit_date,
                visit_type=visit.visit_type,
                label=label,
                metrics=list(visit.metrics),
                progression_score=visit.progression_score,
                imaging_available=visit.imaging_study_id is not None,
            )
        )
    return events


@router.get(
    "/episodes/{episode_id}/trend",
    response_model=List[TrendPoint],
)
async def get_trend(
    episode_id: int,
    metric_key: str = Query(..., min_length=1),
    metric_type: Optional[MetricCategory] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    metrics = await longitudinal_service.get_metric_trend(db, episode_id, metric_key, metric_type)
    points: List[TrendPoint] = []
    for metric in metrics:
        points.append(
            TrendPoint(
                visit_id=metric.visit_id,
                visit_date=metric.visit.visit_date,
                metric_value=metric.metric_value,
                z_score=metric.z_score,
            )
        )
    return points


@router.get(
    "/episodes/{episode_id}/comparison",
    response_model=ImagingComparisonResponse,
)
async def compare_imaging(
    episode_id: int,
    visit_a: int = Query(..., description="Visit id for baseline"),
    visit_b: int = Query(..., description="Visit id for comparison"),
    db: AsyncSession = Depends(get_db),
):
    if visit_a == visit_b:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Visits must be different")
    try:
        result = await longitudinal_service.compare_imaging(db, episode_id, visit_a, visit_b)
        return result
    except ValueError as exc:
        detail_map = {
            "visit_not_found": ("Visit not found", status.HTTP_404_NOT_FOUND),
            "episode_mismatch": ("Visits do not belong to the specified episode.", status.HTTP_400_BAD_REQUEST),
            "imaging_not_available": ("Imaging data is not available for one of the visits.", status.HTTP_400_BAD_REQUEST),
        }
        message = str(exc)
        detail, code = detail_map.get(message, ("Comparison failed", status.HTTP_500_INTERNAL_SERVER_ERROR))
        raise HTTPException(status_code=code, detail=detail) from exc


@router.get(
    "/episodes/{episode_id}/alerts",
    response_model=List[LongitudinalAlertResponse],
)
async def get_alerts(
    episode_id: int,
    db: AsyncSession = Depends(get_db),
) -> List[LongitudinalAlertResponse]:
    alerts = await longitudinal_service.get_alerts(db, episode_id)
    return alerts


@router.post(
    "/alerts/{alert_id}/acknowledge",
    response_model=LongitudinalAlertResponse,
)
async def acknowledge_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
) -> LongitudinalAlertResponse:
    alert = await longitudinal_service.acknowledge_alert(db, alert_id)
    if alert is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    return alert


@router.get(
    "/episodes/{episode_id}/progression",
    response_model=LongitudinalProgressionSummary,
)
async def get_progression(
    episode_id: int,
    db: AsyncSession = Depends(get_db),
) -> LongitudinalProgressionSummary:
    summary = await longitudinal_service.get_progression_summary(db, episode_id)
    metrics_payload = {
        key: ProgressionMetricSummary(
            slope=value["slope"],
            latest_value=value["latest_value"],
            latest_recorded_at=value["latest_recorded_at"],
        )
        for key, value in summary.items()
    }
    return LongitudinalProgressionSummary(metrics=metrics_payload)


@router.post(
    "/episodes/{episode_id}/reports",
    response_model=LongitudinalReportResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_report(
    episode_id: int,
    payload: LongitudinalReportCreate,
    db: AsyncSession = Depends(get_db),
) -> LongitudinalReportResponse:
    try:
        report = await longitudinal_service.create_report(
            db=db,
            episode_id=episode_id,
            created_by=None,  # Fixed: removed undefined current_user reference
            start_date=payload.start_date,
            end_date=payload.end_date,
            report_format=payload.format,
        )
        return report
    except ValueError as exc:
        message = str(exc)
        if message == "no_data":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No data available for this episode.") from exc
        if message == "no_data_in_range":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No visits in selected date range.") from exc
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Report generation failed.") from exc


@router.get(
    "/episodes/{episode_id}/reports",
    response_model=List[LongitudinalReportResponse],
)
async def list_reports(
    episode_id: int,
    db: AsyncSession = Depends(get_db),
) -> List[LongitudinalReportResponse]:
    reports = await longitudinal_service.list_reports(db, episode_id)
    return reports


@router.get(
    "/reports/{report_id}/download",
    response_class=FileResponse,
)
async def download_report(
    report_id: int,
    variant: Optional[str] = Query(None, regex="^(pdf|excel)$"),
    db: AsyncSession = Depends(get_db),
):
    report = await longitudinal_service.get_report(db, report_id)
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    if variant == "pdf":
        if not report.pdf_path:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PDF variant not available")
        file_path = Path(report.pdf_path)
        media_type = "application/pdf"
    else:
        file_path = Path(report.file_path)
        if report.format == report.format.PDF and variant != "pdf":
            media_type = "application/pdf"
        else:
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report file missing")

    return FileResponse(path=file_path, media_type=media_type, filename=file_path.name)


@router.get(
    "/reports/{report_id}/heatmap",
    response_class=FileResponse,
)
async def get_report_heatmap(
    report_id: int,
    db: AsyncSession = Depends(get_db),
):
    report = await longitudinal_service.get_report(db, report_id)
    if report is None or not report.heatmap_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Heatmap not available")
    heatmap_path = Path(report.heatmap_path)
    if not heatmap_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Heatmap file missing")
    return FileResponse(path=heatmap_path, media_type="image/png", filename=heatmap_path.name)


@router.get(
    "/reports/{report_id}/heatmap/summary",
)
async def get_report_heatmap_summary(
    report_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Return metadata for the report heatmap (metrics, time buckets, file path).
    Useful for UI overlays and legends without downloading the PNG.
    """
    report = await longitudinal_service.get_report(db, report_id)
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    if not report.charts_payload:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Heatmap summary unavailable")
    metrics = [k for k in report.charts_payload.keys()]
    time_set = set()
    for rows in report.charts_payload.values():
        for row in rows or []:
            ts = row.get("visit_date")
            if ts:
                time_set.add(ts)
    time_buckets = sorted(time_set)
    return {
        "report_id": report.id,
        "episode_id": report.episode_id,
        "report_type": report.report_type,
        "metrics": metrics,
        "time_buckets": time_buckets,
        "heatmap_path": report.heatmap_path,
    }

@router.post(
    "/reports/schedules",
    response_model=ReportScheduleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_report_schedule(
    payload: ReportScheduleCreate,
    db: AsyncSession = Depends(get_db),
) -> ReportScheduleResponse:
    schedule = await longitudinal_service.create_schedule(db, payload, None)  # Fixed: removed undefined current_user reference
    return schedule


@router.get(
    "/reports/schedules",
    response_model=List[ReportScheduleResponse],
)
async def list_report_schedules(
    db: AsyncSession = Depends(get_db),
) -> List[ReportScheduleResponse]:
    schedules = await longitudinal_service.list_schedules(db)
    return schedules


@router.patch(
    "/reports/schedules/{schedule_id}",
    response_model=ReportScheduleResponse,
)
async def update_report_schedule(
    schedule_id: int,
    payload: ReportScheduleUpdate,
    db: AsyncSession = Depends(get_db),
) -> ReportScheduleResponse:
    schedule = await longitudinal_service.update_schedule_status(
        db,
        schedule_id,
        payload.status,
    )
    if schedule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")
    return schedule


@router.delete(
    "/reports/schedules/{schedule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_report_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    deleted = await longitudinal_service.delete_schedule(db, schedule_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")


@router.post(
    "/reports/schedules/{schedule_id}/runs",
    response_model=ReportRunResponse,
    status_code=status.HTTP_201_CREATED,
)
async def enqueue_schedule_run(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
) -> ReportRunResponse:
    run = await longitudinal_service.enqueue_schedule_run(db, schedule_id)
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")
    return run


@router.get(
    "/reports/schedules/{schedule_id}/runs",
    response_model=List[ReportRunResponse],
)
async def list_schedule_runs(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
) -> List[ReportRunResponse]:
    runs = await longitudinal_service.list_schedule_runs(db, schedule_id)
    return runs


@router.post(
    "/reports/runs/{run_id}/execute",
    response_model=ReportRunResponse,
)
async def execute_schedule_run(
    run_id: int,
    db: AsyncSession = Depends(get_db),
) -> ReportRunResponse:
    run = await longitudinal_service.execute_schedule_run(db, run_id)
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    return run


@router.get(
    "/episodes/{episode_id}/baseline",
)
async def get_personal_baseline(
    episode_id: int,
    metric_key: str = Query(..., min_length=1),
    baseline_window_days: int = Query(90, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    """Get personal baseline for a metric"""
    baseline = await longitudinal_service.calculate_personal_baseline(
        db, episode_id, metric_key, baseline_window_days
    )
    return baseline


@router.get(
    "/episodes/{episode_id}/prediction",
)
async def get_future_prediction(
    episode_id: int,
    metric_key: str = Query(..., min_length=1),
    days_ahead: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    """Predict future metric value"""
    prediction = await longitudinal_service.predict_future_progression(
        db, episode_id, metric_key, days_ahead
    )
    return prediction


@router.get(
    "/episodes/{episode_id}/combined-alerts",
)
async def get_combined_alerts(
    episode_id: int,
    metric_keys: Optional[str] = Query(None, description="Comma-separated metric keys"),
    db: AsyncSession = Depends(get_db),
):
    """Get combined alerts based on multiple metrics"""
    keys_list = None
    if metric_keys:
        keys_list = [k.strip() for k in metric_keys.split(',') if k.strip()]
    alerts = await longitudinal_service.evaluate_combined_alerts(db, episode_id, keys_list)
    return {"alerts": alerts}


@router.get(
    "/reports/schedules/{schedule_id}/monitoring",
)
async def get_schedule_monitoring(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get monitoring statistics for a report schedule"""
    stats = await longitudinal_service.get_schedule_monitoring_stats(db, schedule_id)
    return stats


@router.post(
    "/load-sample-data",
    status_code=status.HTTP_201_CREATED,
    summary="Load sample longitudinal data for testing",
)
async def load_sample_data(
    db: AsyncSession = Depends(get_db),
):  # Fixed: scalar_one_or_none -> scalar
    """
    Load sample episodes, visits, and metrics for longitudinal tracking testing.
    Creates data for existing patients in the database.
    """
    from sqlalchemy import select
    from ..models.patient import Patient
    from ..models.longitudinal import (
        LongitudinalEpisode,
        LongitudinalVisit,
        LongitudinalMetric,
        LongitudinalEpisodeStatus,
        LongitudinalVisitType,
        MetricCategory,
    )
    from datetime import datetime, timedelta
    import random
    
    # Get all patients
    result = await db.execute(select(Patient).limit(10))
    patients = result.scalars().all()
    
    if not patients:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patients found. Please create patients first."
        )
    
    total_episodes = 0
    total_visits = 0
    total_metrics = 0
    
    for patient in patients:
        # Check if patient already has episodes
        existing_result = await db.execute(
            select(LongitudinalEpisode).where(LongitudinalEpisode.patient_id == patient.id)
        )
        if existing_result.scalar():
            continue
        
        # Create 1-2 episodes per patient
        num_episodes = random.randint(1, 2)
        
        for ep_idx in range(num_episodes):
            start_date = datetime.now() - timedelta(days=random.randint(180, 365))
            
            episode = LongitudinalEpisode(
                patient_id=patient.id,
                title=f"Episode {ep_idx + 1} - Cognitive Monitoring",
                start_date=start_date,
                status=LongitudinalEpisodeStatus.ACTIVE if ep_idx == 0 else LongitudinalEpisodeStatus.COMPLETED,
            )
            
            db.add(episode)
            await db.flush()
            total_episodes += 1
            
            # Create 4-8 visits per episode
            num_visits = random.randint(4, 8)
            
            for visit_idx in range(num_visits):
                days_from_start = (visit_idx + 1) * random.randint(20, 40)
                visit_date = start_date + timedelta(days=days_from_start)
                
                visit_type = (
                    LongitudinalVisitType.BASELINE if visit_idx == 0
                    else random.choice([
                        LongitudinalVisitType.FOLLOWUP,
                        LongitudinalVisitType.IMAGING,
                        LongitudinalVisitType.LAB,
                        LongitudinalVisitType.THERAPY,
                    ])
                )
                
                # Calculate progression score (slightly declining over time)
                base_score = 0.9
                decline_rate = 0.02 * visit_idx
                noise = random.uniform(-0.05, 0.05)
                progression_score = max(0.5, base_score - decline_rate + noise)
                
                visit = LongitudinalVisit(
                    episode_id=episode.id,
                    visit_date=visit_date,
                    visit_type=visit_type,
                    progression_score=progression_score,
                    notes=f"Visit {visit_idx + 1} - {visit_type.value.capitalize()} assessment",
                )
                
                db.add(visit)
                await db.flush()
                total_visits += 1
                
                # Create metrics for each visit
                # Cognitive metrics
                cognitive_metrics = [
                    ("mmse_score", random.uniform(20, 30), "points", MetricCategory.COGNITIVE),
                    ("moca_score", random.uniform(18, 28), "points", MetricCategory.COGNITIVE),
                    ("memory_recall", random.uniform(0.6, 1.0), "ratio", MetricCategory.COGNITIVE),
                    ("attention_span", random.uniform(0.5, 1.0), "ratio", MetricCategory.COGNITIVE),
                ]
                
                # Biomarker metrics
                biomarker_metrics = [
                    ("amyloid_beta", random.uniform(300, 600), "pg/mL", MetricCategory.BIOMARKER),
                    ("tau_protein", random.uniform(200, 400), "pg/mL", MetricCategory.BIOMARKER),
                    ("dopamine_level", random.uniform(50, 100), "ng/mL", MetricCategory.BIOMARKER),
                ]
                
                # Imaging metrics
                imaging_metrics = [
                    ("hippocampal_volume", random.uniform(2500, 4000), "mm³", MetricCategory.IMAGING),
                    ("cortical_thickness", random.uniform(2.0, 3.5), "mm", MetricCategory.IMAGING),
                    ("ventricular_volume", random.uniform(30000, 50000), "mm³", MetricCategory.IMAGING),
                ]
                
                # Functional metrics
                functional_metrics = [
                    ("daily_activities_score", random.uniform(0.6, 1.0), "ratio", MetricCategory.FUNCTIONAL),
                    ("mobility_score", random.uniform(0.5, 1.0), "ratio", MetricCategory.FUNCTIONAL),
                ]
                
                all_metrics = cognitive_metrics + biomarker_metrics + imaging_metrics + functional_metrics
                
                for metric_key, metric_value, unit, category in all_metrics:
                    # Add some temporal variation (slight decline over visits)
                    temporal_factor = 1 - (visit_idx * 0.01)
                    adjusted_value = metric_value * temporal_factor
                    
                    # Calculate z-score (simplified)
                    z_score = (adjusted_value - metric_value) / (metric_value * 0.1)
                    
                    metric = LongitudinalMetric(
                        visit_id=visit.id,
                        metric_type=category,
                        metric_key=metric_key,
                        metric_value=adjusted_value,
                        unit=unit,
                        z_score=z_score,
                    )
                    
                    db.add(metric)
                    total_metrics += 1
    
    await db.commit()
    
    return {
        "message": "Sample longitudinal data loaded successfully",
        "total_patients": len(patients),
        "total_episodes": total_episodes,
        "total_visits": total_visits,
        "total_metrics": total_metrics,
    }



