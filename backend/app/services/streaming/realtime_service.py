"""
Real-time Data Streaming Service
سرویس برای streaming داده‌های real-time
"""
from typing import Optional, Dict, Any, List, Callable, Set
from datetime import datetime
import asyncio
import json
import logging
from enum import Enum
from collections import defaultdict
import uuid

logger = logging.getLogger(__name__)


class StreamType(Enum):
    """Types of data streams"""
    PREDICTIONS = "predictions"
    MONITORING = "monitoring"
    CLINICAL_ALERTS = "clinical_alerts"
    DEVICE_DATA = "device_data"
    SYSTEM_METRICS = "system_metrics"
    AI_ML_HEALTH = "ai_ml_health"


class StreamChannel:
    """Represents a streaming channel"""
    
    def __init__(self, channel_id: str, stream_type: StreamType):
        self.channel_id = channel_id
        self.stream_type = stream_type
        self.subscribers: Set[str] = set()  # WebSocket connection IDs
        self.created_at = datetime.now()
        self.message_count = 0
        self.last_message_time: Optional[datetime] = None


class RealTimeStreamingService:
    """Service for real-time data streaming"""
    
    def __init__(self):
        self.channels: Dict[str, StreamChannel] = {}
        self.connections: Dict[str, Dict[str, Any]] = {}  # connection_id -> connection info
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.broadcast_tasks: Dict[str, asyncio.Task] = {}
        self.running = False
    
    def start(self):
        """Start the streaming service"""
        if self.running:
            return
        
        self.running = True
        asyncio.create_task(self._process_message_queue())
        logger.info("Real-time streaming service started")
    
    def stop(self):
        """Stop the streaming service"""
        self.running = False
        for task in self.broadcast_tasks.values():
            task.cancel()
        self.broadcast_tasks.clear()
        logger.info("Real-time streaming service stopped")
    
    def register_connection(
        self,
        connection_id: str,
        websocket: Any,
        user_id: Optional[int] = None,
        channels: Optional[List[str]] = None
    ) -> None:
        """
        Register a WebSocket connection
        
        Args:
            connection_id: Unique connection identifier
            websocket: WebSocket connection object
            user_id: User ID (optional)
            channels: List of channel IDs to subscribe to
        """
        self.connections[connection_id] = {
            "websocket": websocket,
            "user_id": user_id,
            "channels": set(channels or []),
            "connected_at": datetime.now(),
            "message_count": 0
        }
        
        # Subscribe to channels
        if channels:
            for channel_id in channels:
                self.subscribe(connection_id, channel_id)
        
        logger.info(f"Connection {connection_id} registered")
    
    def unregister_connection(self, connection_id: str) -> None:
        """Unregister a WebSocket connection"""
        if connection_id not in self.connections:
            return
        
        # Unsubscribe from all channels
        channels = self.connections[connection_id]["channels"].copy()
        for channel_id in channels:
            self.unsubscribe(connection_id, channel_id)
        
        del self.connections[connection_id]
        logger.info(f"Connection {connection_id} unregistered")
    
    def create_channel(
        self,
        channel_id: str,
        stream_type: StreamType
    ) -> StreamChannel:
        """
        Create a new streaming channel
        
        Args:
            channel_id: Channel identifier
            stream_type: Type of stream
        
        Returns:
            StreamChannel object
        """
        if channel_id in self.channels:
            return self.channels[channel_id]
        
        channel = StreamChannel(channel_id, stream_type)
        self.channels[channel_id] = channel
        logger.info(f"Channel {channel_id} created (type: {stream_type.value})")
        return channel
    
    def subscribe(self, connection_id: str, channel_id: str) -> bool:
        """
        Subscribe connection to a channel
        
        Args:
            connection_id: Connection identifier
            channel_id: Channel identifier
        
        Returns:
            True if successful
        """
        if connection_id not in self.connections:
            return False
        
        if channel_id not in self.channels:
            # Auto-create channel if it doesn't exist
            stream_type = StreamType.MONITORING  # Default
            self.create_channel(channel_id, stream_type)
        
        self.channels[channel_id].subscribers.add(connection_id)
        self.connections[connection_id]["channels"].add(channel_id)
        
        logger.info(f"Connection {connection_id} subscribed to channel {channel_id}")
        return True
    
    def unsubscribe(self, connection_id: str, channel_id: str) -> bool:
        """
        Unsubscribe connection from a channel
        
        Args:
            connection_id: Connection identifier
            channel_id: Channel identifier
        
        Returns:
            True if successful
        """
        if connection_id not in self.connections:
            return False
        
        if channel_id in self.channels:
            self.channels[channel_id].subscribers.discard(connection_id)
        
        self.connections[connection_id]["channels"].discard(channel_id)
        
        logger.info(f"Connection {connection_id} unsubscribed from channel {channel_id}")
        return True
    
    async def broadcast(
        self,
        channel_id: str,
        message: Dict[str, Any],
        exclude_connections: Optional[List[str]] = None
    ) -> int:
        """
        Broadcast message to all subscribers of a channel
        
        Args:
            channel_id: Channel identifier
            message: Message to broadcast
            exclude_connections: List of connection IDs to exclude
        
        Returns:
            Number of connections that received the message
        """
        if channel_id not in self.channels:
            logger.warning(f"Channel {channel_id} does not exist")
            return 0
        
        channel = self.channels[channel_id]
        exclude_connections = exclude_connections or []
        
        # Add metadata
        message_with_metadata = {
            "channel": channel_id,
            "stream_type": channel.stream_type.value,
            "timestamp": datetime.now().isoformat(),
            "message_id": str(uuid.uuid4()),
            "data": message
        }
        
        # Queue message for processing
        await self.message_queue.put({
            "channel_id": channel_id,
            "message": message_with_metadata,
            "exclude_connections": exclude_connections
        })
        
        return len(channel.subscribers) - len(exclude_connections)
    
    async def send_to_connection(
        self,
        connection_id: str,
        message: Dict[str, Any]
    ) -> bool:
        """
        Send message to a specific connection
        
        Args:
            connection_id: Connection identifier
            message: Message to send
        
        Returns:
            True if successful
        """
        if connection_id not in self.connections:
            return False
        
        connection = self.connections[connection_id]
        websocket = connection["websocket"]
        
        try:
            message_with_metadata = {
                "timestamp": datetime.now().isoformat(),
                "message_id": str(uuid.uuid4()),
                "data": message
            }
            
            await websocket.send_json(message_with_metadata)
            connection["message_count"] += 1
            return True
        
        except Exception as e:
            logger.error(f"Error sending message to connection {connection_id}: {e}")
            return False
    
    async def _process_message_queue(self) -> None:
        """Process messages from the queue"""
        while self.running:
            try:
                # Wait for message with timeout
                try:
                    queue_item = await asyncio.wait_for(
                        self.message_queue.get(),
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                channel_id = queue_item["channel_id"]
                message = queue_item["message"]
                exclude_connections = queue_item["exclude_connections"]
                
                if channel_id not in self.channels:
                    continue
                
                channel = self.channels[channel_id]
                sent_count = 0
                failed_connections = []
                
                # Send to all subscribers
                for connection_id in channel.subscribers:
                    if connection_id in exclude_connections:
                        continue
                    
                    if connection_id not in self.connections:
                        failed_connections.append(connection_id)
                        continue
                    
                    success = await self.send_to_connection(connection_id, message)
                    if success:
                        sent_count += 1
                    else:
                        failed_connections.append(connection_id)
                
                # Clean up failed connections
                for connection_id in failed_connections:
                    channel.subscribers.discard(connection_id)
                    if connection_id in self.connections:
                        self.connections[connection_id]["channels"].discard(channel_id)
                
                channel.message_count += 1
                channel.last_message_time = datetime.now()
                
                logger.debug(
                    f"Broadcast to channel {channel_id}: "
                    f"{sent_count} sent, {len(failed_connections)} failed"
                )
            
            except Exception as e:
                logger.error(f"Error processing message queue: {e}")
                await asyncio.sleep(0.1)
    
    def get_channel_stats(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a channel"""
        if channel_id not in self.channels:
            return None
        
        channel = self.channels[channel_id]
        return {
            "channel_id": channel_id,
            "stream_type": channel.stream_type.value,
            "subscribers": len(channel.subscribers),
            "message_count": channel.message_count,
            "created_at": channel.created_at.isoformat(),
            "last_message_time": (
                channel.last_message_time.isoformat()
                if channel.last_message_time else None
            )
        }
    
    def get_connection_stats(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a connection"""
        if connection_id not in self.connections:
            return None
        
        connection = self.connections[connection_id]
        return {
            "connection_id": connection_id,
            "user_id": connection["user_id"],
            "channels": list(connection["channels"]),
            "message_count": connection["message_count"],
            "connected_at": connection["connected_at"].isoformat()
        }
    
    def list_channels(self) -> List[Dict[str, Any]]:
        """List all channels"""
        return [
            self.get_channel_stats(channel_id)
            for channel_id in self.channels.keys()
        ]
    
    def list_connections(self) -> List[Dict[str, Any]]:
        """List all connections"""
        return [
            self.get_connection_stats(connection_id)
            for connection_id in self.connections.keys()
        ]


# Global instance
realtime_service = RealTimeStreamingService()

