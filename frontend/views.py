from rest_framework import generics
from frontend.models import User, Book, BorrowedBook
from .serializers import UserSerializer, BookSerializer, BorrowedBookSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime, timedelta

class EnrollUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class ListBooksView(generics.ListAPIView):
    queryset = Book.objects.filter(is_available=True)
    serializer_class = BookSerializer

@api_view(["POST"])
def borrow_book(request, book_id):
    try:
        book = Book.objects.get(id=book_id, is_available=True)
        user = User.objects.get(email=request.data.get("email"))  # Get user from request

        borrow_days = int(request.data.get("days", 7))  # Default 7 days
        return_date = datetime.now() + timedelta(days=borrow_days)

        # Create a BorrowedBook record
        BorrowedBook.objects.create(user=user, book=book, return_date=return_date)

        # Mark book as unavailable
        book.is_available = False
        book.return_date = return_date
        book.save()

        return Response({"message": f"Book '{book.title}' borrowed successfully until {return_date}"})

    except Book.DoesNotExist:
        return Response({"error": "Book not available"}, status=400)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=400)
