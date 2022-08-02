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
                break
        query = f"intitle:{self.name} inpublisher:{self.publisher}"
        for author in self.authors:
            query += f" inauthor:{author}"
        book_query_response = gbooks.volumes().list(q = query,orderBy = "relevance",langRestrict ="en-GB,en").execute()["items"][0]["volumeInfo"]
        self.thumbnail_small = book_query_response["imageLinks"]["thumbnail"]
        self.about = book_query_response["description"]
        self.categories = book_query_response["categories"]
        self.isbn = book_query_response["industryIdentifiers"][0]["identifier"]
        self.page_count = book_query_response["pageCount"]
        self.publishedDate = book_query_response["publishedDate"]

        regex_result = re.search(r"(https?:\/\/books.google.com\/books\/content\?id=)(.{12})(.*)",self.thumbnail_small)
        if regex_result is not None:
            self.id = regex_result.group(2)

        book_get_response = gbooks.volumes().get(volumeId = self.id).execute()["volumeInfo"]
        if len(book_get_response["imageLinks"]) == 2:
            self.thumbnail = list(book_get_response["imageLinks"].values())[1]
        elif len(book_get_response["imageLinks"]) > 2:
            self.thumbnail = list(book_get_response["imageLinks"].values())[2]
        logger.info("Finished fetching metadata")
