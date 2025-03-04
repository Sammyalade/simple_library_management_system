import requests
import time
import logging
from rest_framework.decorators import api_view
from rest_framework.response import Response
from backend.models import AdminBook

FRONTEND_API_URL = "http://localhost:8000/frontend/webhook/book/"
MAX_RETRIES = 3  # Number of retry attempts
RETRY_DELAY = 5  # Wait time (seconds) before retrying

# Configure logging
logging.basicConfig(filename="webhook_errors.log", level=logging.ERROR)

@api_view(["POST"])
def add_book(request):
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

    logging.error(f"Webhook failed after {MAX_RETRIES} attempts: {data}")
    return Response({"error": "Book added, but sync with frontend failed"}, status=500)

@api_view(["GET"])
def list_books(request):
    return Response(AdminBook.get_all())

@api_view(["DELETE"])
def delete_book(request, title):
    AdminBook.delete(title)
    return Response({"message": f"Book '{title}' deleted successfully!"})

@api_view(["GET"])
def retry_failed_webhooks(request):
    """Retries all failed webhook syncs."""
    try:
        with open("webhook_errors.log", "r") as log_file:
            failed_entries = log_file.readlines()
        
        if not failed_entries:
            return Response({"message": "No failed syncs to retry."})

        success_count = 0
        failed_retries = []

        for entry in failed_entries:
            try:
                data = eval(entry.split("failed after")[1].strip())  # Convert log entry back to dict
                response = requests.post(FRONTEND_API_URL, json=data, timeout=10)
                response.raise_for_status()
                success_count += 1
            except Exception:
                failed_retries.append(entry)

        # Overwrite log with only failed retries
        with open("webhook_errors.log", "w") as log_file:
            log_file.writelines(failed_retries)

        return Response({"message": f"Retried {success_count} failed syncs."})

    except FileNotFoundError:
        return Response({"message": "No webhook errors logged yet."})
