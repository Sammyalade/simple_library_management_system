from django.urls import path
from .views import add_book, list_books, delete_book, retry_failed_webhooks

urlpatterns = [
    path("books/add/", add_book, name="add-book"),
    path("books/list/", list_books, name="list-books"),
    path("books/delete/<str:title>/", delete_book, name="delete-book"),
    path("webhooks/retry/", retry_failed_webhooks, name="retry-webhooks"),
]
