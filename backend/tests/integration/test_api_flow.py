"""
Integration Tests for Complete API Flows
"""
import pytest
from httpx import AsyncClient


class TestCompletePredictionFlow:
    """Test complete prediction workflow"""
    
    @pytest.mark.asyncio
    async def test_complete_prediction_workflow(
        self, client: AsyncClient, test_user, test_db
    ):
        """Test complete flow: Login -> Create Patient -> Add Medical Record -> Create Prediction"""
        from app.models.user import User, UserRole
        from app.core.security import get_password_hash, create_access_token
        
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
        
        # 2. Create Patient
        patient_response = await client.post(
            "/api/v1/patients",
            json={
                "first_name": "Integration",
                "last_name": "Test",
                "date_of_birth": "1950-01-01",
                "gender": "male",
                "email": "integration@test.com",
                "phone": "+1234567890"
            },
            headers=headers
        )
        assert patient_response.status_code == 201
        patient_id = patient_response.json()["id"]
        
        # 3. Add Medical Record
        from app.models.medical_record import MedicalRecord
        from datetime import datetime
        
        medical_record = MedicalRecord(
            patient_id=patient_id,
            visit_date=datetime.now(),
            visit_type="Initial",
            mmse_score=25.0,
            moca_score=24.0,
            memory_score=50.0,
            attention_score=50.0,
            executive_function_score=50.0,
            amyloid_beta=600.0,
            tau_protein=200.0,
            dopamine_level=100.0,
            apoe_e4_status=False,
            hippocampal_volume=3500.0,
            cortical_thickness=2.3,
            ventricular_volume=30000.0,
            white_matter_hyperintensities=2.0,
            brain_volume_total=1100000.0
        )
        test_db.add(medical_record)
        await test_db.commit()
        
        # 4. Create Prediction
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
        assert "alzheimer" in prediction_data
        assert "parkinson" in prediction_data
        assert "recommendations" in prediction_data
        
        # 5. Get Prediction
        prediction_id = prediction_data["id"]
        get_response = await client.get(
            f"/api/v1/predictions/{prediction_id}",
            headers=headers
        )
        assert get_response.status_code == 200
        
        # 6. Review Prediction
        review_response = await client.post(
            f"/api/v1/predictions/{prediction_id}/review",
            json={
                "review_notes": "Integration test review",
                "is_reviewed": True
            },
            headers=headers
        )
        assert review_response.status_code == 200


class TestAuthenticationFlow:
    """Test complete authentication flow"""
    
    @pytest.mark.asyncio
    async def test_complete_auth_flow(self, client: AsyncClient, test_user):
        """Test: Login -> Get Current User -> Refresh Token -> Logout"""
        
        # 1. Login
        login_response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "testpass123"
            }
        )
        assert login_response.status_code == 200
        tokens = login_response.json()
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # 2. Get Current User
        me_response = await client.get("/api/v1/auth/me", headers=headers)
        assert me_response.status_code == 200
        user_data = me_response.json()
        assert user_data["email"] == test_user.email
        
        # 3. Refresh Token
        refresh_response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert refresh_response.status_code == 200
        new_access_token = refresh_response.json()["access_token"]
        assert new_access_token != access_token
        
        # 4. Logout
        logout_response = await client.post(
            "/api/v1/auth/logout",
            headers=headers
        )
        assert logout_response.status_code == 200


class TestPatientManagementFlow:
    """Test complete patient management flow"""
    
    @pytest.mark.asyncio
    async def test_patient_crud_flow(self, client: AsyncClient, auth_headers):
        """Test: Create -> Read -> Update -> Delete Patient"""
        
        # 1. Create Patient
        create_response = await client.post(
            "/api/v1/patients",
            json={
                "first_name": "CRUD",
                "last_name": "Test",
                "date_of_birth": "1960-01-01",
                "gender": "female",
                "email": "crud@test.com",
                "phone": "+1234567890"
            },
            headers=auth_headers
        )
        assert create_response.status_code == 201
        patient_id = create_response.json()["id"]
        
        # 2. Read Patient
        get_response = await client.get(
            f"/api/v1/patients/{patient_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 200
        patient_data = get_response.json()
        assert patient_data["first_name"] == "CRUD"
        
        # 3. Update Patient
        update_response = await client.put(
            f"/api/v1/patients/{patient_id}",
            json={
                "first_name": "Updated",
                "last_name": "Test",
                "date_of_birth": "1960-01-01",
                "gender": "female",
                "email": "updated@test.com",
                "phone": "+1234567890"
            },
            headers=auth_headers
        )
        assert update_response.status_code == 200
        updated_data = update_response.json()
        assert updated_data["first_name"] == "Updated"
        
        # 4. Delete Patient
        delete_response = await client.delete(
            f"/api/v1/patients/{patient_id}",
            headers=auth_headers
        )
        assert delete_response.status_code == 200
        
        # 5. Verify Deletion
        get_after_delete = await client.get(
            f"/api/v1/patients/{patient_id}",
            headers=auth_headers
        )
        assert get_after_delete.status_code == 404

