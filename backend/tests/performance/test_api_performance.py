"""
Performance Tests for API Endpoints
Run with: pytest tests/performance/ -v --durations=10
"""
import pytest
import time
import statistics
import asyncio
from typing import List
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


class TestAPIPerformance:
    """Performance tests for API endpoints"""
    
    @pytest.fixture
    async def auth_token(self, test_client: AsyncClient):
        """Get authentication token for performance tests"""
        response = await test_client.post(
            "/api/v1/auth/login",
            data={"username": "admin", "password": "admin123"}
        )
        if response.status_code == 200:
            return response.json()["access_token"]
        return None
    
    async def measure_response_time(self, client: AsyncClient, method: str, url: str, **kwargs) -> float:
        """Measure response time for a request"""
        start_time = time.perf_counter()
        response = await client.request(method, url, **kwargs)
        end_time = time.perf_counter()
        assert response.status_code < 500, f"Server error: {response.status_code}"
        return (end_time - start_time) * 1000  # Convert to milliseconds
    
    @pytest.mark.slow
    async def test_health_check_performance(self, test_client: AsyncClient):
        """Health check should respond quickly (<100ms)"""
        times = []
        for _ in range(10):
            response_time = await self.measure_response_time(test_client, "GET", "/health")
            times.append(response_time)
        
        avg_time = statistics.mean(times)
        p95_time = statistics.quantiles(times, n=20)[18]  # 95th percentile
        
        assert avg_time < 100, f"Average response time {avg_time}ms exceeds 100ms"
        assert p95_time < 200, f"95th percentile {p95_time}ms exceeds 200ms"
        print(f"Health check - Avg: {avg_time:.2f}ms, P95: {p95_time:.2f}ms")
    
    @pytest.mark.slow
    async def test_login_performance(self, test_client: AsyncClient):
        """Login endpoint should respond within 500ms"""
        times = []
        for _ in range(5):
            response_time = await self.measure_response_time(
                test_client,
                "POST",
                "/api/v1/auth/login",
                data={"username": "admin", "password": "admin123"}
            )
            times.append(response_time)
        
        avg_time = statistics.mean(times)
        assert avg_time < 500, f"Average login time {avg_time}ms exceeds 500ms"
        print(f"Login - Avg: {avg_time:.2f}ms")
    
    @pytest.mark.slow
    async def test_get_patients_performance(self, test_client: AsyncClient, auth_token: str):
        """GET /patients should respond within 300ms"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        times = []
        
        for _ in range(5):
            response_time = await self.measure_response_time(
                test_client,
                "GET",
                "/api/v1/patients",
                headers=headers
            )
            times.append(response_time)
        
        avg_time = statistics.mean(times)
        assert avg_time < 300, f"Average GET /patients time {avg_time}ms exceeds 300ms"
        print(f"GET /patients - Avg: {avg_time:.2f}ms")
    
    @pytest.mark.slow
    async def test_prediction_performance(self, test_client: AsyncClient, auth_token: str, sample_patient):
        """Prediction endpoint should respond within 3 seconds (as per requirements)"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        times = []
        
        # Only run 2-3 times due to resource intensity
        for _ in range(2):
            response_time = await self.measure_response_time(
                test_client,
                "POST",
                "/api/v1/predictions",
                headers=headers,
                json={
                    "patient_id": sample_patient.id,
                    "disease_type": "both"
                }
            )
            times.append(response_time)
        
        avg_time = statistics.mean(times)
        assert avg_time < 3000, f"Average prediction time {avg_time}ms exceeds 3 seconds"
        print(f"Prediction - Avg: {avg_time:.2f}ms")
    
    @pytest.mark.slow
    async def test_concurrent_requests(self, test_client: AsyncClient, auth_token: str):
        """Test performance under concurrent load"""
        import asyncio
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        async def make_request():
            return await self.measure_response_time(
                test_client,
                "GET",
                "/api/v1/patients?limit=10",
                headers=headers
            )
        
        # Run 10 concurrent requests
        start_time = time.perf_counter()
        tasks = [make_request() for _ in range(10)]
        response_times = await asyncio.gather(*tasks)
        total_time = (time.perf_counter() - start_time) * 1000
        
        avg_time = statistics.mean(response_times)
        max_time = max(response_times)
        
        assert avg_time < 500, f"Average concurrent request time {avg_time}ms exceeds 500ms"
        assert total_time < 2000, f"Total time for 10 concurrent requests {total_time}ms exceeds 2 seconds"
        print(f"Concurrent (10 reqs) - Avg: {avg_time:.2f}ms, Max: {max_time:.2f}ms, Total: {total_time:.2f}ms")


@pytest.mark.slow
class TestLoadPerformance:
    """Load testing scenarios"""
    
    @pytest.mark.asyncio
    async def test_sustained_load(self, test_client: AsyncClient):
        """Test sustained load over time"""
        times = []
        errors = 0
        
        # Run 50 requests
        for i in range(50):
            try:
                response_time = await test_client.get("/health")
                times.append(time.perf_counter())
                if response_time.status_code >= 500:
                    errors += 1
            except Exception:
                errors += 1
            
            # Small delay between requests
            if i % 10 == 0:
                await asyncio.sleep(0.1)
        
        error_rate = errors / 50 * 100
        assert error_rate < 5, f"Error rate {error_rate}% exceeds 5%"
        print(f"Sustained load - Errors: {errors}/50 ({error_rate}%)")

