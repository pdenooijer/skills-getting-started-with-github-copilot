import pytest
from fastapi.testclient import TestClient


def test_get_activities(client: TestClient):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200

    activities = response.json()
    assert isinstance(activities, dict)
    assert len(activities) > 0

    # Check that each activity has the required fields
    for name, details in activities.items():
        assert "description" in details
        assert "schedule" in details
        assert "max_participants" in details
        assert "participants" in details
        assert isinstance(details["participants"], list)


def test_signup_for_activity(client: TestClient):
    """Test signing up for an activity"""
    # First get activities to find one to test with
    response = client.get("/activities")
    activities = response.json()
    activity_name = list(activities.keys())[0]

    # Test successful signup
    email = "test@example.com"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200

    result = response.json()
    assert "message" in result
    assert email in result["message"]
    assert activity_name in result["message"]

    # Verify the participant was added
    response = client.get("/activities")
    activities = response.json()
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate(client: TestClient):
    """Test signing up for the same activity twice"""
    # First get activities
    response = client.get("/activities")
    activities = response.json()
    activity_name = list(activities.keys())[0]

    email = "duplicate@example.com"
    # First signup
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Second signup should fail
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400

    result = response.json()
    assert "detail" in result
    assert "already signed up" in result["detail"]


def test_signup_nonexistent_activity(client: TestClient):
    """Test signing up for a non-existent activity"""
    response = client.post("/activities/NonExistentActivity/signup?email=test@example.com")
    assert response.status_code == 404

    result = response.json()
    assert "detail" in result
    assert "Activity not found" in result["detail"]


def test_unregister_from_activity(client: TestClient):
    """Test unregistering from an activity"""
    # First get activities
    response = client.get("/activities")
    activities = response.json()
    activity_name = list(activities.keys())[0]

    email = "unregister@example.com"
    # First signup
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Now unregister
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 200

    result = response.json()
    assert "message" in result
    assert email in result["message"]
    assert activity_name in result["message"]

    # Verify the participant was removed
    response = client.get("/activities")
    activities = response.json()
    assert email not in activities[activity_name]["participants"]


def test_unregister_not_signed_up(client: TestClient):
    """Test unregistering when not signed up"""
    # First get activities
    response = client.get("/activities")
    activities = response.json()
    activity_name = list(activities.keys())[0]

    email = "notsignedup@example.com"
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 400

    result = response.json()
    assert "detail" in result
    assert "not signed up" in result["detail"]


def test_unregister_nonexistent_activity(client: TestClient):
    """Test unregistering from a non-existent activity"""
    response = client.delete("/activities/NonExistentActivity/unregister?email=test@example.com")
    assert response.status_code == 404

    result = response.json()
    assert "detail" in result
    assert "Activity not found" in result["detail"]