"""
Load Testing Suite
Tests for high-load scenarios and stress testing
"""
import pytest
import asyncio
import time
import statistics
from typing import List
from httpx import AsyncClient


pytestmark = pytest.mark.asyncio
pytestmark = pytest.mark.slow


class TestLoadTesting:
    """Load testing scenarios"""
    
    async def make_request(self, client: AsyncClient, method: str, url: str, **kwargs) -> tuple[float, int]:
        """Make a request and return response time and status code"""
        start_time = time.perf_counter()
        try:
            response = await client.request(method, url, **kwargs)
            duration = (time.perf_counter() - start_time) * 1000
            return duration, response.status_code
        except Exception as e:
            duration = (time.perf_counter() - start_time) * 1000
            return duration, 500
    
    @pytest.fixture
    async def auth_token(self, test_client: AsyncClient):
        """Get authentication token"""
        response = await test_client.post(
            "/api/v1/auth/login",
            data={"username": "admin", "password": "admin123"}
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        return None
    
    @pytest.mark.load_test
    async def test_concurrent_login_requests(self, test_client: AsyncClient):
        """Test handling of 50 concurrent login requests"""
        async def login():
            return await self.make_request(
                test_client,
                "POST",
                "/api/v1/auth/login",
                data={"username": "admin", "password": "admin123"}
            )
        
        # Run 50 concurrent login requests
        start_time = time.perf_counter()
        tasks = [login() for _ in range(50)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = (time.perf_counter() - start_time) * 1000
        
        # Analyze results
        response_times = [r[0] for r in results if isinstance(r, tuple)]
        status_codes = [r[1] for r in results if isinstance(r, tuple)]
        errors = sum(1 for r in results if isinstance(r, Exception) or (isinstance(r, tuple) and r[1] >= 500))
        
        avg_time = statistics.mean(response_times) if response_times else 0
        p95_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max(response_times) if response_times else 0
        
        error_rate = (errors / len(results)) * 100
        
        assert error_rate < 10, f"Error rate {error_rate}% exceeds 10%"
        assert avg_time < 1000, f"Average response time {avg_time}ms exceeds 1 second"
        assert total_time < 5000, f"Total time {total_time}ms exceeds 5 seconds for 50 requests"
        
        print(f"\nConcurrent Login (50 reqs):")
        print(f"  Avg: {avg_time:.2f}ms, P95: {p95_time:.2f}ms")
        print(f"  Errors: {errors}/{len(results)} ({error_rate:.1f}%)")
        print(f"  Total time: {total_time:.2f}ms")
    
    @pytest.mark.load_test
    async def test_burst_load(self, test_client: AsyncClient, auth_token: str):
        """Test handling of burst load (100 requests in quick succession)"""
        if not auth_token:
            pytest.skip("Authentication required")
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        async def get_patients():
            return await self.make_request(
                test_client,
                "GET",
                "/api/v1/patients?limit=10",
                headers=headers
            )
        
        # Run 100 requests in burst
        start_time = time.perf_counter()
        tasks = [get_patients() for _ in range(100)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = (time.perf_counter() - start_time) * 1000
        
        response_times = [r[0] for r in results if isinstance(r, tuple)]
        errors = sum(1 for r in results if isinstance(r, Exception) or (isinstance(r, tuple) and r[1] >= 500))
        
        avg_time = statistics.mean(response_times) if response_times else 0
        p99_time = statistics.quantiles(response_times, n=100)[98] if len(response_times) >= 100 else max(response_times) if response_times else 0
        error_rate = (errors / len(results)) * 100
        
        assert error_rate < 5, f"Error rate {error_rate}% exceeds 5%"
        assert p99_time < 2000, f"99th percentile {p99_time}ms exceeds 2 seconds"
        
        print(f"\nBurst Load (100 reqs):")
        print(f"  Avg: {avg_time:.2f}ms, P99: {p99_time:.2f}ms")
        print(f"  Errors: {errors}/{len(results)} ({error_rate:.1f}%)")
        print(f"  Total time: {total_time:.2f}ms")
    
    @pytest.mark.load_test
    async def test_sustained_load(self, test_client: AsyncClient, auth_token: str):
        """Test sustained load over extended period (200 requests over 10 seconds)"""
        if not auth_token:
            pytest.skip("Authentication required")
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response_times = []
        errors = 0
        total_requests = 200
        duration_seconds = 10
        requests_per_second = total_requests / duration_seconds
        delay_between_requests = 1.0 / requests_per_second
        
        start_time = time.perf_counter()
        
        async def make_request_with_delay(index: int):
            await asyncio.sleep(index * delay_between_requests)
            duration, status = await self.make_request(
                test_client,
                "GET",
                "/api/v1/patients?limit=10",
                headers=headers
            )
            return duration, status
        
        tasks = [make_request_with_delay(i) for i in range(total_requests)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.perf_counter() - start_time
        
        for result in results:
            if isinstance(result, tuple):
                response_times.append(result[0])
                if result[1] >= 500:
                    errors += 1
            else:
                errors += 1
        
        avg_time = statistics.mean(response_times) if response_times else 0
        max_time = max(response_times) if response_times else 0
        error_rate = (errors / len(results)) * 100
        
        assert error_rate < 5, f"Error rate {error_rate}% exceeds 5%"
        assert avg_time < 500, f"Average response time {avg_time}ms exceeds 500ms under sustained load"
        
        print(f"\nSustained Load (200 reqs over {total_time:.1f}s):")
        print(f"  Avg: {avg_time:.2f}ms, Max: {max_time:.2f}ms")
        print(f"  Errors: {errors}/{len(results)} ({error_rate:.1f}%)")
        print(f"  Throughput: {len(results)/total_time:.1f} req/s")
    
    @pytest.mark.load_test
    async def test_mixed_workload(self, test_client: AsyncClient, auth_token: str):
        """Test mixed workload with different endpoint types"""
        if not auth_token:
            pytest.skip("Authentication required")
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        async def get_patients():
            return await self.make_request(
                test_client, "GET", "/api/v1/patients?limit=10", headers=headers
            )
        
        async def get_predictions():
            return await self.make_request(
                test_client, "GET", "/api/v1/predictions?limit=10", headers=headers
            )
        
        async def get_reports():
            return await self.make_request(
                test_client, "GET", "/api/v1/reports/summary", headers=headers
            )
        
        # Mix of different endpoints
        tasks = []
        tasks.extend([get_patients() for _ in range(20)])  # 40% of requests
        tasks.extend([get_predictions() for _ in range(20)])  # 40% of requests
        tasks.extend([get_reports() for _ in range(10)])  # 20% of requests
        
        start_time = time.perf_counter()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = (time.perf_counter() - start_time) * 1000
        
        response_times = [r[0] for r in results if isinstance(r, tuple)]
        errors = sum(1 for r in results if isinstance(r, Exception) or (isinstance(r, tuple) and r[1] >= 500))
        
        avg_time = statistics.mean(response_times) if response_times else 0
        error_rate = (errors / len(results)) * 100
        
        assert error_rate < 10, f"Error rate {error_rate}% exceeds 10%"
        assert avg_time < 1000, f"Average response time {avg_time}ms exceeds 1 second"
        
        print(f"\nMixed Workload (50 reqs):")
        print(f"  Avg: {avg_time:.2f}ms")
        print(f"  Errors: {errors}/{len(results)} ({error_rate:.1f}%)")
        print(f"  Total time: {total_time:.2f}ms")
    
    @pytest.mark.load_test
    async def test_prediction_load(self, test_client: AsyncClient, auth_token: str, sample_patient):
        """Test prediction endpoint under load (limited due to resource intensity)"""
        if not auth_token:
            pytest.skip("Authentication required")
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        async def make_prediction():
            return await self.make_request(
                test_client,
                "POST",
                "/api/v1/predictions",
                headers=headers,
                json={
                    "patient_id": sample_patient.id,
                    "disease_type": "both"
                }
            )
        
        # Limited number due to resource intensity
        tasks = [make_prediction() for _ in range(5)]
        
        start_time = time.perf_counter()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = (time.perf_counter() - start_time) * 1000
        
        response_times = [r[0] for r in results if isinstance(r, tuple)]
        errors = sum(1 for r in results if isinstance(r, Exception) or (isinstance(r, tuple) and r[1] >= 500))
        
        if response_times:
            avg_time = statistics.mean(response_times)
            max_time = max(response_times)
            
            # Predictions are resource-intensive, allow more time
            assert avg_time < 5000, f"Average prediction time {avg_time}ms exceeds 5 seconds"
            assert errors == 0, f"Errors occurred during prediction load test: {errors}"
            
            print(f"\nPrediction Load (5 reqs):")
            print(f"  Avg: {avg_time:.2f}ms, Max: {max_time:.2f}ms")
            print(f"  Errors: {errors}/5")
            print(f"  Total time: {total_time:.2f}ms")


class TestStressTesting:
    """Stress testing - push system to limits"""
    
    @pytest.mark.stress_test
    async def test_extreme_concurrency(self, test_client: AsyncClient):
        """Test extreme concurrency (1000 concurrent requests)"""
        async def health_check():
            return await test_client.get("/health")
        
        # Create 1000 concurrent tasks
        tasks = [health_check() for _ in range(1000)]
        
        start_time = time.perf_counter()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = (time.perf_counter() - start_time) * 1000
        
        successes = sum(1 for r in results if not isinstance(r, Exception) and hasattr(r, 'status_code') and r.status_code < 500)
        errors = len(results) - successes
        
        success_rate = (successes / len(results)) * 100
        
        # Allow some failures under extreme load, but most should succeed
        assert success_rate > 90, f"Success rate {success_rate}% below 90% under extreme load"
        
        print(f"\nExtreme Concurrency (1000 reqs):")
        print(f"  Success: {successes}/{len(results)} ({success_rate:.1f}%)")
        print(f"  Errors: {errors}")
        print(f"  Total time: {total_time:.2f}ms")



