from iiif2annos import ocr
import argparse
import os
import requests
import json
from PIL import Image
from io import BytesIO
import math

def downloadCacheImage(url):
    cache="cache"
    if not os.path.exists(cache):
        os.makedirs(cache)
    # cache the download and do a retry if it fails. 
    urlFragment = url.split("/")
    binary=True
    filename = f"{cache}/{urlFragment[len(urlFragment) - 5]}-{urlFragment[len(urlFragment) - 4].replace(",","-")}-{urlFragment[len(urlFragment) - 3].replace(",","-")}.jpg"

    print (f"Looking for cache {filename}")    

    if not os.path.exists(filename):
        print (f"Not found so downloading {url}")
        # Retrieve from URL. 
        tries = 0
        while True:
            try: 
                response = requests.get(url)
                response.raise_for_status()  # Ensure request was successful
                image = Image.open(BytesIO(response.content))
                image.save(filename)
                break

            except Exception as e:
                tries+= 1 
                if tries > 3:
                    raise e
    else:
        print ('Reading from cache')
    return Image.open(filename)

def downloadImage(infoJson, scaleFactor, output):
    print (json.dumps(infoJson["tiles"][0]) )
    tile_width = infoJson["tiles"][0]["width"]
    if "height" in infoJson["tiles"][0]:
        tile_height = infoJson["tiles"][0]["height"]
    else:    
        tile_height = infoJson["tiles"][0]["width"]

    scaled_width = infoJson["width"] / scaleFactor
    scaled_height = infoJson["height"] / scaleFactor   

    x_tiles = math.ceil(scaled_width / tile_width)
    y_tiles = math.ceil(scaled_height / tile_height)

    # Create blank canvas
    final_image = Image.new("RGB", (math.ceil(scaled_width), math.ceil(scaled_height)))
    for x in range(0, x_tiles):
        for y in range(0, y_tiles):
            tileX = x*tile_width * scaleFactor
            tileY = y*tile_height * scaleFactor
            tileWidthScaled = tile_width * scaleFactor
            tileHeightScaled = tile_height * scaleFactor

            tileSizeWidth = tile_width
            if tileX + tileWidthScaled > infoJson["width"]:
                tileWidthScaled = infoJson["width"] - tileX
                tileSizeWidth = math.ceil(tileWidthScaled / scaleFactor)

            tileSizeHeight = tile_height
            if tileY + tileHeightScaled > infoJson["height"]:
                tileHeightScaled = infoJson["height"] - tileY
                tileSizeHeight = math.ceil(tileHeightScaled / scaleFactor)    

            url = f"{infoJson["@id"]}/{tileX},{tileY},{tileWidthScaled},{tileHeightScaled}/{tileSizeWidth},{tileSizeHeight}/0/default.jpg"

            print (f"Downloading {url}")
            # Open image using PIL
            image = downloadCacheImage(url)

            # Save the image to a local file
            final_image.paste(image, (x * tile_width, y * tile_height))

    print (f"Saving: {output}")
    final_image.save(f"{output}")

def convertAltoCoords(value):    
    return math.ceil(abs(int(value)) / 3)

def fixManifest(manifest):
    for canvas in manifest["sequences"][0]["canvases"]:
        # Ensure we use https links particularly for images
        imgSrv = canvas["images"][0]["resource"]["service"]["@id"].replace("http://dams","https://damsssl")
        canvas["images"][0]["resource"]["service"]["@id"] = imgSrv

        id = imgSrv.split("/")[-1]

        # Add a link to the ALTO
        canvas["seeAlso"] = {
            "@id": f"https://dams.llgc.org.uk/behaviour/llgc-id:{id}/fedora-sdef:alto/getAlto", 
            "format": "text/xml",
            "profile": "http://www.loc.gov/standards/alto"
        }

    # Fix the coordinates for the articles as currently they are pointing to the
    # Original tiff sizes which are 3x as big. 
    for art in manifest["structures"]:
        for i in range(0, len(art["canvases"])):
            urlFrag = art["canvases"][i].split("=")
            (x, y, width, height) = urlFrag[1].split(",")

            art["canvases"][i] = f"{urlFrag[0]}={convertAltoCoords(x)},{convertAltoCoords(y)},{convertAltoCoords(width)},{convertAltoCoords(height)}"

def importNewspaper(manifest=None, pid=None):
    if not pid and not manifest:
        raise ValueError("You must specify either a manifest URL or a pid. ")

    if pid:
        manifest = f"https://damsssl.llgc.org.uk/iiif/newspaper/issue/{pid}/manifest.json"
    else:
        pid = manifest.split("/")[-2] 


    root = f"data/{pid}"
    if not os.path.exists(root):
        os.makedirs(root)

    # from pid get manifest
    manifest = requests.get(manifest).json()
    fixManifest(manifest)

    anno_uri=f"http://localhost:5000/data/{pid}"
    # fix http/https links
    images={}
    annoLists = []
    for canvas in manifest["sequences"][0]["canvases"]:
        imgSrv = canvas["images"][0]["resource"]["service"]["@id"]

        canvasName = imgSrv.split("/")[-1]
        imgFilename =f"{root}/{canvasName}.jpg"
        downloadImage(canvas["images"][0]["resource"]["service"], 2, imgFilename)
        images[canvas["@id"]] = imgFilename
        annos = ocr.run_ocr(Image.open(images[canvas["@id"]]), canvas, anno_uri, canvasName, lang="eng", confidence=True)

        annotationsID = f"{anno_uri}/{canvasName}.json"
        annotations = ocr.mkannotations(canvas,annotationsID, annos)
            
        annoLists.append(annotations)

        ocr.addAnnotations(canvas, annotationsID)

    # OCR and store results in data directory

    ocr.save(manifest, annoLists, root)

    return pid

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog='newspaper.py',
                    description='Download and OCR a NLW Newspaper')

    parser.add_argument('pid', help="id of Newspaper to use")
    args = parser.parse_args()

    importNewspaper(pid=args.pid)