# -*- coding: utf-8 -*-

from math import *

def convert(a):
  if abs(a) > 360 :
    a = a%360
  if a < 0 :
    a += 360
  return a

def m_vektor(p1, p2):
  m = (p2[0]-p1[0])**2+(p2[1]-p1[1])**2
  return m**0.5

def mv(v):
  return (v[0]**2+v[1]**2)**0.5

def c_vektor(p1, p2):
  x = p1[0]+(p2[0]-p1[0])/2
  y = p1[1]+(p2[1]-p1[1])/2
  return x, y

def ln_vektor(p1, p2, ln):
  x1, y1 = p1
  x2, y2 = p2
  ab = m_vektor(p1, p2)
  k = ln/ab
  x, y = x2-x1, y2-y1
  return x*k, y*k

def sum_v_in_point(x1,y1,x2,y2):
  return x2+(x1-x2)/2,y2+(y1-y2)/2

def c_okr(r,a=360):
  return pi*r/180*a
def s_okr(r,a=360):
  return pi*r**2/360*a

def init_lists():
  global sin_list,cos_list,tan_list
  sin_list = [sct(a,1) for a in range(361)]
  cos_list = [sct(a,2) for a in range(361)]
  tan_list = [sct(a,3) for a in range(361)]
  tan_list[90] = tan_list[270] = None

def sct(a, typ=1):
  rad = pi*a/180
  if typ == 1 :
    if a in (180, 360):
      return 0
    return sin(rad)
  elif typ == 2 :
    if a in (90, 270):
      return 0
    return cos(rad)
  elif typ == 3 :
    if a in (180, 360):
      return 0
    return tan(rad)
  elif typ == 4 :
    tn = sct(a, 3)
    if tn == 0 :
      return None
    return 1/sct(a, 3)

def asct(x, typ=1):
  if   typ == 1 :
    sct_list = sin_list
  elif typ == 2 :
    sct_list = cos_list
  elif typ == 3 :
    sct_list = tan_list
  if x in sct_list :
    a = sct_list.index(x)
    if a > 180 :
      a = 360-a
    return a
  for a in range(360):
    if sct_list[a] < x < sct_list[a+1] :
      if a > 180 :
        a = 360 - a
      return a

def gip(a,b,c=None):
  if not c :
    return (a**2+b**2)**0.5
  if not a :
    return (c**2-b**2)**0.5
  if not b :
    return (c**2-a**2)**0.5

def v_to_func_from_x(v,x):
  return x*v[1]/v[0]
def v_to_func_from_y(v,y):
  return y*v[0]/v[1]

def move(angle,ln):
  x, y = ln*sct(angle, 2), ln*sct(angle)
  return [x, y]

def angle_to_point(pos1, pos2):
  x1, y1 = pos1
  x2, y2 = pos2
  ln = m_vektor(pos1, pos2)
  sin = abs(y2-y1)/ln
  a = asct(sin)
  if y1 < y2 :
    a = -a
  if 0 < a < 90 and x1 > x2 :
    a = 180-a
  return convert(a)

def get_func(p1, p2, type=1):
  angle = angle_to_point(p1, p2)
  if angle in (90, 270):
    if type == 1:
      return None
    else:
      return lambda x:  p1[0]
  elif angle in (0, 180):
    if type == 1:
      return lambda x : p1[1]
    else:
      return None
  a = float(p2[1]-p1[1])/float(p2[0]-p1[0])
  b = p1[1]-a*p1[0]
  if type == 1 :
    return lambda x : a*x+b
  else:
    return lambda y : (y-b)/a

def point_in_lines(p1, p2, p3, p4):
  if p1[0] == p2[0]:
    x = p1[0]
    y = get_func(p3, p4)(x)
    return x, y
  elif p3[0] == p4[0]:
    x = p3[0]
    y = get_func(p1, p2)(x)
    return x, y
  else:
    a1 = (p2[1]-p1[1])/(p2[0]-p1[0])
    b1 = p1[1]-a1*p1[0]
    a2 = (p4[1]-p3[1])/(p4[0]-p3[0])
    b2 = p3[1]-a2*p3[0]
    if a1 == a2:
      return None
    x = (b2-b1)/(a1-a2)
    y = a1*x+b1
    return x, y

# an = 2Rsin(180/n)
# r = Rcos(180/n)
# a = 2Rsin(pi/n) = 2rtg(pi/n)

global sin_list, cos_list, tan_list
init_lists()
