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
database_url = "https://api.notion.com/v1/databases"

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

def create_page(urls,properties,children):
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
        "properties": properties,
        "children": children
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
            "New Words Count": {
                "number": int(parsed_document.total_new_words)
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
            "Link": {
                "url": metadata.url
            }
        }
    logger.info("Returning page properties")
    return properties

def get_header_children(metadata):
    logger.info("Contructing heading content children")
    children = [
        {
            "object":"block",
            "type":"toggle",
            'toggle': {
             'rich_text': [
                {
                 'type': 'text',
                 'text': {
                   'content': 'Table of Contents',
                   'link': None
                 },
                 'annotations': {
                   'bold': True,
                   'italic': False,
                   'strikethrough': False,
                   'underline': True,
                   'code': False,
                   'color': 'default'
                 },
                 'plain_text': 'Table of Contents',
                 'href': None
                }
                ],
                'color': 'default',
                "children": [
                {
                  "type": "table_of_contents",
                  "table_of_contents": {
                    "color": "default"
                  }
                }
                 ]
             },
          },

        {
            "object":"block",
            "type":"toggle",
            'toggle': {
             'rich_text': [
                {
                 'type': 'text',
                 'text': {
                   'content': 'About',
                   'link': None
                 },
                 'annotations': {
                   'bold': True,
                   'italic': False,
                   'strikethrough': False,
                   'underline': True,
                   'code': False,
                   'color': 'default'
                 },
                 'plain_text': 'About',
                 'href': None
                }
                ],
                'color': 'default',
                "children": [
                {
                  "type": "paragraph",
                  "paragraph": {
                      "rich_text": [{
                          "type":"text",
                          "text": {
                              "content":metadata.about,
                              "link":None
                              }
                          }]
                  }
                }
                 ]
             },
          },
    ]
    logger.info("Returning children array")
    return children

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

def clear_page_content(page_id):
    blocks = get_blocks(page_id)
    count = 0
    headers_count = 3 
    if blocks is not None:
        logger.info(f"Starting to delete {len(blocks)-headers_count} blocks")
        for block in blocks:
            if count >= headers_count:
                block_id = block["id"]
                delete_url = f"{block_url}{block_id}"
                requests.delete(delete_url, headers=headers)
            count += 1
        logger.info("finished deleting all content blocks")

def create_new_words_database(page_id):
    data = {
        "parent": {
          "type": "page_id",
          "page_id": page_id
        },
        "title": [
         {
           "type": "text",
           "text": {
             "content": "New Words",
             "link": None
           }
         }
        ],
        "properties":{
            "Word":{
                "title":{}
            },
            "Definition": {
              "rich_text": {}
            },
            "PageNo": {
              "rich_text": {}
            }
        },
        "icon": {
            "external": {
                "url":"https://iili.io/SvVE5F.png"
            }
        },
    }
    data = json.dumps(data)

    try:
        response = requests.post(database_url,headers=headers,data=data)
        id = response.json()["id"]
        logger.info(f"Successfully createed new words database - {response.status_code} - DatabaseID = {id}")
        return id
    except:
        logger.error("Failed to create new words database,response error")
        return None
def get_new_words_id(page_id):
    blocks = get_blocks(page_id)
    if blocks is not None:
        logger.info(f"Found new_words_id - {blocks[2]['id']}")
        return blocks[2]["id"]
    else:
        logger.error("Couldn't find new_words_id")

def add_new_word(new_words_id,new_word):
    page_data = {
        "parent": {
            "database_id": new_words_id
        },
        "properties": {
            "Word": {
                "title":[
                    {
                        "text": {
                            "content": new_word["text"]
                        }
                    }
                ]
            },
            "Definition": {
             'rich_text': [
                {
                 'type': 'text',
                 'text': {
                   'content': "",
                   'link': None
                 },
                 'annotations': {
                   'bold': False,
                   'italic': True,
                   'strikethrough': False,
                   'underline': False,
                   'code': False,
                   'color': 'default'
                 },
                 'plain_text': '',
                 'href': None
                }
                ]
            },
            "PageNo": {
             'rich_text': [
                {
                 'type': 'text',
                 'text': {
                   'content': new_word["pageNo"],
                   'link': {"url": new_word["url"] }
                 },
                 'annotations': {
                   'bold': False,
                   'italic': False,
                   'strikethrough': False,
                   'underline': True,
                   'code': False,
                   'color': 'default'
                 },
                 'plain_text': new_word["pageNo"],
                 'href': new_word["url"]
                }
                ]

            }
        }
    }
    page_data = json.dumps(page_data)
    try:
        response = requests.post(page_url,headers=headers,data=page_data)
        id = response.json()["id"]
        logger.info(f"Successfully added new word - {response.status_code} - New_word_PageID = {id}")
        return id
    except:
        logger.error("Failed to add new word,response error")
        return None

def append_chapter(page_id,chapter):
    append_url = f"{block_url}{page_id}/children"
    page_data = {
        "children":[
            {
                "object":"block",
                'type': 'heading_2',
                'heading_2': {
                  'rich_text': [
                    {
                      'type': 'text',
                      'text': {
                        'content': chapter["title"],
                        'link': None
                      },
                      'annotations': {
                        'bold': False,
                        'italic': False,
                        'strikethrough': False,
                        'underline': True,
                        'code': False,
                        'color': 'default'
                      },
                      'plain_text': chapter["title"],
                      'href': None
                    }
                  ],
                  'color': 'default'
                }
            },
            {
                "object":"block",
                'type': 'paragraph',
                'paragraph': {
                  'rich_text': [
                    {
                      'type': 'text',
                      'text': {
                        'content': f'{chapter["highlights"]} highlights and {chapter["notes"]} notes',
                        'link': None
                      },
                      'annotations': {
                        'bold': False,
                        'italic': True,
                        'strikethrough': False,
                        'underline': False,
                        'code': False,
                        'color': 'default'
                      },
                      'plain_text': f'{chapter["highlights"]} highlights and {chapter["notes"]} notes',
                      'href': None
                    }
                  ],
                  'color': 'default'
                }
            },
            {
                "object":"block",
                'type': 'paragraph',
                'paragraph': {
                  'rich_text': [

                  ],
                  'color': 'default'
                }
            }
        ]
    }

    data = json.dumps(page_data)
    try:
        response = requests.patch(append_url,headers=headers,data=data)
        logger.info(f"Successfully appended chapter {chapter['title']} - {response.status_code}")
    except:
        logger.error(f"Failed to append chapter {chapter['title']},response error")

def get_highlight_blocks(highlight):
    logger.info("Constructing highlight blocks")
    highlight_block = {
            "object":"block",
            "type":"quote",
            "quote":{
                "rich_text": [
                    {
                        "type":"text",
                        "text":{
                            "content":f"{highlight['text']}\n\nPage: ",
                            "link":None
                        },
                        "plain_text":f"{highlight['text']}\n\nPage: ",
                        "href":None
                    },
                    {
                        "type":"text",
                        "text":{
                            "content":f"{highlight['pageNo']}\n",
                            "link": {
                                "url": highlight["url"]
                            }
                        },
                        "plain_text":f"{highlight['pageNo']}\n",
                        "href":highlight["url"]
                    },
                    {
                        "type":"text",
                        "text":{
                            "content":f"Date: {highlight['date']}",
                            "link":None
                        },
                        "plain_text":f"Date: {highlight['date']}",
                        "href":None
                    }
                ],
                "color":highlight["color"]
            }
    }
    spacer_block = {
        "object":"block",
        'type': 'paragraph',
        'paragraph': {
          'rich_text': [

          ],
          'color': 'default'
        }
    }
    highlight_data_blocks = []
    if highlight["note"] is not None:
        note_block = {
            "object":"block",
            "type":"callout",
            "callout":{
                "rich_text":[
                    {
                        "type":"text",
                        "text":{
                            "content":highlight["note"],
                            "link":None
                        },
                        "plain_text":highlight["note"],
                        "href":None
                    }
                ],
                "icon":{
                    "type":"emoji",
                    "emoji":"💡"
                },
                "color":f"{highlight['color']}_background"
            }
        }
        highlight_data_blocks = [highlight_block,note_block,spacer_block]
    else:
        highlight_data_blocks = [highlight_block,spacer_block]
    logger.info("Finished contructing highlight block")
    return highlight_data_blocks

def append_highlights(page_id,children):
    append_url = f"{block_url}{page_id}/children"
    page_data = {
            "children":children
    }
    data = json.dumps(page_data)
    try:
        response = requests.patch(append_url,headers=headers,data=data)
        logger.info(f"Successfully appended highlights - {response.status_code}")
    except:
        logger.error(f"Failed to append highlights")

