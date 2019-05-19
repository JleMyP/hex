import os
import sys
from random import randrange as rnd
from typing import Tuple, List

import pygame
from pygame import locals

import geom


point_type = Tuple[int] or List[int]


class TrueSix:
    def __init__(self, side_length: int, center: point_type = (0, 0), angle: int = 0):
        self.side_length = side_length
        self.angle = angle

        self.radius_y = side_length * geom.sct(30, 2)
        self.radius_x = side_length * geom.sct(30, 1)
        self.rect = pygame.Rect((0, 0, self.side_length * 2, self.radius_y * 2))
        self.rect.center = center

        self.points = six_angle(side_length, center, angle)
        self.points.append(self.points[0])

        self.funcs = [geom.get_func(self.points[n], self.points[n + 1]) for n in range(6)]

    def copy(self):
        return self.__class__(self.side_length, self.rect.center, self.angle)

    def move(self, x: int, y: int):
        for p in self.points:
            p[0] += x
            p[1] += y

        self.rect.move_ip(x, y)


class TrueSixHorizontal(TrueSix):
    def __init__(self, side_length: int, center: point_type = (0, 0)):
        TrueSix.__init__(self, side_length, center, 0)
        self.func_dict = {
            'bottom-right': self.funcs[0],
            'bottom': self.funcs[1],
            'bottom-left': self.funcs[2],
            'top-left': self.funcs[3],
            'top': self.funcs[4],
            'top-right': self.funcs[5]
        }

    def copy(self):
        return self.__class__(self.side_length, self.rect.center)

    def collide(self, pos: point_type):
        x, y = pos
        left = self.rect.centerx - self.side_length / 2
        right = self.rect.centerx + self.side_length / 2

        if self.rect.collidepoint(pos):
            if left <= x <= right:
                return True

            if x < left:
                func_bottom_left = self.func_dict['bottom-left']
                func_top_left = self.func_dict['top-left']

                # vertical inversion
                if func_top_left(x) <= y <= func_bottom_left(x):
                    return True
            elif x > right:
                func_top_right = self.func_dict['top-right']
                func_bottom_right = self.func_dict['bottom-right']

                # vertical inversion
                if func_bottom_right(x) >= y >= func_top_right(x):
                    return True

        return False


class TrueSixVertical(TrueSix):
    def __init__(self, side_length: int, center: point_type = (0, 0)):
        TrueSix.__init__(self, side_length, center, 30)
        self.func_dict = {
            'bottom-right': self.funcs[0],
            'bottom-left': self.funcs[1],
            'left': self.funcs[2],
            'top-left': self.funcs[3],
            'top-right': self.funcs[4],
            'right': self.funcs[5]
        }

    def copy(self):
        return self.__class__(self.side_length, self.rect.center)

    def collide(self, pos: point_type):
        x, y = pos
        top = self.rect.centery - self.side_length / 2
        bottom = self.rect.centery + self.side_length / 2

        if self.rect.collidepoint(pos):
            if top <= y <= bottom:
                return True

            if y < top:
                func_top_left = self.func_dict['top-left']
                func_top_right = self.func_dict['top-right']

                # vertical inversion
                if y >= func_top_right(x) and y >= func_top_left(x):
                    return True
            elif y > bottom:
                func_bottom_left = self.func_dict['bottom-left']
                func_bottom_right = self.func_dict['bottom-right']

                # vertical inversion
                if y <= func_bottom_left(x) and y <= func_bottom_right(x):
                    return True

        return False


class CellBase:
    def __init__(self):
        raise NotImplementedError()

    def copy(self):
        return self.__class__(self.side_length, self.rect.center, self.pos, self.val)

    def draw(self, color: Tuple[int] or List[int] or int = 0, width: int = 2):
        if not color:
            clr = (int(255 / self.val),) * 3 if self.val else 0
            pygame.draw.polygon(window, clr, self.points[:-1])

        pygame.draw.polygon(window, color, self.points[:-1], width)

    def find_neighbors(self, deep: int) -> List:
        lst = self.neighbors[:]

        for n in range(deep - 1):
            for i in range(len(lst)):
                for s in lst[i].neighbors:
                    if s not in lst:
                        lst.append(s)

        lst.remove(self)
        return lst


class CellHorizontal(CellBase, TrueSixHorizontal):
    def __init__(self, side_length: int, center: point_type, pos: point_type, val: int = 1):
        TrueSixHorizontal.__init__(self, side_length, center)
        self.x, self.y = self.pos = pos
        self.val = val
        self.astar = [0, 0, 0, None]
        self.neighbors = []

    def copy(self):
        return self.__class__(self.side_length, self.rect.center, self.pos, self.val)

    def draw(self, color: Tuple[int] or List[int] or int = 0, width: int = 2):
        if not color:
            clr = (int(255 / self.val),) * 3 if self.val else 0
            pygame.draw.polygon(window, clr, self.points[:-1])

        pygame.draw.polygon(window, color, self.points[:-1], width)

    def find(self, map):
        self.neighbors = []

        if self.y > 0:
            self.neighbors.append(map[self.x][self.y - 1])
        if self.y + 1 < len(map[self.x]):
            self.neighbors.append(map[self.x][self.y + 1])

        y = self.y + self.x % 2 - 1

        if self.x > 0:
            if y >= 0:
                self.neighbors.append(map[self.x - 1][y])
            if y + 1 < len(map[self.x - 1]):
                self.neighbors.append(map[self.x - 1][y + 1])

        if self.x + 1 < len(map):
            if y >= 0:
                self.neighbors.append(map[self.x + 1][y])
            if y + 1 < len(map[self.x + 1]):
                self.neighbors.append(map[self.x + 1][y + 1])


class CellVertical(CellBase, TrueSixVertical):
    def __init__(self, side_length: int, center: point_type, pos: point_type, val: int = 1):
        TrueSixVertical.__init__(self, side_length, center)
        self.x, self.y = self.pos = pos
        self.val = val
        self.astar = [0, 0, 0, None]
        self.neighbors = []

    def find(self, map):
        self.neighbors = []

        if self.y > 0:
            self.neighbors.append(map[self.x][self.y - 1])
        if self.y + 1 < len(map[self.x]):
            self.neighbors.append(map[self.x][self.y + 1])

        if not self.y % 2 and self.x > 0:
            x = self.x - 1
        elif self.y % 2 and self.x + 1 < len(map):
            x = self.x + 1
        else:
            x = None

        if self.x > 0:
            self.neighbors.append(map[self.x - 1][self.y])
        if self.x + 1 < len(map):
            self.neighbors.append(map[self.x + 1][self.y])

        if x is not None:
            if self.y > 0:
                self.neighbors.append(map[x][self.y - 1])
            if self.y + 1 < len(map[self.x]):
                self.neighbors.append(map[x][self.y + 1])

        while None in self.neighbors:
            self.neighbors.remove(None)


class HexMap:
    def __init__(self, width1: int, width2: int, height1: int, height2: int, cells: list):
        self.width1 = width1
        self.width2 = width2
        self.height1 = height1
        self.height2 = height2
        self.cells = cells

    @classmethod
    def init_horizontal(cls, radius: int or None = None, width: int or None = None, height: int or None = None):
        if width is not None and height is not None:
            # TODO: some time throws index error
            w1 = w2 = int(width / 2)
            h1 = h2 = height
            # TODO: shit
            r1 = (win_w / (w1 * 3 + 1.5) + win_w / (w1 * 3)) / 2
            r2 = (win_h / (h1 * 2 + 2) + win_h / (h1 * 2 + 1)) / (2 * geom.sct(30, 2))
            radius = int(min(r1, r2))
            y = radius * geom.sct(30, 2)
        elif radius is not None:
            y = radius * geom.sct(30, 2)
            # TODO: shit
            w1 = int((win_w - radius * 2) // (radius * 3)) + 1
            w2 = int((win_w - radius * 3.5) // (radius * 3)) + 1
            h1 = int(win_h / (y * 2))
            h2 = int((win_h - y) / (y * 2))
        else:
            raise Exception()

        lnx = radius * 3
        lny = y * 2
        six1 = TrueSixHorizontal(radius, (radius, y))
        # TODO: shit
        six2 = TrueSixHorizontal(radius, (radius * 2.5, y * 2))

        # TODO: shit
        right = win_w - radius * 2 - int((w1 - 1) * lnx + (w2 - w1 + 1) * lnx / 2)
        bottom = win_h - int(h1 * lny + (h2 - h1 + 1) * lny / 2)

        six1.move(right / 2 - lnx, bottom / 2 - lny)
        six2.move(right / 2 - lnx, bottom / 2 - lny)

        cells: List[List[CellHorizontal]] = [[] for x in range(int(w1 + w2))]

        for s, w, h, m in ((six1, w1, h1, 0), (six2, w2, h2, 1)):
            for y in range(h):
                s.move(0, lny)
                six = s.copy()

                for x in range(w):
                    six.move(lnx, 0)
                    # TODO: shit
                    cell = CellHorizontal(radius, six.rect.center, (x * 2 + m, y), rnd(5))
                    cells[x * 2 + m].append(cell)

        for line in cells:
            for cell in line:
                cell.find(cells)

        # return HexMap(w1, w2, h1, h2, cells)
        return w1, w2, h1, h2, cells

    @classmethod
    def init_vertical(cls, radius: int):
        six1 = TrueSixVertical(radius)
        # TODO: shit
        lny = radius * 3
        lnx = six1.radius_y * 2
        six1.move(six1.rect.right - lnx, six1.rect.bottom - lny)
        six2 = TrueSix(radius, (six1.rect.centerx + lnx / 2, six1.rect.centery + lny / 2), 30)

        w1 = int(win_w // lnx)
        w2 = int((win_w - lnx / 2) / lnx)
        h1 = int((win_h - six1.rect.bottom) / lny)
        h2 = int((win_h - six2.rect.bottom) / lny)

        right = int(win_w - w1 * lnx - (w2 - w1 + 1) * lnx / 2)
        bottom = int(win_h - radius * 2 - (h1 - 1) * lny - (h2 - h1 + 1) * lny / 2)

        six1.move(right / 2, bottom / 2)
        six2.move(right / 2, bottom / 2)

        cells: List[List[CellVertical or None]] = [[None for y in range(h1 + h2)] for x in range(w1)]

        for s, w, h, m in ((six1, w1, h1, 0), (six2, w2, h2, 1)):
            for y in range(h):
                s.move(0, lny)
                six = s.copy()

                for x in range(w):
                    six.move(lnx, 0)
                    # TODO: shit
                    cells[x][y * 2 + m] = CellVertical(radius, six.rect.center, (x, y * 2 + m), rnd(4))

        for line in cells:
            for c in line:
                if c:
                    c.find(cells)

        # return HexMap(w1, w2, h1, h2, cells)
        return w1, w2, h1, h2, cells

    def draw(self):
        for line in self.cells:
            for cell in line:
                cell.draw()


class AStarFinder:
    def __init__(self, hex_map: HexMap):
        self.hex_map = hex_map
        self.h_func = lambda a, b: ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5
        # TODO: add dataclass or dict

    def find_path(self, start: point_type, finish: point_type):
        xs, ys = start
        opens, closed, path = [map[xs][ys]], [], []
        map[xs][ys].astar = [0, 0, 0, None]

        while opens:
            v = opens.pop(-1)
            closed.append(v)

            if v.pos == finish:
                break

            for next in v.neighbors:
                if not next.val or next in closed:
                    continue

                g = v.astar[0] + 10 * next.val

                if next not in opens:
                    hh = self.h_func(next.pos, finish)
                    next.astar = [g, hh, g + hh, v]
                    opens.append(next)
                else:
                    if g < next.astar[0]:
                        next.astar[0] = g
                        next.astar[2] = g + next.astar[1]
                        next.astar[3] = v

            if opens:
                opens = sort_opens(opens)

        if closed[-1].pos == finish:
            v = closed[-1]

            while 1:
                path.append(v.pos)

                if v.pos == start:
                    break

                v = v.astar[3]

            path.reverse()

        return path

    def sort_opens(self, opens):
        min = -1

        for n in range(len(opens) - 1):
            if opens[n].astar[2] < opens[min].astar[2]:
                min = n

        opens[-1], opens[min] = opens[min], opens[-1]
        return opens


def six_angle(ln: int, pos: point_type, angle: int = 0):
    # a = 2Rsin(pi/n) = R
    x, y = pos
    points = []

    for a in range(angle, 360, 60):
        xn, yn = geom.move(a, ln)
        points.append([x + xn, y + yn])

    return points


def draw():
    window.fill((255, 255, 255))

    # hex_map.draw()

    for line in map:
        for c in line:
            if c:
                c.draw()

    if start:
        start.draw((0, 255, 0), 3)

    if path:
        for x, y in path:
            map[x][y].draw((255, 0, 0), 3)

    pygame.display.update()


def event_callback():
    global start, path, neighbors

    for event in pygame.event.get():
        if event.type == locals.MOUSEBUTTONDOWN:
            for line in map:
                for c in line:
                    if c and c.collide(event.pos):
                        if c.val:
                            if not start:
                                start = c
                                neighbors = c.find_neighbors(3)
                            else:
                                if start == c:
                                    start = path = neighbors = None
                                else:
                                    path = find_path_astar(start.pos, c.pos)

                        return
        elif event.type == locals.QUIT or event.type == locals.KEYDOWN and event.key == locals.K_ESCAPE:
            pygame.quit()
            sys.exit()


def sort_opens(opens):
    min = -1

    for n in range(len(opens) - 1):
        if opens[n].astar[2] < opens[min].astar[2]:
            min = n

    opens[-1], opens[min] = opens[min], opens[-1]
    return opens


def find_path_astar(start, finish):
    h_func = lambda a, b: ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5
    xs, ys = start
    opens, closed, path = [map[xs][ys]], [], []
    map[xs][ys].astar = [0, 0, 0, None]

    while opens:
        v = opens.pop(-1)
        closed.append(v)

        if v.pos == finish:
            break

        for next in v.neighbors:
            if not next.val or next in closed:
                continue

            g = v.astar[0] + 10 * next.val

            if next not in opens:
                hh = h_func(next.pos, finish)
                next.astar = [g, hh, g + hh, v]
                opens.append(next)
            else:
                if g < next.astar[0]:
                    next.astar[0] = g
                    next.astar[2] = g + next.astar[1]
                    next.astar[3] = v

        if opens:
            opens = sort_opens(opens)

    if closed[-1].pos == finish:
        v = closed[-1]

        while 1:
            path.append(v.pos)

            if v.pos == start:
                break

            v = v.astar[3]

        path.reverse()

    return path


os.environ['SDL_VIDEO_CENTERED'] = '1'
win_w, win_h = 800, 600

pygame.init()
window = pygame.display.set_mode((win_w, win_h))
pygame.display.set_caption('Hex A*')
clock = pygame.time.Clock()
font30 = pygame.font.Font('freesansbold.ttf', 30)

w1, w2, h1, h2, map = HexMap.init_horizontal(radius=50)
# w1, w2, h1, h2, map = HexMap.init_vertical(50)
start = path = neighbors = None


while 1:
    event_callback()
    draw()
    clock.tick()
