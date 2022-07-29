import google_api
import re
import logging

logger = logging.getLogger(__name__)

class document:
    def __init__(self,id):
        docs = google_api.connect("docs","v1")
        # Metadatas
        self.id = id
        self.json = docs.documents().get(documentId=id).execute()
        self.title = self.json["title"][12:-1]
        logger.info(f"Parsing {self.title}({self.id}) started")
        self.author = self.json["body"]["content"][2]["table"]["tableRows"][0]["tableCells"][1]["content"][1]["paragraph"]["elements"][0]["textRun"]["content"][0:-1]
        self.publisher = self.json["body"]["content"][2]["table"]["tableRows"][0]["tableCells"][1]["content"][2]["paragraph"]["elements"][0]["textRun"]["content"][0:-1]
        self.highlight_count = self.json["body"]["content"][7]["paragraph"]["elements"][0]["textRun"]["content"][0:-1]
        self.created_by = self.json["body"]["content"][8]["paragraph"]["elements"][0]["textRun"]["content"][0:-1]
        self.last_sync = self.json["body"]["content"][8]["paragraph"]["elements"][2]["textRun"]["content"][0:-1]

        # Contents
        self.chapters = []
        self.new_words = []
        self.highlights = []

        self.total_highlights = 0
        self.total_notes = 0
        chapter_highlights = 0
        chapter_notes = 0

        for i in range(11,len(self.json["body"]["content"])):
            try:
                chapter = self.json["body"]["content"][i]["paragraph"]["elements"][0]["textRun"]["content"][0:-1]
                if chapter and chapter != "\n":
                    chapter_dic = {
                        "title":chapter,
                        "highlights":0,
                        "notes":0
                    }
                    self.chapters.append(chapter_dic)
                    self.highlights.append([])
                    self.new_words.append([])

                    if len(self.chapters)-1:
                        self.chapters[len(self.chapters)-2]["highlights"] = chapter_highlights
                        self.chapters[len(self.chapters)-2]["notes"] = chapter_notes
                        chapter_notes = 0
                        chapter_highlights = 0
                    
            except:
                pass
            try:
                highlight = self.json["body"]["content"][i]["table"]["tableRows"][0]["tableCells"][0]["content"][1]["table"]["tableRows"][0]["tableCells"][1]["content"][0]["paragraph"]["elements"][0]["textRun"]["content"][0:-1]
                note = self.json["body"]["content"][i]["table"]["tableRows"][0]["tableCells"][0]["content"][1]["table"]["tableRows"][0]["tableCells"][1]["content"][2]["paragraph"]["elements"][0]["textRun"]["content"][0:-1]
                highlight = re.sub("\xa0+", "", highlight)
                color = self.json["body"]["content"][i]["table"]["tableRows"][0]["tableCells"][0]["content"][1]["table"]["tableRows"][0]["tableCells"][1]["content"][0]["paragraph"]["elements"][0]["textRun"]["textStyle"]["backgroundColor"]["color"]["rgbColor"]["red"]
                date = self.json["body"]["content"][i]["table"]["tableRows"][0]["tableCells"][0]["content"][1]["table"]["tableRows"][0]["tableCells"][1]["content"][2]["paragraph"]["elements"][0]["textRun"]["content"][0:-1]
                pageNo = self.json["body"]["content"][i]["table"]["tableRows"][0]["tableCells"][0]["content"][1]["table"]["tableRows"][0]["tableCells"][2]["content"][0]["paragraph"]["elements"][0]["textRun"]["content"]
                url = self.json["body"]["content"][i]["table"]["tableRows"][0]["tableCells"][0]["content"][1]["table"]["tableRows"][0]["tableCells"][2]["content"][0]["paragraph"]["elements"][0]["textRun"]["textStyle"]["link"]["url"]
                
                regex_find_date = re.compile(r'\w{3,9}\W\d{1,2},\W\d{4}')
                if regex_find_date.search(note):
                    note = None
                else:
                    date = self.json["body"]["content"][i]["table"]["tableRows"][0]["tableCells"][0]["content"][1]["table"]["tableRows"][0]["tableCells"][1]["content"][4]["paragraph"]["elements"][0]["textRun"]["content"][0:-1]
                    self.total_notes += 1
                    chapter_notes += 1

                if color == 1:
                    color = "red"
                elif color == 0.5764706:
                    color = "blue"
                elif color == 0.77254903:
                    color = "green"
                elif color == 0.99215686:
                    color = "yellow"

                if highlight and highlight != "\n":
                    highlight_data = {
                        "text":highlight,
                        "note":note,
                        "date":date,
                        "pageNo":pageNo,
                        "url":url,
                        "color":color
                    }
                    self.total_highlights += 1
                    chapter_highlights += 1
                    if color == 1:
                        self.new_words[len(self.chapters)-1].append(highlight_data)
                    else:
                        self.highlights[len(self.chapters)-1].append(highlight_data)
            except:
                pass
        else:
            self.chapters[len(self.chapters)-1]["notes"] = chapter_notes
            self.chapters[len(self.chapters)-1]["highlights"] = chapter_highlights

        logger.info(f"Parsing {self.title}({self.id}) completed")
