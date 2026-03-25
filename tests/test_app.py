"""
Tests for the High School Management System API

Tests follow the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and preconditions
- Act: Execute the code being tested
- Assert: Verify the results
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Arrange: Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Arrange: Reset activities to initial state before each test"""
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team for varsity and JV players",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and participate in friendly matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["alex@mergington.edu", "sarah@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and other visual arts",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["nina@mergington.edu"]
        },
        "Music Ensemble": {
            "description": "Join the school orchestra and perform in concerts",
            "schedule": "Mondays and Fridays, 4:00 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu", "isabella@mergington.edu"]
        },
        "Debate Team": {
            "description": "Compete in debate tournaments and develop public speaking skills",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 10,
            "participants": ["thomas@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["grace@mergington.edu", "david@mergington.edu"]
        }
    }
    
    yield
    
    # Reset after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_list(self, client, reset_activities):
        """
        Arrange: Test client is ready
        Act: Request all activities
        Assert: Response contains all 9 activities
        """
        # Arrange (implicit via fixtures)
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_get_activities_contains_required_fields(self, client, reset_activities):
        """
        Arrange: Test client ready with sample activity
        Act: Request all activities
        Assert: Each activity has required fields
        """
        # Arrange (implicit)
        
        # Act
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        # Assert
        assert response.status_code == 200
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)
    
    def test_get_activities_returns_correct_participants(self, client, reset_activities):
        """
        Arrange: Known participants in Chess Club
        Act: Request activities
        Assert: Participants list matches expected members
        """
        # Arrange
        expected_participants = ["michael@mergington.edu", "daniel@mergington.edu"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        actual_participants = data["Chess Club"]["participants"]
        
        # Assert
        assert response.status_code == 200
        assert actual_participants == expected_participants


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant_success(self, client, reset_activities):
        """
        Arrange: New email not yet registered
        Act: Send signup request
        Assert: Request succeeds with confirmation message
        """
        # Arrange
        new_email = "john_doe@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": new_email}
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in data["message"]
        assert new_email in data["message"]
    
    def test_signup_adds_participant_to_activity(self, client, reset_activities):
        """
        Arrange: Fresh activities state
        Act: Sign up new participant
        Assert: Participant appears in activity list
        """
        # Arrange
        new_email = "track_student@mergington.edu"
        activity = "Gym Class"
        get_before = client.get("/activities").json()
        initial_count = len(get_before[activity]["participants"])
        
        # Act
        client.post(
            f"/activities/{activity}/signup",
            params={"email": new_email}
        )
        
        # Assert
        get_after = client.get("/activities").json()
        participants = get_after[activity]["participants"]
        
        assert len(participants) == initial_count + 1
        assert new_email in participants
    
    def test_signup_duplicate_participant_rejected(self, client, reset_activities):
        """
        Arrange: Participant already registered (michael@mergington.edu)
        Act: Attempt to sign up same person again
        Assert: Request fails with 400 error
        """
        # Arrange
        duplicate_email = "michael@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": duplicate_email}
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_nonexistent_activity_rejected(self, client, reset_activities):
        """
        Arrange: Activity does not exist
        Act: Attempt signup for fake activity
        Assert: Request fails with 404 error
        """
        # Arrange
        email = "student@mergington.edu"
        fake_activity = "Nonexistent Activity"
        
        # Act
        response = client.post(
            f"/activities/{fake_activity}/signup",
            params={"email": email}
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in data["detail"]
    
    def test_signup_with_various_email_formats(self, client, reset_activities):
        """
        Arrange: Multiple email format variations
        Act: Sign up with each email format
        Assert: All signups succeed
        """
        # Arrange
        test_emails = [
            "student+tag@mergington.edu",
            "user.name@mergington.edu",
            "test123@mergington.edu"
        ]
        activity = "Programming Class"
        
        # Act & Assert
        for email in test_emails:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": email}
            )
            assert response.status_code == 200


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/remove endpoint"""
    
    def test_remove_participant_success(self, client, reset_activities):
        """
        Arrange: Participant exists in activity
        Act: Send delete request
        Assert: Request succeeds with confirmation message
        """
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client.delete(
            f"/activities/{activity}/remove",
            params={"email": email}
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert "Removed" in data["message"]
        assert email in data["message"]
    
    def test_remove_participant_removes_from_list(self, client, reset_activities):
        """
        Arrange: Two participants in Chess Club, remove one
        Act: Delete first participant
        Assert: Participant removed, other remains
        """
        # Arrange
        email_to_remove = "michael@mergington.edu"
        email_to_keep = "daniel@mergington.edu"
        activity = "Chess Club"
        get_before = client.get("/activities").json()
        initial_count = len(get_before[activity]["participants"])
        
        # Act
        client.delete(
            f"/activities/{activity}/remove",
            params={"email": email_to_remove}
        )
        
        # Assert
        get_after = client.get("/activities").json()
        participants = get_after[activity]["participants"]
        
        assert len(participants) == initial_count - 1
        assert email_to_remove not in participants
        assert email_to_keep in participants
    
    def test_remove_nonexistent_participant_rejected(self, client, reset_activities):
        """
        Arrange: Email never registered
        Act: Attempt to remove non-existent participant
        Assert: Request fails with 400 error
        """
        # Arrange
        email = "never_registered@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client.delete(
            f"/activities/{activity}/remove",
            params={"email": email}
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 400
        assert "not signed up" in data["detail"].lower()
    
    def test_remove_from_nonexistent_activity_rejected(self, client, reset_activities):
        """
        Arrange: Activity doesn't exist
        Act: Attempt to remove from fake activity
        Assert: Request fails with 404 error
        """
        # Arrange
        email = "student@mergington.edu"
        fake_activity = "Fake Activity"
        
        # Act
        response = client.delete(
            f"/activities/{fake_activity}/remove",
            params={"email": email}
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in data["detail"]
    
    def test_remove_and_signup_same_participant(self, client, reset_activities):
        """
        Arrange: Participant registered
        Act: Remove, then sign up again
        Assert: Both operations succeed
        """
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess Club"
        
        # Act - Remove
        remove_response = client.delete(
            f"/activities/{activity}/remove",
            params={"email": email}
        )
        
        # Assert removal
        assert remove_response.status_code == 200
        
        # Act - Sign up again
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert re-signup
        assert signup_response.status_code == 200
        
        # Verify in list
        get_response = client.get("/activities").json()
        assert email in get_response[activity]["participants"]


class TestRoot:
    """Tests for GET / endpoint"""
    
    def test_root_endpoint_redirects(self, client, reset_activities):
        """
        Arrange: Test client ready
        Act: Request root endpoint without following redirect
        Assert: Returns 307 redirect to static index
        """
        # Arrange (implicit)
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
    
    def test_root_endpoint_redirect_follows(self, client, reset_activities):
        """
        Arrange: Test client ready
        Act: Request root and follow redirect
        Assert: Eventually returns successful response
        """
        # Arrange (implicit)
        
        # Act
        response = client.get("/", follow_redirects=True)
        
        # Assert
        assert response.status_code == 200


class TestIntegration:
    """Integration tests: complete user workflows"""
    
    def test_signup_and_remove_full_workflow(self, client, reset_activities):
        """
        Arrange: New participant and activity selected
        Act: Sign up, verify, remove, verify
        Assert: State changes are correct at each step
        """
        # Arrange
        new_email = "workflow_test@mergington.edu"
        activity = "Gym Class"
        
        initial_state = client.get("/activities").json()
        initial_count = len(initial_state[activity]["participants"])
        
        # Act 1: Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": new_email}
        )
        
        # Assert 1: Signup succeeded
        assert signup_response.status_code == 200
        
        # Act 2: Verify signup
        after_signup_state = client.get("/activities").json()
        after_signup_count = len(after_signup_state[activity]["participants"])
        
        # Assert 2: Participant added
        assert after_signup_count == initial_count + 1
        assert new_email in after_signup_state[activity]["participants"]
        
        # Act 3: Remove
        remove_response = client.delete(
            f"/activities/{activity}/remove",
            params={"email": new_email}
        )
        
        # Assert 3: Remove succeeded
        assert remove_response.status_code == 200
        
        # Act 4: Verify removal
        after_removal_state = client.get("/activities").json()
        after_removal_count = len(after_removal_state[activity]["participants"])
        
        # Assert 4: Participant removed, back to original count
        assert after_removal_count == initial_count
        assert new_email not in after_removal_state[activity]["participants"]
    
    def test_multiple_participants_signup_workflow(self, client, reset_activities):
        """
        Arrange: Multiple new emails
        Act: Sign up all to same activity
        Assert: All added successfully, participant count increases
        """
        # Arrange
        new_emails = ["alice@mergington.edu", "bob@mergington.edu", "charlie@mergington.edu"]
        activity = "Art Studio"
        
        initial_state = client.get("/activities").json()
        initial_count = len(initial_state[activity]["participants"])
        
        # Act
        for email in new_emails:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Assert
        final_state = client.get("/activities").json()
        final_count = len(final_state[activity]["participants"])
        final_participants = final_state[activity]["participants"]
        
        assert final_count == initial_count + len(new_emails)
        for email in new_emails:
            assert email in final_participants
