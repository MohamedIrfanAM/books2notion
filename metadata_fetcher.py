import google_api

class book:
    def __init__(self,name):
        gbooks = google_api.connect("books","v1")
        books_count = gbooks.mylibrary().bookshelves().get(shelf = "7").execute()["volumeCount"]
        books_list = gbooks.mylibrary().bookshelves().volumes().list(shelf="7",maxResults = books_count).execute()["items"]

        for book in books_list:
            if book["volumeInfo"]["title"] == name:
                self.name = book["volumeInfo"]["title"]
                self.url = book["accessInfo"]["webReaderLink"][0:-39]
                self.authors = book["volumeInfo"]["authors"]
                self.publisher = book["volumeInfo"]["publisher"]
                self.publishedDate = book["volumeInfo"]["publishedDate"]
        book_query_response = gbooks.volumes().list(q = name,orderBy = "relevance").execute()["items"][0]["volumeInfo"]
        self.thumbnail = book_query_response["imageLinks"]["thumbnail"]
        self.about = book_query_response["description"]
        self.categories = book_query_response["categories"]
