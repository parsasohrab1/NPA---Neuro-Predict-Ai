"""
WebSocket Server for Real-Time Updates
ارسال به‌روزرسانی‌های برخط به داشبورد
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from typing import Dict, List, Set
import json
import asyncio
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """مدیریت اتصالات WebSocket"""
    
    def __init__(self):
        # Store active connections by user_id and channel
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.user_connections: Dict[int, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, channel: str, user_id: int = None):
        """اتصال WebSocket جدید"""
        await websocket.accept()
        
        if channel not in self.active_connections:
            self.active_connections[channel] = set()
        self.active_connections[channel].add(websocket)
        
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(websocket)
        
        logger.info(f"WebSocket connected: channel={channel}, user_id={user_id}")
    
    def disconnect(self, websocket: WebSocket, channel: str, user_id: int = None):
        """قطع اتصال WebSocket"""
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)
            if not self.active_connections[channel]:
                del self.active_connections[channel]
        
        if user_id and user_id in self.user_connections:
            self.user_connections[user_id].discard(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        logger.info(f"WebSocket disconnected: channel={channel}, user_id={user_id}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """ارسال پیام به یک اتصال خاص"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
    
    async def broadcast_to_channel(self, message: dict, channel: str):
        """ارسال پیام به تمام اتصالات یک کانال"""
        if channel not in self.active_connections:
            return
        
        disconnected = set()
        for connection in self.active_connections[channel]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to channel {channel}: {e}")
                disconnected.add(connection)
        
        # Remove disconnected connections
        for conn in disconnected:
            self.active_connections[channel].discard(conn)
    
    async def broadcast_to_user(self, message: dict, user_id: int):
        """ارسال پیام به تمام اتصالات یک کاربر"""
        if user_id not in self.user_connections:
            return
        
        disconnected = set()
        for connection in self.user_connections[user_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to user {user_id}: {e}")
                disconnected.add(connection)
        
        # Remove disconnected connections
        for conn in disconnected:
            self.user_connections[user_id].discard(conn)


# Global connection manager
manager = ConnectionManager()


@router.websocket("/ws/monitoring")
async def websocket_monitoring(
    websocket: WebSocket,
    token: str = Query(...),
    channel: str = Query("all", regex="^(all|ai_ml|clinical|system|security)$")
):
    """
    WebSocket endpoint برای مانیتورینگ برخط
    Channels: all, ai_ml, clinical, system, security
    """
    user_id = None
    
    try:
        # Verify token and get user
        from ..core.security import decode_token
        from ..db.session import AsyncSessionLocal
        from sqlalchemy import select
        
        try:
            payload = decode_token(token)
            user_id_str = payload.get("sub")
            if user_id_str:
                async with AsyncSessionLocal() as db:
                    result = await db.execute(select(User).where(User.id == int(user_id_str)))
                    user = result.scalar_one_or_none()
                    user_id = user.id if user and user.is_active else None
        except Exception:
            user_id = None
        
        await manager.connect(websocket, channel, user_id)
        
        # Send initial connection confirmation
        await manager.send_personal_message({
            "type": "connection",
            "status": "connected",
            "channel": channel,
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)
        
        # Keep connection alive and handle messages
        while True:
            try:
                # Wait for messages from client (ping/pong)
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                message = json.loads(data)
                
                if message.get("type") == "ping":
                    await manager.send_personal_message({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    }, websocket)
                
            except asyncio.TimeoutError:
                # Send heartbeat
                await manager.send_personal_message({
                    "type": "heartbeat",
                    "timestamp": datetime.utcnow().isoformat()
                }, websocket)
            except WebSocketDisconnect:
                break
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket, channel, user_id)


# Helper functions to broadcast updates
async def broadcast_ai_ml_update(data: dict):
    """ارسال به‌روزرسانی AI/ML"""
    await manager.broadcast_to_channel({
        "type": "ai_ml_update",
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }, "ai_ml")
    
    await manager.broadcast_to_channel({
        "type": "ai_ml_update",
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }, "all")


async def broadcast_clinical_update(data: dict):
    """ارسال به‌روزرسانی کلینیکی"""
    await manager.broadcast_to_channel({
        "type": "clinical_update",
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }, "clinical")
    
    await manager.broadcast_to_channel({
        "type": "clinical_update",
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }, "all")


async def broadcast_system_update(data: dict):
    """ارسال به‌روزرسانی سیستم"""
    await manager.broadcast_to_channel({
        "type": "system_update",
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }, "system")
    
    await manager.broadcast_to_channel({
        "type": "system_update",
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }, "all")


async def broadcast_security_update(data: dict):
    """ارسال به‌روزرسانی امنیتی"""
    await manager.broadcast_to_channel({
        "type": "security_update",
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }, "security")
    
    await manager.broadcast_to_channel({
        "type": "security_update",
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }, "all")


async def broadcast_alert(alert: dict, user_id: int = None):
    """ارسال هشدار به کاربر خاص یا همه"""
    message = {
        "type": "alert",
        "data": alert,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if user_id:
        await manager.broadcast_to_user(message, user_id)
    else:
        await manager.broadcast_to_channel(message, "all")

