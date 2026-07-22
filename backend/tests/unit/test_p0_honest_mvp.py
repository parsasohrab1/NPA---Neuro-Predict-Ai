"""
P0 Honest MVP unit tests:
- AI model fail-closed without weights
- MFA login flow (mocked)
- Deterministic imaging features
- Privacy erase
"""
from __future__ import annotations

import asyncio
from datetime import date, datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest

from app.services.ai_model_service import AIModelService, ModelNotReadyError
from app.services.image_processing_service import ImageProcessingService
from app.services.privacy_service import PrivacyService


# ---------------------------------------------------------------------------
# 1) Fail-closed predict without weights
# ---------------------------------------------------------------------------

class TestFailClosedPredict:
    def test_predict_raises_without_weights_when_mock_disallowed(self, tmp_path):
        with patch("app.services.ai_model_service.settings") as mock_settings:
            mock_settings.DEBUG = False
            mock_settings.ALLOW_MOCK_PREDICTIONS = False
            mock_settings.ENSEMBLE_MODEL_PATH = str(tmp_path / "missing.pth")
            mock_settings.MODELS_DIR = str(tmp_path)
            mock_settings.MAX_CONCURRENT_PREDICTIONS = 2

            service = AIModelService()
            assert service.model_ready is False
            assert service.use_mock is False

            with pytest.raises(ModelNotReadyError, match="weights"):
                asyncio.run(service.predict({"age": 70, "gender": "male"}))

    def test_predict_allows_mock_only_when_debug_and_flag(self, tmp_path):
        with patch("app.services.ai_model_service.settings") as mock_settings:
            mock_settings.DEBUG = True
            mock_settings.ALLOW_MOCK_PREDICTIONS = True
            mock_settings.ENSEMBLE_MODEL_PATH = str(tmp_path / "missing.pth")
            mock_settings.MODELS_DIR = str(tmp_path)
            mock_settings.MAX_CONCURRENT_PREDICTIONS = 2

            service = AIModelService()
            assert service.model_ready is False
            assert service.use_mock is True

            result = asyncio.run(service.predict({"age": 70, "gender": "male", "mmse_score": 25}))
            assert "alzheimer" in result
            assert result["model_name"] == "MockPredictionModel"
            # Deterministic mock — no random.uniform
            result2 = asyncio.run(service.predict({"age": 70, "gender": "male", "mmse_score": 25}))
            assert result["alzheimer"]["risk_score"] == result2["alzheimer"]["risk_score"]

    def test_no_random_init_when_weights_missing(self, tmp_path):
        with patch("app.services.ai_model_service.settings") as mock_settings:
            mock_settings.DEBUG = False
            mock_settings.ALLOW_MOCK_PREDICTIONS = False
            mock_settings.ENSEMBLE_MODEL_PATH = str(tmp_path / "missing.pth")
            mock_settings.MODELS_DIR = str(tmp_path)
            mock_settings.MAX_CONCURRENT_PREDICTIONS = 2

            service = AIModelService()
            assert service.model is None
            assert service.model_ready is False


# ---------------------------------------------------------------------------
# 2) MFA login flow (mocked)
# ---------------------------------------------------------------------------

class TestMFALoginFlow:
    @pytest.mark.asyncio
    async def test_login_returns_mfa_challenge_when_enabled(self):
        from app.api import auth as auth_api
        from app.schemas.user import Token

        user = MagicMock()
        user.id = 42
        user.is_active = True
        user.hashed_password = "hashed"
        user.last_login = None

        mfa = MagicMock()
        mfa.is_enabled = True

        form = MagicMock()
        form.username = "alice"
        form.password = "secret"

        db = AsyncMock()
        # First execute: user lookup; second: MFASecret lookup
        user_result = MagicMock()
        user_result.scalar_one_or_none.return_value = user
        mfa_result = MagicMock()
        mfa_result.scalar_one_or_none.return_value = mfa
        db.execute = AsyncMock(side_effect=[user_result, mfa_result])
        db.commit = AsyncMock()

        with patch("app.api.auth.verify_password", return_value=True), \
             patch("app.api.auth.create_access_token", return_value="mfa.jwt.token") as create_tok:
            token: Token = await auth_api.login(form_data=form, db=db)

        assert token.mfa_required is True
        assert token.mfa_token == "mfa.jwt.token"
        assert token.access_token is None
        assert token.refresh_token is None
        create_tok.assert_called()
        # Should not have issued full login tokens (last_login update skipped when MFA)
        assert user.last_login is None

    @pytest.mark.asyncio
    async def test_login_mfa_issues_tokens_after_verify(self):
        from app.api import auth as auth_api
        from app.schemas.user import MFALoginRequest, Token

        user = MagicMock()
        user.id = 42
        user.is_active = True
        user.last_login = None

        db = AsyncMock()
        user_result = MagicMock()
        user_result.scalar_one_or_none.return_value = user
        db.execute = AsyncMock(return_value=user_result)
        db.commit = AsyncMock()

        payload = MFALoginRequest(mfa_token="pending.jwt", code="123456")

        with patch("app.api.auth.decode_token", return_value={"mfa_pending": 42, "sub": "42"}), \
             patch("app.api.auth.SecurityService.verify_mfa_code", new_callable=AsyncMock, return_value=True), \
             patch("app.api.auth.create_access_token", return_value="access.jwt"), \
             patch("app.api.auth.create_refresh_token", return_value="refresh.jwt"):
            token: Token = await auth_api.login_mfa(payload=payload, db=db)

        assert token.mfa_required is False
        assert token.access_token == "access.jwt"
        assert token.refresh_token == "refresh.jwt"
        assert token.mfa_token is None

    @pytest.mark.asyncio
    async def test_backup_codes_encrypted_on_store(self):
        from app.services.security_service import _encrypt_backup_codes, _decrypt_backup_codes

        codes = ["ABCD1234", "EFGH5678"]
        stored = _encrypt_backup_codes(codes)
        assert isinstance(stored, str)
        assert "ABCD1234" not in stored
        assert _decrypt_backup_codes(stored) == codes


# ---------------------------------------------------------------------------
# 3) Deterministic imaging features
# ---------------------------------------------------------------------------

class TestDeterministicImagingFeatures:
    def test_same_input_same_output(self):
        svc = ImageProcessingService()
        rng = np.random.RandomState(0)
        image = rng.rand(64, 64).astype(np.float32)

        texture = svc.extract_texture_features(image)
        quality = svc.assess_image_quality(image)
        f1 = svc.build_deterministic_imaging_features(image, texture, quality, length=32)
        f2 = svc.build_deterministic_imaging_features(image, texture, quality, length=32)

        assert f1.shape == (32,)
        assert f2.shape == (32,)
        assert np.allclose(f1, f2)
        assert f1.dtype == np.float32

    def test_different_images_differ(self):
        svc = ImageProcessingService()
        a = np.zeros((32, 32), dtype=np.float32)
        b = np.ones((32, 32), dtype=np.float32) * 0.8
        fa = svc.build_deterministic_imaging_features(a, length=32)
        fb = svc.build_deterministic_imaging_features(b, length=32)
        assert not np.allclose(fa, fb)


# ---------------------------------------------------------------------------
# 4) Privacy erase
# ---------------------------------------------------------------------------

class TestPrivacyErase:
    @pytest.mark.asyncio
    async def test_erase_subject_data_redacts_phi(self):
        patient = MagicMock()
        patient.id = 7
        patient.patient_id = "PT-ERASE-1"
        patient.first_name = "Jane"
        patient.last_name = "Doe"
        patient.email = "jane@example.com"
        patient.phone = "555-0100"
        patient.address = "1 Main St"
        patient.medical_history = "secret"
        patient.family_history = "secret"
        patient.current_medications = "secret"
        patient.erased_at = None

        patient_result = MagicMock()
        patient_result.scalar_one_or_none.return_value = patient
        empty_episodes = MagicMock()
        empty_episodes.scalars.return_value.all.return_value = []

        db = AsyncMock()
        db.execute = AsyncMock(side_effect=[patient_result, empty_episodes])
        db.commit = AsyncMock()
        db.refresh = AsyncMock()

        result = await PrivacyService.erase_subject_data(db, "PT-ERASE-1")

        assert result["erased"] is True
        assert patient.first_name == "REDACTED"
        assert patient.last_name == "REDACTED"
        assert patient.email is None
        assert patient.phone is None
        assert patient.address is None
        assert patient.erased_at is not None
        assert result["predictions_retained_deidentified"] is True

    @pytest.mark.asyncio
    async def test_erase_missing_patient(self):
        missing = MagicMock()
        missing.scalar_one_or_none.return_value = None
        db = AsyncMock()
        db.execute = AsyncMock(return_value=missing)

        result = await PrivacyService.erase_subject_data(db, "NOPE")
        assert result["erased"] is False
        assert result["reason"] == "patient_not_found"
