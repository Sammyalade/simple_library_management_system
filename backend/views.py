from rest_framework.decorators import api_view
from rest_framework.response import Response
from backend.models import AdminBook

@api_view(["POST"])
def add_book(request):
    data = request.data
    book = AdminBook(data["title"], data["author"], data["publisher"], data["category"])
    book.save()
    return Response({"message": "Book added successfully!"})

@api_view(["GET"])
def list_books(request):
    return Response(AdminBook.get_all())

@api_view(["DELETE"])
def delete_book(request, title):
    AdminBook.delete(title)
    return Response({"message": f"Book '{title}' deleted successfully!"})
