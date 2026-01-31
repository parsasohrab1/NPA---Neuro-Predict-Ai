"""
Real-time Streaming API Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect, Query
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import uuid
import json

from ...services.streaming.realtime_service import (
    realtime_service,
    StreamType
)
from ...core.security import get_current_user
from ...models.user import User

router = APIRouter(prefix="/streaming", tags=["Real-time Streaming"])


class BroadcastRequest(BaseModel):
    """Broadcast message request"""
    channel_id: str
    message: Dict[str, Any]
    exclude_connections: Optional[List[str]] = None


class CreateChannelRequest(BaseModel):
    """Create channel request"""
    channel_id: str
    stream_type: str


@router.websocket("/connect")
async def websocket_connect(
    websocket: WebSocket,
    channels: Optional[str] = Query(None, description="Comma-separated channel IDs"),
    user_id: Optional[int] = Query(None)
):
    """
    WebSocket endpoint for real-time streaming
    
    Parameters:
        channels: Comma-separated list of channel IDs to subscribe to
        user_id: User ID (optional, will be extracted from token if available)
    """
    await websocket.accept()
    
    connection_id = str(uuid.uuid4())
    
    # Parse channels
    channel_list = []
    if channels:
        channel_list = [ch.strip() for ch in channels.split(",") if ch.strip()]
    
    # Register connection
    realtime_service.register_connection(
        connection_id=connection_id,
        websocket=websocket,
        user_id=user_id,
        channels=channel_list
    )
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "connection_id": connection_id,
            "channels": channel_list,
            "timestamp": realtime_service.channels[channel_list[0]].created_at.isoformat() if channel_list else None
        })
        
        # Handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                msg_type = message.get("type")
                
                if msg_type == "subscribe":
                    channel_id = message.get("channel_id")
                    if channel_id:
                        realtime_service.subscribe(connection_id, channel_id)
                        await websocket.send_json({
                            "type": "subscription",
                            "status": "subscribed",
                            "channel_id": channel_id
                        })
                
                elif msg_type == "unsubscribe":
                    channel_id = message.get("channel_id")
                    if channel_id:
                        realtime_service.unsubscribe(connection_id, channel_id)
                        await websocket.send_json({
                            "type": "subscription",
                            "status": "unsubscribed",
                            "channel_id": channel_id
                        })
                
                elif msg_type == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": realtime_service.channels[channel_list[0]].created_at.isoformat() if channel_list else None
                    })
                
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Unknown message type: {msg_type}"
                    })
            
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format"
                })
    
    except WebSocketDisconnect:
        realtime_service.unregister_connection(connection_id)
    
    except Exception as e:
        logger.error(f"Error in WebSocket connection {connection_id}: {e}")
        realtime_service.unregister_connection(connection_id)


@router.post("/broadcast")
async def broadcast_message(
    request: BroadcastRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Broadcast message to a channel
    
    Parameters:
        channel_id: Channel identifier
        message: Message to broadcast
        exclude_connections: List of connection IDs to exclude
    """
    try:
        sent_count = await realtime_service.broadcast(
            channel_id=request.channel_id,
            message=request.message,
            exclude_connections=request.exclude_connections
        )
        
        return {
            "status": "success",
            "channel_id": request.channel_id,
            "sent_count": sent_count,
            "message": "Message broadcasted successfully"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error broadcasting message: {str(e)}"
        )


@router.post("/channels")
async def create_channel(
    request: CreateChannelRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new streaming channel
    
    Parameters:
        channel_id: Channel identifier
        stream_type: Type of stream
    """
    try:
        try:
            stream_type = StreamType(request.stream_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid stream type: {request.stream_type}"
            )
        
        channel = realtime_service.create_channel(
            channel_id=request.channel_id,
            stream_type=stream_type
        )
        
        return {
            "status": "success",
            "channel_id": channel.channel_id,
            "stream_type": channel.stream_type.value,
            "message": "Channel created successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating channel: {str(e)}"
        )


@router.get("/channels")
async def list_channels(
    current_user: User = Depends(get_current_user)
):
    """
    List all streaming channels
    
    Returns:
        List of channels with statistics
    """
    try:
        channels = realtime_service.list_channels()
        return {
            "status": "success",
            "count": len(channels),
            "channels": channels
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing channels: {str(e)}"
        )


@router.get("/channels/{channel_id}")
async def get_channel_stats(
    channel_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get statistics for a channel
    
    Parameters:
        channel_id: Channel identifier
    
    Returns:
        Channel statistics
    """
    try:
        stats = realtime_service.get_channel_stats(channel_id)
        
        if not stats:
            raise HTTPException(
                status_code=404,
                detail=f"Channel {channel_id} not found"
            )
        
        return {
            "status": "success",
            "channel": stats
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting channel stats: {str(e)}"
        )


@router.get("/connections")
async def list_connections(
    current_user: User = Depends(get_current_user)
):
    """
    List all active connections
    
    Returns:
        List of connections with statistics
    """
    try:
        connections = realtime_service.list_connections()
        return {
            "status": "success",
            "count": len(connections),
            "connections": connections
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing connections: {str(e)}"
        )


@router.get("/connections/{connection_id}")
async def get_connection_stats(
    connection_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get statistics for a connection
    
    Parameters:
        connection_id: Connection identifier
    
    Returns:
        Connection statistics
    """
    try:
        stats = realtime_service.get_connection_stats(connection_id)
        
        if not stats:
            raise HTTPException(
                status_code=404,
                detail=f"Connection {connection_id} not found"
            )
        
        return {
            "status": "success",
            "connection": stats
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting connection stats: {str(e)}"
        )


# Import logger
import logging
logger = logging.getLogger(__name__)

