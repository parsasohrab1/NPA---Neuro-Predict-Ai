"""
Integration Tests for Medical Device Integration
"""
import pytest
from httpx import AsyncClient

from app.services.integration.device_streaming import (
    DeviceStreamingService,
    DeviceType
)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_start_device_stream(client: AsyncClient, auth_headers: dict):
    """Test starting device stream"""
    stream_data = {
        "device_id": "DEVICE001",
        "device_type": "vital_signs_monitor",
        "device_url": "http://device.example.com",
        "interval": 1.0
    }
    
    response = await client.post(
        "/api/v1/devices/stream/start",
        json=stream_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["device_id"] == "DEVICE001"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_stop_device_stream(client: AsyncClient, auth_headers: dict):
    """Test stopping device stream"""
    # First start a stream
    stream_data = {
        "device_id": "DEVICE002",
        "device_type": "vital_signs_monitor",
        "interval": 1.0
    }
    
    await client.post(
        "/api/v1/devices/stream/start",
        json=stream_data,
        headers=auth_headers
    )
    
    # Stop the stream
    response = await client.post(
        "/api/v1/devices/stream/stop/DEVICE002",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_stream_status(client: AsyncClient, auth_headers: dict):
    """Test getting device stream status"""
    # Start a stream first
    stream_data = {
        "device_id": "DEVICE003",
        "device_type": "lab_analyzer",
        "interval": 1.0
    }
    
    await client.post(
        "/api/v1/devices/stream/start",
        json=stream_data,
        headers=auth_headers
    )
    
    # Get status
    response = await client.get(
        "/api/v1/devices/stream/status/DEVICE003",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "stream_info" in data


@pytest.mark.asyncio
@pytest.mark.integration
async def test_list_active_streams(client: AsyncClient, auth_headers: dict):
    """Test listing active device streams"""
    response = await client.get(
        "/api/v1/devices/stream/list",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "streams" in data
    assert isinstance(data["streams"], list)


@pytest.mark.asyncio
@pytest.mark.integration
def test_device_streaming_service_start_stop():
    """Test device streaming service start/stop"""
    device_service = DeviceStreamingService()
    
    # Start stream
    success = asyncio.run(device_service.start_stream(
        device_id="TEST_DEVICE",
        device_type=DeviceType.VITAL_SIGNS_MONITOR,
        interval=1.0
    ))
    
    assert success == True
    assert "TEST_DEVICE" in device_service.active_streams
    
    # Stop stream
    success = asyncio.run(device_service.stop_stream("TEST_DEVICE"))
    assert success == True
    assert "TEST_DEVICE" not in device_service.active_streams


@pytest.mark.asyncio
@pytest.mark.integration
def test_device_streaming_service_callback():
    """Test device streaming service callback registration"""
    device_service = DeviceStreamingService()
    
    callback_called = []
    
    async def test_callback(data):
        callback_called.append(data)
    
    # Register callback
    device_service.register_callback("TEST_DEVICE", test_callback)
    
    assert "TEST_DEVICE" in device_service.callbacks
    assert len(device_service.callbacks["TEST_DEVICE"]) == 1
    
    # Unregister callback
    device_service.unregister_callback("TEST_DEVICE", test_callback)
    
    assert len(device_service.callbacks.get("TEST_DEVICE", [])) == 0

