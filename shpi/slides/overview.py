﻿#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pi3d
import sys
import os
from math import sin, cos, radians
import time
import json

from .. import config
from ..core import peripherals
from ..core import graphics
from ..core import mqttclient

try:
    import urllib.request as urlopen
except:
    from urllib2 import urlopen

try:
    unichr
except NameError:
    unichr = chr

shape = []
# shape.append((0,0,2))

for x in range(0, 181):
    shape.append((150 * sin(radians(x*2)), 150 * cos(radians(x*2)), 2))
    if x % 15 == 0:
        shape.append((140 * sin(radians(x*2)), 140 * cos(radians(x*2)), 2))
        shape.append((150 * sin(radians(x*2)), 150 * cos(radians(x*2)), 2))

#myTime = time.strftime("%-I:%M %p")
# shape.append((0,0,2))
background = pi3d.Sprite(camera=graphics.CAMERA, w=780, h=460, z=2.5, x=0, y=0)
background.set_shader(graphics.MATSH)
background.set_material((0.0, 0.0, 0.0))
background.set_alpha(0.7)

# default orientated in x,z plane so rotate
ball = pi3d.Disk(radius=150, sides=20, z=2.5, rx=90, camera=graphics.CAMERA)
ball.set_shader(graphics.MATSH)
ball.set_material((1, 1, 1))
ball.set_alpha(0.6)

# default orientated in x,z plane so rotate
dot = pi3d.Disk(radius=8, sides=20, z=0.1, rx=90, camera=graphics.CAMERA)
dot.set_shader(graphics.MATSH)
dot.set_material((1, 0, 0))
dot.set_alpha(1)

line = pi3d.Lines(vertices=shape, line_width=5, strip=True)
line.set_shader(graphics.MATSH)
line.set_material((0.3, 0.1, 0))
line.set_alpha(1)

seps = []
seps.append((-400, 0, 2.5))
seps.append((400, 0, 2.5))
seps.append((0, 0, 2.5))
seps.append((0, 240, 2.5))
seps.append((00, -240, 2.5))

seperator = pi3d.Lines(vertices=seps, line_width=10, strip=True)
seperator.set_shader(graphics.MATSH)
seperator.set_material((1, 1, 1))
seperator.set_alpha(0.1)

clock_sec = pi3d.Lines(
    vertices=[(0, 0, 1.2), (0, 140, 1.2)], line_width=3, strip=True)
clock_sec.set_shader(graphics.MATSH)
clock_sec.set_material((1, 0, 0))

clock_min = pi3d.Lines(
    vertices=[(0, 0, 2), (0, 120, 2)], line_width=7, strip=True)
clock_min.set_shader(graphics.MATSH)
clock_min.set_material((0, 0, 0))

clock_hour = pi3d.Lines(
    vertices=[(0, 0, 2), (0, 70, 2)], line_width=10, strip=True)
clock_hour.set_shader(graphics.MATSH)
clock_hour.set_material((0, 0, 0))

text = pi3d.PointText(graphics.pointFont, graphics.CAMERA,
                      max_chars=80, point_size=128)

press_block2 = pi3d.TextBlock(-70, -185, 0.1, 0.0, 6, justify=0.0, text_format=unichr(0xE00B),
                              size=0.4, spacing="F", space=0.02, colour=(0.0, 1.0, 0.0, 0.7))
air_block2 = pi3d.TextBlock(30, -190, 0.1, 0.0, 6, justify=0.0, text_format=unichr(0xE002),
                            size=0.4, spacing="F", space=0.02, colour=(1.0, 1.0, 1.0, 0.7))
temp_block2 = pi3d.TextBlock(-50, 190, 0.1, 0.0, 6, justify=0.0, text_format=unichr(0xE021),
                             size=0.49, spacing="F", space=0.02, colour=(1.0, 0.0, 0.0, 0.7))
temp_block = pi3d.TextBlock(-250, 120, 0.1, 0.0, 6, justify=0.5, data_obj=peripherals.eg_object,
                            attr="act_temp", text_format="{:2.1f}°", size=0.79, spacing="F",
                            space=0.02, colour=(1.0, 1.0, 1.0, 1.0))
hum_block2 = pi3d.TextBlock(32, 187, 0.1, 0.0, 3, justify=0.0, text_format=unichr(0xE003),
                            size=0.45, spacing="F", space=0.02, colour=(0.0, 0.0, 1.0, 0.7))
hum_block = pi3d.TextBlock(200, 120, 0.1, 0.0, 3, justify=0.5, data_obj=peripherals.eg_object,
                           attr="humidity", text_format="{:1.0f}%", size=0.79, spacing="F",
                           space=0.02, colour=(1.0, 1.0, 1.0, 1.0))
air_block = pi3d.TextBlock(200, -120, 0.1, 0.0, 3, justify=0.5, data_obj=peripherals.eg_object,
                           attr="a4", text_format="{:3d}", size=0.79, spacing="F", space=0.02,
                           colour=(1.0, 1.0, 1.0, 1.0))
press_block = pi3d.TextBlock(-250, -120, 0.1, 0.0, 7, justify=0.5, data_obj=peripherals.eg_object,
                             attr="pressure", text_format="{:2.0f}hPa", size=0.50, spacing="F",
                             space=0.02, colour=(1.0, 1.0, 1.0, 1.0))

text.add_text_block(press_block2)
text.add_text_block(air_block2)
text.add_text_block(hum_block2)
text.add_text_block(temp_block2)
text.add_text_block(hum_block)
text.add_text_block(temp_block)
text.add_text_block(air_block)
text.add_text_block(press_block)


def inloop(textchange=False, activity=False, offset=0):
    if textchange:
        text.regen()
        # text2.regen()
    seconds = time.localtime(time.time()).tm_sec
    minutes = time.localtime(time.time()).tm_min
    hours = time.localtime(time.time()).tm_hour
    clock_min.rotateToZ(360-(minutes*6-1))
    clock_hour.rotateToZ(360-hours*30-minutes*0.5)
    ball.draw()
    seperator.draw()
    background.draw()
    # cloud.draw()
    # hum.draw()
    # temp.draw()
    # press.draw()
    text.draw()
    clock_min.draw()
    clock_hour.draw()
    clock_sec.rotateToZ(360-seconds*6)
    clock_sec.draw()
    dot.draw()
    if offset != 0:
        #graphics.slider_change(text2.text, offset)
        offset = graphics.slider_change(text.text, offset)
        if offset == 0:
            text.regen()
            # text2.regen()
    line.draw()

    return activity, offset
