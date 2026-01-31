"""
Medical Devices Integration API Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from typing import Optional, List
from pydantic import BaseModel

from ...services.integration.device_streaming import DeviceStreamingService, DeviceType
from ...core.security import get_current_user
from ...models.user import User

router = APIRouter(prefix="/devices", tags=["Medical Devices"])

# Initialize device streaming service
device_service = DeviceStreamingService()


class StartStreamRequest(BaseModel):
    """Start stream request"""
    device_id: str
    device_type: str
    device_url: Optional[str] = None
    interval: float = 1.0


@router.post("/stream/start")
async def start_device_stream(
    request: StartStreamRequest,
    current_user: User = Depends(get_current_user)
):
    """
    شروع streaming از دستگاه پزشکی
    
    Parameters:
        device_id: شناسه دستگاه
        device_type: نوع دستگاه
        device_url: URL دستگاه (اختیاری)
        interval: فاصله زمانی streaming (ثانیه)
    
    Returns:
        نتیجه شروع streaming
    """
    try:
        # Convert device_type string to enum
        try:
            device_type_enum = DeviceType(request.device_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid device type: {request.device_type}"
            )
        
        success = await device_service.start_stream(
            device_id=request.device_id,
            device_type=device_type_enum,
            device_url=request.device_url,
            interval=request.interval
        )
        
        if success:
            return {
                "status": "success",
                "message": f"Stream started for device {request.device_id}",
                "device_id": request.device_id
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to start device stream"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error starting device stream: {str(e)}"
        )


@router.post("/stream/stop/{device_id}")
async def stop_device_stream(
    device_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    توقف streaming از دستگاه
    
    Parameters:
        device_id: شناسه دستگاه
    
    Returns:
        نتیجه توقف streaming
    """
    try:
        success = await device_service.stop_stream(device_id)
        
        if success:
            return {
                "status": "success",
                "message": f"Stream stopped for device {device_id}",
                "device_id": device_id
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"No active stream found for device {device_id}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error stopping device stream: {str(e)}"
        )


@router.get("/stream/status/{device_id}")
async def get_stream_status(
    device_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    دریافت وضعیت streaming دستگاه
    
    Parameters:
        device_id: شناسه دستگاه
    
    Returns:
        وضعیت streaming
    """
    try:
        status = device_service.get_stream_status(device_id)
        
        if status:
            return {
                "status": "success",
                "stream_info": status
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"No active stream found for device {device_id}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting stream status: {str(e)}"
        )


@router.get("/stream/list")
async def list_active_streams(
    current_user: User = Depends(get_current_user)
):
    """
    لیست تمام stream های فعال
    
    Returns:
        لیست stream های فعال
    """
    try:
        streams = device_service.list_active_streams()
        
        return {
            "status": "success",
            "count": len(streams),
            "streams": streams
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing streams: {str(e)}"
        )


@router.websocket("/stream/{device_id}")
async def websocket_device_stream(
    websocket: WebSocket,
    device_id: str
):
    """
    WebSocket endpoint برای دریافت real-time data از دستگاه
    
    Parameters:
        device_id: شناسه دستگاه
    """
    await websocket.accept()
    
    # Register callback to send data via WebSocket
    async def send_data(data: dict):
        try:
            await websocket.send_json(data)
        except Exception as e:
            logger.error(f"Error sending data via WebSocket: {e}")
    
    # Register callback
    device_service.register_callback(device_id, send_data)
    
    try:
        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()
            # Handle any incoming messages if needed
            await websocket.send_json({"status": "received", "message": data})
    
    except WebSocketDisconnect:
        # Unregister callback on disconnect
        device_service.unregister_callback(device_id, send_data)
        logger.info(f"WebSocket disconnected for device {device_id}")
    
    except Exception as e:
        logger.error(f"Error in WebSocket connection: {e}")
        device_service.unregister_callback(device_id, send_data)

