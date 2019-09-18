from pynput.keyboard import Key, Listener
from robotFunctions import *


def on_press(key):
	if key == Key.down:
		robot.Back()

	if key == Key.up:
		robot.Forward()
	if key == Key.right:
		robot.TurnRight()
	if key == Key.left:
		robot.TurnLeft()
	if key == Key.space:
		robot.FlyWheelsOn()
	if key == Key.shift:
		robot.FlyWheelsOff()
def on_release(key):
	robot.Stop()
	if key == Key.esc:
		# Stop listener
 		return False

# Collect events until released

with Listener(
	on_press=on_press,
	on_release=on_release) as listener:
		listener.join()
