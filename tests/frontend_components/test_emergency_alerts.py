from datetime import datetime

import pytest


class TestEmergencyAlerts:
    """Test emergency alerts functionality"""

    @pytest.mark.asyncio
    async def test_get_emergency_alerts(self, emergency_service):
        """Test fetching emergency alerts"""
        # Arrange
        alerts = [
            {
                "id": "alert1",
                "type": "safety",
                "severity": "high",
                "title": "محتوى غير مناسب",
                "description": "تم اكتشاف محتوى قد يكون غير مناسب",
                "timestamp": datetime.utcnow().isoformat(),
                "acknowledged": False,
            }
        ]
        emergency_service.get_alerts.return_value = alerts

        # Act
        result = await emergency_service.get_alerts()

        # Assert
        assert len(result) == 1
        assert result[0]["type"] == "safety"
        assert result[0]["severity"] == "high"
        assert result[0]["acknowledged"] is False

    @pytest.mark.asyncio
    async def test_acknowledge_alert(self, emergency_service):
        """Test acknowledging an alert"""
        # Arrange
        emergency_service.acknowledge_alert.return_value = True

        # Act
        result = await emergency_service.acknowledge_alert("alert1")

        # Assert
        assert result is True
        emergency_service.acknowledge_alert.assert_called_once_with("alert1")
