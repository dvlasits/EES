import RPi.GPIO as GPIO
import atexit
GPIO.setmode(GPIO.BCM)
from time import sleep
import pigpio
from ESCD2in import *
import ESCD2in
import pixy
from ctypes import *
from pixy import *
import VL53L1X
class Blocks (Structure):
  _fields_ = [ ("m_signature", c_uint),
    ("m_x", c_uint),
    ("m_y", c_uint),
    ("m_width", c_uint),
    ("m_height", c_uint),
    ("m_angle", c_uint),
    ("m_index", c_uint),
    ("m_age", c_uint) ]
class Robot:
    def __init__(self):
        for i in range(13,20):
            GPIO.setup(i,GPIO.OUT,initial = 1)
        GPIO.setup(8,GPIO.OUT,initial = 1)
        GPIO.setup(26, GPIO.OUT, initial = 1)
        GPIO.setup(11, GPIO.OUT, initial = 1)
        GPIO.setup(27, GPIO.OUT, initial= 1)
        pixy.init ()
        pixy.change_prog ("color_connected_components")
        self.tof = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=0x29)
        self.tof.open() # Initialise the i2c bus and configure the sensor
        self.tof.start_ranging(1)
        #ESCD2in.calibrate()

    def Back(self):
        self.Stop()
        GPIO.output(26, GPIO.HIGH)
        GPIO.output(27, GPIO.HIGH)
        GPIO.output(8, GPIO.HIGH)
        GPIO.output(11, GPIO.HIGH)
        GPIO.output(16, GPIO.LOW)
        GPIO.output(13, GPIO.LOW)

    def Forward(self):
        self.Stop()
        GPIO.output(26, GPIO.LOW)
        GPIO.output(27,GPIO.LOW)
        GPIO.output(8, GPIO.LOW)
        GPIO.output(11, GPIO.LOW)
        GPIO.output(16, GPIO.LOW)
        GPIO.output(13,GPIO.LOW)


    def getDis(self):
        return self.tof.get_distance()
    def TurnRight(self):
        self.Stop()
        GPIO.output(8, GPIO.HIGH)
        GPIO.output(11,GPIO.HIGH)
        GPIO.output(26, GPIO.LOW)
        GPIO.output(27, GPIO.LOW)
        GPIO.output(16, GPIO.LOW)
        GPIO.output(13, GPIO.LOW)

    def TurnLeft(self):
        self.Stop()
        GPIO.output(8, GPIO.LOW)#LOW to HIGH 14 TO 17
        GPIO.output(11,GPIO.LOW)# LOW to HIGH 15 TO 18
        GPIO.output(26, GPIO.HIGH)
        GPIO.output(27, GPIO.HIGH)
        GPIO.output(16, GPIO.LOW)
        GPIO.output(13, GPIO.LOW)

    def Stop(self):
        for i in range(13,20):
            GPIO.output(i,GPIO.HIGH)
        GPIO.output(8, GPIO.HIGH)
        GPIO.output(11, GPIO.HIGH)
        GPIO.output(26, GPIO.HIGH)
        GPIO.output(27, GPIO.HIGH)
    def FlyWheelsOn(self):
        ESCD2in.manual_drive("1500")
    def FlyWheelsOff(self):
        ESCD2in.manual_drive("0")

    def Shutdown(self):
        GPIO.cleanup()
        print("Process Safely Stopped")
        ESCD2in.stopstop()
        self.tof.stop_ranging()

    def getBlocks(self):
        blocks = BlockArray(100)
        count = pixy.ccc_get_blocks (100, blocks)
        if count > 0:
            for index in range (0, count):
                centerx = blocks[index].m_x + blocks[index].m_width/2
                centery = blocks[index].m_y - blocks[index].m_height/2
            return 1,centerx, centery, blocks[index].m_width, blocks[index].m_height
        return None,None,None,None,None


robot = Robot()
atexit.register(robot.Shutdown)
