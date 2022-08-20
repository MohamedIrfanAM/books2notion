import list_docs
from notion_query import notion_client
from doc_parser import document
import cover
from metadata_fetcher import book
from dictionary import dictionary_class
from datetime import datetime
import logging
import sys
import re
import asyncio

logging.basicConfig(
        level=logging.DEBUG, 
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
        datefmt='%d/%m/%Y %H:%M:%S' ,     
        handlers=[
        logging.FileHandler("books2notion.log",'w'),
        logging.StreamHandler(sys.stdout),
    ])
logger = logging.getLogger()

dictionary = dictionary_class()
notion_query = notion_client()

async def validate_time_diff(doc):
    notion_last_sync_info = await notion_query.get_last_sync(doc["docs_id"])
    if notion_last_sync_info is not None:
        logger.info(f"Found existing notion page having docs_id - {doc['docs_id']}")
        notion_last_sync_time = notion_last_sync_info["last_sync_time"]
        full_sync_bool = notion_last_sync_info["full_sync_bool"]
        notion_time_string = notion_last_sync_time[:-10]
        doc_time_string = doc["modified_time"][:-5]
        notion_time = datetime.strptime(notion_time_string,"%Y-%m-%dT%H:%M:%S")
        doc_time_utc = datetime.strptime(doc_time_string,"%Y-%m-%dT%H:%M:%S")
        doc_time = notion_query.utc_to_local(doc_time_utc)
        time_diff = (doc_time - notion_time).total_seconds()/60
        if time_diff >= 0 or full_sync_bool:
            logger.info("New changes found or full_sync mode is enabled, intitiializing syncing process")
            return_info = {
                    "page_id":notion_last_sync_info["page_id"],
                    "progress_no":notion_last_sync_info["progress_no"],
                    "parsed_chapters":notion_last_sync_info["parsed_chapters"],
                    "parsed_highlights":notion_last_sync_info["parsed_highlights"],
                    "parsed_notes":notion_last_sync_info["parsed_notes"],
                    "parsed_new_words":notion_last_sync_info["parsed_new_words"],
                    "full_sync_bool":full_sync_bool
            }
            return return_info
        else:
            logger.info("No new changed found")
            return False
    else:
        logger.info(f"couldn't find existing notion page for docs_id - {doc['docs_id']}, creating a new page.")
        return None


async def sync():
    docs = list_docs.ids()
    for doc in docs:
        last_sync_response = await validate_time_diff(doc)
        if last_sync_response is not False:
            mode = "append"
            parsed_document = None
            page_id = ""
            new_words_id = ""
            if last_sync_response is not None:
                if last_sync_response["full_sync_bool"]:
                    mode = "sync-full"
                page_id = last_sync_response["page_id"]
                page_id = re.sub("-","",str(page_id))
                new_words_id = await notion_query.get_new_words_id(page_id)
                new_words_id = re.sub("-","",str(new_words_id))
                if mode == 'sync' or mode == 'sync-full':
                    await notion_query.clear_page_content(page_id)
                    parsed_document = document(doc["docs_id"])
                    await notion_query.update_properties(page_id,parsed_document)
                    if mode == 'sync-full':
                        await notion_query.delete_new_words(new_words_id)
                else:
                    progress_no = last_sync_response["progress_no"]
                    parsed_chapters = last_sync_response["parsed_chapters"]
                    parsed_highlights = last_sync_response["parsed_highlights"]
                    parsed_notes = last_sync_response["parsed_notes"]
                    parsed_new_words = last_sync_response["parsed_new_words"]
                    parsed_document = document(doc["docs_id"],progress_no,parsed_chapters,parsed_highlights,parsed_notes,parsed_new_words)
                    await notion_query.update_properties(page_id,parsed_document)
            else:
                parsed_document = document(doc["docs_id"])
                metadata = book(parsed_document.title)
                if metadata.thumbnail is not None:
                    urls = cover.get_url(metadata.thumbnail)
                else:
                    urls = None
                properties = notion_query.get_page_properties(parsed_document,metadata,doc["docs_id"])
                children = notion_query.get_header_children(metadata)
                page_id = str( await notion_query.create_page(urls,properties,children))
                page_id = re.sub("-","",str(page_id))
                await notion_query.update_properties(page_id,parsed_document)
                new_words_id = await notion_query.create_new_words_database(page_id)
                new_words_id = re.sub("-","",str(new_words_id))

            logger.info(f"Syncing {parsed_document.title}...")
            for new_word in parsed_document.new_words:
                    if mode == 'sync':
                        if not await notion_query.new_word_exists(new_words_id,new_word):
                                definition = await dictionary.get_definitions(new_word['text'])
                                await notion_query.add_new_word(new_words_id,new_word,definition)
                    elif mode == 'append' or mode == 'sync-full':
                        definition = await dictionary.get_definitions(new_word['text'])
                        await notion_query.add_new_word(new_words_id,new_word,definition)

            for i in range(len(parsed_document.chapters)):
                chapter = parsed_document.chapters[i]
                if len(chapter["title"]) > 0:
                    await notion_query.append_chapter(page_id,chapter)
                highlight_children = []
                for highlight in parsed_document.highlights[i]:
                    highlight_data_blocks = notion_query.get_highlight_blocks(highlight)
                    highlight_children.extend(highlight_data_blocks)
                await notion_query.append_highlights(page_id,highlight_children)

            logger.info(f"Finished syncing {parsed_document.title} successfully")
        else:
            logger.info(f"Document({doc['docs_id']}) highlights and notes are already synced with notion ")

def main():
    asyncio.run(sync())
