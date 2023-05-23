from microbit import *
import sys
import os

# Pin definition
RST_PIN  = pin0
DC_PIN   = 25
CS_PIN   = 8
BUSY_PIN = pin1
PWR_PIN  = 18
#MISO_PIN = pin15
#SCLK_PIN = pin13

class Microbit:
    def module_init(self):
        self.GPIO.setmode(self.GPIO.BCM)
        self.GPIO.setwarnings(False)
        self.GPIO.setup(self.RST_PIN, self.GPIO.OUT)
        self.GPIO.setup(self.DC_PIN, self.GPIO.OUT)
        self.GPIO.setup(self.CS_PIN, self.GPIO.OUT)
        self.GPIO.setup(self.PWR_PIN, self.GPIO.OUT)
        self.GPIO.setup(self.BUSY_PIN, self.GPIO.IN)
        
        self.GPIO.output(self.PWR_PIN, 1)

        # SPI device, bus = 0, device = 0
        self.SPI.open(0, 0)
        self.SPI.max_speed_hz = 4000000
        self.SPI.mode = 0b00
        return 0

    def module_exit(self):
        print("spi end")
        self.SPI.close()

        print("close 5V, Module enters 0 power consumption ...")
        #self.GPIO.output(self.RST_PIN, 0)
        #self.GPIO.output(self.DC_PIN, 0)
        #self.GPIO.output(self.PWR_PIN, 0)

        #self.GPIO.cleanup([self.RST_PIN, self.DC_PIN, self.CS_PIN, self.BUSY_PIN, self.PWR_PIN])

implementation = Microbit()

for func in [x for x in dir(implementation) if not x.startswith('_')]:
    setattr(sys.modules[__name__], func, getattr(implementation, func))

import PIL
from PIL import Image

# Display resolution
EPD_WIDTH       = 168
EPD_HEIGHT      = 400

class EPD:
    def __init__(self):
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
        self.BLACK  = 0x000000   #   00  BGR
        self.WHITE  = 0xffffff   #   01
        self.YELLOW = 0x00ffff   #   10
        self.RED    = 0x0000ff   #   11
        
    # Hardware reset
    def reset(self):
        RST_PIN.write_digital(1)
        sleep(200)
        RST_PIN.write_digital(0)         # module reset
        sleep(2)
        RST_PIN.write_digital(1)
        sleep(200)

    def send_command(self, cmd):
        DC_PIN.write_digital(0)
        CS_PIN.write_digital(0)
        spi.write(bytes([cmd]))
        CS_PIN.write_digital(1)

    def send_data(self, d):
        DC_PIN.write_digital(1)
        CS_PIN.write_digital(0)
        spi.write(bytes([d]))
        CS_PIN.write_digital(1)
        
    def ReadBusyH(self):
        print("e-Paper busy H")
        while(BUSY_PIN.read_digital() == 0):      # 0: idle, 1: busy
            sleep(5)
        print("e-Paper busy H release")

    def ReadBusyL(self):
        print("e-Paper busy L")
        while(BUSY_PIN.read_digital() == 1):      # 0: busy, 1: idle
            epdconfig.delay_ms(5)
        print("e-Paper busy L release")

    def TurnOnDisplay(self):
        self.send_command(0x12) # DISPLAY_REFRESH
        self.send_data(0x01)
        self.ReadBusyH()

        self.send_command(0x02) # POWER_OFF
        self.send_data(0X00)
        self.ReadBusyH()
        
    def init(self):
        if (epdconfig.module_init() != 0):
            return -1
        # EPD hardware init start

        self.reset()

        self.send_command(0x66)
        self.send_data(0x49)
        self.send_data(0x55)
        self.send_data(0x13)
        self.send_data(0x5D)
        self.send_data(0x05)
        self.send_data(0x10)

        self.send_command(0xB0)
        self.send_data(0x00) # 1 boost

        self.send_command(0x01)
        self.send_data(0x0F)
        self.send_data(0x00)

        self.send_command(0x00)
        self.send_data(0x4F)
        self.send_data(0x6B)

        self.send_command(0x06)
        self.send_data(0xD7)
        self.send_data(0xDE)
        self.send_data(0x12)

        self.send_command(0x61)
        self.send_data(0x00)
        self.send_data(0xA8)
        self.send_data(0x01)
        self.send_data(0x90)

        self.send_command(0x50)
        self.send_data(0x37)

        self.send_command(0x60)
        self.send_data(0x0C)
        self.send_data(0x05)

        self.send_command(0xE3)
        self.send_data(0xFF)

        self.send_command(0x84)
        self.send_data(0x00)
        return 0

    def getbuffer(self, image):
        # Create a pallette with the 4 colors supported by the panel
        pal_image = Image.new("P", (1,1))
        pal_image.putpalette( (0,0,0,  255,255,255,  255,255,0,   255,0,0) + (0,0,0)*252)

        # Check if we need to rotate the image
        imwidth, imheight = image.size
        if(imwidth == self.width and imheight == self.height):
            image_temp = image
        elif(imwidth == self.height and imheight == self.width):
            image_temp = image.rotate(90, expand=True)
        else:
            logger.warning("Invalid image dimensions: %d x %d, expected %d x %d" % (imwidth, imheight, self.width, self.height))

        # Convert the soruce image to the 4 colors, dithering if needed
        image_4color = image_temp.convert("RGB").quantize(palette=pal_image)
        buf_4color = bytearray(image_4color.tobytes('raw'))

        # into a single byte to transfer to the panel
        buf = [0x00] * int(self.width * self.height / 4)
        idx = 0
        for i in range(0, len(buf_4color), 4):
            buf[idx] = (buf_4color[i] << 6) + (buf_4color[i+1] << 4) + (buf_4color[i+2] << 2) + buf_4color[i+3]
            idx += 1

        return buf

    def display(self, image):
        if self.width % 4 == 0 :
            Width = self.width // 4
        else :
            Width = self.width // 4 + 1
        Height = self.height

        self.send_command(0x04)
        self.ReadBusyH()

        self.send_command(0x10)
        for j in range(0, Height):
            for i in range(0, Width):
                self.send_data(image[i + j * Width])

        self.TurnOnDisplay()
        
    def Clear(self, color=0x55):
        if self.width % 4 == 0 :
            Width = self.width // 4
        else :
            Width = self.width // 4 + 1
        Height = self.height

        self.send_command(0x04)
        self.ReadBusyH()

        self.send_command(0x10)
        for j in range(0, Height):
            for i in range(0, Width):
                self.send_data(color)

        self.TurnOnDisplay()

    def sleep(self):
        self.send_command(0x02) # POWER_OFF
        self.send_data(0x00)

        self.send_command(0x07) # DEEP_SLEEP
        self.send_data(0XA5)
        
        sleep(2000)
        epdconfig.module_exit()

from PIL import Image,ImageDraw,ImageFont
import traceback

print("epd3in0g Demo")

epd = epd3in0g.EPD()   
print("init and Clear")
epd.init()
epd.Clear()
font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
font40 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 40)

# Drawing on the image
epd.init()
print("1.Drawing on the image...")
Himage = Image.new('RGB', (epd.width, epd.height), 0xffffff)  
draw = ImageDraw.Draw(Himage)
draw.text((5, 0), 'hello world', font = font18, fill = epd.RED)
draw.text((5, 20), '3inch e-Paper', font = font24, fill = epd.YELLOW)
draw.text((5, 45), u'微雪电子', font = font40, fill = epd.BLACK)
draw.text((5, 85), u'微雪电子', font = font40, fill = epd.YELLOW)
draw.text((5, 125), u'微雪电子', font = font40, fill = epd.RED)
draw.line((5, 170, 80, 245), fill = epd.RED)
draw.line((80, 170, 5, 245), fill = epd.YELLOW)
draw.rectangle((5, 170, 80, 245), outline = epd.BLACK)
draw.rectangle((90, 170, 165, 245), fill = epd.YELLOW)
draw.arc((5, 250, 80, 325), 0, 360, fill = epd.BLACK)
draw.chord((90, 250, 165, 325), 0, 360, fill = epd.RED)
epd.display(epd.getbuffer(Himage))
sleep(3000)

# Switch width and height for landscape display
epd.init()
print("2.Drawing on the image...")
Himage = Image.new('RGB', (epd.height, epd.width), epd.WHITE)      
draw = ImageDraw.Draw(Himage)
draw.text((5, 0), 'hello world', font = font18, fill = epd.RED)
draw.text((5, 20), '3inch e-Paper', font = font24, fill = epd.YELLOW)
draw.text((5, 45), u'微雪电子', font = font40, fill = epd.BLACK)
draw.text((5, 85), u'微雪电子', font = font40, fill = epd.YELLOW)
draw.text((5, 125), u'微雪电子', font = font40, fill = epd.RED)
draw.line((205, 5, 295, 65), fill = epd.RED)
draw.line((295, 5, 205, 65), fill = epd.YELLOW)
draw.rectangle((205, 5, 295, 65), outline = epd.BLACK)
draw.rectangle((305, 5, 395, 65), fill = epd.RED)
draw.arc((205, 75, 295, 165), 0, 360, fill = epd.BLACK)
draw.chord((305, 75, 395, 165), 0, 360, fill = epd.YELLOW)
epd.display(epd.getbuffer(Himage))
sleep(3000)

# read bmp file 
epd.init()
print("3.read bmp file")
Himage = Image.open(os.path.join(picdir, '3inch-1.bmp'))
epd.display(epd.getbuffer(Himage))
sleep(3000)

epd.init()
print("4.read bmp file")
Himage = Image.open(os.path.join(picdir, '3inch-2.bmp'))
epd.display(epd.getbuffer(Himage))
sleep(3000)

epd.init()
print("5.read bmp file")
Himage = Image.open(os.path.join(picdir, '3inch-3.bmp'))
epd.display(epd.getbuffer(Himage))
sleep(3000)

epd.init()
print("Clear...")
epd.Clear()

print("Goto Sleep...")

epd.sleep()
