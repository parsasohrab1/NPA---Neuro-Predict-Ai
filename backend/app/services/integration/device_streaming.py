"""
Medical Device Real-time Data Streaming
سرویس برای دریافت داده‌های real-time از دستگاه‌های پزشکی
"""
from typing import Optional, Callable, Dict, Any, List
from datetime import datetime
import asyncio
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class DeviceType(Enum):
    """Types of medical devices"""
    VITAL_SIGNS_MONITOR = "vital_signs_monitor"
    LAB_ANALYZER = "lab_analyzer"
    IMAGING_DEVICE = "imaging_device"
    RESPIRATORY_DEVICE = "respiratory_device"
    CARDIAC_MONITOR = "cardiac_monitor"


class DeviceStreamingService:
    """Service for real-time device data streaming"""
    
    def __init__(self):
        self.active_streams: Dict[str, Dict[str, Any]] = {}
        self.callbacks: Dict[str, List[Callable]] = {}
    
    async def start_stream(
        self,
        device_id: str,
        device_type: DeviceType,
        device_url: Optional[str] = None,
        interval: float = 1.0
    ) -> bool:
        """
        Start streaming data from device
        
        Args:
            device_id: Device identifier
            device_type: Type of device
            device_url: Device URL/endpoint
            interval: Streaming interval in seconds
        
        Returns:
            True if successful
        """
        if device_id in self.active_streams:
            logger.warning(f"Stream already active for device {device_id}")
            return False
        
        try:
            stream_info = {
                "device_id": device_id,
                "device_type": device_type,
                "device_url": device_url,
                "interval": interval,
                "active": True,
                "start_time": datetime.now(),
                "message_count": 0
            }
            
            self.active_streams[device_id] = stream_info
            
            # Start streaming task
            asyncio.create_task(self._stream_loop(device_id))
            
            logger.info(f"Started streaming from device {device_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error starting stream for device {device_id}: {e}")
            return False
    
    async def stop_stream(self, device_id: str) -> bool:
        """
        Stop streaming from device
        
        Args:
            device_id: Device identifier
        
        Returns:
            True if successful
        """
        if device_id not in self.active_streams:
            logger.warning(f"No active stream for device {device_id}")
            return False
        
        try:
            self.active_streams[device_id]["active"] = False
            del self.active_streams[device_id]
            
            logger.info(f"Stopped streaming from device {device_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error stopping stream for device {device_id}: {e}")
            return False
    
    async def _stream_loop(self, device_id: str) -> None:
        """Internal streaming loop"""
        stream_info = self.active_streams.get(device_id)
        if not stream_info:
            return
        
        device_type = stream_info["device_type"]
        interval = stream_info["interval"]
        
        while stream_info.get("active", False):
            try:
                # Simulate data retrieval from device
                # در production، اینجا باید actual device communication باشد
                data = await self._get_device_data(device_id, device_type)
                
                if data:
                    # Notify callbacks
                    await self._notify_callbacks(device_id, data)
                    stream_info["message_count"] += 1
                
                await asyncio.sleep(interval)
            
            except Exception as e:
                logger.error(f"Error in stream loop for device {device_id}: {e}")
                await asyncio.sleep(interval)
    
    async def _get_device_data(
        self,
        device_id: str,
        device_type: DeviceType
    ) -> Optional[Dict[str, Any]]:
        """
        Get data from device
        
        Args:
            device_id: Device identifier
            device_type: Type of device
        
        Returns:
            Device data dictionary
        """
        # در production، اینجا باید actual device communication باشد
        # برای حالا فقط mock data برمی‌گردانیم
        
        if device_type == DeviceType.VITAL_SIGNS_MONITOR:
            return {
                "device_id": device_id,
                "timestamp": datetime.now().isoformat(),
                "blood_pressure": {
                    "systolic": 120,
                    "diastolic": 80
                },
                "heart_rate": 72,
                "temperature": 98.6,
                "respiratory_rate": 16,
                "oxygen_saturation": 98
            }
        
        elif device_type == DeviceType.LAB_ANALYZER:
            return {
                "device_id": device_id,
                "timestamp": datetime.now().isoformat(),
                "test_code": "TEST001",
                "test_name": "Blood Test",
                "result_value": "120",
                "units": "mg/dL",
                "status": "F"
            }
        
        return None
    
    def register_callback(
        self,
        device_id: str,
        callback: Callable
    ) -> None:
        """
        Register callback for device data
        
        Args:
            device_id: Device identifier
            callback: Callback function
        """
        if device_id not in self.callbacks:
            self.callbacks[device_id] = []
        
        self.callbacks[device_id].append(callback)
        logger.info(f"Registered callback for device {device_id}")
    
    def unregister_callback(
        self,
        device_id: str,
        callback: Callable
    ) -> None:
        """
        Unregister callback
        
        Args:
            device_id: Device identifier
            callback: Callback function
        """
        if device_id in self.callbacks:
            if callback in self.callbacks[device_id]:
                self.callbacks[device_id].remove(callback)
                logger.info(f"Unregistered callback for device {device_id}")
    
    async def _notify_callbacks(
        self,
        device_id: str,
        data: Dict[str, Any]
    ) -> None:
        """Notify all registered callbacks"""
        if device_id not in self.callbacks:
            return
        
        for callback in self.callbacks[device_id]:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)
            except Exception as e:
                logger.error(f"Error in callback for device {device_id}: {e}")
    
    def get_stream_status(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        Get stream status for device
        
        Args:
            device_id: Device identifier
        
        Returns:
            Stream status dictionary
        """
        return self.active_streams.get(device_id)
    
    def list_active_streams(self) -> List[Dict[str, Any]]:
        """
        List all active streams
        
        Returns:
            List of stream information
        """
        return list(self.active_streams.values())

