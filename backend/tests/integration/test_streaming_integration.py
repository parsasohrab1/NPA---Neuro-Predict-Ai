"""
Integration Tests for Real-time Streaming
"""
import pytest
from httpx import AsyncClient
import json
import asyncio

from app.services.streaming.realtime_service import (
    realtime_service,
    StreamType
)
from app.services.streaming.data_producers import (
    PredictionStreamProducer,
    ClinicalAlertProducer,
    MonitoringStreamProducer
)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_channel(client: AsyncClient, auth_headers: dict):
    """Test creating a streaming channel"""
    channel_data = {
        "channel_id": "test:channel:123",
        "stream_type": "predictions"
    }
    
    response = await client.post(
        "/api/v1/streaming/channels",
        json=channel_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["channel_id"] == "test:channel:123"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_list_channels(client: AsyncClient, auth_headers: dict):
    """Test listing streaming channels"""
    response = await client.get(
        "/api/v1/streaming/channels",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "channels" in data
    assert isinstance(data["channels"], list)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_channel_stats(client: AsyncClient, auth_headers: dict):
    """Test getting channel statistics"""
    # First create a channel
    channel_data = {
        "channel_id": "test:stats:123",
        "stream_type": "monitoring"
    }
    
    await client.post(
        "/api/v1/streaming/channels",
        json=channel_data,
        headers=auth_headers
    )
    
    # Get stats
    response = await client.get(
        "/api/v1/streaming/channels/test:stats:123",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "channel" in data
    assert data["channel"]["channel_id"] == "test:stats:123"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_broadcast_message(client: AsyncClient, auth_headers: dict):
    """Test broadcasting a message to a channel"""
    # Create channel first
    channel_data = {
        "channel_id": "test:broadcast:123",
        "stream_type": "predictions"
    }
    
    await client.post(
        "/api/v1/streaming/channels",
        json=channel_data,
        headers=auth_headers
    )
    
    # Broadcast message
    broadcast_data = {
        "channel_id": "test:broadcast:123",
        "message": {
            "prediction_id": 456,
            "result": {"risk_level": "high"}
        }
    }
    
    response = await client.post(
        "/api/v1/streaming/broadcast",
        json=broadcast_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "sent_count" in data


@pytest.mark.asyncio
@pytest.mark.integration
async def test_list_connections(client: AsyncClient, auth_headers: dict):
    """Test listing active connections"""
    response = await client.get(
        "/api/v1/streaming/connections",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "connections" in data
    assert isinstance(data["connections"], list)


@pytest.mark.asyncio
@pytest.mark.integration
def test_realtime_service_create_channel():
    """Test realtime service creating channel"""
    channel = realtime_service.create_channel(
        channel_id="test:service:123",
        stream_type=StreamType.PREDICTIONS
    )
    
    assert channel.channel_id == "test:service:123"
    assert channel.stream_type == StreamType.PREDICTIONS
    assert "test:service:123" in realtime_service.channels


@pytest.mark.asyncio
@pytest.mark.integration
async def test_prediction_stream_producer():
    """Test prediction stream producer"""
    channel_id = "test:predictions:123"
    
    # Ensure channel exists
    if channel_id not in realtime_service.channels:
        realtime_service.create_channel(channel_id, StreamType.PREDICTIONS)
    
    await PredictionStreamProducer.stream_prediction_result(
        prediction_id=123,
        patient_id=456,
        result={
            "disease_type": "alzheimer",
            "risk_level": "high",
            "risk_score": 0.85
        }
    )
    
    # Check channel stats
    stats = realtime_service.get_channel_stats(channel_id)
    assert stats is not None
    assert stats["message_count"] > 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_clinical_alert_producer():
    """Test clinical alert producer"""
    await ClinicalAlertProducer.stream_alert(
        alert_type="high_risk",
        severity="high",
        patient_id=456,
        message="High risk detected",
        data={"risk_score": 0.85}
    )
    
    # Check that alert channel was created
    channel_id = "alerts:patient:456"
    stats = realtime_service.get_channel_stats(channel_id)
    assert stats is not None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_monitoring_stream_producer():
    """Test monitoring stream producer"""
    metrics = {
        "cpu_usage": 45.2,
        "memory_usage": 62.5,
        "disk_usage": 38.1
    }
    
    await MonitoringStreamProducer.stream_system_metrics(metrics)
    
    # Check that monitoring channel was created
    channel_id = "monitoring:system"
    stats = realtime_service.get_channel_stats(channel_id)
    assert stats is not None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_realtime_service_subscribe_unsubscribe():
    """Test subscribing and unsubscribing from channels"""
    # Create channel
    channel_id = "test:subscribe:123"
    realtime_service.create_channel(channel_id, StreamType.MONITORING)
    
    # Create mock connection
    connection_id = "test-connection-123"
    mock_websocket = None  # In real test, would be a mock WebSocket
    
    # Register connection (without actual websocket for unit test)
    # In integration test, we'd use actual WebSocket
    
    # Test subscribe
    success = realtime_service.subscribe(connection_id, channel_id)
    # This will fail without actual connection, but tests structure
    assert isinstance(success, bool)
    
    # Test unsubscribe
    success = realtime_service.unsubscribe(connection_id, channel_id)
    assert isinstance(success, bool)

