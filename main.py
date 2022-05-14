import json
import time
import traceback
from adafruit_servokit import ServoKit
from math import isnan
from numpy import sqrt, arccos, arcsin, arctan, arctan2, rad2deg
from robot import *

robot = Robot()

try:
    robot.Default()
    time.sleep(1)

    # # TESTING SHOULDER MOVEMENT (DEBUG)
    # for i in range(0, 11, 2):
    #     robot.Legs["LF"]._1SetServoPosition(i / 10, 0.5, 0)
    #     robot.Legs["RF"]._SetServoPosition(i / 10, 0.5, 0)
    #     time.sleep(0.5)
    # for i in range(10, -1, -2):
    #     robot.Legs["LF"]._SetServoPosition(i / 10, 0.5, 0)
    #     robot.Legs["RF"]._SetServoPosition(i / 10, 0.5, 0)
    #     time.sleep(0.5)

    # for i in range(0, 11, 2):
    #     robot.Legs["LR"]._SetServoPosition(i / 10, 0.5, 0)
    #     robot.Legs["RR"]._SetServoPosition(i / 10, 0.5, 0)
    #     time.sleep(0.5)
    # for i in range(10, -1, -2):
    #     robot.Legs["LR"]._SetServoPosition(i / 10, 0.5, 0)
    #     robot.Legs["RR"]._SetServoPosition(i / 10, 0.5, 0)
    #     time.sleep(0.5)

    # TESTNG UPPER LEG MOVEMENT LIMITS (DEBUG)
    # robot.Legs["LF"]._SetServoPosition(0, 0, 0)
    # for i in range(5):
    #     robot.Legs["RF"]._SetServoPosition(1, 0.5, 0.5)
    #     time.sleep(0.5)
    #     robot.Legs["RF"]._SetServoPosition(0, 0.5, 0.5)
    #     time.sleep(0.5)

    # Move forelegs out of the way for rear leg test
    # robot.Legs["LF"]._SetServoPosition(0, 1, 0)
    # robot.Legs["RF"]._SetServoPosition(0, 1, 0)
    # robot.Legs["LF"]._SetServoPosition(0, 0, 1)
    # robot.Legs["RF"]._SetServoPosition(0, 0, 1)
    # robot.Legs["LF"]._SetServoPosition(0, 0, 0)
    # robot.Legs["RF"]._SetServoPosition(0, 0, 0)
    # for i in range(0, 11, 2):
    #     robot.Legs["LR"]._SetServoPosition(0, i/10, 1-i/10)
    #     time.sleep(0.2)
    #     robot.Legs["RR"]._SetServoPosition(0, i/10, 1-i/10)
    #     time.sleep(0.2)

    # for i in range(0, 11, 2):
    #     robot.Legs["LF"]._SetServoPosition(0, i/10, 0.5)
    #     time.sleep(0.2)
    #     robot.Legs["RF"]._SetServoPosition(0, i/10, 0.5)
    #     time.sleep(0.2)

    # TESTNG FORELEG MOVEMENT LIMITS (DEBUG)


    # Walking
    robot.Default()
    for i in range(5):
        robot.Walk()

    # And salute
    # robot.Salute()

    # time.sleep(.5)
    robot.PowerDown()

except Exception:
    # On failure, turn off all power to all servos
    robot.PowerDown()
    traceback.print_exc()
