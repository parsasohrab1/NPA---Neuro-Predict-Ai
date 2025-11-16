from app.services.monitoring_service import MonitoringService


def test_prometheus_format_contains_numeric_lines():
    metrics = {
        "metrics": {
            "cpu_usage_percent": 12.5,
            "memory_usage_percent": 64.0,
            "disk_usage_percent": 70.1,
        }
    }
    text = MonitoringService.format_prometheus_metrics(metrics)
    assert "cpu_usage_percent" in text
    assert "memory_usage_percent" in text
    assert "disk_usage_percent" in text
    # formatted as "key value timestamp"
    for line in text.splitlines():
        parts = line.split()
        assert len(parts) == 3
        float(parts[1])  # value
        int(parts[2])    # timestamp


