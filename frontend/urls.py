from django.urls import path
from .views import EnrollUserView, ListBooksView, borrow_book, receive_book_webhook

urlpatterns = [
    path("users/enroll/", EnrollUserView.as_view(), name="enroll-user"),
    path("books/", ListBooksView.as_view(), name="list-books"),
    path("books/<int:book_id>/borrow/", borrow_book, name="borrow-book"),
    path("webhook/book/", receive_book_webhook, name="receive-book-webhook"),
]
