import requests
import json

class database:
    def __init__(self,docs_id):
        self.docs_id = docs_id
        secret_file = open('secrets.json') 
        secret_data = json.load(secret_file) 

        key = secret_data['key']
        database_id = secret_data['database_id']

        secret_file.close() 

        self.query_url = f"https://api.notion.com/v1/databases/{database_id}/query"

        self.headers = {
            'Authorization': f'Bearer {key}',
            "Notion-Version": "2022-02-22",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        self.filter = {
            "filter": {
                "property": "docs_id",
                "rich_text": {
                    "equals": self.docs_id
                }
            }
        }
        self.filter_data = json.dumps(self.filter)
    def get_last_sync(self):
        try:
            response = requests.post(self.query_url,headers=self.headers,data=self.filter_data)
            last_sync_time = response.json()["results"][0]["properties"]["last_sync"]["date"]["start"]
            return last_sync_time
        except:
            return None

