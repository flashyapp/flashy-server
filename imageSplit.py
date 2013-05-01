'''
Created on Mar 24, 2013

@author: beauzeaux
'''
import numpy as np
from scipy.ndimage import laplace
from scipy.misc import imsave

from PIL import Image


def __midpoint(a, b):
    return (a[1] + b[0])/float(2)
    
def __createBands(bins, minlen = 2):
    bands = []
    c     = 0
    start = 0
    end   = 0
    
    while c < len(bins):
        while c < len(bins) and bins[c] == 0: 
            c += 1
            start = c
            end = start
        while c < len(bins) and bins[c] > 0:
                c+=1
                end = c
        if start != end and (end - start) >= minlen:
                bands.append((start,end))
                start = 0
                end = 0
                    
    if start != end and (end - start) >= minlen:
        bands.append((start, len(bins)))
        
    return bands

def __subImage(img, box):
    return img[box[0]:box[2], box[1]: box[3]]

    
def divLines(inputImage):
    img = np.asarray(inputImage.convert('L'))
    ret = []
    vbands = []
    
    masked = laplace(img)       # laplace backgrounding (dumb but works)
    # row work
    hcounts = np.sum(masked, axis=1)
    hbands = __createBands(hcounts)
    vbands = [__createBands(np.sum(masked[hi[0] : hi[1], :], axis=0)) for hi in hbands]
    # The midpoints between items are the dividing lines
    # These list comprehensions are difficult to understand but necessary for performance
    hlines = [int(float(a[1] + b[0])/2) for a, b in zip(hbands[:-1], hbands[1:])] + [len(img)]
    vlines = [ [0] + [int(float(a[1] + b[0]) / 2) for a, b in zip(vband[:-1], vband[1:])] + [len(img[0])] for vband in vbands]
        
    return zip(hlines, vlines)
    
def splitImage(img, divLines):
    ret = []
    divLines.insert(0, (0, []))
    # Convert to list comprehension for speedup
    for prev_row, cur_row in zip(divLines[:-1], divLines[1:]):
        for prev_col, cur_col in zip(cur_row[1][:-1], cur_row[1][1:]):
            ret.append(img.crop((prev_col, prev_row[0], cur_col, cur_row[0])))
    return ret
        
if __name__ == "__main__":
    img = Image.open("test/test.gif")
    a = divLines(img)
    r = splitImage(img, a)
    from pprint import pprint
    for c, out in enumerate(r):
        out.convert("RGB").save("{0}.jpg".format(c))
