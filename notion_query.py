import requests
import json

class query:
    def __init__(self):
        secret_file = open('secrets.json') 
        secret_data = json.load(secret_file) 

        self.key = secret_data['key']
        self.database_id = secret_data['database_id']

        secret_file.close() 

        self.query_url = f"https://api.notion.com/v1/databases/{self.database_id}/query"
        self.page_url = "https://api.notion.com/v1/pages" 

        self.headers = {
            'Authorization': f'Bearer {self.key}',
            "Notion-Version": "2022-02-22",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def get_last_sync(self,docs_id):
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
            return last_sync_time
        except:
            return None

    def create_page(self,icon_url,cover_url,properties):
        page_data = {
            "parent": { 
                "database_id": self.database_id 
            },
            "icon": {
                "external": {
                    "url": icon_url
                }
            },
            "cover": {
                "external": {
                    "url": cover_url
                }
            },
            "properties": properties 
        }
        page_data = json.dumps(page_data)
        try:
            response = requests.post(self.page_url,headers=self.headers,data=page_data)
        except:
            print("create page response error")

