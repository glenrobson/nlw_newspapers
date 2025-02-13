import os
from config.config import Config
import json 
from datetime import datetime
def all():
    """
      Get all Loaded newspapers

      returns: 
      list of Newspapers
      newspaper.thumb
      newspaper.name
      newspaper.date
      newspaper.summary

    """

    newspapers = []

    for dir in os.listdir(Config.DATA_DIR):
        pid = dir
        dir = f"{Config.DATA_DIR}/{dir}"
        if os.path.isdir(dir):
            with open(f"{dir}/manifest.json", "r") as file:
                manifest = json.load(file)

                newspaper = Newspaper(manifest)

                newspapers.append(newspaper)

    return newspapers

def get(pid):
    with open(f"{Config.DATA_DIR}/{pid}/manifest.json", "r") as file:
        manifest = json.load(file)

        return Newspaper(manifest)

def metadataFromJson(data):       
    metadata = {}
    for entry in data:
        if isinstance(entry["label"], list):
            for lang in entry["label"]:
                if lang["@language"] == "en":
                    label = lang["@value"]
        else:
            label = entry["label"]            

        if isinstance(entry["value"], list):
            if isinstance(entry["value"][0], dict): 
                for lang in entry["value"]:
                    if lang["@language"] == "en":
                        value = lang["@value"]
            else:
                value = ""
                for item in entry["value"]:
                    value = f"{value} {item},"
                value = value[:-1]
        else:
            value = entry["value"]
    return metadata        
    
class Article:
    def __init__(self, range):
        self.id = range["@id"].split("/")[-1]
        self.uri = range["@id"]
        self.name = range["label"]
        self.metadata = metadataFromJson(range["metadata"])
        self.target = range["canvases"][0]
        self.pid = self.target.split("#")[0].split("/")[-1]
        self.article = self.id.split("/")[-1]
        self.annotations = range["contentLayer"][0]["@id"]
        (x, y, width, height) = self.target.split("=")[1].split(",")
        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)

class Page:
    def __init__(self, canvas):
        self.imgSrv = canvas["images"][0]["resource"]["service"]["@id"]
        self.pid = self.imgSrv.split("/")[-1]
        self.label = canvas["label"]
        self.thumb = f"{self.imgSrv}/full/,768/0/default.jpg"


class Newspaper:
    def __init__(self, manifest):
        self.manifest = manifest
        self.pid = manifest["@id"].split("/")[-2]
        self.name = manifest["label"]
        self.date = manifest["navDate"]

        imgSrv = manifest["sequences"][0]["canvases"][0]["images"][0]["resource"]["service"]["@id"]
        self.thumb = f"{imgSrv}/full/,768/0/default.jpg"

        self.metadata = metadataFromJson(manifest["metadata"])

        self.pages = []
        for canvas in manifest["sequences"][0]["canvases"]:
            self.pages.append(Page(canvas))

    def dateString(self):
        date_object = datetime.strptime(self.date, "%Y-%m-%dT%H:%M:%SZ")

        return date_object.strftime("%d %B %Y")    

    def infoJsonURL(self, pagePid):
        for page in self.pages:
            if page.pid == str(pagePid):
                return f"{page.imgSrv}/info.json"
            
    def getArticles(self, pagePid):
        articles = []
        for articleJson in self.manifest["structures"]:
            article = Article(articleJson)
            if article.pid == str(pagePid):
                articles.append(article)

        return articles    

    def article(self, id):    
        article = None
        for articleJson in self.manifest["structures"]:
            article = Article(articleJson)
            if article.id == id:
                return article

        return article    

    def alto(self, pagePid):
        for canvas in self.manifest["sequences"][0]["canvases"]:
            if pagePid in canvas["@id"]:
                return canvas["seeAlso"]["@id"]
            
    def canvasId(self, pagePid):        
        for canvas in self.manifest["sequences"][0]["canvases"]:
            if pagePid in canvas["@id"]:
                return canvas["@id"]
            
