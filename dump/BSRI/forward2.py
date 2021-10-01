from Point3D import *
import cv2
import numpy as np

R = 150 # radius of the dome
r = 33 # radius of the spherical mirror in cm

dx, dy, dz = 0,R,0 # dome coord
ang = radians(70) - atan(13.8/8.3) # mirror coord
mx, my, mz  = 0,  -18*sin( 70*pi/180 - atan(8.3/13.8) ), -18*cos( 70*pi/180 - atan(8.3/13.8) )
px, py, pz = 0, 75, -20 # projector coordinate
cx,cy,cz = 0,0,0 # a coordinate that the projector light ray shoots on

projectorThrow = 2.2
aspect = 4.0/3.0

img = cv2.imread("CircularMesh.jpg")
h,w,d = img.shape

mirVect = Point3D(mx,my,mz)
projCenter = Point3D(cx, cy, cz)
projector = Point3D(px, py, pz)
projectingVect = sub(projCenter, projector)
projectionDepth = w * projectorThrow


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
    print("unexpectec")
    return False
  d = (-1*b+sqrt(b**2-4*a*c))/(2*a)

  #start debugg from here
  f.mult(d)
  v = add(u,f)
  show(v)
  v.add(mirVect)
  u.add(mirVect)
  projector.add(mirVect)
  return v

def domeToCircle(u):
  # shift to origin
  v = u.copy()
  v.y = v.y - R
  posY = Point3D(0,1,0)
  phi = angleBetween(v, posY)
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



test = [(w//4,w//4), (w//4*3, w//4), (w//4,w//4*3), (w//4*3,w//4*3)]
for t in test: 
  v = mirrorToDome(imagePlaneToMirror(pixelToImagePlane(t[0],t[1])))
  #show(v)
  


imgWarped = np.full([h,w,3],255,dtype=img.dtype)
imgCenter = correctToDistorted(w/2,h/2)
scale = 0.7
for i in range(w):
  for j in range(h):
    onMirror = imagePlaneToMirror(pixelToImagePlane(i,j))
    if onMirror != False: #(onMirror.y < mirVect.y):
      onDome = mirrorToDome(onMirror)
      distorted = circleToPixel(domeToCircle(onDome))
      distorted.sub(imgCenter)
      distorted.mult(scale)

      disx = int(distorted.x + w/2)
      disy = int(distorted.y + h/2)

      if(disy >= 0 and disy < h and disx >= 0 and disx < w):
        imgWarped[j][i] = img[disy][disx]



cv2.imshow('image',imgWarped)
cv2.waitKey(0)
cv2.destroyAllWindows()
