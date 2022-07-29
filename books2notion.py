import list_docs
import notion_query
import doc_parser
import cover
from metadata_fetcher import book
from datetime import datetime,timedelta
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S' , filename="books2notion.log" , filemode="w")
logger = logging.getLogger()

def time_diff(doc):
    if notion_query.get_last_sync(doc["docs_id"]):

        notion_time_string = notion_query.get_last_sync(doc["docs_id"])[:-10]
        doc_time_string = doc["modified_time"][:-5]

        notion_time = datetime.strptime(notion_time_string,"%Y-%m-%dT%H:%M:%S")
        doc_time = datetime.strptime(doc_time_string,"%Y-%m-%dT%H:%M:%S")
        doc_time = doc_time + timedelta(hours=5,minutes=30)
        
        time_diff = (doc_time - notion_time).total_seconds()/60
        return time_diff
    else:
        return None

def main():
    docs = list_docs.ids()
    for doc in docs:
        min_diff = time_diff(doc)
        if min_diff > 5 or not min_diff:
            document = doc_parser.document(doc["docs_id"])
            metadata = book(document.title)

if __name__ == "__main__":
    main()
