#!/usr/bin/env python

# Copyright 2011 Tom Offermann <tom@micheleandtom.com>
#
# Answering the Instagram Engineering Challenge: The Unshredder.
#
# This script opens the shredded `TokyoPanoramaShredded.png` image, 
# unshreds it, and saves the good-as-the-original image as `unshredded.jpg`.

from collections import deque
from PIL import Image

# Globals
INPUT = 'TokyoPanoramaShredded.png'
OUTPUT = 'unshredded.jpg'

class Shred(object):
    """Represent a shred of a complete image."""
    def __init__(self, image):
        self.image = image
        self.width = image.size[0]
        self.height = image.size[1]
        self.data = image.load()
        # A stripe is multiple 1 pixel cols, averaged together
        self.left_stripe = self._stripe(0, 4)
        self.right_stripe = self._stripe(self.width - 4, 4)
    
    def _column(self, x):
        """
        Return list of pixels along x coordinate, where y coordinate
        ranges from 0 to image height.
        """
        pixels = []
        for y in range(self.height):
            p = self.data[x, y]
            pixels.append(p)
        return pixels
    
    def _stripe(self, start_pixel, num_pixels):
        """
        Get lists of pixels along multiple x coordinates.  Average
        the pixels that have the same y coordinate.
        
        Return list of avg pixel values, where y coordinate ranges
        from 0 to image height.
        """
        cols = []     # list of lists of 1-pixel columns
        for n in range(num_pixels):
            cols.append(self._column(start_pixel + n))
        stripe = []
        avg = ()
        for pixels in zip(*cols):
            r = g = b = 0
            for p in pixels:
                r += p[0]
                g += p[1]
                b += p[2]
            col_count = len(pixels)
            avg = (float(r/col_count), float(g/col_count), 
                   float(b/col_count), 255)
            stripe.append(avg)
        return stripe
    
    def dump(self):
        """Dump for debugging."""
        print "(%s, %s)" % (self.width, self.height)
        self.image.show()
    
def split(image):
    """
    Split image into dict of Shred objects.
        Key: leftmost x coordinate
        Value: Shred object
    """
    shred_width = 32
    image_width, image_height = image.size
    shreds = {}
    for x in range(0, image_width, shred_width):
        img = image.crop((x, 0, shred_width + x, image_height))
        s = Shred(img)
        shreds[x] = s
    return shreds

def score(stripe1, stripe2):
    """
    For each pair of pixels in 2 stripes, find the absolute value of the
    differences between the RGB values.  Sum for every pixel pair.
    
    The lower the sum, the more closely the stripes match. 
    (0 is perfect match.)
    
    Return score.
    """
    scr = 0
    count = 0
    for p1, p2 in zip(stripe1, stripe2):
        r = abs(p1[0] - p2[0])
        g = abs(p1[1] - p2[1])
        b = abs(p1[2] - p2[2])
        scr += r + g + b
    return scr

def best_match(unscram, scram):
    """
    Match the left and right stripes of unscram with every Shred
    in scram to find the best match.
    
    scores is dict:
        key = 2-tuple of index of scram (a dict of Shreds)
        value = score
    
    Return: 
        the index of the best match
        side of the unscram deque to which the best match should be added.
    """
    leftmost = unscram[0].left_stripe
    rightmost = unscram[-1].right_stripe
    scores = {}
    for k, v in scram.items():
        scores[(k, 'left')] = score(leftmost, v.right_stripe)
        scores[(k, 'right')] = score(rightmost, v.left_stripe)
    match_shred = min(scores, key=scores.get)
    return match_shred[0], match_shred[1]

def unshred(shreds_dict):
    """
    The unshredded image begins as a single Shred from shreds_dict. Next, 
    find the Shred that best matches one of the edges of the unshredded 
    image, append it to unshredded, and delete it from shreds_dict.
    
    Loop until all Shreds from shreds_dict have been added to image. 
    
    Return the ordered deque of shreds. 
    """
    scram = shreds_dict
    unscram = deque([scram[0]])
    del scram[0]
    while scram:
        key, side = best_match(unscram, scram)
        if side == 'left':
            unscram.appendleft(scram[key])
        elif side == 'right':
            unscram.append(scram[key])
        del scram[key]
    return unscram

def glue(shreds):
    """Transform ordered list of Shreds into new Image."""
    width = sum([s.width for s in shreds])
    height = shreds[0].height
    img = Image.new("RGBA", (width, height))
    x_dest = 0                # x coordinate of insertion point.
    for s in shreds:
        img.paste(s.image, (x_dest, 0))
        x_dest += s.width     # Move insertion point for next shred.
    return img

def main():
    global INPUT, OUTPUT
    shredded = Image.open(INPUT)
    shreds = split(shredded)
    un_deque = unshred(shreds)
    unshredded = glue(un_deque)
    unshredded.show()
    unshredded.save(OUTPUT, "JPEG")

if __name__ == '__main__':
    main()
    