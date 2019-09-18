import time, os

def main():
    """Testing CLI for the robot
    """
    #os.system('clear')
    while True:

        data = input("Remote control [r], Calibrate [c] Autonomous [a] or Exit [x]: ").lower()
        if data == "r":
            print("Waiting for remote control commands")
            time.sleep(10)
        if data == "c":
            print("Disconnect the battery and press Enter")
            inp = input() #Add code to do relay connect/disconnect instead

            print("Connect the battery now, you will here two beeps, then wait for a gradual falling tone then press Enter")
            inp = input() #Add sleep as necessary instead

            print("You should another tone from every motor")
            for i in range(13):
                if i%5==0:
                    print("{} seconds till next process".format(13-i))
                time.sleep(1)
            print("Motors spinning up for 10 seconds at the lowest speed")
            print("Motors spinning down, and stopping")
        elif data == "a":
            print("Starting autonomous collection")
            time.sleep(10)
        elif data == "x":
            exit()
        else:
            pass
        print("")

if __name__ == "__main__":
    exit(main())
