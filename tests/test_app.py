"""Integration tests for the Mergington High School Activities API using AAA pattern"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    # Arrange: Store original state
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
            "description": "Competitive basketball team for interscholastic play",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and participate in matches",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["alex@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and sculpture techniques",
            "schedule": "Tuesdays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in plays and musicals throughout the school year",
            "schedule": "Mondays and Thursdays, 4:30 PM - 6:00 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu", "charlotte@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and critical thinking skills",
            "schedule": "Wednesdays and Saturdays, 3:00 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["aiden@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific principles",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 22,
            "participants": ["noah@mergington.edu", "mia@mergington.edu"]
        }
    }
    
    # Clear current activities
    activities.clear()
    # Restore original state
    activities.update(original_activities)
    
    yield
    
    # Cleanup (reset for next test)
    activities.clear()
    activities.update(original_activities)


# ============================================================================
# GET /activities Tests
# ============================================================================

class TestGetActivities:
    """Test suite for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all registered activities"""
        # Arrange: Test client is ready
        
        # Act: Make GET request to activities endpoint
        response = client.get("/activities")
        
        # Assert: Verify response status and content
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Science Club" in data

    def test_get_activities_includes_activity_details(self, client):
        """Test that each activity contains required fields"""
        # Arrange: Test client is ready
        
        # Act: Make GET request to activities endpoint
        response = client.get("/activities")
        
        # Assert: Verify activity structure
        data = response.json()
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club

    def test_get_activities_includes_current_participants(self, client):
        """Test that activity participants are returned correctly"""
        # Arrange: Test client is ready
        
        # Act: Make GET request to activities endpoint
        response = client.get("/activities")
        
        # Assert: Verify participants list matches expected
        data = response.json()
        chess_participants = data["Chess Club"]["participants"]
        assert "michael@mergington.edu" in chess_participants
        assert "daniel@mergington.edu" in chess_participants
        assert len(chess_participants) == 2


# ============================================================================
# POST /activities/{activity_name}/signup Tests
# ============================================================================

class TestSignupForActivity:
    """Test suite for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_student_success(self, client):
        """Test successful signup of a new student for an activity"""
        # Arrange: Prepare test data
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act: Send signup request
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert: Verify response and state change
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert email in activities[activity_name]["participants"]

    def test_signup_duplicate_student_returns_400(self, client):
        """Test that duplicate signup returns 400 error"""
        # Arrange: Prepare test data with existing participant
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in Chess Club
        
        # Act: Send signup request for already-registered student
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert: Verify error response
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()

    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test that signup to non-existent activity returns 404"""
        # Arrange: Prepare test data with invalid activity
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act: Send signup request for invalid activity
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert: Verify 404 response
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_signup_multiple_students_to_same_activity(self, client):
        """Test that multiple different students can signup to same activity"""
        # Arrange: Prepare test data
        activity_name = "Basketball Team"
        email1 = "player1@mergington.edu"
        email2 = "player2@mergington.edu"
        
        # Act: Sign up first student
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email1}
        )
        
        # Act: Sign up second student
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email2}
        )
        
        # Assert: Both signups succeed and participants are added
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert email1 in activities[activity_name]["participants"]
        assert email2 in activities[activity_name]["participants"]

    def test_signup_with_url_encoded_activity_name(self, client):
        """Test signup with URL-encoded activity names (spaces)"""
        # Arrange: Prepare test data with spaces in activity name
        activity_name = "Chess Club"
        encoded_name = "Chess%20Club"
        email = "player@mergington.edu"
        
        # Act: Send signup request with encoded activity name
        response = client.post(
            f"/activities/{encoded_name}/signup",
            params={"email": email}
        )
        
        # Assert: Signup succeeds with encoded name
        assert response.status_code == 200
        assert email in activities[activity_name]["participants"]


# ============================================================================
# POST /activities/{activity_name}/unregister Tests
# ============================================================================

class TestUnregisterFromActivity:
    """Test suite for POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_student_success(self, client):
        """Test successful unregistration of a student from an activity"""
        # Arrange: Prepare test data with existing participant
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        initial_count = len(activities[activity_name]["participants"])
        
        # Act: Send unregister request
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert: Verify response and state change
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count - 1

    def test_unregister_nonexistent_student_returns_400(self, client):
        """Test that unregistering non-registered student returns 400"""
        # Arrange: Prepare test data with non-registered student
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"
        
        # Act: Send unregister request for non-registered student
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert: Verify error response
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"].lower()

    def test_unregister_from_nonexistent_activity_returns_404(self, client):
        """Test that unregister from non-existent activity returns 404"""
        # Arrange: Prepare test data with invalid activity
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act: Send unregister request for invalid activity
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert: Verify 404 response
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_unregister_then_signup_again(self, client):
        """Test that student can signup again after unregistering"""
        # Arrange: Prepare test data
        activity_name = "Programming Class"
        email = "reregister@mergington.edu"
        
        # Act: Sign up for activity
        signup1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Act: Unregister from activity
        unregister = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Act: Sign up again for activity
        signup2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert: All operations succeed
        assert signup1.status_code == 200
        assert unregister.status_code == 200
        assert signup2.status_code == 200
        assert email in activities[activity_name]["participants"]

    def test_unregister_multiple_students_independently(self, client):
        """Test that unregistering one student doesn't affect others"""
        # Arrange: Prepare test data
        activity_name = "Drama Club"
        email1 = "lucas@mergington.edu"
        email2 = "charlotte@mergington.edu"
        
        # Act: Unregister first student
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email1}
        )
        
        # Assert: First student is removed, second remains
        assert response.status_code == 200
        assert email1 not in activities[activity_name]["participants"]
        assert email2 in activities[activity_name]["participants"]

    def test_unregister_with_url_encoded_activity_name(self, client):
        """Test unregister with URL-encoded activity names (spaces)"""
        # Arrange: Prepare test data
        activity_name = "Chess Club"
        encoded_name = "Chess%20Club"
        email = "michael@mergington.edu"
        
        # Act: Send unregister request with encoded activity name
        response = client.post(
            f"/activities/{encoded_name}/unregister",
            params={"email": email}
        )
        
        # Assert: Unregister succeeds with encoded name
        assert response.status_code == 200
        assert email not in activities[activity_name]["participants"]


# ============================================================================
# Integrated Workflow Tests
# ============================================================================

class TestIntegratedWorkflows:
    """Test suite for realistic workflows combining multiple operations"""
    
    def test_complete_signup_and_unregister_workflow(self, client):
        """Test complete workflow: get activities, signup, verify, unregister"""
        # Arrange: Test client is ready
        activity_name = "Tennis Club"
        email = "workflow@mergington.edu"
        
        # Act: Get all activities
        get_response = client.get("/activities")
        initial_participants = len(get_response.json()[activity_name]["participants"])
        
        # Act: Sign up for activity
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Act: Verify signup by getting activities again
        verify_response = client.get("/activities")
        after_signup_participants = len(verify_response.json()[activity_name]["participants"])
        
        # Act: Unregister from activity
        unregister_response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Act: Verify unregister by getting activities again
        final_response = client.get("/activities")
        final_participants = len(final_response.json()[activity_name]["participants"])
        
        # Assert: All steps succeed and participant count is correct
        assert signup_response.status_code == 200
        assert unregister_response.status_code == 200
        assert after_signup_participants == initial_participants + 1
        assert final_participants == initial_participants
        assert email not in final_response.json()[activity_name]["participants"]

    def test_multiple_activities_independent_operations(self, client):
        """Test that operations on one activity don't affect another"""
        # Arrange: Prepare test data for two activities
        activity1 = "Chess Club"
        activity2 = "Gym Class"
        email = "testuser@mergington.edu"
        
        # Act: Sign up for activity 1
        response1 = client.post(
            f"/activities/{activity1}/signup",
            params={"email": email}
        )
        
        # Assert: Activity 1 has new participant, activity 2 doesn't
        assert response1.status_code == 200
        assert email in activities[activity1]["participants"]
        assert email not in activities[activity2]["participants"]
        
        # Act: Sign up for activity 2
        response2 = client.post(
            f"/activities/{activity2}/signup",
            params={"email": email}
        )
        
        # Assert: Both activities now have the participant
        assert response2.status_code == 200
        assert email in activities[activity1]["participants"]
        assert email in activities[activity2]["participants"]
        
        # Act: Unregister from activity 1
        response3 = client.post(
            f"/activities/{activity1}/unregister",
            params={"email": email}
        )
        
        # Assert: Only activity 1 removal affected
        assert response3.status_code == 200
        assert email not in activities[activity1]["participants"]
        assert email in activities[activity2]["participants"]
