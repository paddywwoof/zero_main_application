#!/usr/bin/python
 
from __future__ import absolute_import, division, print_function, unicode_literals
import random,time, os , sys, smbus
import pi3d
import RPi.GPIO as gpio
import subprocess
from random import randint
PIR = 18
BACKLIGHT = 19 #single wire backlight control needs almost realtime, keep that in mind, run python as root
TOUCHINT = 26
ADDR = 0x5c
tm = 0
nexttm = 0
lastmovex = 0
movex = 0
touch_pressed = False
lastx = 0
lasty = 0
yc = 0
xc = 0
actpos = 0
gpio.setmode(gpio.BCM)
gpio.setwarnings(False)
gpio.setup(TOUCHINT, gpio.IN)
bus = smbus.SMBus(2)



def get_touch():
   global xc,yc    
   try:
         data = bus.read_i2c_block_data(ADDR, 0x40, 8)
         x1 = data[0] | (data[4] << 8)
         y1 = data[1] | (data[5] << 8)

         if ((-1 < x1  < 801) & (-1 < y1  < 481)):
          if ((-20 < (xc-x1) < 20) & (-20 < (yc-y1) < 20)):  #catch bounches 
           xc = x1
           yc = y1
           #print(x1,y1)
           return x1,y1;
          else:
           xc = x1
           yc = y1
           
           #print('not identical')
           return get_touch()
         else:
          return get_touch()
  



   except:
       time.sleep(0.03)  #wait on  I2C error
       #print('i2cerror')
       return get_touch() 
       pass    







def touch_debounce(channel):  
 global lastx, lasty, touch_pressed
 x,y = get_touch()
 if (channel == TOUCHINT):
  touch_pressed = True  
  lastx = x
  lasty = y
 else:
  return x,y;

gpio.add_event_detect(TOUCHINT, gpio.RISING, callback=touch_debounce, bouncetime=100)                                  #touch interrupt



bus.write_byte_data(0x5c,0x6e,0b00001110)                                              # interrupt configuration i2c


PIC_DIR = '/home/pi/backgrounds'
TMDELAY = 100 




def get_files():
  global SHUFFLE, PIC_DIR
  file_list = []
  extensions = ['.png','.jpg','.jpeg'] 
  for root, dirnames, filenames in os.walk(PIC_DIR):
      for filename in filenames:
          ext = os.path.splitext(filename)[1].lower()
          if ext in extensions and not filename.startswith('.'):
              file_list.append(os.path.join(root, filename)) 
  random.shuffle(file_list) 

  return file_list, len(file_list)


 
iFiles, nFi = get_files()
pic_num = nFi - 1


class EgClass(object):
  uhrzeit = "00:00"
  load = 0.00
  airquality = 0
  act_hum = 20.0
  freespace = 00000
  gpu_temp = 00.0
  set_temp = 23.0
  diffx = 00000
  act_temp = 23.0
  pressure = 0.00
    
eg_object = EgClass()



mytext = '1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZüöäÜÖÄ,.%:° -'
mytext = mytext + chr(0xE000) #arrow
mytext = mytext + chr(0xE001) #circle
mytext = mytext + chr(0xE002) #cloud
mytext = mytext + chr(0xE003) #raindrop
mytext = mytext + chr(0xE004) #fire
mytext = mytext + chr(0xE005) #house
mytext = mytext + chr(0xE006) #filledcircle
#mytext = mytext + chr(0xE007) #raining
#mytext = mytext + chr(0xE008) #timer
mytext = mytext + chr(0xE009) #clock
#mytext = mytext + chr(0xE00A) #eye
mytext = mytext + chr(0xE00B) #gauge
mytext = mytext + chr(0xE00C) #sun
#mytext = mytext + chr(0xE00D) #cloudsun
#mytext = mytext + chr(0xE00E) #lightoff
mytext = mytext + chr(0xE00F) #lighton
mytext = mytext + chr(0xE010) #settings
#mytext = mytext + chr(0xE011) #heart
#mytext = mytext + chr(0xE012) #book
mytext = mytext + chr(0xE013) #child
#mytext = mytext + chr(0xE014) #alarmclock
#mytext = mytext + chr(0xE015) #presence
#mytext = mytext + chr(0xE016) #wifi
#mytext = mytext + chr(0xE017) #mic
#mytext = mytext + chr(0xE018) #bluetooth
#mytext = mytext + chr(0xE019) #web
#mytext = mytext + chr(0xE01A) #speechbubble
#mytext = mytext + chr(0xE01B) #ampere
mytext = mytext + chr(0xE01C) #motion
#mytext = mytext + chr(0xE01D) #electric
#mytext = mytext + chr(0xE01E) #close
#mytext = mytext + chr(0xE01F) #leaf
mytext = mytext + chr(0xE020) #socket
mytext = mytext + chr(0xE021) #temp
#mytext = mytext + chr(0xE022) #tesla
#mytext = mytext + chr(0xE023) #raspi
#mytext = mytext + chr(0xE024) #privacy
mytext = mytext + chr(0xE025) #circle2
#mytext = mytext + chr(0xE026) #bell
#mytext = mytext + chr(0xE027) #nobell
#mytext = mytext + chr(0xE028) #moon
#mytext = mytext + chr(0xE029) #freeze
#mytext = mytext + chr(0xE02A) #whatsapp
#mytext = mytext + chr(0xE02B) #touch
mytext = mytext + chr(0xE02C) #settings2
#mytext = mytext + chr(0xE02D) #storm
mytext = mytext + chr(0xE035) #shutter
#mytext = mytext + chr(0xE034) #doublearrow
#mytext = mytext + chr(0xE033) #usb
#mytext = mytext + chr(0xE032) #magnet
mytext = mytext + chr(0xE031) #phone
#mytext = mytext + chr(0xE030) #compass
#mytext = mytext + chr(0xE02E) #trash
#mytext = mytext + chr(0xE02F) #cam




DISPLAY = pi3d.Display.create(layer=0,w=800, h=480,background=(0.0, 0.0, 0.0, 1.0),frames_per_second=60, tk=False)     
shader = pi3d.Shader("uv_flat")  
CAMERA = pi3d.Camera(is_3d=False) 
CAMERAFIXED = pi3d.Camera(is_3d=False)

def tex_load(fname):

  slide = pi3d.ImageSprite(fname,shader=shader,camera=CAMERAFIXED,w=800,h=480,z=2)   
  slide.set_alpha(0)

  return slide

sfg = tex_load(iFiles[pic_num])



pointFont = pi3d.Font("opensans.ttf", shadow=(0, 0, 0, 255), shadow_radius=4,grid_size=11, codepoints=mytext)



text = pi3d.PointText(pointFont, CAMERA, max_chars=220, point_size=128)  #for slide 1, from 0 - 800px
text2 = pi3d.PointText(pointFont, CAMERA, max_chars=220, point_size=128) #for slide 2, from 800 - 1600px
fixed = pi3d.PointText(pointFont, CAMERAFIXED, max_chars=20, point_size=128) #always fixed


circle_block = pi3d.TextBlock(-60,-220,0.1,0.0,6,text_format = chr(0xE006) + chr(0xE006) + chr(0xE006) + chr(0xE006)+chr(0xE006)+chr(0xE006), size= 0.25, spacing="F",space=0.3,colour=(1.0,1.0,1.0,0.2))
circle_active = pi3d.TextBlock(-60,-220,0.1,0.0,1,text_format = chr(0xE006), size= 0.3, spacing="F",space=0.3,colour=(1.0,1.0,1.0,1.0))
fixed.add_text_block(circle_active)
fixed.add_text_block(circle_block)




temp_block = pi3d.TextBlock(-350, 130, 0.1, 0.0, 15, data_obj=eg_object,attr="act_temp",text_format= chr(0xE021) +"{:2.1f}°C", size=0.99, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 1.0))
text.add_text_block(temp_block)

uhrzeit_block = pi3d.TextBlock(400, 130, 0.1, 0.0, 15, data_obj=eg_object,attr="uhrzeit", text_format= chr(0xE009) +"{:s}", size=0.99, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 1.0))
text2.add_text_block(uhrzeit_block) 




while DISPLAY.loop_running():



  if gpio.input(TOUCHINT):                              # check if touch is pressed, to detect sliding
       x,y = get_touch();
       if ((x != 0) and lastx):
        movex = (lastx - x)                              #calculate slider movement
        CAMERA.offset((lastmovex-movex, 0, 0))
        lastmovex = movex
        time.sleep(0.01)
 
  else:

    if lastmovex:
     actpos += lastmovex  # save for identifying which slide..    
     lastmovex = 0
     if (actpos > 0):
      CAMERA.offset(((actpos),0,0))
      actpos = 0
    
    diffpos = actpos % 800   

   
    if  0 < (diffpos) < 400:

     if diffpos < 5:
      CAMERA.offset((diffpos,0,0))
      actpos -= diffpos
     else:
      CAMERA.offset((5,0,0))
      actpos -= 5
      
    if  399 < (diffpos) < 800:

     if diffpos > 795:
      CAMERA.offset((-(800-diffpos),0,0))
      actpos += (800-diffpos)
     else:
      CAMERA.offset((-5,0,0))
      actpos += 5
     

    
    

    if ((actpos % 800) == 0): #just for now, we need to implement a variable to do this only one time after slide
     circle_active.set_position(x=(int)(-60-(actpos/38)))
     fixed.regen()
 
     
       

      #text2.regen()
      #text.regen()               
     

    if time.time() > nexttm:                                     # change background
      nexttm = time.time() + TMDELAY
      a = 0.0 
      sbg = sfg
      sbg.positionZ(3)
      pic_num = (pic_num + 1) % nFi
      sfg = tex_load(iFiles[pic_num]) 

    if a < 1.0:                                              # fade to new background
        activity = True
        a += 0.01 
        sbg.draw() 
        sfg.set_alpha(a)
  sfg.draw()
  text.draw()
  text2.draw()
  fixed.draw()


DISPLAY.destroy()
