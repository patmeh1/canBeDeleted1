"""Test suite for signup functionality"""
import pytest


class TestSignupSuccess:
    """Tests for successful signup scenarios"""
    
    def test_signup_new_student_returns_200(self, client):
        """Test successful signup returns 200 OK"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
    
    def test_signup_adds_student_to_participants(self, client):
        """Test that signup adds student to participants list"""
        email = "newstudent@mergington.edu"
        client.post(f"/activities/Chess Club/signup?email={email}")
        
        # Verify student was added
        response = client.get("/activities")
        data = response.json()
        assert email in data["Chess Club"]["participants"]
    
    def test_signup_returns_success_message(self, client):
        """Test that signup returns appropriate success message"""
        email = "newstudent@mergington.edu"
        response = client.post(f"/activities/Chess Club/signup?email={email}")
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert "Chess Club" in data["message"]
    
    def test_signup_multiple_different_students(self, client):
        """Test signing up multiple different students"""
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        for email in emails:
            response = client.post(f"/activities/Chess Club/signup?email={email}")
            assert response.status_code == 200
        
        # Verify all students were added
        response = client.get("/activities")
        data = response.json()
        for email in emails:
            assert email in data["Chess Club"]["participants"]
    
    def test_signup_same_student_different_activities(self, client):
        """Test that a student can sign up for multiple activities"""
        email = "multitasker@mergington.edu"
        activities = ["Chess Club", "Basketball Team", "Swimming Club"]
        
        for activity in activities:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify student is in all activities
        response = client.get("/activities")
        data = response.json()
        for activity in activities:
            assert email in data[activity]["participants"]
    
    def test_signup_with_url_encoded_activity_name(self, client):
        """Test signup with URL-encoded activity name"""
        email = "student@mergington.edu"
        # "Programming Class" should be URL encoded
        response = client.post(f"/activities/Programming%20Class/signup?email={email}")
        assert response.status_code == 200
        
        # Verify student was added
        response = client.get("/activities")
        data = response.json()
        assert email in data["Programming Class"]["participants"]
    
    def test_signup_with_special_characters_in_email(self, client):
        """Test signup with special characters in email"""
        emails = [
            "john.doe@mergington.edu",
            "jane_smith@mergington.edu",
            "bob+test@mergington.edu"
        ]
        
        for email in emails:
            response = client.post(f"/activities/Chess Club/signup?email={email}")
            assert response.status_code == 200


class TestSignupErrors:
    """Tests for error conditions in signup"""
    
    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test signup to non-existent activity returns 404"""
        response = client.post(
            "/activities/NonExistent Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
    
    def test_signup_nonexistent_activity_error_message(self, client):
        """Test error message for non-existent activity"""
        response = client.post(
            "/activities/NonExistent Club/signup?email=student@mergington.edu"
        )
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_signup_duplicate_student_returns_400(self, client):
        """Test that signing up the same student twice returns 400"""
        email = "student@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response2.status_code == 400
    
    def test_signup_duplicate_student_error_message(self, client):
        """Test error message for duplicate signup"""
        email = "student@mergington.edu"
        
        # First signup
        client.post(f"/activities/Chess Club/signup?email={email}")
        
        # Second signup
        response = client.post(f"/activities/Chess Club/signup?email={email}")
        data = response.json()
        assert "detail" in data
        assert "already registered" in data["detail"].lower()
    
    def test_signup_existing_participant_returns_400(self, client):
        """Test that signing up an existing participant returns 400"""
        # Try to sign up someone who's already in the activity
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
    
    def test_signup_empty_activity_name(self, client):
        """Test signup with empty activity name"""
        response = client.post("/activities/ /signup?email=student@mergington.edu")
        assert response.status_code == 404


class TestSignupEdgeCases:
    """Tests for edge cases in signup"""
    
    def test_signup_preserves_participant_order(self, client):
        """Test that signup preserves the order of participants"""
        emails = ["a@test.edu", "b@test.edu", "c@test.edu"]
        
        for email in emails:
            client.post(f"/activities/Chess Club/signup?email={email}")
        
        response = client.get("/activities")
        data = response.json()
        participants = data["Chess Club"]["participants"]
        
        # New participants should be at the end
        assert participants[-3:] == emails
    
    def test_signup_does_not_modify_other_activities(self, client):
        """Test that signing up for one activity doesn't affect others"""
        # Get initial state
        response = client.get("/activities")
        initial_data = response.json()
        initial_basketball = initial_data["Basketball Team"]["participants"].copy()
        
        # Sign up for Chess Club
        client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        
        # Check Basketball Team is unchanged
        response = client.get("/activities")
        new_data = response.json()
        assert new_data["Basketball Team"]["participants"] == initial_basketball
    
    def test_signup_case_sensitive_activity_name(self, client):
        """Test that activity names are case sensitive"""
        response = client.post(
            "/activities/chess club/signup?email=student@mergington.edu"
        )
        # Should fail because "chess club" != "Chess Club"
        assert response.status_code == 404
