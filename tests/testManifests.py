import unittest
import json
from nlw_newspapers import importer

class TestManifest(unittest.TestCase):

    def testManifestUpgrade(self):
        with open("tests/fixtures/3036869.json", "r") as file:
            manifest = json.load(file)

            importer.fixManifest(manifest)

            for canvas in manifest["sequences"][0]["canvases"]:
                self.assertFalse(canvas["images"][0]["resource"]["service"]["@id"] in "http://dams", "Expected ID to be updated to https version.")

                self.assertTrue("seeAlso" in canvas, "Expected a seeAlso pointing to the ALTO")

                seeAlso = canvas["seeAlso"]
                self.assertEqual(seeAlso["format"], "text/xml")
                self.assertEqual(seeAlso["profile"], "http://www.loc.gov/standards/alto")

            article1 = manifest["structures"][0]
            canvas = article1["canvases"][0]

            self.assertEqual(canvas, "http://dams.llgc.org.uk/iiif/3036869/canvas/3036870#xywh=28,1205,3356,7520", "Expected coordinates to be divided by 3 and positive. ")


