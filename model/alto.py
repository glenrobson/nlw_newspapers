import requests
import xml.etree.ElementTree as ET
import re
from model.annotations import AnnotationPage, AnnotationLine, Annotation
import math

ALTO_NS = {"alto": "http://www.loc.gov/standards/alto/ns-v2#"}

def get(newspaper, article):
    altoURL = newspaper.alto(article.pid)
    canvas = newspaper.canvasId(article.pid)

    response = requests.get(altoURL)
    response.raise_for_status()

    root = ET.fromstring(response.content)

    match = re.search(r"(\d+)", article.id)

    print (f".//ComposedBlock[ID='ART{match.group(1)}']")
    page = AnnotationPage()
    for line in root.findall(f".//alto:ComposedBlock[@ID='ART{match.group(1)}']//alto:TextLine", ALTO_NS):
        print (f"FOund {line}")
        page.append(XMLAnnotationLine(line, canvas))

    return page


class XMLAnnotationLine(AnnotationLine):
    def __init__(self, line, canvas):
        super().__init__() 

        for word in line.findall(".//alto:String", ALTO_NS):
            self.words.append(XMLAnnotation(word, canvas))   


class XMLAnnotation(Annotation):
    def __init__(self, word, canvas):
        self.uri = word.get("ID")
        self.motivation = "commenting"
        self.confidence = word.get("WC")
        self.value = word.get("CONTENT")

        self.x = math.ceil(int(word.get("HPOS")) / 3)
        self.y = math.ceil(int(word.get("VPOS")) / 3)
        self.width = math.ceil(int(word.get("WIDTH")) / 3)
        self.height = math.ceil(int(word.get("HEIGHT")) / 3)

        self.target = f"{canvas}#xywh={self.x},{self.y},{self.width},{self.height}"
        self.canvas = canvas
        self.pid = self.canvas.split("/")[-1]