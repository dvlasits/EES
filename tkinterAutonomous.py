#from source3 import *

import tkinter as tk
from tkinter.ttk import Radiobutton
from tkinter import messagebox, Scale
import threading

import atexit
from time import time, sleep

class Robot:
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
        return int(round(time(), 0))

    def setDefaultFlywheelDuty(self, duty):
        pass


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

        def clicked(event=None):
            pass

        def unclicked(event=None):
            self.robot.stop()

        def updateFlywheelDuty(event=None):
            duty = self.slider.get()
            print(duty)
            self.robot.setDefaultFlywheelDuty(duty)

        self.up = NoHoverButton(self.frame, text="Start collection", height=5, width=10)
        self.up.pack(padx=10, pady=10)#grid(column=0, row=0)
        self.up.bind("<ButtonPress>", lambda x: self.robot.autonomous())
        self.up.bind("<ButtonRelease>", unclicked)

        self.calibrate = NoHoverButton(self.frame, text="Calibrate\nflywheels") #, height=5, width=5)
        self.calibrate.pack(padx=10, pady=10)#.grid(column=1, row=0)
        self.calibrate.bind("<ButtonPress>", lambda x: unclicked) #self.robot.flywheels.calibrate())
        self.calibrate.bind("<ButtonRelease>", lambda x: unclicked)

        self.slider = Scale(self.frame, from_=1000, to=2000, tickinterval=250,
            resolution=10, length=75, command=updateFlywheelDuty)
        self.slider.set(1130)
        self.slider.pack(padx=10, pady=10)#.grid(column=2, row=0)


    def close(self):
        """Shutdown the robot, and close the app window"""
        self.robot.stop()
        self.robot.flyWheelsOff()
        messagebox.showerror('Closing window!', 'You are closing the window')
        self.robot.shutdown()
        exit()

def main():
    app = App()
    app.root.mainloop()

if __name__ == "__main__":
    exit(main())
