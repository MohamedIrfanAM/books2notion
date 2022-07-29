import google_api
import re
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
                self.publishedDate = book["volumeInfo"]["publishedDate"]
        query = f"intitle:{self.name} inauthor:{self.authors[0]} inpublisher:{self.publisher}"
        book_query_response = gbooks.volumes().list(q = query,orderBy = "relevance",langRestrict ="en-GB,en").execute()["items"][0]["volumeInfo"]
        self.thumbnail_small = book_query_response["imageLinks"]["thumbnail"]
        self.about = book_query_response["description"]
        self.categories = book_query_response["categories"]
        self.isbn = book_query_response["industryIdentifiers"][0]["identifier"]
        self.page_count = book_query_response["pageCount"]

        regex_result = re.search(r"(https?://books.google.com/books/content\?id=)(\w+)(&.*)",self.thumbnail_small)
        self.id = regex_result.group(2)

        book_get_response = gbooks.volumes().get(volumeId = self.id).execute()["volumeInfo"]
        if len(book_get_response["imageLinks"]) == 2:
            self.thumbnail = list(book_get_response["imageLinks"].values())[1]
        elif len(book_get_response["imageLinks"]) > 2:
            self.thumbnail = list(book_get_response["imageLinks"].values())[2]
        logger.info("Finished fetching metadata")
