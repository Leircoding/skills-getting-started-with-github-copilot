import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    # Reset participants for all activities before each test
    for activity in activities.values():
        activity["participants"] = []


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_for_activity():
    email = "student1@mergington.edu"
    response = client.post(f"/activities/Chess Club/signup?email={email}")
    assert response.status_code == 200
    assert email in activities["Chess Club"]["participants"]
    assert "Signed up" in response.json()["message"]


def test_signup_duplicate():
    email = "student2@mergington.edu"
    client.post(f"/activities/Chess Club/signup?email={email}")
    response = client.post(f"/activities/Chess Club/signup?email={email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_nonexistent_activity():
    response = client.post("/activities/Nonexistent/signup?email=foo@bar.com")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_unregister_from_activity():
    email = "student3@mergington.edu"
    client.post(f"/activities/Chess Club/signup?email={email}")
    response = client.post(f"/activities/Chess Club/unregister?email={email}")
    assert response.status_code == 200
    assert email not in activities["Chess Club"]["participants"]
    assert "Removed" in response.json()["message"]


def test_unregister_not_signed_up():
    email = "student4@mergington.edu"
    response = client.post(f"/activities/Chess Club/unregister?email={email}")
    assert response.status_code == 404
    assert "Participant not found" in response.json()["detail"]


def test_unregister_nonexistent_activity():
    response = client.post("/activities/Nonexistent/unregister?email=foo@bar.com")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]
