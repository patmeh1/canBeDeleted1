"""Test suite for unregister functionality"""
import pytest


class TestUnregisterSuccess:
    """Tests for successful unregister scenarios"""
    
    def test_unregister_existing_student_returns_200(self, client):
        """Test successful unregister returns 200 OK"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
    
    def test_unregister_removes_student_from_participants(self, client):
        """Test that unregister removes student from participants list"""
        email = "michael@mergington.edu"
        
        # Verify student is initially there
        response = client.get("/activities")
        data = response.json()
        assert email in data["Chess Club"]["participants"]
        
        # Unregister
        client.delete(f"/activities/Chess Club/unregister?email={email}")
        
        # Verify student was removed
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Chess Club"]["participants"]
    
    def test_unregister_returns_success_message(self, client):
        """Test that unregister returns appropriate success message"""
        email = "michael@mergington.edu"
        response = client.delete(f"/activities/Chess Club/unregister?email={email}")
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert "Chess Club" in data["message"]
    
    def test_unregister_multiple_students(self, client):
        """Test unregistering multiple students from same activity"""
        emails = ["michael@mergington.edu", "daniel@mergington.edu"]
        
        for email in emails:
            response = client.delete(f"/activities/Chess Club/unregister?email={email}")
            assert response.status_code == 200
        
        # Verify all students were removed
        response = client.get("/activities")
        data = response.json()
        for email in emails:
            assert email not in data["Chess Club"]["participants"]
    
    def test_unregister_from_multiple_activities(self, client):
        """Test unregistering same student from multiple activities"""
        email = "test@mergington.edu"
        activities = ["Chess Club", "Basketball Team", "Swimming Club"]
        
        # Sign up for all activities
        for activity in activities:
            client.post(f"/activities/{activity}/signup?email={email}")
        
        # Unregister from all activities
        for activity in activities:
            response = client.delete(f"/activities/{activity}/unregister?email={email}")
            assert response.status_code == 200
        
        # Verify student is removed from all
        response = client.get("/activities")
        data = response.json()
        for activity in activities:
            assert email not in data[activity]["participants"]
    
    def test_unregister_with_url_encoded_activity_name(self, client):
        """Test unregister with URL-encoded activity name"""
        email = "emma@mergington.edu"
        
        # Unregister from Programming Class
        response = client.delete(f"/activities/Programming%20Class/unregister?email={email}")
        assert response.status_code == 200
        
        # Verify student was removed
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Programming Class"]["participants"]
    
    def test_unregister_does_not_affect_other_participants(self, client):
        """Test that unregistering one student doesn't affect others"""
        # Get initial participants
        response = client.get("/activities")
        initial_data = response.json()
        initial_participants = initial_data["Chess Club"]["participants"].copy()
        
        # Unregister one student
        client.delete("/activities/Chess Club/unregister?email=michael@mergington.edu")
        
        # Check other student is still there
        response = client.get("/activities")
        data = response.json()
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]
        assert len(data["Chess Club"]["participants"]) == len(initial_participants) - 1


class TestUnregisterErrors:
    """Tests for error conditions in unregister"""
    
    def test_unregister_nonexistent_activity_returns_404(self, client):
        """Test unregister from non-existent activity returns 404"""
        response = client.delete(
            "/activities/NonExistent Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
    
    def test_unregister_nonexistent_activity_error_message(self, client):
        """Test error message for non-existent activity"""
        response = client.delete(
            "/activities/NonExistent Club/unregister?email=student@mergington.edu"
        )
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_unregister_non_registered_student_returns_400(self, client):
        """Test unregistering a student who isn't registered returns 400"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
    
    def test_unregister_non_registered_student_error_message(self, client):
        """Test error message for non-registered student"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
        )
        data = response.json()
        assert "detail" in data
        assert "not registered" in data["detail"].lower()
    
    def test_unregister_twice_returns_400(self, client):
        """Test that unregistering the same student twice returns 400"""
        email = "michael@mergington.edu"
        
        # First unregister should succeed
        response1 = client.delete(f"/activities/Chess Club/unregister?email={email}")
        assert response1.status_code == 200
        
        # Second unregister should fail
        response2 = client.delete(f"/activities/Chess Club/unregister?email={email}")
        assert response2.status_code == 400
    
    def test_unregister_from_wrong_activity(self, client):
        """Test unregistering from an activity the student isn't in"""
        # michael is in Chess Club, not Basketball Team
        response = client.delete(
            "/activities/Basketball Team/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 400
    
    def test_unregister_empty_activity_name(self, client):
        """Test unregister with empty activity name"""
        response = client.delete(
            "/activities/ /unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404


class TestUnregisterEdgeCases:
    """Tests for edge cases in unregister"""
    
    def test_unregister_preserves_other_participants_order(self, client):
        """Test that unregistering preserves order of remaining participants"""
        # Add more participants
        emails = ["a@test.edu", "b@test.edu", "c@test.edu"]
        for email in emails:
            client.post(f"/activities/Chess Club/signup?email={email}")
        
        # Get current participants
        response = client.get("/activities")
        data = response.json()
        participants_before = data["Chess Club"]["participants"].copy()
        
        # Unregister the middle one
        client.delete("/activities/Chess Club/unregister?email=b@test.edu")
        
        # Check order is preserved
        response = client.get("/activities")
        data = response.json()
        participants_after = data["Chess Club"]["participants"]
        
        # Should have a@test.edu and c@test.edu in the same relative positions
        assert "a@test.edu" in participants_after
        assert "c@test.edu" in participants_after
        assert "b@test.edu" not in participants_after
        assert participants_after.index("a@test.edu") < participants_after.index("c@test.edu")
    
    def test_unregister_does_not_modify_other_activities(self, client):
        """Test that unregistering from one activity doesn't affect others"""
        # Get initial state
        response = client.get("/activities")
        initial_data = response.json()
        initial_basketball = initial_data["Basketball Team"]["participants"].copy()
        
        # Unregister from Chess Club
        client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        
        # Check Basketball Team is unchanged
        response = client.get("/activities")
        new_data = response.json()
        assert new_data["Basketball Team"]["participants"] == initial_basketball
    
    def test_unregister_case_sensitive_activity_name(self, client):
        """Test that activity names are case sensitive"""
        response = client.delete(
            "/activities/chess club/unregister?email=michael@mergington.edu"
        )
        # Should fail because "chess club" != "Chess Club"
        assert response.status_code == 404
    
    def test_unregister_case_sensitive_email(self, client):
        """Test that email comparison is case sensitive"""
        # michael@mergington.edu exists, but MICHAEL@mergington.edu doesn't
        response = client.delete(
            "/activities/Chess Club/unregister?email=MICHAEL@mergington.edu"
        )
        assert response.status_code == 400
