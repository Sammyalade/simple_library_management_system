import pytest
from frontend.models import User, Book
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
@pytest.mark.django_db
def sample_user():
    """Create a sample user."""
    return User.objects.create(
        email="testuser@example.com",
        firstname="Test",
        lastname="User"
    )

@pytest.fixture
@pytest.mark.django_db
def sample_book():
    """Create a sample book."""
    return Book.objects.create(
        title="Sample Book",
        author="John Doe",
        publisher="TechPress",
        category="Technology",
        is_available=True
    )

@pytest.mark.django_db
def test_enroll_user(api_client):
    """Test user enrollment."""
    response = api_client.post("/frontend/users/enroll/", {
        "email": "newuser@example.com",
        "firstname": "New",
        "lastname": "User"
    })
    assert response.status_code == 201  # Ensure user is created successfully

@pytest.mark.django_db
def test_list_available_books(api_client, sample_book):
    """Test listing available books."""
    response = api_client.get("/frontend/books/")
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["title"] == "Sample Book"

@pytest.mark.django_db
def test_borrow_book_success(api_client, sample_book, sample_user):
    """Test successful book borrowing."""
    response = api_client.post(
        f"/frontend/books/{sample_book.id}/borrow/",
        {"email": sample_user.email, "days": 7},
    )
    assert response.status_code == 200
    assert "borrowed successfully" in response.data["message"]

@pytest.mark.django_db
def test_borrow_book_failure(api_client, sample_user):
    """Test borrowing a book that doesn't exist."""
    response = api_client.post("/frontend/books/999/borrow/", {"email": sample_user.email})
    assert response.status_code == 400
    assert response.data["error"] == "Book not available"

@pytest.mark.django_db
def test_receive_book_webhook(api_client):
    """Test receiving a book through the webhook."""
    book_data = {
        "title": "Webhook Book",
        "author": "Jane Doe",
        "publisher": "WebPress",
        "category": "Fiction"
    }
    response = api_client.post("/frontend/webhook/book/", book_data)
    assert response.status_code == 200
    assert response.data["message"] == "Book added to frontend successfully!"
