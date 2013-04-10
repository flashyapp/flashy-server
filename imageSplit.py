'''
Created on Mar 24, 2013

@author: beauzeaux
'''
import numpy
from numpy import zeros
from PIL import Image


    
def __blur(img, r):
    ret = hMotionBlur(img, k=r)
    ret = vMotionBlur(ret, k=r)
    return ret
    
def __hMotionBlur(img, k=5, m=1):
    rows = len(img)
    cols = len(img[0])
    ret = zeros((rows,cols))
    for r in range(0, rows):
        s = sum(img[k][:r])
        for c in range(0, k):
            s = s + img[r][c+k]
            a = m / float(k + 1 + r)
            ret[r][c] = s * a
            a = m / float(2 * k + 1)
            for c in range(k, cols -k):
                s = s + img[r][c+k] - img[r][c-k-1]
                ret[r][c] = s * a
                for c in range(cols -k, cols):
                    s = s - img[r][c-k-1]
                    a = m / (2 * k + 1 - c)
                    ret[r][c] = s * a
                    
    return ret

def __vMotionBlur(img, k=5, m=1):
    rows = len(img)
    cols = len(img[0])
    ret = zeros((rows,cols))
    for c in range(0, cols):
        s = sum([x[c] for x in img[:k]])
        for r in range(0, k):
            s = s + img[r+k][c]
            a = m / float(k + 1 + r)
            ret[r][c] = s * a
            a = m / float(2 * k + 1)
            for r in range(k, rows - k):
                s = s + img[r+k][c] - img[r-k-1][c]
                ret[r][c] = s * a
                for r in range(rows - k, rows):
                    s = s - img[r-k-1][c]
                    a = m / (2 * k + 1 - r)
                    ret[r][c] = s * a
                    
    return ret


def __midpoint(a, b):
    return (a[1] + b[0])/float(2)
    
def __counts(img, threshold = 127):
    height = len(img)
    width = len(img[0])
    colCounts = [0]*width
    rowCounts = [0]*height
    for r in range(height):
        for c in range(width):
            if img[r][c] > threshold:
                colCounts[c] += 1
                rowCounts[r] += 1
    return (rowCounts, colCounts)
                
            
def __backmask(img):
    height = len(img)
    width = len(img[0])
    c, v = numpy.histogram(img)
    mi = numpy.where(c == max(c))[0][0]
    lower = v[mi]
    upper = v[mi + 1]
    for r in range(height):
        for c in range(width):
            if lower < img[r][c] and img[r][c] <=upper:
                img[r][c] = 0
            else:
                img[r][c] = 255
                
def __createBands(bins, threshold=1, minlen=1):
    bands = []
    c     = 0
    start = 0
    end   = 0
    
    while c < len(bins):
        while c < len(bins) and bins[c] < threshold: 
            c += 1
            start = c
            end = start
        while c < len(bins) and bins[c] >= threshold:
            c+=1
            end = c
        if start != end and (end - start) >= minlen:
            bands.append((start,end))
        start = 0
        end = 0
                    
    if start != end and (end - start) >= minlen:
        bands.append((start, len(bins)))
    return bands
        
def divLines(img):
    px = list(img.getdata())
    width, height = img.size
    img  = [px[i * width:(i + 1) * width] for i in xrange(height)]
    height = len(img)
    width  = len(img[0])
    __backmask(img) 
    colCounts = [0]*width
    rowCounts = [0]*height
    rowCounts, colCounts = __counts(img, threshold=127)

    threshold = 100              # 1 /threshold size to be counted
    hbands = __createBands(rowCounts, minlen=(height/threshold))
    vbands = __createBands(colCounts, minlen=(width/threshold))
    ys = [0]*(len(vbands) - 1)
    xs = [0]*(len(hbands) - 1)
    
    for c in range(1, len(vbands)):
        ys[c - 1] = int(__midpoint(vbands[c - 1], vbands[c]))
        
    for c in range(1, len(hbands)):
        xs[c - 1] = int(__midpoint(hbands[c - 1], hbands[c]))
        
    return [ys, xs]

def splitImage(img, divLines):
    width, height = img.size
    ret = []
    # add the left and right hand sides of the page
    divLines[0].insert(0, 0)     
    divLines[0].append(width)
    # add the top and bottom of the page
    divLines[1].insert(0, 0)
    divLines[1].append(height)

    for x in range(1, len(divLines[0])):
        for y in range(1, len(divLines[1])):
            box = (divLines[0][x-1], divLines[1][y-1],
                   divLines[0][x], divLines[1][y])
            ret.append(img.crop(box))

    return ret

if __name__ == "__main__":
    exit(1)                     # comment to run test code, added for safety
    i = Image.open("test.gif")
    a = divLines(i)
    imgs = splitImage(i, a)
    for id, img in enumerate(imgs):
        img.save(str(id) + ".gif")
