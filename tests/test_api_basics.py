"""Test suite for basic API endpoints"""
import pytest


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static_html(self, client):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
    
    def test_root_redirect_is_temporary(self, client):
        """Test that redirect is a 307 Temporary Redirect"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_200(self, client):
        """Test that getting activities returns 200 OK"""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_json(self, client):
        """Test that response is valid JSON"""
        response = client.get("/activities")
        assert response.headers["content-type"] == "application/json"
        data = response.json()
        assert isinstance(data, dict)
    
    def test_get_activities_contains_all_activities(self, client):
        """Test that all expected activities are returned"""
        response = client.get("/activities")
        data = response.json()
        
        expected_activities = [
            "Chess Club",
            "Basketball Team",
            "Swimming Club",
            "Art Studio",
            "Drama Club",
            "Debate Team",
            "Science Olympiad",
            "Programming Class",
            "Gym Class"
        ]
        
        for activity in expected_activities:
            assert activity in data
    
    def test_activity_has_required_fields(self, client):
        """Test that each activity has all required fields"""
        response = client.get("/activities")
        data = response.json()
        
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity_data in data.items():
            for field in required_fields:
                assert field in activity_data, f"{activity_name} missing {field}"
    
    def test_activity_participants_is_list(self, client):
        """Test that participants field is a list"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert isinstance(activity_data["participants"], list)
    
    def test_activity_max_participants_is_positive(self, client):
        """Test that max_participants is a positive integer"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert isinstance(activity_data["max_participants"], int)
            assert activity_data["max_participants"] > 0
    
    def test_initial_participants_count(self, client):
        """Test that initial participant counts are correct"""
        response = client.get("/activities")
        data = response.json()
        
        # Each activity should start with 2 participants
        for activity_name, activity_data in data.items():
            assert len(activity_data["participants"]) == 2
