import json
import argparse
from config.config import Config
from model.annotations import AnnotationPage, AnnotationLine, Annotation

def get(newspaper, article):
    with open(f"{Config.DATA_DIR}/{newspaper.pid}/{article.pid}.json") as file:
        annotations = json.load(file)

        rightX = article.x + article.width 
        bottomY = article.y + article.height
        # print (f"Article box: {article.x}, {article.y} > {rightX}, {bottomY}")

        articleAnnos = []
        for anno in annotations["resources"]:
            annotation = Annotation(anno)

            if annotation.x > article.x and annotation.y > article.y and annotation.x + annotation.width < rightX and annotation.y + annotation.height < bottomY:
                articleAnnos.append(annotation)

        articleAnnos = sorted(articleAnnos, key=lambda anno: anno.y)
        lineHeight = 25 # pixels
        page = AnnotationPage()
        line = AnnotationLine()
        lastHeight = 0
        lastLineHeight = 0
        for anno in articleAnnos:
            if lastHeight != 0 and anno.y - lastHeight >= lastLineHeight:
                #print (f"New line {anno.y} - {lastHeight} = {anno.y - lastHeight} > {lastLineHeight}")
                # start a new line
                line.sort()
                page.append(line)
                line = AnnotationLine()
                lastHeight = anno.y # Set the height to the first word on the line
                lastLineHeight = anno.height

            if lastHeight == 0:
                lastHeight = anno.y    
                lastLineHeight = anno.height
            line.append(anno)
            #print (anno)
            #print (lastHeight)
            
        line.sort()
        page.append(line)
        #print (page)
        return page     



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog='newspaper.py',
                    description='Download and OCR a NLW Newspaper')

    parser.add_argument('pid', help="id of Newspaper to use")
    parser.add_argument('--region', help="x,y,w,h")
    args = parser.parse_args()

    with open(f"data/3036869/{args.pid}.json") as file:
        annotations = json.load(file)

        (x, y, w, h) = args.region.replace(" ", "").split(",")

        for anno in annotations["resources"]:

            (annoX, annoY, annoWidth, annoHeight) = anno["on"].split("=")[1].split(",")
            rightX = annoX + annoWidth
            bottomY = annoY + annoHeight

            if annoX > x and annoY > y and x < rightX and y < bottomY:
                print (anno)

