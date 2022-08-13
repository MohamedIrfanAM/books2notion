import requests
import logging

logger = logging.getLogger(__name__)

class dictionary_class:
    def __init__(self):
        pass
    async def get_definitions(self,word):
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        try:
            response = requests.get(url)
            definitions_rich_text = [] 
            if response.json() is not None and response.status_code == 200:
                meanings = response.json()[0]["meanings"]
                url = response.json()[0]["sourceUrls"]
                for meaning in meanings:
                    definition_rich_text = [
                        {
                         'type': 'text',
                         'text': {
                            'content': f"{meaning['partOfSpeech']}: ",
                            'link': {
                               "url":f"{url[0]}#{str(meaning['partOfSpeech']).capitalize()}"
                               }
                            },
                         'annotations': {
                           'bold': True,
                           'italic': False,
                           'strikethrough': False,
                           'underline': False,
                           'code': False,
                           'color': 'default'
                         },
                         'plain_text': f"{meaning['partOfSpeech']}: ",
                         'href': f"{url[0]}#{str(meaning['partOfSpeech']).capitalize()}"
                         },
                        {
                         'type': 'text',
                         'text': {
                           'content': f"{meaning['definitions'][0]['definition']}\n",
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
                         'plain_text': f"{meaning['definitions'][0]['definition']}\n",
                         'href': None
                        }
                    ]
                    definitions_rich_text.extend(definition_rich_text)
            return definitions_rich_text
        except:
            logger.error("Dictionary request error")

