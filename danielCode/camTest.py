from robotFunctions import *
import time
def TurnToFace():
    try:
        u,x,y,width,height = robot.getBlocks()
        if x is None:
            #robot.TurnLeft()
            time.sleep(0.2)
            robot.Stop()
            time.sleep(1)
        for i in range(40):
            u,x,y,width,height = robot.getBlocks()
            if x is not None:
                break
        if x > 180:
            robot.TurnRight()
            while x > 210:
                u,x,y,width,height = robot.getBlocks()
            robot.Stop()
        elif x < 180:
            robot.TurnLeft()
            while x < 150:
                u,x,y,width,height = robot.getBlocks()
            robot.Stop()
        return True
    except TypeError:
        print("lost it")
        return False

def GetBall():
    try:
        time.sleep(1)
        if not TurnToFace(robot):
            return False
        u,x,y,width,height = robot.getBlocks()

        '''while y < 50:
            u,x,y,width,height = robot.getBlocks()'''
        robot.Forward()
        time.sleep(0.5)
        robot.FlyWheelsOn()


        while x is not None:
            u,x,y,width,height = robot.getBlocks()
        time.sleep(1.7)
        robot.FlyWheelsOff()
    except TypeError:
        robot.FlyWheelsOff()
        robot.Stop()
        print("couldn't see a ball")
        time.sleep(1)
        return False



while True:
    u,x,y,width,height = robot.getBlocks()
    if x is not None:
        robot.Stop()
        GetBall()
    else:
        robot.TurnRight()
