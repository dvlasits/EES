from source5 import *

import tkinter as tk
from tkinter.ttk import Radiobutton
from tkinter import messagebox, Scale
import threading

#import atexit
#from time import time, sleep

"""class Robot:
    def forward(self):
        pass

    def turnLeft(self):
        pass

    def turnRight(self):
        pass

    def backward(self):
        pass

    def stop(self):
        pass

    def shutdown(self):
        pass

    def flyWheelsOn(self, duty=""):
        pass

    def flyWheelsOff(self):
        pass

    def getDistance(self):
        return int(round(time(), 0))"""


class NoHoverButton(tk.Button):
    def __init__(self, master, **kw):
        tk.Button.__init__(self,master=master,**kw)
        self.defaultBackground = self["background"]
        self['activebackground'] = self["background"]

    def setBackground(self, colour):
        self["activebackground"] = colour
        self["background"] = colour

    def resetBackground(self):
        self.setBackground(self.defaultBackground)


class App:
    def __init__(self):
        self.root = tk.Tk()

        self.robot = Robot()
        atexit.register(self.robot.shutdown)

        self.TITLE = "Robot control"
        self.root.title = self.TITLE
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        self.frame = self.getNewFrame()
        self.thread = None
        self.main()

    def getNewFrame(self):
        """Create a new frame
        Return 1: frame [tk.Frame]; the App frame"""
        #Create a Frame
        frame = tk.Frame(self.root, width=600, height=300)
        frame.pack(fill="both", expand=True)
        frame.grid_propagate(False)
        return frame

    def videoLoop(self):
        """Update the distance"""
        try:
            while not self.stopEvent.is_set():
                #Get the distance
                self.distance["text"] = "Distance:\n{}".format(self.robot.getDistance())

        except RuntimeError as e:
            print("Runtime error: {}".format(e))


    def main(self):
        """Produce the app window"""

        self.flywheelsFlag = 0
        self.flywheelsDuty = 1130

        def toggleFlywheels(event=None):
            """Toggle the flywheels and the button colour"""
            self.flywheelsFlag = (self.flywheelsFlag+1)%2
            self.flywheelsDuty = self.slider.get()
            if self.flywheelsFlag:
                self.flwheels.setBackground("red")
            else:
                self.flwheels.resetBackground()
            #print("On" if self.flywheelsFlag else "Off", self.flywheelsDuty)

            if self.flywheelsFlag:
                self.robot.flyWheelsOn(self.flywheelsDuty)
            else:
                self.robot.flyWheelsOff()

        def clicked(event=None):
            pass

        def unclicked(event=None):
            self.robot.stop()

        self.up = NoHoverButton(self.frame, text="^", height=5, width=5)
        self.up.grid(column=1, row=0)
        self.up.bind("<ButtonPress>", lambda x: self.robot.forward())
        self.up.bind("<ButtonRelease>", unclicked)

        self.left = NoHoverButton(self.frame, text="<", height=5, width=5)
        self.left.grid(column=0, row=1)
        self.left.bind("<ButtonPress>", lambda x: self.robot.turnLeft())
        self.left.bind("<ButtonRelease>", unclicked)

        self.right = NoHoverButton(self.frame, text=">", height=5, width=5)
        self.right.grid(column=2, row=1)
        self.right.bind("<ButtonPress>", lambda x: self.robot.turnRight())
        self.right.bind("<ButtonRelease>", unclicked)

        self.down = NoHoverButton(self.frame, text="v", height=5, width=5)
        self.down.grid(column=1, row=2)
        self.down.bind("<ButtonPress>", lambda x: self.robot.backward())
        self.down.bind("<ButtonRelease>", unclicked)

        self.flwheels = NoHoverButton(self.frame, text="*", height=5, width=5)
        self.flwheels.grid(column=1, row=1)
        self.flwheels.bind("<ButtonPress>", toggleFlywheels)


        self.calibrate = NoHoverButton(self.frame, text="Calibrate\nflywheels") #, height=5, width=5)
        self.calibrate.grid(column=3, row=1)
        self.calibrate.bind("<ButtonPress>", lambda x: unclicked) #self.robot.flywheels.calibrate())
        self.calibrate.bind("<ButtonRelease>", lambda x: unclicked)

        self.slider = Scale(self.frame, from_=1000, to=2000, tickinterval=250, resolution=10, length=75)
        self.slider.set(self.flywheelsDuty)
        self.slider.grid(column=3, row=2)

        self.distance = tk.Label(self.frame, text="Distance:\nNone")
        self.distance.grid(column=3, row=0)

        self.stopEvent = threading.Event()
        self.thread = threading.Thread(target=self.videoLoop, args=())
        self.thread.start()

    def close(self):
        """Shutdown the robot, and close the app window"""
        self.robot.stop()
        self.robot.flyWheelsOff()
        messagebox.showerror('Closing window!', 'You are closing the window')
        self.stopEvent.set()
        self.robot.shutdown()
        exit()

def main():
    app = App()
    app.root.mainloop()

if __name__ == "__main__":
    exit(main())
