"""Integration tests for complex scenarios"""
import pytest


class TestSignupUnregisterIntegration:
    """Tests for signup and unregister working together"""
    
    def test_signup_then_unregister_cycle(self, client):
        """Test signing up and then unregistering works correctly"""
        email = "cycletest@mergington.edu"
        activity = "Chess Club"
        
        # Sign up
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify signed up
        response = client.get("/activities")
        data = response.json()
        assert email in data[activity]["participants"]
        
        # Unregister
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200
        
        # Verify unregistered
        response = client.get("/activities")
        data = response.json()
        assert email not in data[activity]["participants"]
    
    def test_signup_unregister_signup_again(self, client):
        """Test that a student can re-signup after unregistering"""
        email = "resigner@mergington.edu"
        activity = "Chess Club"
        
        # Sign up
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Unregister
        client.delete(f"/activities/{activity}/unregister?email={email}")
        
        # Sign up again
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify signed up again
        response = client.get("/activities")
        data = response.json()
        assert email in data[activity]["participants"]
    
    def test_multiple_students_complex_workflow(self, client):
        """Test complex workflow with multiple students"""
        students = {
            "alice@test.edu": ["Chess Club", "Drama Club"],
            "bob@test.edu": ["Chess Club", "Basketball Team"],
            "charlie@test.edu": ["Drama Club", "Basketball Team"]
        }
        
        # Sign everyone up
        for email, activities in students.items():
            for activity in activities:
                response = client.post(f"/activities/{activity}/signup?email={email}")
                assert response.status_code == 200
        
        # Verify all signups
        response = client.get("/activities")
        data = response.json()
        assert "alice@test.edu" in data["Chess Club"]["participants"]
        assert "alice@test.edu" in data["Drama Club"]["participants"]
        assert "bob@test.edu" in data["Chess Club"]["participants"]
        
        # Unregister alice from Chess Club
        client.delete("/activities/Chess Club/unregister?email=alice@test.edu")
        
        # Verify alice is only in Drama Club now
        response = client.get("/activities")
        data = response.json()
        assert "alice@test.edu" not in data["Chess Club"]["participants"]
        assert "alice@test.edu" in data["Drama Club"]["participants"]
        
        # Bob should still be in Chess Club
        assert "bob@test.edu" in data["Chess Club"]["participants"]


class TestCapacityManagement:
    """Tests for activity capacity management"""
    
    def test_activity_has_max_participants_limit(self, client):
        """Test that activities have max participant limits defined"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "max_participants" in activity_data
            assert activity_data["max_participants"] > 0
    
    def test_can_fill_activity_to_capacity(self, client):
        """Test that we can fill an activity to its max capacity"""
        response = client.get("/activities")
        data = response.json()
        chess_max = data["Chess Club"]["max_participants"]
        current_count = len(data["Chess Club"]["participants"])
        spots_available = chess_max - current_count
        
        # Fill remaining spots
        for i in range(spots_available):
            email = f"student{i}@test.edu"
            response = client.post(f"/activities/Chess Club/signup?email={email}")
            assert response.status_code == 200
        
        # Verify we're at capacity
        response = client.get("/activities")
        data = response.json()
        assert len(data["Chess Club"]["participants"]) == chess_max
    
    def test_participant_count_accuracy(self, client):
        """Test that participant counts are accurate after operations"""
        # Get initial count
        response = client.get("/activities")
        initial_count = len(response.json()["Chess Club"]["participants"])
        
        # Add 3 students
        for i in range(3):
            client.post(f"/activities/Chess Club/signup?email=new{i}@test.edu")
        
        # Check count increased by 3
        response = client.get("/activities")
        new_count = len(response.json()["Chess Club"]["participants"])
        assert new_count == initial_count + 3
        
        # Remove 2 students
        client.delete("/activities/Chess Club/unregister?email=new0@test.edu")
        client.delete("/activities/Chess Club/unregister?email=new1@test.edu")
        
        # Check count decreased by 2
        response = client.get("/activities")
        final_count = len(response.json()["Chess Club"]["participants"])
        assert final_count == initial_count + 1


class TestDataIntegrity:
    """Tests for data integrity and consistency"""
    
    def test_activity_structure_consistency(self, client):
        """Test that all activities have consistent structure"""
        response = client.get("/activities")
        data = response.json()
        
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity_data in data.items():
            # Check all required fields exist
            for field in required_fields:
                assert field in activity_data
            
            # Check data types
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
    
    def test_no_duplicate_participants_in_same_activity(self, client):
        """Test that no duplicates can exist in participant list"""
        email = "test@mergington.edu"
        
        # Try to sign up twice
        client.post(f"/activities/Chess Club/signup?email={email}")
        client.post(f"/activities/Chess Club/signup?email={email}")
        
        # Verify only one instance exists
        response = client.get("/activities")
        data = response.json()
        count = data["Chess Club"]["participants"].count(email)
        assert count == 1
    
    def test_activities_are_isolated(self, client):
        """Test that modifying one activity doesn't affect others"""
        email = "isolated@test.edu"
        
        # Get initial state of all activities
        response = client.get("/activities")
        initial_data = response.json()
        
        # Modify Chess Club
        client.post(f"/activities/Chess Club/signup?email={email}")
        
        # Check other activities are unchanged
        response = client.get("/activities")
        new_data = response.json()
        
        for activity_name in ["Basketball Team", "Swimming Club", "Drama Club"]:
            assert new_data[activity_name]["participants"] == initial_data[activity_name]["participants"]
    
    def test_participants_list_contains_valid_emails(self, client):
        """Test that all participants have valid email format"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant
                assert len(participant) > 3  # At least x@y format


class TestConcurrentOperations:
    """Tests simulating concurrent operations"""
    
    def test_multiple_signups_to_different_activities(self, client):
        """Test multiple signups happening concurrently"""
        email = "concurrent@test.edu"
        activities = ["Chess Club", "Basketball Team", "Swimming Club", "Drama Club"]
        
        # Sign up to all activities
        responses = []
        for activity in activities:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            responses.append(response)
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200
        
        # Verify presence in all activities
        response = client.get("/activities")
        data = response.json()
        for activity in activities:
            assert email in data[activity]["participants"]
    
    def test_signup_and_unregister_different_students(self, client):
        """Test signing up one student while unregistering another"""
        # Sign up new student
        response1 = client.post(
            "/activities/Chess Club/signup?email=newstudent@test.edu"
        )
        
        # Unregister existing student
        response2 = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        
        # Both should succeed
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify final state
        response = client.get("/activities")
        data = response.json()
        assert "newstudent@test.edu" in data["Chess Club"]["participants"]
        assert "michael@mergington.edu" not in data["Chess Club"]["participants"]
