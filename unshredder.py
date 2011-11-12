#!/usr/bin/env python

from PIL import Image

def main():
    image = Image.open('TokyoPanoramaShredded.png')
    print image.getpixel((0, 0))

if __name__ == '__main__':
    main()