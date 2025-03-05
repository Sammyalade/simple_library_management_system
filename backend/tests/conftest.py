import pytest  # ← Add this line
from django.conf import settings
import os

LOG_FILE = "webhook_errors.log"

@pytest.fixture(autouse=True)
def cleanup():
    """Ensure a clean state before and after tests."""
    settings.MONGO_DB["books"].delete_many({})  # Clears all books
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
