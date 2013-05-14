# The MIT License (MIT)

# Copyright (c) 2013 Flashy

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

__author__ = "Nick Beaulieu"
__copyright__ = "Copyright 2013, Flashyapp"
__credits__ = ["Nick Beaulieu", "Joe Turchiano", "Adam Yabroudi"]
__license__ = "MIT"
__maintainer__ = "Nick Beaulieu"
__email__ = "nsbeauli@princeton.edu"
__status__ = "Production"
__date__ = "Mon May 13 19:50:55 EDT 2013"
__version__ = "1.0"

import numpy as np
from scipy.ndimage.filters import gaussian_filter
from scipy.misc import imsave

from PIL import Image
from ImageEnhance import Contrast

def __midpoint(a, b):
    return (a[1] + b[0])/float(2)
    
def __createBands(bins, minlen = 10):
    """Create a list of bands of the form (start, end)
    where the value data is non-zero and the resulting band is of length greater than
    minlen
    
    Arguments
    bins -- the array to generate the bands from
    
    Keyword arguments
    minlen -- the minimum length of a band
    """
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
    """Remove the background from an image
    using a trivial method of finding the most common value by lightness
    and removing that value
        
    Arguments
    img -- the numpy 2d list containing image lightness data

    Returns
    a numpy 2d list of 0 if the pixel is background or
    255 if the pixel is foreground
    """
    height = len(img)
    width = len(img[0])
    
    hist, band_edges = np.histogram(img, bins=2)
    mi = np.where(hist == max(hist))[0][0]
    lower = band_edges[mi]
    upper = band_edges[mi + 1]

    ret = np.where( (lower < img) & (img <= upper), 0, 255)
    return np.uint8(ret)
                
def divLines(inputImage):
    """Find the dividing lines for a given image
    
    Arguments
    img -- a PIL image

    Returns
    a list of the form (hline, vlines) where
    hline is the horizontal dividing line
    and vlines are the vertical dividing lines ABOVE it
    """
    width, height = inputImage.size
    # Double the contrast to increase distance between light and dark pixels
    img = np.array(Contrast(inputImage.convert('L')).enhance(2))
    ret = []
    vbands = []
    
    masked = __backmask(img)
    # blur the mask to avoid splitting in small gaps
    masked = gaussian_filter(masked, width / 150) # arbitrary use of 1/150 of image as blur size (change this if failing on particular document types)
    
    hcounts = np.sum(masked, axis=1)
    hbands = __createBands(hcounts)
    vbands = [__createBands(np.sum(masked[hi[0] : hi[1], :], axis=0)) for hi in hbands]
    # The midpoints between items are the dividing lines
    # These list comprehensions are difficult to understand but necessary for performance
    hlines = [int(float(a[1] + b[0])/2) for a, b in zip(hbands[:-1], hbands[1:])] + [len(img)]
    vlines = [ [0] + [int(float(a[1] + b[0]) / 2) for a, b in zip(vband[:-1], vband[1:])] + [len(img[0])] for vband in vbands]
        
    return zip(hlines, vlines)
    
def splitImage(img, divLines):
    """Get the subcrops of an image from the dividing linst
    
    Arguments
    img -- a PIL Image
    divLines -- a list of the form (hline, vlines) as defined in the
    return value of divLines
    
    Returns
    An array of PIL Images that are the subcrops of Image according to
    the dividing lines
    """    
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
    """
    Testing routine for the image splitting algorithm
    """
    import sys
    img = Image.open(sys.argv[1])
    a = divLines(img)
    r = splitImage(img, a)
    from pprint import pprint
    for i, row in enumerate(r):
        for j, img in enumerate(row):
            img.convert("RGB").save("{0}-{1}.jpg".format(i,j))

    

