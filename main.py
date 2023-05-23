from microbit import *

buf = []

display.off()

# Pin definition
RST_PIN  = pin0
DC_PIN   = pin2
CS_PIN   = pin3
BUSY_PIN = pin1
PWR_PIN  = pin4
#MISO_PIN = pin15
#SCLK_PIN = pin13

# Display resolution
EPD_WIDTH       = 168
EPD_HEIGHT      = 400

class EPD:
    def __init__(self):
        spi.init()
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
            sleep(5)
        print("e-Paper busy L release")

    def TurnOnDisplay(self):
        self.send_command(0x12) # DISPLAY_REFRESH
        self.send_data(0x01)
        self.ReadBusyH()

        self.send_command(0x02) # POWER_OFF
        self.send_data(0X00)
        self.ReadBusyH()
        
    def init(self):
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
    
    def display(self, l):
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
                self.send_data(l[i + j * Width])

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
        
print("epd3in0g Demo")

epd = EPD()   
print("init and Clear")
epd.init()
epd.Clear()

# Drawing on the image
epd.init()
print("1.Drawing on the image...")
epd.display(buf)
sleep(3000)

print("Goto Sleep...")

epd.sleep()
