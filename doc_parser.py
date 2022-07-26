import google_api
import re
import json

class document:
    def __init__(self,id):
        docs = google_api.connect("docs","v1")
        # Metadatas
        self.id = id
        self.json = docs.documents().get(documentId=id).execute()
        self.title = self.json["title"][12:-1]
        self.author = self.json["body"]["content"][2]["table"]["tableRows"][0]["tableCells"][1]["content"][1]["paragraph"]["elements"][0]["textRun"]["content"][0:-1]
        self.publisher = self.json["body"]["content"][2]["table"]["tableRows"][0]["tableCells"][1]["content"][2]["paragraph"]["elements"][0]["textRun"]["content"][0:-1]
        self.highlight_count = self.json["body"]["content"][7]["paragraph"]["elements"][0]["textRun"]["content"][0:-1]
        self.created_by = self.json["body"]["content"][8]["paragraph"]["elements"][0]["textRun"]["content"][0:-1]
        self.last_sync = self.json["body"]["content"][8]["paragraph"]["elements"][2]["textRun"]["content"][0:-1]

        # Contents
        self.chapters = []
        self.new_words = []
        self.highlights = []
        for i in range(11,len(self.json["body"]["content"])):
            try:
                chapter = self.json["body"]["content"][i]["paragraph"]["elements"][0]["textRun"]["content"][0:-1]
                if chapter and chapter != "\n":
                    self.chapters.append(chapter)
                    self.highlights.append([])
                    self.new_words.append([])
            except:
                pass
            try:
                highlight = self.json["body"]["content"][i]["table"]["tableRows"][0]["tableCells"][0]["content"][1]["table"]["tableRows"][0]["tableCells"][1]["content"][0]["paragraph"]["elements"][0]["textRun"]["content"][0:-1]
                highlight = re.sub("\xa0+", "", highlight)
                color = self.json["body"]["content"][i]["table"]["tableRows"][0]["tableCells"][0]["content"][1]["table"]["tableRows"][0]["tableCells"][1]["content"][0]["paragraph"]["elements"][0]["textRun"]["textStyle"]["backgroundColor"]["color"]["rgbColor"]["red"]
                date = self.json["body"]["content"][i]["table"]["tableRows"][0]["tableCells"][0]["content"][1]["table"]["tableRows"][0]["tableCells"][1]["content"][2]["paragraph"]["elements"][0]["textRun"]["content"][0:-1]
                pageNo = self.json["body"]["content"][i]["table"]["tableRows"][0]["tableCells"][0]["content"][1]["table"]["tableRows"][0]["tableCells"][2]["content"][0]["paragraph"]["elements"][0]["textRun"]["content"]
                url = self.json["body"]["content"][i]["table"]["tableRows"][0]["tableCells"][0]["content"][1]["table"]["tableRows"][0]["tableCells"][2]["content"][0]["paragraph"]["elements"][0]["textRun"]["textStyle"]["link"]["url"]

                if highlight and highlight != "\n":
                    highlight_data = {
                        "text":highlight,
                        "date":date,
                        "pageNo":pageNo,
                        "url":url
                    }
                    if color == 1:
                        self.new_words[len(self.chapters)-1].append(highlight_data)
                    elif color == 0.5764706:
                        self.highlights[len(self.chapters)-1].append(highlight_data)
            except:
                pass
