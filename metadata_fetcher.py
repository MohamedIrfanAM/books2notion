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
                self.found_book = True
                self.name = book["volumeInfo"]["title"]
                self.url = book["accessInfo"]["webReaderLink"][0:-39]
                if "authors" in book["volumeInfo"]:
                    self.authors = book["volumeInfo"]["authors"]
                else:
                    self.authors = []
                if "publisher" in book["volumeInfo"]:
                    self.publisher = book["volumeInfo"]["publisher"]
                else:
                    self.publisher = ""

                query = f"intitle:{self.name}"
                for author in self.authors:
                    query += f" inauthor:{author}"
                if len(self.publisher):
                    query += f" inpublisher:{self.publisher}"

                try:
                    books_query = gbooks.volumes().list(q = query,orderBy = "relevance",langRestrict ="en-GB,en").execute()["items"][0]
                    book_query_response = books_query["volumeInfo"]

                    if "imageLinks" in book_query_response:
                        self.thumbnail = book_query_response["imageLinks"]["thumbnail"]
                    else:
                        self.thumbnail = None
                    if "industryIdentifiers" in book_query_response:
                        self.isbn = book_query_response["industryIdentifiers"][0]["identifier"]
                    else:
                        self.isbn = 0
                    if "id" in book_query_response:
                        self.id = books_query['id']
                    else:
                        self.id = ""
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

                    try:
                        self.isbn = int(self.isbn)
                    except:
                        self.isbn = 0
                except:
                    self.thumbnail = None
                    self.isbn = 0
                    self.id = ""
                    self.about = ""
                    self.categories = []
                    self.page_count = 0
                    self.publishedDate = ""
                break
        else:
            self.found_book = False
            logger.info(f"Book with title '{name}' does not exist in books library")

