import google_api
import logging

logger = logging.getLogger(__name__)

class book:
    def __init__(self,name):
        gbooks = google_api.connect("books","v1")
        books_count = gbooks.mylibrary().bookshelves().get(shelf = "7").execute()["volumeCount"]
        books_list = gbooks.mylibrary().bookshelves().volumes().list(shelf="7",maxResults = books_count).execute()["items"]
        logger.info(f"Total {books_count} books found")
        for book in books_list:
            if book["volumeInfo"]["title"] == name:
                logger.info(f"Fetching metadata for {name}")
                self.name = book["volumeInfo"]["title"]
                self.url = book["accessInfo"]["webReaderLink"][0:-39]
                self.authors = book["volumeInfo"]["authors"]
                self.publisher = book["volumeInfo"]["publisher"]
                break

        query = f"intitle:{self.name}"
        for author in self.authors:
            query += f" inauthor:{author}"
        query += f" inpublisher:{self.publisher}"

        books_query = gbooks.volumes().list(q = query,orderBy = "relevance",langRestrict ="en-GB,en").execute()["items"][0]
        book_query_response = books_query["volumeInfo"]
        self.thumbnail = book_query_response["imageLinks"]["thumbnail"]
        self.isbn = book_query_response["industryIdentifiers"][0]["identifier"]
        self.id = books_query['id']

        try:
            self.isbn = int(self.isbn)
        except:
            self.isbn = 0

        if "description" in book_query_response:
            self.about = book_query_response["description"]
        else:
            self.about = ""
        if "categories" in book_query_response:
            self.categories = book_query_response["categories"]
        else:
            self.categories = []
        if "pageCount" in book_query_response:
            self.page_count = book_query_response["pageCount"]
        else:
            self.page_count = 0
        if "publishedDate" in book_query_response:
            self.publishedDate = book_query_response["publishedDate"]
        else:
            self.publishedDate = ""

