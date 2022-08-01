import list_docs
import notion_query
from doc_parser import document
import cover
from metadata_fetcher import book
from datetime import datetime,timedelta
import logging
import sys
import re

logging.basicConfig(
        level=logging.DEBUG, 
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
        datefmt='%d/%m/%Y %H:%M:%S' ,     
        handlers=[
        logging.FileHandler("books2notion.log",'w'),
        logging.StreamHandler(sys.stdout),
    ])
logger = logging.getLogger()

def validate_time_diff(doc):
    notion_last_sync_info = notion_query.get_last_sync(doc["docs_id"])
    if notion_last_sync_info is not None:
        logger.info(f"Found existing notion page having docs_id - {doc['docs_id']}")
        notion_last_sync_time = notion_last_sync_info["last_sync_time"]
        notion_last_sync_page_id = notion_last_sync_info["page_id"]
        notion_time_string = notion_last_sync_time[:-10]
        doc_time_string = doc["modified_time"][:-5]
        notion_time = datetime.strptime(notion_time_string,"%Y-%m-%dT%H:%M:%S")
        doc_time = datetime.strptime(doc_time_string,"%Y-%m-%dT%H:%M:%S")
        doc_time = doc_time + timedelta(hours=5,minutes=30)
        
        time_diff = (doc_time - notion_time).total_seconds()/60
        if time_diff > 5:
            logger.info("Time differance is greater than 5 minutes, intitiializing syncing process")
            return notion_last_sync_page_id
        else:
            logger.info("Time difference is less than 5 minutes")
            return False
    else:
        logger.info(f"couldn't find existing notion page for docs_id - {doc['docs_id']}, creating a new page.")
        return None


def main():
    docs = list_docs.ids()
    for doc in docs:
        last_sync_response = validate_time_diff(doc)
        if last_sync_response is not False:
            parsed_document = document(doc["docs_id"])
            if last_sync_response is not None:
                page_id = last_sync_response
                page_id = re.sub("-","",str(page_id))
                notion_query.clear_page_content(page_id)
            else:
                metadata = book(parsed_document.title)
                urls = cover.get_url(metadata.thumbnail)
                properties = notion_query.get_page_properties(parsed_document,metadata,doc["docs_id"])
                children = notion_query.get_header_children(metadata)
                page_id = str(notion_query.create_page(urls,properties,children))
                page_id = re.sub("-","",str(page_id))
        else:
            logger.info(f"Document({doc['docs_id']}) highlights and notes are already synced with notion ")


if __name__ == "__main__":
    main()
