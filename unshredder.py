#!/usr/bin/env python

from PIL import Image

def main():
    image = Image.open('TokyoPanoramaShredded.png')
    pixel_data = image.load()
    print pixel_data[0, 0]

if __name__ == '__main__':
    main()