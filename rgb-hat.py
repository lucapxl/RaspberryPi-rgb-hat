#!/usr/bin/env python
### BEGIN INIT INFO
# Provides:          rgb-hat
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start RGB Cooling HAT daemon at boot time
# Description:       Enable service provided by daemon.
### END INIT INFO

import Adafruit_GPIO.I2C as I2C
import time
import os
import smbus
import Adafruit_SSD1306
import subprocess
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

bus = smbus.SMBus(1)
hat_addr = 0x0d
fan_reg = 0x08
count = 0
Max_LED = 3
level_temp = 0

# Raspberry Pi pin configuration:
RST = None     # on the PiOLED this pin isnt used

# 128x32 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
#bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Load default font.
font = ImageFont.load_default()

# Alternatively load a TTF font.  Make sure the .ttf font file is in the same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
# font = ImageFont.truetype('Minecraftia.ttf', 8)

def setFanSpeed(speed):
    bus.write_byte_data(hat_addr, fan_reg, speed&0xff)

def setRGB(num, r, g, b):
    if num >= Max_LED:
        bus.write_byte_data(0x0d, 0x00, 0xff)
        bus.write_byte_data(0x0d, 0x01, r&0xff)
        bus.write_byte_data(0x0d, 0x02, g&0xff)
        bus.write_byte_data(0x0d, 0x03, b&0xff)
    elif num >= 0:
        bus.write_byte_data(0x0d, 0x00, num&0xff)
        bus.write_byte_data(0x0d, 0x01, r&0xff)
        bus.write_byte_data(0x0d, 0x02, g&0xff)
        bus.write_byte_data(0x0d, 0x03, b&0xff)

def getCPULoadRate():
    f1 = os.popen("cat /proc/stat", 'r')
    stat1 = f1.readline()
    count = 10
    data_1 = []
    for i  in range (count):
        data_1.append(int(stat1.split(' ')[i+2]))
    total_1 = data_1[0]+data_1[1]+data_1[2]+data_1[3]+data_1[4]+data_1[5]+data_1[6]+data_1[7]+data_1[8]+data_1[9]
    idle_1 = data_1[3]

    time.sleep(1)

    f2 = os.popen("cat /proc/stat", 'r')
    stat2 = f2.readline()
    data_2 = []
    for i  in range (count):
        data_2.append(int(stat2.split(' ')[i+2]))
    total_2 = data_2[0]+data_2[1]+data_2[2]+data_2[3]+data_2[4]+data_2[5]+data_2[6]+data_2[7]+data_2[8]+data_2[9]
    idle_2 = data_2[3]

    total = int(total_2-total_1)
    idle = int(idle_2-idle_1)
    usage = int(total-idle)
    #print("idle:"+str(idle)+"  total:"+str(total))
    usageRate =int(float(usage * 100/ total))
    #print("usageRate:%d"%usageRate)
    return "CPU:"+str(usageRate)+"%"


def setOLEDshow():
    # Draw a black filled box to clear the image.
    draw.rectangle((0,0,width,height), outline=0, fill=0)

    #cmd = "top -bn1 | grep load | awk '{printf \"CPU:%.0f%%\", $(NF-2)*100}'"
    #CPU = subprocess.check_output(cmd, shell = True)
    CPU = getCPULoadRate()

    cmd = os.popen('vcgencmd measure_temp').readline()
    CPU_TEMP = cmd.replace("temp=","Temp:").replace("'C\n","C")
    global g_temp
    g_temp = float(cmd.replace("temp=","").replace("'C\n",""))

    cmd = "free -m | awk 'NR==2{printf \"RAM:%s/%s MB \", $2-$3,$2}'"
    MemUsage = subprocess.check_output(cmd, shell = True).decode("utf-8") 

    cmd = "df -h | awk '$NF==\"/\"{printf \"Disk:%d/%dMB\", ($2-$3)*1024,$2*1024}'"
    Disk = subprocess.check_output(cmd, shell = True).decode("utf-8") 

    cmd = "hostname -I | cut -d\' \' -f1"
    IP = subprocess.check_output(cmd, shell = True).decode("utf-8") 

    # Write two lines of text.

    draw.text((x, top), str(CPU), font=font, fill=255)
    draw.text((x+56, top), str(CPU_TEMP), font=font, fill=255)
    draw.text((x, top+8), str(MemUsage),  font=font, fill=255)
    draw.text((x, top+16), str(Disk),  font=font, fill=255)
    draw.text((x, top+24), "IP:" + str(IP),  font=font, fill=255)

    # Display image.
    disp.image(image)
    disp.display()
    time.sleep(.1)

setFanSpeed(0x02)
setRGB(Max_LED, 0x00, 0x00, 0xff)

while True:
    setOLEDshow()	
    
    # SET RGB Light and FAN speed depending on temperature
    if abs(g_temp - level_temp) >= 1:
        if g_temp <= 45:
            level_temp = 45
            setRGB(Max_LED, 0x00, 0x00, 0xff)
            setFanSpeed(0x04)
        elif g_temp <= 47:
            level_temp = 47
            setRGB(Max_LED, 0x1e, 0x90, 0xff)
            setFanSpeed(0x04)
        elif g_temp <= 49:
            level_temp = 49
            setRGB(Max_LED, 0x00, 0xbf, 0xff)
            setFanSpeed(0x06)
        elif g_temp <= 51:
            level_temp = 51
            setRGB(Max_LED, 0x5f, 0x9e, 0xa0)
            setFanSpeed(0x08)
        elif g_temp <= 53:
            level_temp = 53
            setRGB(Max_LED, 0xff, 0xff, 0x00)
            setFanSpeed(0x09)
        elif g_temp <= 55:
            level_temp = 55
            setRGB(Max_LED, 0xff, 0xd7, 0x00)
            setFanSpeed(0x01)
        elif g_temp <= 57:
            level_temp = 57
            setRGB(Max_LED, 0xff, 0xa5, 0x00)
            setFanSpeed(0x01)
        elif g_temp <= 59:
            level_temp = 59
            setRGB(Max_LED, 0xff, 0x8c, 0x00)
            setFanSpeed(0x01)
        elif g_temp <= 61:
            level_temp = 61
            setRGB(Max_LED, 0xff, 0x45, 0x00)
            setFanSpeed(0x01)
        elif g_temp >= 63:
            level_temp = 63
            setRGB(Max_LED, 0xff, 0x00, 0x00)
            setFanSpeed(0x01)

    time.sleep(.5)