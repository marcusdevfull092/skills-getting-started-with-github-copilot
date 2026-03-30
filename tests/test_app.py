"""
Unit tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the API"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to original state before each test"""
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
        }
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(original_activities)
    yield
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_success(self, client, reset_activities):
        """Test successfully retrieving all activities"""
        response = client.get("/activities")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all activities are returned
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        
        # Verify activity structure
        assert data["Chess Club"]["max_participants"] == 12
        assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]

    def test_get_activities_list_size(self, client, reset_activities):
        """Test that all activities are returned"""
        response = client.get("/activities")
        data = response.json()
        
        assert len(data) == 3

    def test_get_activities_structure(self, client, reset_activities):
        """Test the structure of returned activities"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_details in data.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client, reset_activities):
        """Test successfully signing up for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Signed up newstudent@mergington.edu for Chess Club"
        
        # Verify student was added to participants
        assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]

    def test_signup_multiple_students_same_activity(self, client, reset_activities):
        """Test multiple students signing up for the same activity"""
        student1 = "student1@mergington.edu"
        student2 = "student2@mergington.edu"
        
        response1 = client.post(f"/activities/Gym%20Class/signup?email={student1}")
        response2 = client.post(f"/activities/Gym%20Class/signup?email={student2}")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert student1 in activities["Gym Class"]["participants"]
        assert student2 in activities["Gym Class"]["participants"]

    def test_signup_same_student_different_activities(self, client, reset_activities):
        """Test the same student signing up for different activities"""
        student = "newstudent@mergington.edu"
        
        response1 = client.post(f"/activities/Chess%20Club/signup?email={student}")
        response2 = client.post(f"/activities/Gym%20Class/signup?email={student}")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert student in activities["Chess Club"]["participants"]
        assert student in activities["Gym Class"]["participants"]

    def test_signup_duplicate_email_same_activity(self, client, reset_activities):
        """Test that the same email cannot sign up twice for the same activity"""
        student = "newstudent@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(f"/activities/Chess%20Club/signup?email={student}")
        assert response1.status_code == 200
        
        # Second signup with same email should fail
        response2 = client.post(f"/activities/Chess%20Club/signup?email={student}")
        assert response2.status_code == 400
        data = response2.json()
        assert "already signed up" in data["detail"].lower()

    def test_signup_activity_not_found(self, client, reset_activities):
        """Test signup for non-existent activity returns 404"""
        response = client.post(
            "/activities/NonExistentActivity/signup?email=student@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_invalid_activity_name(self, client, reset_activities):
        """Test signup with various invalid activity names"""
        invalid_names = ["Basketball", "Drama Club", "Music Ensemble"]
        
        for activity_name in invalid_names:
            response = client.post(
                f"/activities/{activity_name}/signup?email=student@mergington.edu"
            )
            assert response.status_code == 404

    def test_signup_already_signed_up_student(self, client, reset_activities):
        """Test that already signed up students cannot sign up again"""
        # michael@mergington.edu is already in Chess Club
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()

    def test_signup_email_case_sensitivity(self, client, reset_activities):
        """Test email validation (assuming case-sensitive)"""
        email1 = "student@mergington.edu"
        email2 = "Student@mergington.edu"  # Different case
        
        response1 = client.post(f"/activities/Chess%20Club/signup?email={email1}")
        response2 = client.post(f"/activities/Chess%20Club/signup?email={email2}")
        
        # Both should succeed as they are different strings (case-sensitive)
        assert response1.status_code == 200
        assert response2.status_code == 200

    def test_signup_response_format(self, client, reset_activities):
        """Test the response format of a successful signup"""
        response = client.post(
            "/activities/Programming%20Class/signup?email=test@mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "message" in data
        assert isinstance(data["message"], str)
        assert "test@mergington.edu" in data["message"]
        assert "Programming Class" in data["message"]


class TestRootEndpoint:
    """Tests for GET / endpoint"""

    def test_root_redirect(self, client):
        """Test that root path redirects to index.html"""
        response = client.get("/", follow_redirects=False)
        
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"

    def test_root_redirect_follow(self, client):
        """Test root path redirect following"""
        response = client.get("/", follow_redirects=True)
        
        assert response.status_code == 200


class TestActivityData:
    """Tests for activity data structure and consistency"""

    def test_initial_state_activities(self, reset_activities):
        """Test that activities are initialized correctly"""
        assert len(activities) == 3
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities

    def test_activity_max_participants(self, reset_activities):
        """Test max participants for each activity"""
        assert activities["Chess Club"]["max_participants"] == 12
        assert activities["Programming Class"]["max_participants"] == 20
        assert activities["Gym Class"]["max_participants"] == 30

    def test_initial_participants(self, reset_activities):
        """Test initial participants count"""
        assert len(activities["Chess Club"]["participants"]) == 2
        assert len(activities["Programming Class"]["participants"]) == 2
        assert len(activities["Gym Class"]["participants"]) == 2

    def test_available_spots(self, reset_activities):
        """Test calculation of available spots"""
        chess_spots = activities["Chess Club"]["max_participants"] - len(activities["Chess Club"]["participants"])
        assert chess_spots == 10

        programming_spots = activities["Programming Class"]["max_participants"] - len(activities["Programming Class"]["participants"])
        assert programming_spots == 18

        gym_spots = activities["Gym Class"]["max_participants"] - len(activities["Gym Class"]["participants"])
        assert gym_spots == 28


class TestEdgeCases:
    """Tests for edge cases and error scenarios"""

    def test_signup_empty_email(self, client, reset_activities):
        """Test signup with empty email parameter"""
        response = client.post("/activities/Chess%20Club/signup?email=")
        
        # API accepts empty email (no validation on backend)
        # This demonstrates the current API behavior
        assert response.status_code == 200

    def test_signup_special_characters_email(self, client, reset_activities):
        """Test signup with special characters in email"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=student+test@mergington.edu"
        )
        
        # Should succeed as it's a valid email format
        assert response.status_code == 200

    def test_signup_with_spaces_in_activity_name(self, client, reset_activities):
        """Test signup with activity names containing spaces"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=student@mergington.edu"
        )
        
        assert response.status_code == 200

    def test_multiple_enrollments_update_count(self, client, reset_activities):
        """Test that participant count updates correctly"""
        initial_count = len(activities["Chess Club"]["participants"])
        
        client.post("/activities/Chess%20Club/signup?email=new1@mergington.edu")
        assert len(activities["Chess Club"]["participants"]) == initial_count + 1
        
        client.post("/activities/Chess%20Club/signup?email=new2@mergington.edu")
        assert len(activities["Chess Club"]["participants"]) == initial_count + 2
