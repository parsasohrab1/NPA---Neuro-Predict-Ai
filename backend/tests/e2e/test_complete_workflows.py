"""
End-to-End Tests for Complete User Workflows
"""
import pytest
from httpx import AsyncClient


class TestDoctorWorkflow:
    """E2E tests for doctor workflow"""
    
    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_complete_doctor_workflow(self, client: AsyncClient, test_user, test_db):
        """Test complete doctor workflow: Login -> Dashboard -> Patient Management -> Prediction"""
        from app.core.security import create_access_token
        
        # 1. Login
        login_response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "testpass123"
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. View Dashboard (Get current user)
        me_response = await client.get("/api/v1/auth/me", headers=headers)
        assert me_response.status_code == 200
        user_data = me_response.json()
        assert user_data["role"] == "doctor"
        
        # 3. View Patients List
        patients_response = await client.get("/api/v1/patients", headers=headers)
        assert patients_response.status_code == 200
        
        # 4. Create New Patient
        patient_response = await client.post(
            "/api/v1/patients",
            json={
                "first_name": "E2E",
                "last_name": "Patient",
                "date_of_birth": "1955-03-15",
                "gender": "male",
                "email": "e2e.patient@test.com",
                "phone": "+1234567890",
                "address": "123 Test St"
            },
            headers=headers
        )
        assert patient_response.status_code == 201
        patient_id = patient_response.json()["id"]
        
        # 5. Add Medical Record
        from app.models.medical_record import MedicalRecord
        from datetime import datetime
        
        medical_record = MedicalRecord(
            patient_id=patient_id,
            visit_date=datetime.now(),
            visit_type="Initial",
            mmse_score=24.0,
            moca_score=23.0,
            memory_score=48.0,
            attention_score=48.0,
            executive_function_score=48.0,
            amyloid_beta=650.0,
            tau_protein=220.0,
            dopamine_level=95.0,
            apoe_e4_status=True,
            hippocampal_volume=3300.0,
            cortical_thickness=2.2,
            ventricular_volume=32000.0,
            white_matter_hyperintensities=3.0,
            brain_volume_total=1080000.0
        )
        test_db.add(medical_record)
        await test_db.commit()
        
        # 6. Create Prediction
        prediction_response = await client.post(
            "/api/v1/predictions",
            json={
                "patient_id": patient_id,
                "disease_type": "alzheimer"
            },
            headers=headers
        )
        assert prediction_response.status_code == 201
        prediction_data = prediction_response.json()
        prediction_id = prediction_data["id"]
        
        # 7. View Prediction Results
        view_prediction = await client.get(
            f"/api/v1/predictions/{prediction_id}",
            headers=headers
        )
        assert view_prediction.status_code == 200
        pred_data = view_prediction.json()
        assert "alzheimer" in pred_data
        assert "recommendations" in pred_data
        
        # 8. Review Prediction
        review_response = await client.post(
            f"/api/v1/predictions/{prediction_id}/review",
            json={
                "review_notes": "E2E test review - confirmed high risk",
                "is_reviewed": True
            },
            headers=headers
        )
        assert review_response.status_code == 200
        
        # 9. View Patient with Predictions
        patient_with_preds = await client.get(
            f"/api/v1/patients/{patient_id}",
            headers=headers
        )
        assert patient_with_preds.status_code == 200


class TestAdminWorkflow:
    """E2E tests for admin workflow"""
    
    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_complete_admin_workflow(self, client: AsyncClient, test_admin):
        """Test complete admin workflow: Login -> Monitoring -> System Health"""
        from app.core.security import create_access_token
        
        # 1. Login as Admin
        login_response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": test_admin.email,
                "password": "admin123"
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. View Admin Dashboard (Get current user)
        me_response = await client.get("/api/v1/auth/me", headers=headers)
        assert me_response.status_code == 200
        user_data = me_response.json()
        assert user_data["role"] == "admin"
        
        # 3. Monitor AI/ML Health
        ml_health = await client.get(
            "/api/v1/monitoring/ai/ml-health?hours=24",
            headers=headers
        )
        assert ml_health.status_code == 200
        
        # 4. Monitor System Health
        system_health = await client.get(
            "/api/v1/monitoring/system/health",
            headers=headers
        )
        assert system_health.status_code == 200
        
        # 5. View Audit Logs
        audit_logs = await client.get(
            "/api/v1/monitoring/security/audit-logs?limit=50",
            headers=headers
        )
        assert audit_logs.status_code == 200
        
        # 6. View System Performance
        performance = await client.get(
            "/api/v1/monitoring/system/performance?hours=24",
            headers=headers
        )
        assert performance.status_code == 200


class TestErrorRecovery:
    """E2E tests for error recovery scenarios"""
    
    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_error_recovery_workflow(self, client: AsyncClient, auth_headers):
        """Test system behavior under error conditions"""
        
        # 1. Try to access nonexistent resource
        response = await client.get(
            "/api/v1/patients/99999",
            headers=auth_headers
        )
        assert response.status_code == 404
        
        # 2. Try invalid request
        response = await client.post(
            "/api/v1/patients",
            json={"invalid": "data"},
            headers=auth_headers
        )
        assert response.status_code in [400, 422]
        
        # 3. System should still work after errors
        response = await client.get(
            "/api/v1/patients",
            headers=auth_headers
        )
        assert response.status_code == 200


class TestConcurrentAccess:
    """E2E tests for concurrent user access"""
    
    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_concurrent_users(self, client: AsyncClient, test_user, test_admin):
        """Test multiple users accessing system concurrently"""
        import asyncio
        from app.core.security import create_access_token
        
        async def doctor_workflow():
            token = create_access_token({"sub": str(test_user.id)})
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.get("/api/v1/patients", headers=headers)
            return response.status_code == 200
        
        async def admin_workflow():
            token = create_access_token({"sub": str(test_admin.id)})
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.get("/api/v1/monitoring/system/health", headers=headers)
            return response.status_code == 200
        
        # Run concurrent workflows
        results = await asyncio.gather(
            doctor_workflow(),
            admin_workflow(),
            doctor_workflow(),
            admin_workflow()
        )
        
        assert all(results)

