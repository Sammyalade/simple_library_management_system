from django.urls import path
from .views import add_book, list_books, delete_book

urlpatterns = [
    path("books/", list_books, name="list-books"),
    path("books/add/", add_book, name="add-book"),
    path("books/delete/<str:title>/", delete_book, name="delete-book"),
]
