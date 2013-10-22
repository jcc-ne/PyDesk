import Image
import sys

def main():
    imgFile = sys.argv[1]
    cropImage(imgFile)
    

def cropImage(imgFile, dimension=(175, 23, 780, 980), legend=False):
    im = Image.open(imgFile)
    terms = imgFile.split(".")
    ext = "extCrop"
    if legend:
	dimension=(955, 23, 200, 1000)
	ext = "extLeg"
    crop = im.crop(dimension)
    crop.save("%s_%s.%s" % (terms[0], ext, terms[1]))

if __name__ == "__main__":
    main()

