import numpy as np
import cv2
import time
from math import *
from scipy.optimize import minimize

#load fisheye image
#img = cv2.imread('CircularMesh.jpg',1)
img = cv2.imread('image115.jpg',1)
h, w, d = img.shape
desiredVirtualImageWidth = 1080
#find fisheye image ROI(Region of Interest)
roiCenter = (300,255) #(600,510)
roiX,roiY = roiCenter
roiRadius = 250

# Select ROI from image
cv2.circle(img, roiCenter, roiRadius, color = (255,0,0))
cv2.imshow('image',img)
cv2.waitKey(0)
cv2.destroyAllWindows()

#if a pixel is in region of interest
def inROI(x,y):
  return (x-roiX)**2 + (y-roiY)**2 <= roiRadius**2

def imageToVirtualImage(i,j):
    #shift to center
    i -= roiX
    j -= roiY
    # scale to virtual image size
    i *= desiredVirtualImageWidth/roiRadius/2*0.95
    j *= desiredVirtualImageWidth/roiRadius/2*0.95
    # shift to virtual image center
    i += desiredVirtualImageWidth/2
    j += desiredVirtualImageWidth/2
    return int(i),int(j)

maxU = -1
maxV = -1
minU = 100000
minV = 100000

# the transformation between pixels is f(i,j) = (u,v)
mapping = np.load('mapping.npy')
for i in range(w):
  for j in range(h):
    if inROI(i,j):
      x,y = imageToVirtualImage(i,j)
      u,v = mapping[x][y]
      maxU = max(maxU, u)
      maxV = max(maxV, v)

nw, nh = int(maxU)+1, int(maxV)+1
imgOut = np.full([nh,nw,3],255,dtype=img.dtype)
for i in range(w):
  for j in range(h):
    if inROI(i,j):
      x,y = imageToVirtualImage(i,j)
      u,v = mapping[x][y]
      imgOut[int(v)][int(u)] = img[j][i]

cv2.imshow('Prewarped image', imgOut)
cv2.waitKey(0)
cv2.destroyAllWindows()
