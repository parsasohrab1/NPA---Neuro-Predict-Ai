"""
Data Producers for Real-time Streaming
تولیدکنندگان داده برای streaming
"""
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio
import logging

from .realtime_service import realtime_service, StreamType

logger = logging.getLogger(__name__)


class PredictionStreamProducer:
    """Producer for AI prediction results"""
    
    @staticmethod
    async def stream_prediction_result(
        prediction_id: int,
        patient_id: int,
        result: Dict[str, Any]
    ) -> None:
        """
        Stream prediction result
        
        Args:
            prediction_id: Prediction identifier
            patient_id: Patient identifier
            result: Prediction result data
        """
        channel_id = f"predictions:{patient_id}"
        
        # Ensure channel exists
        if channel_id not in realtime_service.channels:
            realtime_service.create_channel(channel_id, StreamType.PREDICTIONS)
        
        message = {
            "prediction_id": prediction_id,
            "patient_id": patient_id,
            "result": result,
            "status": "completed"
        }
        
        await realtime_service.broadcast(channel_id, message)
        logger.info(f"Streamed prediction result for patient {patient_id}")


class MonitoringStreamProducer:
    """Producer for system monitoring data"""
    
    @staticmethod
    async def stream_system_metrics(metrics: Dict[str, Any]) -> None:
        """
        Stream system metrics
        
        Args:
            metrics: System metrics data
        """
        channel_id = "monitoring:system"
        
        if channel_id not in realtime_service.channels:
            realtime_service.create_channel(channel_id, StreamType.SYSTEM_METRICS)
        
        message = {
            "type": "system_metrics",
            "metrics": metrics
        }
        
        await realtime_service.broadcast(channel_id, message)
    
    @staticmethod
    async def stream_ai_ml_health(health_data: Dict[str, Any]) -> None:
        """
        Stream AI/ML health metrics
        
        Args:
            health_data: AI/ML health data
        """
        channel_id = "monitoring:ai_ml"
        
        if channel_id not in realtime_service.channels:
            realtime_service.create_channel(channel_id, StreamType.AI_ML_HEALTH)
        
        message = {
            "type": "ai_ml_health",
            "data": health_data
        }
        
        await realtime_service.broadcast(channel_id, message)


class ClinicalAlertProducer:
    """Producer for clinical alerts"""
    
    @staticmethod
    async def stream_alert(
        alert_type: str,
        severity: str,
        patient_id: Optional[int],
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Stream clinical alert
        
        Args:
            alert_type: Type of alert
            severity: Alert severity (low, medium, high, critical)
            patient_id: Patient identifier (optional)
            message: Alert message
            data: Additional alert data
        """
        if patient_id:
            channel_id = f"alerts:patient:{patient_id}"
        else:
            channel_id = "alerts:global"
        
        if channel_id not in realtime_service.channels:
            realtime_service.create_channel(channel_id, StreamType.CLINICAL_ALERTS)
        
        alert_message = {
            "type": "clinical_alert",
            "alert_type": alert_type,
            "severity": severity,
            "patient_id": patient_id,
            "message": message,
            "data": data or {}
        }
        
        await realtime_service.broadcast(channel_id, alert_message)
        logger.info(f"Streamed clinical alert: {alert_type} - {severity}")


class DeviceDataProducer:
    """Producer for device data"""
    
    @staticmethod
    async def stream_device_data(
        device_id: str,
        data: Dict[str, Any]
    ) -> None:
        """
        Stream device data
        
        Args:
            device_id: Device identifier
            data: Device data
        """
        channel_id = f"devices:{device_id}"
        
        if channel_id not in realtime_service.channels:
            realtime_service.create_channel(channel_id, StreamType.DEVICE_DATA)
        
        message = {
            "device_id": device_id,
            "data": data
        }
        
        await realtime_service.broadcast(channel_id, message)


# Background task for periodic monitoring
async def start_monitoring_stream(interval: float = 5.0):
    """
    Start periodic monitoring stream
    
    Args:
        interval: Stream interval in seconds
    """
    while True:
        try:
            # This would fetch actual metrics in production
            # For now, we'll use mock data
            metrics = {
                "cpu_usage": 45.2,
                "memory_usage": 62.5,
                "disk_usage": 38.1,
                "network_io": {
                    "bytes_sent": 1024000,
                    "bytes_recv": 2048000
                }
            }
            
            await MonitoringStreamProducer.stream_system_metrics(metrics)
            await asyncio.sleep(interval)
        
        except Exception as e:
            logger.error(f"Error in monitoring stream: {e}")
            await asyncio.sleep(interval)

