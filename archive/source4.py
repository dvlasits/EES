from time import sleep, time
import random
import atexit
import math
import cv2
import io
import os

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

import ESCD3in
import VL53L1X
import Diablo3 as Diablo

import pixy
from ctypes import *
from pixy import *


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
        """Initialise the robot, by setting it up, and performing any other
        necessary procedures"""
        self.setup()

    def setup(self):
        """Create an ESC, a motors & a TOF object"""
        GPIO.setup(35,GPIO.OUT,initial=0)
        self.ESCs = ESCD3in.PairESCController()
        self.defaultFlywheelDuty = "1130"

        self.motors = Diablo.Diablo()
        if False:
            print(Diablo.ScanForDiablo)
        self.motors.i2cAddress = 0x25
        self.motors.Init()
        self.motors.ResetEpo()

        self.tof = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=0x29)
        self.tof.open()
        #Start ranging, 1 = Short Range, 2 = Medium Range, 3 = Long Range
        self.tof.start_ranging(1)


    def shutdown(self):
        """Fully shutdown the robot, i.e. powering of the motors, the ESCs, the TOF"""
        self.stop()
        self.ESCs.stopstop()
        self.tof.stop_ranging()
        self.motors.SetEpoIgnore(True)
        print("Process Safely Stopped")

    def remoteControl(self):
        """Remote control the robot from the command line"""
        from pynput.keyboard import Key, Listener
        self.flag = False

        def on_press(key):
            if key == Key.down:
                self.backward()
            if key == Key.up:
                self.forward()
            if key == Key.right:
                self.turnRight()
            if key == Key.left:
                self.turnLeft()
            if key == Key.space:
                if self.flag == False:
                    self.flyWheelsOn()
                    self.flag = True
                else:
                    self.flyWheelsOff()
                    self.flag = False
            if key == Key.tab:
                print(self.getDistance())

        def on_release(key):
            self.stop()
            if key == Key.esc:
                self.ESCs.stop()
                return False

        print("Waiting for remote control commands")
        with Listener(on_press=on_press,on_release=on_release) as listener:
                listener.join()

    def setDefaultFlywheelDuty(self, duty):
        """Set the default duty of the flywheels"""
        self.defaultFlywheelDuty = str(duty)

    def flyWheelsOn(self, duty=None):
        """Set the duty of the ESCs to a given value
        Optional parameter 1: duty [string]; set the duty of both ESCs to this value"""
        if duty is None:
            duty = self.defaultFlywheelDuty
        self.ESCs.manual_drive(str(duty))

    def flyWheelsOff(self):
        """Set the duty of the ESCs to 0 - i.e. turn them off"""
        self.ESCs.manual_drive("0")

    def forward(self):
        """Drive the robot forwards"""
        self.motors.SetMotors(-1)

    def backward(self):
        """Drive the robot backwards"""
        self.motors.SetMotors(1)

    def turnRight(self):
        """Turn the robot right"""
        self.motors.SetMotor1(-1)
        self.motors.SetMotor2(1)

    def turnLeft(self):
        """Turn the robot left"""
        self.motors.SetMotor1(1)
        self.motors.SetMotor2(-1)

    def stop(self):
        """Stop the robot"""
        self.motors.MotorsOff()

    def getDistance(self):
        """Get the distance from the TOF sensor to the nearest obstacle
        Return 1: distance [int]; the distance to the nearest obstacle"""
        return self.tof.get_distance()

    def getOptoSwitch(self):
        """Get the value of the opto switch in the chute, unimplemented, so always True
        Return 1: value [boolean]; whether the opto switch is tripeed
        """
        return True

    def getBlocks(self):
        """Get various information about the most prominent circle in the image
        Return 1: centrex [int]; the x centre of the nearest circle
        Return 2: centrey [int]; the y centre of the nearest circle
        Return 3: blockWidth [int];
        Return 4: blockHeight [int];
        """
        blocks = BlockArray(100)
        count = pixy.ccc_get_blocks(100, blocks)
        if count > 0:
            for index in range (0, count):
                centerx = blocks[index].m_x + blocks[index].m_width/2
                centery = blocks[index].m_y - blocks[index].m_height/2
            return 1,centerx, centery, blocks[index].m_width, blocks[index].m_height
        return None,None,None,None,None

    def autonomousTest(self):
        """Drive continuously in a circle, and collect any balls that are seen
        whilst turning
        """
        while True:
            u,x,y,width,height = self.getBlocks()
            if x is not None:
                if x < 260 and x > 150: #If the ball is central
                    #print(y)
                    self.stop()
                    self.forward()
                    sleep(0.5)
                    self.flyWheelsOn()
                    sleep(2)
                    self.flyWheelsOff()
                    self.stop()
            else:
                self.turnRight()

    def isAboutToCrash(self, threshold=1000):
        """Check if the distance between a robot and a detected obstacle
        is below a threshold
        Return 1: answer [boolean]; is the robot about to crash"""
        return self.getDistance()<threshold

    def avoidWall(self, direction=None, threshold=1000):
        """Turn in a random (or specified) direction to avoid the wall,
        then keep turning for another random period of time
        Optional parameter 1: direction [int]; the direction in which to turn
        """
        self.stop()
        direction = random.choice([0,1]) if direction is None else direction

        while isAboutToCrash(threshold):
            if direction == 0:
                self.turnRight()
            else:
                self.turnLeft()

        latencyPeriod = random.uniform(0.2,1.5)
        sleep(latencyPeriod)

        self.stop()

    def autonomous(self):
        """Autonomously collect balls
        Continuously drive forward, unless:
         - you see a ball, in which case turn to pick it up
         - you are too close to a wall, in case turn randomly to avoid it
        """
        print("Starting autonomous collection")
        directionFlag = 0 #0: drive forwards, 1: turn right
        while True:
            if self.isAboutToCrash():
                self.avoidWall()

            u,x,y,width,height = self.getBlocks()
            if x is not None:
                if x < 260 and x > 150: #If the ball is central, collect it

                    self.stop()

                    #Spin up the flywheels, speed up by doing highest first
                    self.flyWheelsOn("2000")
                    sleep(0.1)
                    self.flyWheelsOn()
                    #if y < 100: sleep(0.5)

                    #Drive forward until the ball is out of view, and has gone up the ramp
                    self.forward()
                    aboutToCrashFlag = False

                    while x is not None:
                        u,x,y,width,height = self.getBlocks()
                        if self.isAboutToCrash():
                            #Defer wall avoidance to the beginning of the loop
                            aboutToCrashFlag = True
                            break
                    if aboutToCrashFlag:
                        self.flyWheelsOff()
                        self.stop()
                        continue

                    #sleep(0.5)

                    switch, startTime = self.getOptoSwitch(), time()
                    while not o: #opto switch
                        switch = self.getOptoSwitch()
                        if self.isAboutToCrash():
                            aboutToCrashFlag = True
                            break
                        elif time() > startTime+5:
                            break
                    if aboutToCrashFlag:
                        self.flyWheelsOff()
                        self.stop()
                        continue

                    self.flyWheelsOff()
                    self.stop()

                elif x < 150: #If the ball is to the right, turn right
                    self.turnRight()
                elif x > 260: #If the ball is to the left, turn left
                    self.turnLeft()
            else:
                if random.uniform(0,10) < 0.5:
                    directionFlag = (directionFlag+1)%2
                if directionFlag:
                    self.forward()
                else:
                    self.turnRight()


def main():
    """Testing CLI for the robot
    """
    robot = Robot()
    atexit.register(robot.shutdown)

    while True:
        os.system('clear')
        data = input("Remote control [r], Calibrate [c] Autonomous [a] or Exit [x]: ").lower()
        if data == "r":
            robot.remoteControl()
        if data == "c":
            robot.ESCs.calibrate()
        elif data == "a":
            robot.autonomousOld()
        elif data == "x":
            exit()
        else:
            pass

if __name__ == "__main__":
    exit(main())
