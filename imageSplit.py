'''
Created on Mar 24, 2013

@author: beauzeaux
'''
import numpy as np
from scipy.ndimage.filters import gaussian_filter
from scipy.misc import imsave

from PIL import Image
from ImageEnhance import Contrast

def __midpoint(a, b):
    return (a[1] + b[0])/float(2)
    
def __createBands(bins, minlen = 10):
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

def __backmask(img):
    height = len(img)
    width = len(img[0])
    
    hist, band_edges = np.histogram(img, bins=2)
    mi = np.where(hist == max(hist))[0][0]
    lower = band_edges[mi]
    upper = band_edges[mi + 1]

    ret = np.where( (lower < img) & (img <= upper), 0, 255)
    return np.uint8(ret)
                
def divLines(inputImage):
    width, height = inputImage.size
    img = np.array(Contrast(inputImage.convert('L')).enhance(2))
    # img = gaussian_filter(img, width / 100)
    ret = []
    vbands = []
    
    masked = __backmask(img)
    masked = gaussian_filter(masked, width / 150)
    
    # Image.fromarray(masked).save("masked.jpg")
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
        cards = []
        for prev_col, cur_col in zip(cur_row[1][:-1], cur_row[1][1:]):
            cards.append(img.crop((prev_col, prev_row[0], cur_col, cur_row[0])))
        ret.append(cards)
    return ret
        
if __name__ == "__main__":
    img = Image.open("testing.png")
    a = divLines(img)
    r = splitImage(img, a)
    from pprint import pprint
    for i, row in enumerate(r):
        for j, img in enumerate(row):
            img.convert("RGB").save("{0}-{1}.jpg".format(i,j))

    

