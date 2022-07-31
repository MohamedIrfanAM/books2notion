import requests
import json
import logging

logger = logging.getLogger(__name__)

secret_file = open('secrets.json') 
secret_data = json.load(secret_file) 

key = secret_data['key']
database_id = secret_data['database_id']

secret_file.close() 

query_url = f"https://api.notion.com/v1/databases/{database_id}/query"
page_url = "https://api.notion.com/v1/pages" 
block_url = "https://api.notion.com/v1/blocks/"

headers = {
    'Authorization': f'Bearer {key}',
    "Notion-Version": "2022-02-22",
    "Accept": "application/json",
    "Content-Type": "application/json",
}

def get_last_sync(docs_id):
    logger.info(f"getting last_sync time for docs_id - {docs_id}")
    filter_data = {
        "filter": {
            "property": "docs_id",
            "rich_text": {
                "equals": docs_id
            }
        }
    }
    filter_data = json.dumps(filter_data)
    try:
        response = requests.post(query_url,headers=headers,data=filter_data)
        last_sync_time = response.json()["results"][0]["properties"]["last_sync"]["date"]["start"]
        page_id = response.json()["results"][0]["id"]
        last_sync_info = {
                "last_sync_time":last_sync_time,
                "page_id":page_id
                }
        if response.status_code == 200 and last_sync_time is not None:
            logger.info(f"Found last_sync time and PageID = {page_id}")
            return last_sync_info
        else:
            logger.info("Last sync time is None")
            return None
    except:
        logger.error("Failed to find last_sync time or PageID")
        return None

def create_page(urls,properties):
    page_data = {
        "parent": { 
            "database_id": database_id 
        },
        "icon": {
            "external": {
                "url": urls["icon"]
            }
        },
        "cover": {
            "external": {
                "url": urls["cover"] 
            }
        },
        "properties": properties 
    }
    page_data = json.dumps(page_data)
    try:
        response = requests.post(page_url,headers=headers,data=page_data)
        id = response.json()["id"]
        logger.info(f"Successfully createed page - {response.status_code} - PageID = {id}")
        return id
    except:
        logger.error("Failed to create page,response error")
        return None

def get_page_properties(parsed_document,metadata,docs_id):
    logger.info("Constructing properties")
    properties = {
            "Title": {
                "title":[
                    {
                        "text": {
                            "content": metadata.name
                        }
                    }
                ]
            },
            "Author": {
              "rich_text": [
                {
                  "type": "text",
                  "text": {
                    "content": ','.join([author for author in metadata.authors])
                  },
                }
              ]
            },
            "Publisher": {
              "rich_text": [
                {
                  "type": "text",
                  "text": {
                    "content": metadata.publisher
                  },
                }
              ]
            },
            "docs_id": {
              "rich_text": [
                { "type": "text",
                  "text": {
                    "content": docs_id
                  },
                }
              ]
            },
            "books_id": {
              "rich_text": [
                {
                  "type": "text",
                  "text": {
                    "content": metadata.id
                  },
                }
              ]
            },
            "Highlight Count": {
                "number": int(parsed_document.total_highlights)
            },
            "Page Count": {
                "number": int(metadata.page_count)
            },
            "Note Count": {
                "number": int(parsed_document.total_notes)
            },
            "ISBN": {
                "number": int(metadata.isbn)
            },
            "Publish Date": {
              "date": {
                "start": metadata.publishedDate
              }
            },
            "Link": {
                "url": metadata.url
            }
        }
    logger.info("Returning page properties")
    return properties

def get_blocks(page_id):
    retrieve_url = f"{block_url}{page_id}/children"
    params = { "page_size" : 100}
    blocks = []
    try:
        response = requests.get(retrieve_url,headers=headers,params=params)
        response_data = response.json()
        logger.info(f"status_code from get_blocks - {response.status_code}")
        blocks.extend(response_data["results"])
        while response_data["has_more"]:
            params = {
                    "page_size":100,
                    "start_cursor":response_data["next_cursor"]
                    }
            response = requests.get(retrieve_url,headers=headers,params=params)
            response_data = response.json()
            blocks.extend(response_data["results"])
        return blocks
    except:
        logger.error("get_blocks requests error")

def delete_page(page_id):
    blocks = get_blocks(page_id)
