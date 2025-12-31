import pytest
from fastapi.testclient import TestClient


def test_root_redirect(client: TestClient):
    """Test that root endpoint serves the static index.html"""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    # Check that it contains expected HTML content
    assert "Mergington High School" in response.text
    assert "Extracurricular Activities" in response.text