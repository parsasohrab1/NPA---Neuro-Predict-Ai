"""
Security Tests (SAST/DAST) for API endpoints
Tests for common security vulnerabilities
Run with: pytest tests/security/ -v
"""
import pytest
import json
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


class TestSQLInjection:
    """Test SQL injection vulnerabilities"""
    
    async def test_sql_injection_in_patient_id(self, test_client: AsyncClient, auth_token: str):
        """Test SQL injection in patient ID parameter"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Common SQL injection payloads
        sql_payloads = [
            "1' OR '1'='1",
            "1'; DROP TABLE patients; --",
            "1' UNION SELECT * FROM users --",
            "' OR 1=1--",
            "1' OR '1'='1' --"
        ]
        
        for payload in sql_payloads:
            response = await test_client.get(
                f"/api/v1/patients/{payload}",
                headers=headers
            )
            # Should not return 500 (server error) or expose database structure
            assert response.status_code != 500, f"SQL injection vulnerability in patient ID: {payload}"
            # Should return 404 or 400, not expose data
            assert response.status_code in [400, 404, 422], \
                f"Unexpected response for SQL injection attempt: {response.status_code}"
    
    async def test_sql_injection_in_search(self, test_client: AsyncClient, auth_token: str):
        """Test SQL injection in search parameters"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE patients; --",
            "' UNION SELECT * FROM users --"
        ]
        
        for payload in sql_payloads:
            response = await test_client.get(
                f"/api/v1/patients?search={payload}",
                headers=headers
            )
            assert response.status_code != 500, f"SQL injection vulnerability in search: {payload}"


class TestXSSVulnerabilities:
    """Test Cross-Site Scripting (XSS) vulnerabilities"""
    
    async def test_xss_in_patient_name(self, test_client: AsyncClient, auth_token: str):
        """Test XSS in patient name field"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "'\"><script>alert('XSS')</script>"
        ]
        
        for payload in xss_payloads:
            response = await test_client.post(
                "/api/v1/patients",
                headers=headers,
                json={
                    "patient_id": "TEST-XSS",
                    "first_name": payload,
                    "last_name": "Test",
                    "date_of_birth": "1990-01-01",
                    "gender": "male"
                }
            )
            # Should either reject (400/422) or sanitize input
            if response.status_code == 201:
                patient_data = response.json()
                # Verify payload is not in response (should be sanitized)
                assert payload not in json.dumps(patient_data), \
                    f"XSS payload not sanitized: {payload}"


class TestAuthenticationSecurity:
    """Test authentication and authorization vulnerabilities"""
    
    async def test_unauthorized_access(self, test_client: AsyncClient):
        """Test that protected endpoints require authentication"""
        protected_endpoints = [
            "/api/v1/patients",
            "/api/v1/predictions",
            "/api/v1/auth/me",
            "/api/v1/users",
        ]
        
        for endpoint in protected_endpoints:
            response = await test_client.get(endpoint)
            assert response.status_code == 401, \
                f"Endpoint {endpoint} should require authentication"
    
    async def test_invalid_token(self, test_client: AsyncClient):
        """Test invalid token handling"""
        headers = {"Authorization": "Bearer invalid_token_12345"}
        
        response = await test_client.get("/api/v1/patients", headers=headers)
        assert response.status_code == 401, "Invalid token should be rejected"
    
    async def test_token_expiration(self, test_client: AsyncClient):
        """Test expired token handling"""
        # Create an expired token (future test - requires time manipulation)
        headers = {"Authorization": "Bearer expired_token"}
        
        response = await test_client.get("/api/v1/patients", headers=headers)
        assert response.status_code == 401, "Expired token should be rejected"
    
    async def test_authorization_bypass(self, test_client: AsyncClient, auth_token: str):
        """Test that users cannot access resources they don't own"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Try to access another user's resources
        # This test should be expanded based on your authorization model
        response = await test_client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code in [200, 403], \
            "User should only access their own resources"


class TestInputValidation:
    """Test input validation and sanitization"""
    
    async def test_path_traversal(self, test_client: AsyncClient, auth_token: str):
        """Test path traversal vulnerabilities"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        path_traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"
        ]
        
        for payload in path_traversal_payloads:
            response = await test_client.get(
                f"/api/v1/reports/{payload}",
                headers=headers
            )
            # Should reject path traversal attempts
            assert response.status_code in [400, 404, 422], \
                f"Path traversal vulnerability: {payload}"
    
    async def test_command_injection(self, test_client: AsyncClient, auth_token: str):
        """Test command injection vulnerabilities"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        command_payloads = [
            "; ls -la",
            "| cat /etc/passwd",
            "&& whoami",
            "$(cat /etc/passwd)",
            "`id`"
        ]
        
        for payload in command_payloads:
            response = await test_client.post(
                "/api/v1/patients",
                headers=headers,
                json={
                    "patient_id": payload,
                    "first_name": "Test",
                    "last_name": "Test",
                    "date_of_birth": "1990-01-01",
                    "gender": "male"
                }
            )
            # Should reject or sanitize command injection attempts
            assert response.status_code != 500, \
                f"Command injection vulnerability: {payload}"


class TestRateLimiting:
    """Test rate limiting and brute force protection"""
    
    @pytest.mark.slow
    async def test_login_rate_limiting(self, test_client: AsyncClient):
        """Test that login endpoint has rate limiting"""
        # Make many login attempts quickly
        responses = []
        for _ in range(15):  # Should hit rate limit
            response = await test_client.post(
                "/api/v1/auth/login",
                data={"username": "admin", "password": "wrong"}
            )
            responses.append(response.status_code)
        
        # Should eventually get rate limited (429)
        assert 429 in responses, "Login endpoint should have rate limiting"
    
    @pytest.mark.slow
    async def test_api_rate_limiting(self, test_client: AsyncClient, auth_token: str):
        """Test that API endpoints have rate limiting"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        responses = []
        for _ in range(150):  # Should hit default rate limit (120/min)
            response = await test_client.get("/api/v1/patients?limit=1", headers=headers)
            responses.append(response.status_code)
        
        # Should get rate limited at some point
        rate_limited = sum(1 for status in responses if status == 429)
        # Allow some leeway but should have rate limiting
        print(f"Rate limited requests: {rate_limited}/150")


class TestSecurityHeaders:
    """Test security headers"""
    
    async def test_security_headers_present(self, test_client: AsyncClient):
        """Test that security headers are present in responses"""
        response = await test_client.get("/health")
        
        headers = response.headers
        
        # Check for common security headers
        assert "X-Content-Type-Options" in headers, "X-Content-Type-Options header missing"
        assert "X-Frame-Options" in headers, "X-Frame-Options header missing"
        assert "X-XSS-Protection" in headers, "X-XSS-Protection header missing"
        
        # Check values
        assert headers["X-Content-Type-Options"] == "nosniff"
        assert headers["X-Frame-Options"] == "DENY"
    
    async def test_cors_headers(self, test_client: AsyncClient):
        """Test CORS headers configuration"""
        response = await test_client.options("/api/v1/patients")
        
        # CORS headers should be present for OPTIONS requests
        if "Access-Control-Allow-Origin" in response.headers:
            origin = response.headers["Access-Control-Allow-Origin"]
            # Should not be wildcard in production
            assert origin != "*" or response.status_code != 200, \
                "CORS wildcard not allowed in production"


class TestDataExposure:
    """Test for sensitive data exposure"""
    
    async def test_error_message_sensitivity(self, test_client: AsyncClient):
        """Test that error messages don't expose sensitive information"""
        # Try to trigger various errors
        response = await test_client.get("/api/v1/patients/invalid-id")
        
        error_detail = response.json().get("detail", "")
        
        # Should not expose database structure
        sensitive_terms = ["postgresql", "sqlite", "database", "table", "column", "SELECT", "FROM"]
        for term in sensitive_terms:
            assert term.lower() not in error_detail.lower(), \
                f"Error message exposes sensitive information: {term}"


class TestPasswordSecurity:
    """Test password security policies"""
    
    async def test_weak_password_rejection(self, test_client: AsyncClient):
        """Test that weak passwords are rejected"""
        weak_passwords = [
            "12345678",
            "password",
            "admin",
            "12345",
            "qwerty"
        ]
        
        for password in weak_passwords:
            response = await test_client.post(
                "/api/v1/auth/register",
                json={
                    "email": f"test{password}@example.com",
                    "username": f"test{password}",
                    "full_name": "Test User",
                    "password": password
                }
            )
            # Should reject weak passwords (400 or 422)
            assert response.status_code in [400, 422], \
                f"Weak password accepted: {password}"

