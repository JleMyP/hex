import pygame, geom, sys, os
from pygame.locals import *
from random import randrange as rnd


class TrueSix(object):
  def __init__(self, ln, center=(0,0), a=0):
    self.R, self.an, self.a = ln, 120, a
    self.r = ln*geom.sct(30, 2)
    self.points = six_angle(ln, center, a)
    self.points.append(self.points[0])
    self.rect = pygame.Rect((0, 0, self.R*2, self.r*2))
    self.rect.center = center
    self.funcs = [geom.get_func(self.points[n], self.points[n+1]) for n in range(6)]
  
  def move(self, x, y):
    for p in self.points:
      p[0], p[1] = p[0]+x, p[1]+y
    self.rect.move_ip(x, y)
  
  def collide(self, pos):
    x, y = pos
    l, r = self.rect.centerx-self.R/2, self.rect.centerx+self.R/2
    if self.rect.collidepoint(pos):
      if l <= x <= r:
        return True
      elif x < l:
        fd, fu = self.funcs[2:4]
        if y >= fu(x) and y <= fd(x):
          return True
      elif x > r:
        fu, fd = self.funcs[-1], self.funcs[0]
        if y >= fu(x) and y <= fd(x):
          return True
    return False
  
  def collide2(self, pos):
    x, y = pos
    t, b = self.rect.centery-self.R/2, self.rect.centery+self.R/2
    if self.rect.collidepoint(pos):
      if t <= y <= b:
        return True
      elif y < t:
        fr, fl = self.funcs[:2]
        if y <= fl(x) and y <= fr(x):
          return True
      elif y > b:
        fl, fr = self.funcs[3:5]
        if y >= fl(x) and y >= fr(x):
          return True
    return False
  
  def copy(self):
    return TrueSix(self.R, self.rect.center, self.a)


class Cell(TrueSix):
  def __init__(self, ln, center, pos, val=1):
    TrueSix.__init__(self, ln, center)
    self.x, self.y = self.pos = pos
    self.val, self.astar = val, [0, 0, 0, None]
  
  def copy(self):
    return self.__class__(self.R, self.rect.center, self.pos, self.val)
  
  def draw(self, color=0, width=2):
    if not color:
      clr = (int(255/self.val),)*3 if self.val else 0
      pygame.draw.polygon(window, clr, self.points[:-1])
    pygame.draw.polygon(window, color, self.points[:-1], width)
  
  def find(self, map):
    self.sosedi = []
    if self.y > 0:
      self.sosedi.append(map[self.x][self.y-1])
    if self.y+1 < len(map[self.x]):
      self.sosedi.append(map[self.x][self.y+1])
    y = self.y + self.x%2 - 1
    if self.x > 0:
      if y >= 0:
        self.sosedi.append(map[self.x-1][y])
      if y+1 < len(map[self.x-1]):
        self.sosedi.append(map[self.x-1][y+1])
    if self.x+1 < len(map):
      if y >= 0:
        self.sosedi.append(map[self.x+1][y])
      if y+1 < len(map[self.x+1]):
        self.sosedi.append(map[self.x+1][y+1])


class Cell2(Cell):
  collide = TrueSix.collide2
  def __init__(self, ln, center, pos, val=1):
    TrueSix.__init__(self, ln, center, 30)
    self.x, self.y = self.pos = pos
    self.val = val
  
  def find(self, map):
    self.sosedi = []
    if self.y > 0:
      self.sosedi.append(map[self.x][self.y-1])
    if self.y+1 < len(map[self.x]):
      self.sosedi.append(map[self.x][self.y+1])
    
    if not self.y%2 and self.x > 0:
      x = self.x-1
    elif self.y%2 and self.x+1 < len(map):
      x = self.x+1
    else: x = None
    
    if self.x > 0:
      self.sosedi.append(map[self.x-1][self.y])
    if self.x+1 < len(map):
      self.sosedi.append(map[self.x+1][self.y])
    
    if not (x is None):
      if self.y > 0:
        self.sosedi.append(map[x][self.y-1])
      if self.y+1 < len(map[self.x]):
        self.sosedi.append(map[x][self.y+1])
     
    while None in self.sosedi: self.sosedi.remove(None)


class Player(object):
  def __init__(self, pos, r):
    self.cell = map[pos[0]][pos[1]]
    self.r = r
    

def six_angle(ln, pos, angle=0):
# a = 2Rsin(pi/n) = R
  x, y = pos
  points = []
  for a in range(angle, 360, 60):
    xn, yn = geom.move(a, ln)
    points.append([x+xn, y+yn])
  return points

def find_sosedi(cell, lvl):
  lst = cell.sosedi[:]
  for n in range(lvl-1):
    for i in range(len(lst)):
      for s in lst[i].sosedi:
        if s not in lst: lst.append(s)
  lst.remove(cell)
  return lst

def draw():
  window.fill((255,255,255))
  for line in map:
    for c in line:
      if c: c.draw()
  if start:
    start.draw((0,255,0), 3)
    for c in sosedi: c.draw((255,0,255), 3)
  if path:
    for x, y in path: map[x][y].draw((255,0,0), 3)
  pygame.display.update()

def event_callback():
  global start, path, sosedi
  for event in pygame.event.get():
    if event.type == MOUSEBUTTONDOWN:
      for line in map:
        for c in line:
          if c and c.collide(event.pos) and c.val:
            if not start:
              start = c
              sosedi = find_sosedi(c, 3)
            else:
              if start == c:
                start = path = sosedi = None
              else:
                path = find_path_astar(start.pos, c.pos)

def init_map(r):
  if not isinstance(r, int):
    w1 = w2 = r[0]/2
    h1 = h2 = r[1]
    r1 = (win_w/(w1*3+1.5)+win_w/(w1*3))/2
    r2 = (win_h/(h1*2+2)+win_h/(h1*2+1))/(2*geom.sct(30, 2))
    r = int(min(r1, r2))
    y = r*geom.sct(30,2)
  else:
    y = r*geom.sct(30,2)
    w1  = (win_w-r*2)//(r*3)+1
    w2 = (win_w-r*3.5)//(r*3)+1
    h1 = int(win_h/(y*2))
    h2 = int((win_h-y)/(y*2))
  
  lnx, lny = r*3, y*2
  six1 = TrueSix(r, (r, y))
  six2 = TrueSix(r, (r*2.5, y*2))
  
  right = win_w-r*2-int((w1-1)*lnx+(w2-w1+1)*lnx/2)
  bottom = win_h-int(h1*lny+(h2-h1+1)*lny/2)
  
  six1.move(right/2-lnx, bottom/2-lny)
  six2.move(right/2-lnx, bottom/2-lny)
  
  cells = [[] for x in range(w1+w2)]
  for s, w, h, m in ((six1, w1, h1, 0), (six2, w2, h2, 1)):
    for y in range(h):
      s.move(0, lny)
      six = s.copy()
      for x in range(w):
        six.move(lnx, 0)
        cells[x*2+m].append(Cell(r, six.rect.center, (x*2+m, y), rnd(5)))
  for line in cells:
    for c in line: c.find(cells)
  return w1, w2, h1, h2, right, bottom, cells

def init_map2(r):
  six1 = TrueSix(r, a=30)
  lny, lnx = r*3, six1.r*2
  six1.move(six1.rect.right-lnx, six1.rect.bottom-lny)
  six2 = TrueSix(r, (six1.rect.centerx+lnx/2, six1.rect.centery+lny/2), 30)
  
  w1  = win_w//lnx
  w2 = (win_w-lnx/2)//lnx
  h1 = (win_h-six1.rect.bottom)//lny
  h2 = (win_h-six2.rect.bottom)//lny
  
  right = int(win_w-w1*lnx-(w2-w1+1)*lnx/2)
  bottom = int(win_h-r*2-(h1-1)*lny-(h2-h1+1)*lny/2)
  
  six1.move(right/2, bottom/2)
  six2.move(right/2, bottom/2)
  
  cells = [[None for y in range(h1+h2)] for x in range(w1)]
  for s, w, h, m in ((six1, w1, h1, 0), (six2, w2, h2, 1)):
    for y in range(h):
      s.move(0, lny)
      six = s.copy()
      for x in range(w):
        six.move(lnx, 0)
        cells[x][y*2+m] = Cell2(r, six.rect.center, (x, y*2+m), rnd(4))

  for line in cells:
    for c in line:
     if c: c.find(cells)
  return w1, w2, h1, h2, right, bottom, cells

def sort_opens(opens):
  min = -1
  for n in range(len(opens)-1):
    if opens[n].astar[2] < opens[min].astar[2]:
      min = n
  opens[-1], opens[min] = opens[min], opens[-1]
  return opens

def find_path_astar(start, finish):
  h_func = lambda a, b: ((b[0]-a[0])**2+(b[1]-a[1])**2)**0.5
  xs, ys = start
  xf, yf = finish
  opens, closed, path = [map[xs][ys]], [], []
  map[xs][ys].astar = [0, 0, 0, None]
  while opens:
    v = opens.pop(-1)
    closed.append(v)
    if v.pos == finish:
      break
    for next in v.sosedi:
      if not next.val or next in closed:
        continue
      g = v.astar[0]+10*next.val
      if next not in opens:
        hh = h_func(next.pos, finish)
        next.astar = [g, hh, g+hh, v]
        opens.append(next)
      else:
        if g < next.astar[0]:
          next.astar[0], next.astar[2], next.astar[3] = g, g+next.astar[1], v
    if opens:
      opens = sort_opens(opens)
  if closed[-1].pos == finish:
    v = closed[-1]
    while 1:
      path.append(v.pos)
      if v.pos == start: break
      v = v.astar[3]
    path.reverse()
  return path



sys.stderr = sys.stdout = open('err.txt', 'w')
os.environ['SDL_VIDEO_CENTERED'] = "1"
ru = lambda x: str(x).decode('utf-8')

win_w, win_h = 0, 0
pygame.init()
window = pygame.display.set_mode((win_w, win_h), FULLSCREEN)
win_w, win_h = window.get_size()
pygame.display.set_caption('hex')
clock = pygame.time.Clock()
font30 = pygame.font.Font('freesansbold.ttf', 30)

w1, w2, h1, h2, right, bottom, map = init_map((24,12))
print w1, w2, h1, h2
start = path = sosedi = None


while 1:
  event_callback()
  draw()
  clock.tick()