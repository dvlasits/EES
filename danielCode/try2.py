from robotFunctions import *
import time#
while True:
    u,x,y,width,height = robot.getBlocks()
    if x is not None:

        if x < 260 and x > 150:
            print(y)
            robot.Stop()
            robot.Forward()
            time.sleep(0.5)
            robot.FlyWheelsOn()
            time.sleep(2)
            robot.FlyWheelsOff()
            robot.Stop()
    else:
        robot.TurnRight()
'''    for i in range(250):
        time.sleep(0.01)
        if robot.getDis() < 500:
            print("something in the way")
            break'''
