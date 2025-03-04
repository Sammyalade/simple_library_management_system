from rest_framework import serializers
from .models import User, Book, BorrowedBook

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "firstname", "lastname", "created_at"]

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ["id", "title", "author", "publisher", "category", "is_available", "return_date"]

class BorrowedBookSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    book = BookSerializer()

    class Meta:
        model = BorrowedBook
        fields = ["id", "user", "book", "borrow_date", "return_date"]
