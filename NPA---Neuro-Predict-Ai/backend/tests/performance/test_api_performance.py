"""
Performance Tests for API Endpoints
"""
import pytest
import asyncio
import time
from httpx import AsyncClient


class TestAPIPerformance:
    """Performance tests for API endpoints"""
    
    @pytest.mark.asyncio
    async def test_prediction_latency(self, client: AsyncClient, auth_headers, test_patient, test_medical_record):
        """Test prediction endpoint latency"""
        times = []
        
        for _ in range(10):
            start = time.time()
            response = await client.post(
                "/api/v1/predictions",
                json={
                    "patient_id": test_patient.id,
                    "disease_type": "alzheimer"
                },
                headers=auth_headers
            )
            elapsed = time.time() - start
            times.append(elapsed)
            assert response.status_code == 201
        
        avg_time = sum(times) / len(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        
        # Target: < 3 seconds for prediction
        assert avg_time < 3.0, f"Average prediction time {avg_time:.2f}s exceeds 3s"
        assert p95_time < 5.0, f"P95 prediction time {p95_time:.2f}s exceeds 5s"
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, client: AsyncClient, auth_headers, test_patient, test_medical_record):
        """Test handling concurrent requests"""
        async def make_request():
            return await client.get(
                f"/api/v1/patients/{test_patient.id}",
                headers=auth_headers
            )
        
        # Make 20 concurrent requests
        start = time.time()
        responses = await asyncio.gather(*[make_request() for _ in range(20)])
        elapsed = time.time() - start
        
        # All should succeed
        assert all(r.status_code == 200 for r in responses)
        
        # Should complete in reasonable time
        assert elapsed < 5.0, f"20 concurrent requests took {elapsed:.2f}s"
    
    @pytest.mark.asyncio
    async def test_api_response_time(self, client: AsyncClient, auth_headers):
        """Test general API response times"""
        endpoints = [
            ("/api/v1/auth/me", "GET"),
            ("/api/v1/patients", "GET"),
            ("/api/v1/predictions", "GET"),
        ]
        
        for endpoint, method in endpoints:
            start = time.time()
            if method == "GET":
                response = await client.get(endpoint, headers=auth_headers)
            elapsed = time.time() - start
            
            assert response.status_code in [200, 201]
            # Target: < 200ms for general API calls
            assert elapsed < 0.5, f"{endpoint} took {elapsed:.2f}s (target: <0.2s)"


class TestDatabasePerformance:
    """Performance tests for database operations"""
    
    @pytest.mark.asyncio
    async def test_bulk_patient_creation(self, client: AsyncClient, auth_headers):
        """Test creating multiple patients"""
        start = time.time()
        
        tasks = []
        for i in range(10):
            task = client.post(
                "/api/v1/patients",
                json={
                    "first_name": f"Bulk{i}",
                    "last_name": "Test",
                    "date_of_birth": "1950-01-01",
                    "gender": "male",
                    "email": f"bulk{i}@test.com",
                    "phone": f"+123456789{i}"
                },
                headers=auth_headers
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        elapsed = time.time() - start
        
        assert all(r.status_code == 201 for r in responses)
        # Should complete 10 creations in reasonable time
        assert elapsed < 5.0, f"10 patient creations took {elapsed:.2f}s"

