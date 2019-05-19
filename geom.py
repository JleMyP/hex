# -*- coding: utf-8 -*-

from math import *


def convert(a):
    if abs(a) > 360:
        a = a % 360
    if a < 0:
        a += 360
    return a


def m_vektor(p1, p2):
    m = (p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2
    return m ** 0.5


def init_lists():
    sin_list = [sct(a, 1) for a in range(361)]
    cos_list = [sct(a, 2) for a in range(361)]
    tan_list = [sct(a, 3) for a in range(361)]
    tan_list[90] = tan_list[270] = None
    return sin_list, cos_list, tan_list


def sct(a, typ=1):
    rad = pi * a / 180
    if typ == 1:
        if a in (180, 360):
            return 0
        return sin(rad)
    elif typ == 2:
        if a in (90, 270):
            return 0
        return cos(rad)
    elif typ == 3:
        if a in (180, 360):
            return 0
        return tan(rad)
    elif typ == 4:
        tn = sct(a, 3)
        if tn == 0:
            return None
        return 1 / sct(a, 3)


def asct(x, typ=1):
    if typ == 1:
        sct_list = sin_list
    elif typ == 2:
        sct_list = cos_list
    elif typ == 3:
        sct_list = tan_list

    if x in sct_list:
        a = sct_list.index(x)

        if a > 180:
            a = 360 - a

        return a

    for a in range(360):
        if sct_list[a] < x < sct_list[a + 1]:
            if a > 180:
                a = 360 - a

            return a


def move(angle, ln):
    x = ln * sct(angle, 2)
    y = ln * sct(angle)
    return [x, y]


def angle_to_point(pos1, pos2):
    x1, y1 = pos1
    x2, y2 = pos2
    ln = m_vektor(pos1, pos2)
    sin = abs(y2 - y1) / ln
    a = asct(sin)

    if y1 < y2:
        a = -a

    if 0 < a < 90 and x1 > x2:
        a = 180 - a

    return convert(a)


def get_func(p1, p2, type=1):
    angle = angle_to_point(p1, p2)

    if angle in (90, 270):
        if type == 1:
            return None
        return lambda x: p1[0]
    elif angle in (0, 180):
        if type == 1:
            return lambda x: p1[1]
        return None

    a = float(p2[1] - p1[1]) / float(p2[0] - p1[0])
    b = p1[1] - a * p1[0]

    if type == 1:
        return lambda x: a * x + b
    return lambda y: (y - b) / a


sin_list, cos_list, tan_list = init_lists()
