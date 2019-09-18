from pivideostream2 import PiVideoStream
from time import sleep, time
from PIL import Image
import numpy as np
import atexit
import math
import cv2
import io
import os

from picamera.array import PiRGBArray
from imutils.video import FPS
from picamera import PiCamera
import imutils

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

import ESCD3in

class Robot:
    def __init__(self):
        self.setup()

    def setup(self):
        for i in range(14,20):
            GPIO.setup(i,GPIO.OUT,initial=1)
        GPIO.setup(8,GPIO.OUT,initial=1)
        GPIO.setup(11, GPIO.OUT,initial=1)
        GPIO.setup(26, GPIO.OUT, initial=1)
        GPIO.setup(27, GPIO.OUT, initial=1)
        self.ESCs = ESCD3in.PairESCController()
        #self.ESCs.calibrate()

    def shutdown(self):
        self.stop()
        GPIO.cleanup()
        self.ESCs.stopstop()
        print("Process Safely Stopped")

    def remoteControl(self):
        from pynput.keyboard import Key, Listener
        flag = False

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
                    if flag == False:
                        self.flyWheelsOn()
                        flag = True
                    else:
                        self.flyWheelsOff()
                        flag = False

        def on_release(key):
            self.stop()
            if key == Key.esc:
                self.ESCs.stop()
                return False

        with Listener(on_press=on_press,on_release=on_release) as listener:
                listener.join()

    def toggleGPIOPins(self, highPins, lowPins):
        for p in highPins:
            GPIO.output(p, GPIO.HIGH)
        for p in lowPins:
            GPIO.output(p, GPIO.LOW)

    def flyWheelsOn(self, duty=1400):
        self.ESCs.manual_drive(str(duty))

    def flyWheelsOff(self):
        self.ESCs.manual_drive("0")

    def backward(self):
        self.stop()
        self.toggleGPIOPins(highPins=[26,27,8,11], lowPins=[16,19])

    def forward(self):
        self.stop()
        self.toggleGPIOPins(highPins=[], lowPins=[26,27,8,11,16,19])

    def turnRight(self):
        self.stop()
        self.toggleGPIOPins(highPins=[8,11], lowPins=[26,27,16,19])

    def turnLeft(self):
        self.stop()
        self.toggleGPIOPins(highPins=[26,27], lowPins=[8,11,16,19])

    def stop(self):
        self.toggleGPIOPins(highPins=list(range(14,20))+[8,11,26,27], lowPins=[])

    def findBall(self, frame, display=False):
        """A function that takes an img (and any other optional params)
           and returns the centre of the position of the nearest ball
        """
        greenLower, greenUpper = (22, 86, 20), (40, 255, 255)

        #blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        #Construct a mask for the color "green", then perform smooth it to remove noise
        mask = cv2.inRange(hsv, greenLower, greenUpper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        # find contours in the mask and initialize the current
        # (x, y) center of the ball
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        center = None

        if len(cnts) > 0:
            # find the largest contour in the mask, then use it to compute the minimum enclosing circle
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            if radius > 20:
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            if display:
                imgX, imgY = frame.shape
                cv2.circle(frame,(x,y),(0,255,0),2) #Draw the outer circle
                cv2.line(frame, (int(imgX/2), 0), (int(imgX/2), imgY), (255,0,0), 2)

        if display:
            cv2.imshow("Analysed frame",frame)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        return center


    def turnToBall(self):
        print("Turning towards and collecting balls")
        vs = PiVideoStream().start(brightness=65,contrast=30)
        sleep(2) #Allow the stream to setup
        bad, activated = 0, 0

        width = 600
        badThreshold = 30
        closeThreshold = 50
        centerLine = 334
        turnThreshold = 100

        try:
            while True:

                if False: #If you can see a wall close
                    self.turnLeft()
                    time.sleep(random.random()*3)
                    pass

                #Grab the frame from the threaded video stream and resize it to have a maximum width of 400 pixels
                startImgAnalysis = time()
                frame = vs.read()
                frame = imutils.resize(frame, width=width)

                '''cv2.imshow("Analysed frame",frame)
                cv2.waitKey(0)
                cv2.destroyAllWindows()'''

                #_ = input()

                center = self.findBall(frame)
                endImgAnalysis = time()

                if center is None: #If no balls (of the right size) are found
                    print("No balls found")
                    if activated == 0:
                        pass
                    else:
                        bad += 1
                    if bad > badThreshold:
                        print("Activate nulled")
                        #self.flyWheelsOff()
                        self.turnLeft()
                        bad = 0
                        activated = 0
                else: #If a ball has been found
                    print("Ball found")

                    x, y = center[0], center[1]

                    if activated == 0 and y < closeThreshold:
                        self.stop()
                        sleep(2)
                        #self.flyWheelsOn()
                        self.forward()
                        activated = 1


                    if activated == 1 and abs(centerLine-center[0]) > turnThreshold:
                        timeToTurn = (((x)/(centerLine*2))*(0.25+0.25)) - 0.2
                        print("Turning")
                        if timeToTurn > 0:
                            self.turnRight()
                            sleep(abs(timeToTurn))
                        else:
                            self.turnLeft()
                            sleep(abs(timeToTurn))
                        self.forward()

        # do a bit of cleanup
        finally:
            vs.stop()
            self.shutdown()


def main():
    robot = Robot()
    atexit.register(robot.shutdown)

    while True:
        os.system('clear')
        data = input("Remote control [r], Turn to ball [t] or Exit [x]: ").lower()
        if data == "r":
            robot.remoteControl()
        elif data == "t":
            robot.turnToBall()
        elif data == "x":
            exit()
        else:
            pass

if __name__ == "__main__":
    exit(main())
