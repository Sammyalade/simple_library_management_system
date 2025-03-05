import pytest
import os
import json
import time
import logging
import requests
from rest_framework.test import APIClient
from backend.models import AdminBook
from backend.views import retry_failed_webhooks

FRONTEND_API_URL = "http://localhost:8000/frontend/webhook/book/"
LOG_FILE = "webhook_errors.log"
logger = logging.getLogger(__name__)

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def sample_book():
    return {
        "title": "Test Book",
        "author": "John Doe",
        "publisher": "TechPress",
        "category": "Technology"
    }

@pytest.fixture(autouse=True)
def cleanup():
    """Ensure a clean state before and after tests."""
    AdminBook.clear()  # Clear MongoDB collection
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

def test_add_book_success(api_client, sample_book, requests_mock):
    """Test adding a book with a successful webhook call."""
    requests_mock.post(FRONTEND_API_URL, json={"message": "Synced successfully"}, status_code=200)
    response = api_client.post("/backend/books/add/", sample_book, format="json")
    
    assert response.status_code == 200
    assert response.json()["message"] == "Book added successfully and synced with frontend!"
    assert any(book["title"] == sample_book["title"] for book in AdminBook.get_all())

def test_add_book_webhook_failure(api_client, sample_book, requests_mock):
    """Test adding a book when the webhook fails after retries."""
    requests_mock.post(FRONTEND_API_URL, status_code=500)
    response = api_client.post("/backend/books/add/", sample_book, format="json")
    
    assert response.status_code == 500
    assert response.json()["error"] == "Book added, but sync with frontend failed"
    assert os.path.exists(LOG_FILE)  # Ensure failure is logged

def test_list_books(api_client, sample_book):
    """Test listing books."""
    book = AdminBook(**sample_book)
    book.save()
    response = api_client.get("/backend/books/list/")
    
    assert response.status_code == 200
    assert any(book["title"] == sample_book["title"] for book in response.json())

def test_delete_book(api_client, sample_book):
    """Test deleting a book."""
    book = AdminBook(**sample_book)
    book.save()
    response = api_client.delete(f"/backend/books/delete/{sample_book['title']}/")
    
    assert response.status_code == 200
    assert not any(book["title"] == sample_book["title"] for book in AdminBook.get_all())

def test_retry_failed_webhooks(api_client, sample_book, requests_mock):
    """Test retrying failed webhooks."""
    with open(LOG_FILE, "w") as log_file:
        log_file.write(json.dumps(sample_book) + "\n")

    requests_mock.post(FRONTEND_API_URL, json={"message": "Synced"}, status_code=200)

    response = api_client.get("/backend/webhooks/retry/")  # Use API client instead of direct function call

    assert response.status_code == 200
    assert "Retried 1 failed syncs" in response.json()["message"]

    # Allow some time for file operations
    time.sleep(1)

    assert not os.path.exists(LOG_FILE)  # Ensure log file is deleted after successful retries
