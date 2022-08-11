import json
import logging
import os
import requests
from datetime import datetime,timedelta
import re

class notion_client:

    def __init__(self):

        self.logger = logging.getLogger(__name__)

        self.key = os.getenv('NOTION_KEY')
        self.database_id = os.getenv('NOTION_DATABASE_ID')

        self.query_url = f"https://api.notion.com/v1/databases/{self.database_id}/query"
        self.page_url = "https://api.notion.com/v1/pages" 
        self.block_url = "https://api.notion.com/v1/blocks/"
        self.database_url = "https://api.notion.com/v1/databases"

        self.headers = {
            'Authorization': f'Bearer {self.key}',
            "Notion-Version": "2022-02-22",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
    async def get_last_sync(self,docs_id):
        self.logger.info(f"getting last_sync time for docs_id - {docs_id}")
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
            response = requests.post(self.query_url,headers=self.headers,data=filter_data)
            last_sync_time = response.json()["results"][0]["properties"]["last_sync"]["date"]["start"]
            page_id = response.json()["results"][0]["id"]
            progress_no = response.json()["results"][0]["properties"]["parse_progress"]["number"]
            parsed_chapters = response.json()["results"][0]["properties"]["Chapter Count"]["number"]
            parsed_highlights = response.json()["results"][0]["properties"]["Highlight Count"]["number"]
            parsed_notes = response.json()["results"][0]["properties"]["Note Count"]["number"]
            parsed_new_words = response.json()["results"][0]["properties"]["New Words Count"]["number"]
            full_sync_bool = response.json()["results"][0]["properties"]["Full_Sync"]["checkbox"]
            last_sync_info = {
                    "last_sync_time":last_sync_time,
                    "page_id":page_id,
                    "progress_no": progress_no,
                    "parsed_chapters": parsed_chapters,
                    "parsed_highlights":parsed_highlights,
                    "parsed_notes": parsed_notes,
                    "parsed_new_words":parsed_new_words,
                    "full_sync_bool":full_sync_bool
            }
            if response.status_code == 200 and last_sync_time is not None:
                self.logger.info(f"Found last_sync time and PageID = {page_id}")
                return last_sync_info
            else:
                self.logger.info("Last sync time is None")
                return None
        except:
            self.logger.error("Failed to find last_sync time or PageID")
            return None

    async def create_page(self,urls,properties,children):
        page_data = {
            "parent": { 
                "database_id": self.database_id 
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
            "properties": properties, "children": children
        }
        page_data = json.dumps(page_data)
        try:
            response = requests.post(self.page_url,headers=self.headers,data=page_data)
            id = response.json()["id"]
            self.logger.info(f"Successfully createed page - {response.status_code} - PageID = {id}")
            return id
        except:
            self.logger.error("Failed to create page,response error")
            return None

    def get_page_properties(self,parsed_document,metadata,docs_id):
        self.logger.info("Constructing properties")
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
        self.logger.info("Returning page properties")
        return properties

    def get_header_children(self,metadata):
        self.logger.info("Contructing heading content children")
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
                                  "content":metadata.about[:min(2000,len(metadata.about))],
                                  "link":None
                                  }
                              }]
                      }
                    }
                     ]
                 },
              },
        ]
        self.logger.info("Returning children array")
        return children

    async def get_blocks(self,page_id):
        retrieve_url = f"{self.block_url}{page_id}/children"
        params = { "page_size" : 100}
        blocks = []
        try:
            response = requests.get(retrieve_url,headers=self.headers,params=params)
            response_data = response.json()
            self.logger.info(f"status_code from get_blocks - {response.status_code}")
            blocks.extend(response_data["results"])
            while response_data["has_more"]:
                params = {
                        "page_size":100,
                        "start_cursor":response_data["next_cursor"]
                }
                response = requests.get(retrieve_url,headers=self.headers,params=params)
                response_data = response.json()
                blocks.extend(response_data["results"])
            return blocks
        except:
            self.logger.error("get_blocks requests error")

    async def clear_page_content(self,page_id):
        blocks = await self.get_blocks(page_id)
        headers_count = 3
        if blocks is not None:
            blocks = blocks[headers_count:]
            clear_page_client = requests.Session()
            self.logger.info(f"Starting to delete {len(blocks)-headers_count} blocks")
            for block in blocks:
                    block_id = block["id"]
                    delete_url = f"{self.block_url}{block_id}"
                    clear_page_client.delete(delete_url, headers=self.headers)
            self.logger.info("finished deleting all content blocks")

    async def get_new_words_pages(self,new_word_id):
        new_word_query_url = f"https://api.notion.com/v1/databases/{new_word_id}/query"
        self.logger.info(f"getting all new word pages in database - {new_word_id}")
        filter_data = {
            "filter": {
                "property": "Word",
                "rich_text": {
                    "is_not_empty": True
                }
            },
            "page_size":100
        }
        filter_data = json.dumps(filter_data)
        try:
            response = requests.post(new_word_query_url,headers=self.headers,data=filter_data)
            response_data = response.json()
            page_ids = [result["id"] for result in response_data["results"]]
            while response_data["has_more"]:
                filter_data = {
                    "filter": {
                        "property": "",
                        "rich_text": {
                            "is_not_empty": True
                        }
                    },
                    "page_size":100,
                    "start_cursor":response_data["next_cursor"]
                }
                response = requests.post(new_word_query_url,headers=self.headers,data=filter_data,)
                response_data = response.json()
                page_ids.extend([result["id"] for result in response_data["results"]])

            self.logger.error("Returning page ids for all new words")
            return page_ids
        except:
            self.logger.error("failed to find new_words pages")
            return None

    async def delete_new_words(self,new_word_id):
        page_ids = await self.get_new_words_pages(new_word_id)
        delete_new_words_client = requests.Session()
        if page_ids is not None:
            self.logger.error(f"starting to delete {len(page_ids)} new_words")
            for page_id in page_ids:
                delete_url = f"{self.block_url}{page_id}"
                delete_new_words_client.delete(delete_url, headers=self.headers)
            self.logger.info("finished deleting all new_words")
        else:
            self.logger.info("No new words to delete")

    async def create_new_words_database(self,page_id):
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
            response = requests.post(self.database_url,headers=self.headers,data=data)
            id = response.json()["id"]
            self.logger.info(f"Successfully createed new words database - {response.status_code} - DatabaseID = {id}")
            return id
        except:
            self.logger.error("Failed to create new words database,response error")
            return None
    async def get_new_words_id(self,page_id):
        blocks = await self.get_blocks(page_id)
        if blocks is not None:
            self.logger.info(f"Found new_words_id - {blocks[2]['id']}")
            return blocks[2]["id"]
        else:
            self.logger.error("Couldn't find new_words_id")

    async def add_new_word(self,new_words_id,new_word,definition):
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
                 'rich_text': definition
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
            response = requests.post(self.page_url,headers=self.headers,data=page_data)
            id = response.json()["id"]
            self.logger.info(f"Successfully added new word - {response.status_code} - New_word_PageID = {id}")
            return id
        except:
            self.logger.error("Failed to add new word,response error")
            return None

    async def append_chapter(self,page_id,chapter):
        append_url = f"{self.block_url}{page_id}/children"
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
            response = requests.patch(append_url,headers=self.headers,data=data)
            self.logger.info(f"Successfully appended chapter {chapter['title']} - {response.status_code}")
        except:
            self.logger.error(f"Failed to append chapter {chapter['title']},response error")

    def get_highlight_blocks(self,highlight):
        self.logger.info("Constructing highlight blocks")
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
        self.logger.info("Finished contructing highlight block")
        return highlight_data_blocks

    async def append_highlights(self,page_id,children):
        append_url = f"{self.block_url}{page_id}/children"
        page_data = {
                "children":children
        }
        data = json.dumps(page_data)
        try:
            response = requests.patch(append_url,headers=self.headers,data=data)
            self.logger.info(f"Successfully appended highlights - {response.status_code}")
        except:
            self.logger.error(f"Failed to append highlights")

    async def update_properties(self,page_id,parsed_document):
        utc_now = datetime.utcnow()
        ist_now = str(utc_now + timedelta(hours=5,minutes=30))
        time = (re.sub(' ','T',ist_now[:-3]))+"+05:30"
        update_url = f"{self.page_url}/{page_id}"
        page_data = {
            "properties" : {
                "Highlight Count": {
                    "number": int(parsed_document.total_highlights)
                },
                "New Words Count": {
                    "number": int(parsed_document.total_new_words)
                },
                "Note Count": {
                    "number": int(parsed_document.total_notes)
                },
                "Chapter Count": {
                    "number": int(parsed_document.total_chapters)
                },
                "parse_progress": {
                    "number": int(parsed_document.progress_no)
                },
                "last_sync": {
                  "date": {
                    "start": time
                  }
                },
                "Full_Sync": {
                    "checkbox": False
                }
            }
        }
        data = json.dumps(page_data)
        try:
            response = requests.patch(update_url,headers=self.headers,data=data)
            self.logger.info(f"Successfully updated page properties - {response.status_code}")
        except:
            self.logger.error(f"Failed to update properties,response error")

    async def new_word_exists(self,new_word_id,new_word):
        check_url = f"https://api.notion.com/v1/databases/{new_word_id}/query"
        filter_data = {
            "filter": {
                "property": "Word",
                "rich_text": {
                    "equals": new_word['text']
                }
            }
        }
        filter_data = json.dumps(filter_data)
        try:
            response = requests.post(check_url,headers=self.headers,data=filter_data)
            if len(response.json()["results"]) == 0:
                self.logger.info(f"{new_word} doesn't exist in the database")
                return False
            else:
                self.logger.info(f"{new_word} exists in the database")
                return True
        except:
            self.logger.error("Failed to check if new_word exists,response error")
            return None

