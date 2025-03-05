import os
import json
import time
import logging
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from backend.models import AdminBook

FRONTEND_API_URL = "http://localhost:8000/frontend/webhook/book/"
MAX_RETRIES = 3  # Number of retry attempts
RETRY_DELAY = 5  # Wait time (seconds) before retrying
LOG_FILE = "webhook_errors.log"

# Configure logging
logging.basicConfig(filename=LOG_FILE, level=logging.ERROR)

@api_view(["POST"])
def add_book(request):
    """Handles adding a book and syncing with the frontend via webhook."""
    data = request.data
    book = AdminBook(
        title=data["title"],
        author=data["author"],
        publisher=data["publisher"],
        category=data["category"]
    )
    book.save()

    # Try sending webhook with retries
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(FRONTEND_API_URL, json=data, timeout=10)
            response.raise_for_status()  # Raise exception for HTTP errors
            return Response({"message": "Book added successfully and synced with frontend!"})
        except requests.RequestException as e:
            logging.error(f"Webhook attempt {attempt + 1} failed: {e}")
            time.sleep(RETRY_DELAY)  # Wait before retrying

    # If all retries fail, log the failed request
    logging.error(f"Webhook failed after {MAX_RETRIES} attempts: {json.dumps(data)}")
    with open(LOG_FILE, "a") as log_file:
        log_file.write(json.dumps(data) + "\n")

    return Response({"error": "Book added, but sync with frontend failed"}, status=500)

@api_view(["GET"])
def list_books(request):
    """Returns a list of all books."""
    return Response(AdminBook.get_all())

@api_view(["DELETE"])
def delete_book(request, title):
    """Deletes a book by title."""
    AdminBook.delete(title)
    return Response({"message": f"Book '{title}' deleted successfully!"})

@api_view(["GET"])
def retry_failed_webhooks(request):
    """Retries all failed webhook syncs."""
    if not os.path.exists(LOG_FILE):
        return Response({"message": "No failed syncs to retry."})

    retried_count = 0
    remaining_failures = []

    with open(LOG_FILE, "r") as log_file:
        failed_entries = log_file.readlines()

    for entry in failed_entries:
        try:
            data = json.loads(entry.strip())  # Proper JSON parsing
            response = requests.post(FRONTEND_API_URL, json=data, timeout=10)

            if response.status_code == 200:
                retried_count += 1
            else:
                remaining_failures.append(entry)  # Keep failed retries

        except json.JSONDecodeError:
            remaining_failures.append(entry)

    # If all were retried successfully, delete log file
    if not remaining_failures:
        os.remove(LOG_FILE)
    else:
        with open(LOG_FILE, "w") as log_file:
            log_file.writelines(remaining_failures)  # Save remaining failures

    return Response({"message": f"Retried {retried_count} failed syncs."})