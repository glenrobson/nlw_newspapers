import re

class Annotation:
    def __init__(self, anno):
        self.uri = anno["@id"]
        self.motivation = anno["motivation"]
        match = re.search(r"Confidence: (\d+): ", anno["resource"]["chars"])
        if match:
            self.confidence = match.group(1)
            self.value = re.sub("Confidence:.*\d+: ","",anno["resource"]["chars"])
        else:    
            self.value = anno["resource"]["chars"]        

        self.value = self.value.replace("|","").replace("{","").replace("}","").replace("_","")    
        self.target = anno["on"]
        self.canvas = anno["on"].split("#")[0]
        self.pid = self.canvas.split("/")[-1]
        (x, y, width, height) = anno["on"].split("=")[1].split(",")
        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)

    def __str__(self):
        return f"{self.x},{self.y},{self.width},{self.height}  '{self.value}' - Confidence {self.confidence}"  

class AnnotationLine:
    def __init__(self):
        self.words = []

    def append(self, anno: Annotation):
        self.words.append(anno)    

    def sort(self):
        self.words = sorted(self.words, key=lambda anno: anno.x)                 

class AnnotationPage:
    def __init__(self):
        self.lines = []

    def append(self, line: AnnotationLine):
        self.lines.append(line)    

    def __str__(self):
        lines = ""
        for line in self.lines:
            for word in line.words:
                lines = f"{lines} {word.value}"
            lines = f"{lines}\n"    

        return lines