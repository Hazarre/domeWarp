from Point3D import *
import numpy as np
import cv2
import time
from math import *
from scipy.optimize import minimize

# This program involves three steps to obtain the pre-warping for dome projection with a spherical mirror.
# 1) use backward trace (opposite to direction of light) to find the mapping of the boundry of the ROI on the pre-warped image
# 2) use forward trace to grab all the other mapping for pixels wihtin-  ROI
# 3) save the mapping of (i,j) to (u,v) for image transformation: pre-warpedImg[u][v] = inputImg[i][j]

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



img = cv2.imread("C:\\Users\\henry\\Desktop\\BSRI\\CircularMesh.jpg", 1)
h,w,d = img.shape

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

def angleBetween2(a,b):
  adotb = a[0]*b[0]+a[1]*b[1]+a[2]*b[2]
  return acos(adotb/(mag(a)*mag(b)))

negY = [0,-1,0]
projectionCenter = findPointOnMirror(roiX,roiY)
projectionDirection = projectionCenter - projectorCoord
tiltAngle = -angleBetween2(projectionDirection,negY)

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


#######################################Forward 

mirVect = Point3D(mx,my,mz)
projCenter = Point3D(0,0,0)
projector = Point3D(px, py, pz)
projectingVect = sub(projCenter, projector)
projectionDepth = w * throw


def pixelToImagePlane(i, j):
  # map to Image on centered on x - axis
  u = Point3D(w/2-i, -projectionDepth, h/2-j)
  # tilt to projection plane into projection direction
  negY = Point3D(0,-1,0)
  theta = -(angleBetween(negY,projectingVect))
  v = u.copy()
  v.y = u.y*cos(theta) - u.z*sin(theta)
  v.z = u.y*sin(theta) + u.z*cos(theta)
  v.add(projector)
  return v

def imagePlaneToMirror(u):
  i = sub(u,projector)
  a = i.magSquared()
  b = 2*dot(i,projector) - 2*dot(mirVect,i)
  c = projector.magSquared() + mirVect.magSquared() - 2*dot(projector,mirVect) - r**2
  if b**2- 4*a*c < 0:
    return False
  d = (-1*b - sqrt(b**2- 4*a*c))/(2*a)
  i.mult(d)
  v = add(projector, i)
  return v

def mirrorToDome(u):
  u.sub(mirVect)
  projector.sub(mirVect)
  theta = angleBetween(u,projector)
  n = u.copy()
  n.setMag(2*projector.mag()*cos(theta))
  k = sub(n,projector)
  f = sub(k,u)
  a = dot(f,f)
  b = 2*dot(u,f) - 2*R*f.y
  c = dot(u,u) - 2*R*u.y
  if b**2- 4*a*c < 0:
    print("unexpectect")
    return False
  d = (-1*b+sqrt(b**2-4*a*c))/(2*a)
  f.mult(d)
  v = add(u,f)
  v.add(mirVect)
  u.add(mirVect)
  projector.add(mirVect)
  return v

def domeToCircle(u):
  # shift to origin
  v = u.copy()
  v.y = v.y - R
  posZ = Point3D(0,0,1)
  phi = angleBetween(v, posZ)
  v.z = 0
  v.setMag(2*R*phi/pi)
  v.y = v.y + R
  return v

def circleToPixel(u):
  # shift to origin
  v = u.copy()
  v.y = v.y - R
  # rotate about y-axis
  l = v.copy()
  # x y coords are now becoming pixel i, v
  v.x = l.x*cos(-pi/2) - l.y*sin(-pi/2)
  v.y = l.x*sin(-pi/2) + l.y*cos(-pi/2)
  v.mult(h/(2*R))
  return v

def correctToDistorted(i, j):
  return circleToPixel(domeToCircle(mirrorToDome(imagePlaneToMirror(pixelToImagePlane(i,j)))))



mapping = np.full((h,w,2), -1, dtype=int) # mapping[i][j] = u,v


boundary = {}
for i in range(w):
  for j in range(h):
    if inROI(i,j):
      rx,ry,rz = toProjectionPlane(findPointOnMirror(i,j)) #sol.x is the reflection points
      boundary[int(rz)]=rx

     
      
      print(rx, ry, rz)
      break


stime = time.time()
imgWarped = np.full([h,w,3],255,dtype=img.dtype)
imgCenter = correctToDistorted(w/2,h/2)


for i in range(w):
  for j in range(h):
    v = pixelToImagePlane(i,j)
    x = v.x
    z = int(v.z)

    if z in boundary:
      print(z)
      if abs(v.x) <= boundary[z]:
        onMirror = imagePlaneToMirror(v)
        onDome = mirrorToDome(onMirror)
        distorted = circleToPixel(domeToCircle(onDome))
        distorted.sub(imgCenter)
        distorted.mult(scale)

        disx = int(distorted.x + w/2)
        disy = int(distorted.y + h/2)

        if(disy >= 0 and disy < h and disx >= 0 and disx < w):
          imgWarped[j][i] = img[disy][disx]


etime = time.time()
print(etime-stime)
cv2.imshow('image',imgWarped)
cv2.waitKey(0)
cv2.destroyAllWindows()
