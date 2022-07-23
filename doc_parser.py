import google_api
import re
import json

class document:
    def __init__(self,id):
        docs = google_api.connect("docs","v1")
        progress_file = open("parse_progress.json","r")
        progress_dic = json.load(progress_file)
        if id in progress_dic:
            progress_no = progress_dic[id]["pageNo"]
            progress_chapter = progress_dic[id]["chapterNo"]
        else:
            progress_no = 10
            progress_chapter = 0
        progress_file.close()
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
        for i in range(progress_chapter):
            self.chapters.append("")
            self.highlights.append([])
            self.new_words.append([])
        if progress_no < (len(self.json["body"]["content"])-1):
            progress_no += 1
            for i in range(progress_no,len(self.json["body"]["content"])):
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

            if id not in progress_dic:
                save_progress = {
                        id:{
                        "pageNo":(len(self.json["body"]["content"])-1),
                        "chapterNo":len(self.chapters)
                    }
                }
                progress_dic.update(save_progress)
            else:
                progress_dic[id]["pageNo"] = (len(self.json["body"]["content"])-1)
                progress_dic[id]["chapterNo"] = len(self.chapters)
            json_object = json.dumps(progress_dic, indent=4)
            with open("parse_progress.json", "w") as progress_file:
                progress_file.write(json_object)
                progress_file.close()
