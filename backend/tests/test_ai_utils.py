from app.services.ai_model_service import AIModelService


def test_confidence_monotonicity():
    svc = AIModelService()
    # Confidence is highest near 0 and 1, lowest at 0.5
    c_low = svc._calculate_confidence(0.01)
    c_mid = svc._calculate_confidence(0.5)
    c_high = svc._calculate_confidence(0.99)
    assert c_low > c_mid
    assert c_high > c_mid
    assert 0.0 <= c_mid <= 1.0


def test_risk_level_thresholds():
    svc = AIModelService()
    assert str(svc._determine_risk_level(0.10)).lower().find("low") != -1
    assert str(svc._determine_risk_level(0.50)).lower().find("medium") != -1
    assert str(svc._determine_risk_level(0.90)).lower().find("high") != -1


