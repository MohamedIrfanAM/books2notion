import requests
import json

secret_file = open('secrets.json') 
secret_data = json.load(secret_file) 

key = secret_data['key']
database_id = secret_data['database_id']

secret_file.close() 

query_url = f"https://api.notion.com/v1/databases/{database_id}/query"
page_url = "https://api.notion.com/v1/pages" 

headers = {
    'Authorization': f'Bearer {key}',
    "Notion-Version": "2022-02-22",
    "Accept": "application/json",
    "Content-Type": "application/json",
}

def get_last_sync(docs_id):
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
        return last_sync_time
    except:
        return None

def create_page(icon_url,cover_url,properties):
    page_data = {
        "parent": { 
            "database_id": database_id 
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
        response = requests.post(page_url,headers=headers,data=page_data)
    except:
            print("create page response error")

