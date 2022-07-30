import list_docs
import notion_query
from doc_parser import document
import cover
from metadata_fetcher import book
from datetime import datetime,timedelta
import logging
import sys

logging.basicConfig(
        level=logging.DEBUG, 
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
        datefmt='%d/%m/%Y %H:%M:%S' ,     
        handlers=[
        logging.FileHandler("books2notion.log",'w'),
        logging.StreamHandler(sys.stdout),
    ])
logger = logging.getLogger()

def time_diff(doc):
    notion_last_sync_time = notion_query.get_last_sync(doc["docs_id"]) 
    if notion_last_sync_time is not None:

        notion_time_string = notion_last_sync_time(doc["docs_id"])[:-10]
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
        minute_diff = time_diff(doc)
        if minute_diff is None or minute_diff > 5:
            parsed_document = document(doc["docs_id"])
            if minute_diff is not None:
                pass
            else:
                metadata = book(parsed_document.title)
                urls = cover.get_url(metadata.thumbnail)
                properties = notion_query.get_page_properties(parsed_document,metadata,doc["docs_id"])
                notion_query.create_page(urls, properties)





if __name__ == "__main__":
    main()
