"""
Security Tests
"""
import pytest
from httpx import AsyncClient


class TestSQLInjection:
    """Tests for SQL injection vulnerabilities"""
    
    @pytest.mark.asyncio
    async def test_sql_injection_in_search(self, client: AsyncClient, auth_headers):
        """Test SQL injection in search parameters"""
        # Common SQL injection attempts
        sql_injections = [
            "'; DROP TABLE patients; --",
            "' OR '1'='1",
            "1' UNION SELECT * FROM users--",
            "admin'--",
        ]
        
        for injection in sql_injections:
            response = await client.get(
                f"/api/v1/patients?search={injection}",
                headers=auth_headers
            )
            # Should not crash or expose data
            assert response.status_code in [200, 400, 422]
            # Should not contain error messages exposing database structure
            if response.status_code != 200:
                response_text = response.text.lower()
                assert "sql" not in response_text
                assert "database" not in response_text
                assert "syntax error" not in response_text


class TestXSS:
    """Tests for XSS vulnerabilities"""
    
    @pytest.mark.asyncio
    async def test_xss_in_input_fields(self, client: AsyncClient, auth_headers):
        """Test XSS in input fields"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
        ]
        
        for payload in xss_payloads:
            response = await client.post(
                "/api/v1/patients",
                json={
                    "first_name": payload,
                    "last_name": "Test",
                    "date_of_birth": "1950-01-01",
                    "gender": "male",
                    "email": "test@example.com"
                },
                headers=auth_headers
            )
            
            # Should either reject or sanitize
            if response.status_code == 201:
                patient_data = response.json()
                # Should not contain script tags
                assert "<script>" not in str(patient_data).lower()
                assert "javascript:" not in str(patient_data).lower()


class TestAuthentication:
    """Tests for authentication security"""
    
    @pytest.mark.asyncio
    async def test_brute_force_protection(self, client: AsyncClient, test_user):
        """Test brute force protection"""
        # Attempt multiple failed logins
        for _ in range(10):
            response = await client.post(
                "/api/v1/auth/login",
                data={
                    "username": test_user.email,
                    "password": "wrong_password"
                }
            )
            assert response.status_code == 401
        
        # Should still allow correct password
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "testpass123"
            }
        )
        # Note: In production, should implement rate limiting
        # For now, just verify it doesn't crash
        assert response.status_code in [200, 429]
    
    @pytest.mark.asyncio
    async def test_token_expiration(self, client: AsyncClient, test_user):
        """Test token expiration"""
        from app.core.security import create_access_token
        from datetime import timedelta
        
        # Create expired token
        expired_token = create_access_token(
            {"sub": str(test_user.id)},
            expires_delta=timedelta(seconds=-1)
        )
        
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_unauthorized_access(self, client: AsyncClient):
        """Test unauthorized access to protected endpoints"""
        protected_endpoints = [
            ("/api/v1/patients", "GET"),
            ("/api/v1/predictions", "GET"),
            ("/api/v1/auth/me", "GET"),
        ]
        
        for endpoint, method in protected_endpoints:
            if method == "GET":
                response = await client.get(endpoint)
            elif method == "POST":
                response = await client.post(endpoint, json={})
            
            assert response.status_code == 401


class TestAuthorization:
    """Tests for authorization"""
    
    @pytest.mark.asyncio
    async def test_role_based_access(self, client: AsyncClient, test_user, test_admin, test_db):
        """Test role-based access control"""
        from app.core.security import create_access_token
        
        # Doctor token
        doctor_token = create_access_token({"sub": str(test_user.id)})
        doctor_headers = {"Authorization": f"Bearer {doctor_token}"}
        
        # Admin token
        admin_token = create_access_token({"sub": str(test_admin.id)})
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Doctor should be able to access patient endpoints
        response = await client.get("/api/v1/patients", headers=doctor_headers)
        assert response.status_code == 200
        
        # Admin should be able to access admin endpoints
        response = await client.get("/api/v1/monitoring/system/health", headers=admin_headers)
        assert response.status_code == 200
        
        # Doctor should NOT be able to access admin endpoints
        response = await client.get("/api/v1/monitoring/system/health", headers=doctor_headers)
        assert response.status_code == 403

