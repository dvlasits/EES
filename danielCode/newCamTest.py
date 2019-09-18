# USAGE
# python picamera_fps_demo.py
# python picamera_fps_demo.py --display 1

# import the necessary packages
from __future__ import print_function
from pivideostream2 import PiVideoStream
from imutils.video import FPS
import imutils
from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse
import imutils
import time
import cv2
from robotFunctions import *
# created a *threaded *video stream, allow the camera sensor to warmup,
# and start the FPS counter

print("[INFO] sampling THREADED frames from `picamera` module...")
vs = PiVideoStream().start(brightness = 65,contrast = 100)
time.sleep(2.0)
greenLower = (22, 86, 8)
greenUpper = (40, 255, 255)
count = 0
# loop over some frames...this time using the threaded stream
robot.TurnLeft()
bad = 0
activated = 0
FLysOn = 0
try:
	while True:
		start = time.time()
		count += 1
		# grab the frame from the threaded video stream and resize it
		# to have a maximum width of 400 pixels
		frame = vs.read()
		# check to see if the frame should be displayed to our screen
		frame = imutils.resize(frame, width=600)
		#blurred = cv2.GaussianBlur(frame, (11, 11), 0)
		hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

		# construct a mask for the color "green", then perform
		# a series of dilations and erosions to remove any small
		# blobs left in the mask
		mask = cv2.inRange(hsv, greenLower, greenUpper)
		mask = cv2.erode(mask, None, iterations=2)
		mask = cv2.dilate(mask, None, iterations=2)

		# find contours in the mask and initialize the current
		# (x, y) center of the ball
		cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
			cv2.CHAIN_APPROX_SIMPLE)
		cnts = imutils.grab_contours(cnts)
		center = None

		# only proceed if at least one contour was found
		if len(cnts) > 0:
			# find the largest contour in the mask, then use
			# it to compute the minimum enclosing circle and
			# centroid
			c = max(cnts, key=cv2.contourArea)
			((x, y), radius) = cv2.minEnclosingCircle(c)

			M = cv2.moments(c)
			center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
			# only proceed if the radius meets a minimum size
			if radius > 10 and radius < 20:
				if activated == 2:
					activated = 1
				if activated == 0:
					robot.Stop()
					time.sleep(0.5)
					activated  = 2
					#robot.FlyWheelsOn()
					robot.Forward()
				print(center[0])
				
				if activated == 2 and abs(334-center[0]) > 100:
					x = center[0]
					timeToTurn = (((x-0)/(668-0))*(0.6--0.6)) + - 0.6
					if timeToTurn > 0:
						robot.TurnRight()
						time.sleep(abs(timeToTurn))
					else:
						robot.TurnLeft()
						time.sleep(abs(timeToTurn))
					robot.Forward()
				print(center[1],"y")
				if activated == 1 and center[1] < 250 and FLysOn == 0:
					robot.FlyWheelsOn()
					FlysOn = 1
					
		
				# draw the circle and centroid on the frame,
				# then update the list of tracked points
				'''cv2.circle(frame, (int(x), int(y)), int(radius),
					(0, 255, 255), 2)
				cv2.circle(frame, center, 5, (0, 0, 255), -1)'''
			else:
				print("no tennis ball")
				if activated != 1 and activated != 2:
					pass
				else:
					bad += 1
					print(bad,"Bad")
				if bad > 20:
					print("Activate nulled")
					robot.Stop()
					robot.FlyWheelsOff()
					robot.TurnLeft()
					bad = 0
					activated = 0
					FLysOn = 0
					time.sleep(10)
		else:
			print("no tennis ball")
			if activated != 1 and activated != 2:
				pass
			else:
				bad += 1
				print(bad,"bad")
			if bad > 20:
				print("Activate nulled")
				robot.Stop()
				robot.FlyWheelsOff()
				robot.TurnLeft()
				bad = 0
				activated = 0
				FlysOn = 0
				time.sleep(10)
		# update the points queu

		# show the frame to our screen
		'''cv2.imshow("Frame", frame)
		key = cv2.waitKey(1) & 0xFF'''

# do a bit of cleanup
finally:
	cv2.destroyAllWindows()
	vs.stop()
