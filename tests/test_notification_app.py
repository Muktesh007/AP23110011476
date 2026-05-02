from unittest.mock import patch
from notification_app_be.app import app


class DummyResponse:
    def __init__(self, data):
        self._data = data

    def json(self):
        return self._data


def test_home_route_returns_status_ok():
    client = app.test_client()
    response = client.get("/")

    assert response.status_code == 200
    assert response.get_json()["message"] == "Notification API is running"


@patch("notification_app_be.app.requests.get")
def test_notifications_route_prioritizes_notifications(mock_get):
    mock_get.return_value = DummyResponse({
        "notifications": [
            {"Type": "Event", "Timestamp": "2025-01-01T12:00:00Z"},
            {"Type": "Placement", "Timestamp": "2025-01-01T11:00:00Z"},
            {"Type": "Result", "Timestamp": "2025-01-01T13:00:00Z"}
        ]
    })

    client = app.test_client()
    response = client.get("/notifications")

    assert response.status_code == 200
    data = response.get_json()
    assert data[0]["Type"] == "Placement"
    assert data[1]["Type"] == "Result"
    assert data[2]["Type"] == "Event"
