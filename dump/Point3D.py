from math import *

class Point3D:
  def __init__(self, x, y, z):
    self.x = x
    self.y = y
    self.z = z

  def mag(self):
    return sqrt(self.x**2 + self.y**2 + self.z**2)

  def magSquared(self):
    return self.x**2 + self.y**2 + self.z**2

  def copy(self):
    return Point3D(self.x , self.y , self.z)

  def setMag(self,m):
    r = m/self.mag()
    self.x *= r
    self.y *= r
    self.z *= r

  def dot(self,b):
    self.x *= b.x
    self.y *= b.y
    self.z *= b.z

  def add(self,b):
    self.x += b.x
    self.y += b.y
    self.z += b.z

  def sub(self,b):
    self.x -= b.x
    self.y -= b.y
    self.z -= b.z

  def mult(self,b):
    self.x *= b
    self.y *= b
    self.z *= b

def show(a):
  print(a.x, a.y, a.z)

def dot(a,b):
  return a.x*b.x + a.y*b.y + a.z*b.z

def add(a,b):
  return Point3D(a.x + b.x, a.y + b.y, a.z + b.z)

def sub(a,b):
  return Point3D(a.x - b.x, a.y - b.y, a.z - b.z)

def mult(a,b):
  return Point3D(a.x*b , a.y*b , a.z*b)

def angleBetween(a,b):
   return acos(dot(a,b)/a.mag()/b.mag())
