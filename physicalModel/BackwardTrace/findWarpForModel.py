import numpy as np
import cv2
import time
from math import *
from scipy.optimize import minimize

#ser virtual ROI(Region of Interest)
desiredVirtualImageWidth = 1080
roiRadius = int(desiredVirtualImageWidth/2)
roiCenter = (roiRadius,roiRadius)
roiX,roiY = roiCenter

#parameters in (cm)
# dome
R = 150 # radius of the dome
dx, dy, dz = 0,R,0
domeCoord = np.array([dx, dy, dz])

# spherical mirror
r = 33 # radius of the spherical mirror in cm
ang = radians(70) - atan(13.8/8.3)
mx, my, mz  = (0,-18*sin(ang),-18*cos(ang))
mirCoord = np.array([mx, my, mz]) # the mirror has center at (0,0,0)

# projector
px, py, pz = 0, 65, -20
projectorCoord = np.array([px,py,pz]) # the coordinates of the projector (only the y matters, its the distance of it from the center of the spherical mirror)

# projectoinCenter(the line between projecion center and the projector is perpendicular to the projection plane )
aspect = 4.0/3.0
throw = 2.2
h,w = desiredVirtualImageWidth,desiredVirtualImageWidth
projectionDepth = throw*w
domeCoverRatio = 1 # 1 means 100% or the projection covers the entire dome

# rasterization: imaging a correctly projected image on the dome and find the corresponding warped picture
def pixelToWorldCoord(i,j):
  #shift center to origin
  x = i-roiX
  y = j-roiY

  #correct scale and flip
  scale = (R/roiRadius)*sqrt(domeCoverRatio)
  x *= -scale
  y *= scale

  # map 2d circle to 3d hemisphere
  theta = atan2(y,x)
  phi = pi*sqrt(x**2+y**2)/(2*R)
  z = abs(R*cos(phi))
  y = R*sin(phi)*sin(theta)
  x = R*sin(phi)*cos(theta)

  # shift back to location of dome coord
  y += R
  return x,y,z

def inROI(x,y):
  return (x-roiX)**2 + (y-roiY)**2 <= roiRadius**2

def outerProduct(a,b):
  return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2] , a[0]*b[1]-a[1]*b[0])

def lightRayDisSquared(x):
  x1 ,x2, x3 = x[0], x[1], x[2]
  return sqrt((px-x1)**2+(py-x2)**2+(pz-x3)**2) + sqrt((wx-x1)**2+(wy-x2)**2+(wz-x3)**2)

def pointOnMirror(x):#Constraint 1
  return (x[0]-mx)**2 + (x[1]-my)**2 + (x[2]-mz)**2 - r**2

def pointOnPlane(x): #Constraint 2
  return (x[0]-mx)*n[0] + (x[1]-my)*n[1] + (x[2]-mz)*n[2]

def pointOnDome(x):#Constraint 1
  return (x[0]-dx)**2 + (x[1]-dy)**2 + (x[2]-dz)**2 - R**2 <= 0.01

# used for later minimization
x0 = [0,r,0]
bnds = [(mx-r,mx+r),(my,my+r),(mz-r,mz+r)]# the (lowerBound, UpperBound for x,y,z)
con1 = {'type': 'eq', 'fun':pointOnMirror}
con2 = {'type': 'eq', 'fun':pointOnPlane}
cons = [con1, con2]

wx,wy,wz = 0,0,0
n = (1,1,1)
def findPointOnMirror(i,j):
  global n,wx,wy,wz
  wx,wy,wz = pixelToWorldCoord(i,j)
  n = outerProduct((wx-mx,wy-my,wz-mz) ,(px-mx,py-my,pz-mz))
  sol = minimize(lightRayDisSquared,x0,bounds = bnds, constraints=cons)
  return sol.x

def mag(v):
   return sqrt(v[0]**2+v[1]**2+v[2]**2)

def angleBetween(a,b):
  adotb = a[0]*b[0]+a[1]*b[1]+a[2]*b[2]
  return acos(adotb/(mag(a)*mag(b)))

negY = [0,-1,0]
projectionCenter = findPointOnMirror(roiX,roiY)
projectionDirection = projectionCenter - projectorCoord
tiltAngle = -angleBetween(projectionDirection,negY)

def toProjectionPlane(u): 
    # input u is a vector
    #rotate in respect to the projector
    u = u - projectorCoord
    # tilt back to tilt angle
    y = u[1]*cos(tiltAngle) - u[2]*sin(tiltAngle)
    z = u[1]*sin(tiltAngle) + u[2]*cos(tiltAngle)
    u[1] = y
    u[2] = z
    u = u/float(y)*projectionDepth
    return u

start_time = time.time()
maxU = -1*10000
maxV = -1*10000
minU = 10000
minV = 10000
mapping = np.full((h,w,2), -1, dtype=int) # mapping[i][j] = u,v

for i in range(w):
  for j in range(h):
    if inROI(i,j):
      rx,ry,rz = toProjectionPlane(findPointOnMirror(i,j)) #sol.x is the reflection points
      u = int(round(rx))
      v = int(round(rz))
      mapping[i][j][0] = u
      mapping[i][j][1] = v
      maxU = max(maxU,u)
      maxV = max(maxV,v)
      minU = min(minU,u)
      minV = min(minV,v)

for i in range(w):
  for j in range(h):
    print()
    if mapping[i][j][0] != -1:
      mapping[i][j][0] -= minU
      mapping[i][j][1] -= minV


elapsed_time = time.time() - start_time
print(elapsed_time)
np.save('mapping', mapping)

# the width and height of the new image(can be scaled later)
nw = maxU-minU+1
nh = maxV-minV+1