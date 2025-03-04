from django.conf import settings

class AdminBook:
    def __init__(self, title, author, publisher, category):
        self.collection = settings.MONGO_DB["books"]
        self.title = title
        self.author = author
        self.publisher = publisher
        self.category = category

    def save(self):
        self.collection.insert_one({
            "title": self.title,
            "author": self.author,
            "publisher": self.publisher,
            "category": self.category
        })

    @staticmethod
    def get_all():
        return list(settings.MONGO_DB["books"].find({}, {"_id": 0}))

    @staticmethod
    def delete(title):
        settings.MONGO_DB["books"].delete_one({"title": title})
