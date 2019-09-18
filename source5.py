from time import sleep, time
import random
import atexit
import math
import cv2
import io
import os
import Diablo_py3 as Diablo
#import xbox
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

import ESCD3in
import VL53L1X

#import pixy
from ctypes import *
#from pixy import *



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
        GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.DIABLO = Diablo.Diablo()
        self.DIABLO.i2cAddress = 0x25
        self.DIABLO.Init()
        self.DIABLO.ResetEpo()
        self.DIABLO.SetEnabled(True)
        self.ESCs = ESCD3in.PairESCController()
        self.defaultFlywheelDuty = "1060"
        #pixy.init()
        #pixy.change_prog("color_connected_components")
        self.tof = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=0x29)
        self.tof.open()
        self.tof.start_ranging(3) # Start ranging, 1 = Short Range, 2 = Medium Range, 3 = Long Range

    def shutdown(self):
        """Fully shutdown the robot, i.e. powering of the motors, the ESCs,
        the TOF, and clean up to GPIO pins"""
        self.stop()
        self.ESCs.stopstop()
        self.tof.stop_ranging()
        GPIO.cleanup()
        print("Process Safely Stopped")

    def remoteControl(self):
        """Remote control the robot from the command line"""
        from pynput.keyboard import Key, Listener
        self.flag = False

        def on_press(key):
            if key == Key.down:
                self.backward(0.8)
            if key == Key.up:
                self.forward(1,0) #meant to be 0.8,0.7
            if key == Key.right:
                self.turnRight(0.5)
            if key == Key.left:
                self.turnLeft(0.5)
            if key == Key.space:
                if self.flag == False:
                    self.flyWheelsOn()
                    self.flag = True
                else:
                    self.flyWheelsOff()
                    self.flag = False
            if key == Key.tab:
                print(self.getDistance())
            if key == Key.shift:
                print(self.getButtonPressed())

        def on_release(key):
            self.stop()
            if key == Key.esc:
                self.ESCs.stop()
                return False

        with Listener(on_press=on_press,on_release=on_release) as listener:
                listener.join()



    def setDefaultFlywheelDuty(self, duty):
        """Set the default duty of the flywheels"""
        duty = "2000"
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

    def backward(self,L,R = None):
        """Drive the robot backwards"""
        if R is not None:
            self.forward(-L,-R)
        else:
            self.forward(-L)

    def forward(self,L,R = None):
        """Drive the robot forwards"""
        if R is not None:
            self.DIABLO.SetMotor1(-R)
            self.DIABLO.SetMotor2(-L)
        else:
            if L < 0:
                self.forward(L,L/1.2)
            else:
                self.forward(L,L/1.04)
    
    def turnRight(self,P):
        """Turn the robot right"""
        self.forward(P,-P)

    def turnLeft(self,P):
        self.forward(-P,P)

    def stop(self):
        """Stop the robot"""
        self.DIABLO.MotorsOff()

    def getDistance(self):
        """Get the distance from the TOF sensor to the nearest obstacle
        Return 1: distance [int]; the distance to the nearest obstacle"""
        return self.tof.get_distance()



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
                print(blocks[index].m_width)
                if True:
                    return 1,centerx, centery, blocks[index].m_width, blocks[index].m_height
        return None,None,None,None,None

    def getButtonPressed(self):
        input_state = GPIO.input(24)
        if input_state == False:
            return True
        return False

    def getBall(self,x):
        print("seen a ball")
        if x > 210:
            pass
            '''self.turnRight(0.4)
            sleep(0.8)
            self.stop()'''
        elif x < 180:
            pass
            '''self.turnLeft(0.4)
            sleep(0.8)
            self.stop()'''
        print("ball is centred")
        #print(y)
        self.stop()
        self.flyWheelsOn()
        sleep(1)
        self.forward(0.8,0.7)
        self.drive()
        self.flyWheelsOff()
        self.stop()

    def autonomousTest(self):
        timestarted = time()
        self.forward(random.uniform(0.4,0.8),random.uniform(0.4,0.8))
        timeto = random.randint(2,10)
        count = 0
        startturn = time() - 10
        while self.getButtonPressed() == False:
            u,x,y,width,height = self.getBlocks()
            if x is not None:
                self.getBall(x)
                timestarted = -10000
            dis = self.getDistance()
            if dis < 1100:
                count += 1
            else:
                count = 0
            if count > 20:
                self.flyWheelsOff()
                self.backward(0.8,0.75)
                sleep(0.8)
                self.turnRight(0.7)
                sleep(random.uniform(1.5,2.5))
                self.stop()
                self.flyWheelsOn()
                self.forward(0.8,0.75)
                sleep(random.uniform(3,6))
                self.stop()
                self.flyWheelsOff()
                timestarted = -10000
            if time() - timestarted > timeto:
                timestarted = time()
                option = random.randint(1,3)
                if option == 1:
                    self.forward(0.9,0.85)
                if option == 2:
                    self.forward(0.9,0.6)
                if option == 3:
                    self.forward(0.7,0.9)
                timeto = random.randint(2,10)
            if time()-startturn > 6 and random.randint(1,3) == 2:
                print("Activated base turn")
                self.autonomousBaseTurn(True)
                startturn = time()
                timestarted = -10000



    def forBack(self):
        while self.getButtonPressed() == True:
            pass
        count = 0
        while self.getButtonPressed() == False:
            self.flyWheelsOn()
            self.forward(0.8,0.7)
            self.drivewall()
            if self.getButtonPressed():
                self.stop()
                return
            if count%2 == 0:
                self.forward(1,0)
                sleep(2.8)
            else:
                self.forward(0,1)
                sleep(2)
            self.stop()
            sleep(1)
            count += 1
        self.stop()
        self.flyWheelsOff()

    def drivewall(self):
        count = 0
        while True:
            dis = self.getDistance()
            if dis < 1100:
                count += 1
            else:
                count = 0
            if count > 20:
                self.stop()
                sleep(1)
                return
            if self.getButtonPressed():
                self.stop()
                self.flyWheelsOff()
                return

    def drive(self):
        count = 0
        for i in range(70):
            dis = self.getDistance()
            if dis < 550:
                count += 1
            else:
                count = 0
            if count > 4:

                self.flyWheelsOff()
                self.backward(0.8,0.75)
                sleep(0.8)
                self.turnRight(0.7)
                sleep(random.uniform(1.5,2.5))
                self.flyWheelsOn()
                self.forward(0.8,0.75)
                sleep(random.uniform(3,6))
                self.stop()
                self.flyWheelsOff()

                return
            sleep(0.01)
        self.stop()
        return



    def autonomousBaseTurn(self,limited = False):
        """Drive continuously in a circle, and collect any balls that are seen
        whilst turning
        """
        '''while True:
            if self.getButtonPressed():
                break'''
        self.turnRight(0.6)
        start = time()
        end = random.uniform(3,5)
        while True:
            u,x,y,width,height = self.getBlocks()
            if x is not None:
                if x < 260 and x > 150:
                    print("ball is centred")
                    self.stop()
                    self.flyWheelsOn()
                    sleep(1)
                    self.forward(0.8,0.7)
                    self.drive()
                    self.flyWheelsOff()
                    self.stop()
                    sleep(1)
                    self.turnRight(0.6)
            else:
                self.turnRight(0.6)
            if self.getButtonPressed() == True:
                return
            if limited:
                if time() - start > end:
                    return

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
        directionFlag = 0 #0: drive forwards, 1: turn right
        while True:
            if self.isAboutToCrash():
                self.avoidWall()

            u,x,y,width,height = self.getBlocks()
            if x is not None:
                if x < 260 and x > 150: #If the ball is central, collect it

                    self.stop()

                    #Spin up the flywheels, speed up by doing highest first
                    #self.flyWheelsOn("2000")
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
                        elif time() > startTime+6:
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


    def buttonControll(self):
        joy = xbox.Joystick()
        self.forward(0.5,0.5)
        sleep(0.4)
        self.stop()#
        #self.ESCs.calibrate()
        self.forward(0.5,0.5)
        sleep(0.4)
        self.stop()

        while True:
            while self.getButtonPressed() == True:
                pass
            sleep(0.5)
            ad = 0
            while self.getButtonPressed() == False:

                if joy.connected():
                    self.forward(joy.leftY(),joy.rightY())
                    if joy.A() and ad == 0:
                        ad = 1
                        self.flyWheelsOn()
                        sleep(0.5)
                    if joy.A() and ad == 1:
                        self.flyWheelsOff()
                        ad = 0
                        sleep(0.5)
                else:
                    self.stop()
                    self.flyWheelsOff()
            sleep(0.5)

            print("Button pushed")
            while self.getButtonPressed() == True:
                pass
            sleep(0.5)

            print("button let go")
            start = time()
            activated = 0
            while self.getButtonPressed() == False:
                if time() - start > 5:
                    self.autonomousTest()
                    self.stop()
                    self.flyWheelsOff()
                    activated = 1
                    break
            sleep(0.5)

            if activated == 1:
                continue
            while self.getButtonPressed() == True:
                pass
            sleep(0.5)

            print("button let go")
            start = time()
            while self.getButtonPressed() == False:
                if time() - start > 5:
                    self.autonomousBaseTurn()
                    self.stop()
                    self.flyWheelsOff()
                    activated = 1
                    break
            sleep(0.5)
            if activated == 1:
                continue
            while self.getButtonPressed() == True:
                pass
            sleep(0.5)

            print("button let go")
            start = time()
            while self.getButtonPressed() == False:
                if time() - start > 5:
                    self.forBack()
                    self.stop()
                    self.flyWheelsOff()
                    activated = 1
                    break
            if activated == 1:
                continue
            sleep(0.5)
            print("button pressed")
            while self.getButtonPressed() == True:
                pass
            sleep(0.5)
            self.ESCs.calibrate()

def main():
    """Testing CLI for the robot
    """
    robot = Robot()
    atexit.register(robot.shutdown)
    while True:
        os.system('clear')
        #robot.buttonControll()
        data = input("Remote control [r], Calibrate [c] Autonomous [a] or Exit [x]: ").lower()
        if data == "r":
            robot.remoteControl()
        elif data == "c":
            robot.ESCs.calibrate()
        elif data == "a":
            robot.autonomousTest()
        elif data == "b":
            robot.buttonControll()
        elif data == "x":
            exit()
        else:
            pass

main()
