import json
import time
import threading
from adafruit_servokit import ServoKit
from math import isnan
from numpy import sqrt, arccos, arcsin, arctan, arctan2, rad2deg

LEFT = 1
RIGHT = 2
FORE = 4
AFT = 8
LOWER = 16
UPPER = 32
SHOULDER = 64

R_SHOULDER = 43.0   # shoulder width in mm
R_THIGH = 44.0      # thigh length in mm
R_FORELEG = 52.8    # foreleg length in mm

# Orig X, Y plane
# Me   X, Z plane

# a1: displacement in the z-direction of joint one from the ground (i.e height)
# (for me, y direction = R_SHOULDER)

# a2: displacement from the axes of rotation from Motor 1 to Motor 2
# ( R_THIGH )

# a3: displacement in the z-direction from joint 1 to joint 2 (in this case 0 because both are at the same height)
# ( 0 )

# a4:  the displacement from the axis of rotation from Motor 2 to the tool tip
# ( R_FORELEG )

kit = ServoKit(channels=16)


class Leg:
    def __init__(self, servos):
        self.Servos = servos
        self.ForelegServo = next(
            filter(lambda servo: servo.Location & LOWER, servos), None)
        self.ThighServo = next(
            filter(lambda servo: servo.Location & UPPER, servos), None)
        self.ShoulderServo = next(
            filter(lambda servo: servo.Location & SHOULDER, servos), None)

    def UpperLegOffsetAngle(self):
        return 0

    def IK(self, x, z, shoulder=90, t=0):
        # shoulder is the angle of the shoulder (where 90 is horizontal, 0 is vertical)
        # x, z are expressed in mm - 0, 0 is defined as where the shoulder joint attaches to the rest of the leg,
        # t is the amount of time in milliseconds to take
        # so neutral y position is distance of should servo to upper arm.
        # Sets servo angles in degrees from neutral position
        r_xz = sqrt(x**2 + z**2)                     # radius (x, z)

        # Shoulder angle
        theta_0 = shoulder

        # Thigh angle
        phi_3 = rad2deg(arccos((R_THIGH**2 + r_xz**2 - R_FORELEG**2) / (2 * R_THIGH * r_xz)))
        phi_4 = rad2deg(arctan2(x, z)) - 90     # Rotate 90 degrees so that 0 degrees is horizontal facing front
        theta_1 = phi_3 + phi_4
        if (x < 0):
            theta_1 += 360
        print(F'> theta_1... ({theta_1:.2f})')

        # Foreleg angle
        phi_5 = arccos((R_FORELEG**2 + R_THIGH**2 - r_xz**2) / (2 * R_THIGH * R_FORELEG))
        theta_2 = rad2deg(phi_5)
        print(F'> theta_2... ({theta_2:.2f})')

        # Convert degrees into servo location (0 .. 1)
        servo_angle_shoulder = (90 - theta_0) / 90                                # Shoulder starts at 90 degrees rotation
        servo_angle_thigh = (theta_1 + self.UpperLegOffsetAngle()) / 180.0
        servo_angle_foreleg = theta_2 / 180.0

        if isnan(servo_angle_shoulder) or servo_angle_shoulder < 0 or servo_angle_shoulder > 1: raise RuntimeError(f'Invalid shoulder position {servo_angle_shoulder} ({x}, {z})')
        if isnan(servo_angle_thigh) or servo_angle_thigh < 0 or servo_angle_thigh > 1: raise RuntimeError(f'Invalid thigh position {servo_angle_thigh} ({x}, {z})')
        if isnan(servo_angle_foreleg) or servo_angle_foreleg < 0 or servo_angle_foreleg > 1: raise RuntimeError(f'Invalid foreleg position {servo_angle_foreleg} ({x}, {z})')

        # Get the current position of the servos to move and the iteration value 
        # per interval to move within the time specified
        s0pos = self.ShoulderServo.GetPosition()
        if s0pos == -1: s0pos = servo_angle_shoulder
        s1pos = self.ThighServo.GetPosition()
        if s1pos == -1: s1pos = servo_angle_thigh
        s2pos = self.ForelegServo.GetPosition()
        if s2pos == -1: s2pos = servo_angle_foreleg

        s0iter = (servo_angle_shoulder - s0pos) / 10.0
        s1iter = (servo_angle_thigh - s1pos) / 10.0
        s2iter = (servo_angle_foreleg - s2pos) / 10.0

        # Check all is ok before proceeding
        if not self._validate(s0pos, s1pos, s2pos): return

        print(F'> moving to ({servo_angle_shoulder:.2f}, {servo_angle_thigh:.2f}, {servo_angle_foreleg:.2f})')
        try:
            for i in range(1, 11):
                self.ShoulderServo.SetPosition(s0pos + s0iter * i)
                self.ThighServo.SetPosition(s1pos + s1iter * i)
                self.ForelegServo.SetPosition(s2pos + s2iter * i)
                # Pause for one tenth of the required time.
                time.sleep(t / 10.0 / 1000)
        except Exception:
            pass

    def _validate(self, s0pos, s1pos, s2pos):
        if (0 <= s0pos <= 1) and (0 <= s1pos <= 1) and (0 <= s2pos <= 1):
            return True
        raise RuntimeError(f'Invalid position ({s0pos}, {s1pos}, {s2pos})')
        return False

    def _SetServoPosition(self, shoulder, upper, lower, t=0):
        s0pos = self.ShoulderServo.GetPosition()
        if s0pos == -1: s0pos = upper
        s1pos = self.ThighServo.GetPosition()
        if s1pos == -1: s1pos = upper
        s2pos = self.ForelegServo.GetPosition()
        if s2pos == -1: s2pos = lower

        rnge = max(10, t / 50)

        s0iter = (shoulder - s0pos) / rnge
        s1iter = (upper - s1pos) / rnge
        s2iter = (lower - s2pos) / rnge

        for i in range(int(rnge)):
            self.ShoulderServo.SetPosition(s0pos + s0iter * rnge)
            self.ThighServo.SetPosition(s1pos + s1iter * rnge)
            self.ForelegServo.SetPosition(s2pos + s2iter * rnge)
            time.sleep(t / rnge / 1000.0)

    def PowerDown(self):
        for servo in self.Servos:
            servo.PowerDown()

    def Default(self):
        self.IK(0, -78)

    def Lift(self):
        self.IK(20, -65, 90, 200)

    def Extend(self):
        self.IK(60, -65, 90, 200)

    def Lower(self):
        self.IK(50, -79, 90, 200)

    def Zero(self):
        self.IK(0, -79, 90, 200)

    def Step(self):
        self.Lift()
        self.Extend()
        self.Lower() 
        self.Zero()       


class FrontLeg(Leg):

    # Set the upper leg offset angle to 45 degrees (to compensate for diagonally positioned front leg upper servo)
    def UpperLegOffsetAngle(self):
        return 30

    def Salute(self):
        # self._SetServoPosition(1, 0, 0)
        self.IK(64, 58, 10, 400)
        self.Default()


class RearLeg(Leg):

    def UpperLegOffsetAngle(self):
        return 0


class RobotServo:
    def __init__(self, servo, min, max, direction, side, foreaft, limb):
        self.servo = servo
        self.min = min
        self.max = max
        self.direction = direction
        self.Location = side | foreaft | limb
        self.Position = -1

    # Sets the location of the servo from 0 to 1 (float)
    def SetPosition(self, value):
        assert(0 <= value <= 1)

        if self.direction > 0:
            self.servo.angle = (self.max - self.min) * value + self.min
        else:
            self.servo.angle = (self.max - self.min) * (1 - value) + self.min

        self.Position = value

    def GetPosition(self):
        return self.Position

    def PowerDown(self):
        self.servo.angle = None


class Robot:
    servos = []

    def __init__(self):
        # Servo definitions provide the following information for each servo:
        # - the actual servo (from kit.servo list)
        # - the range of motion of the servo mounted in the robot (min and max)
        # - the direction that the servo moves, left and right are opposites
        # - a bitwise anded list describing the servo and its location
        with open('config.json', 'r') as f:
            config = json.load(f)

        for servo in config["servos"]:
            side = LEFT if servo["side"] == "LEFT" else RIGHT
            foreaft = FORE if servo["foreaft"] == "FORE" else AFT
            limbs = {"SHOULDER": SHOULDER, "UPPER": UPPER, "LOWER": LOWER}
            limb = limbs[servo["limb"]]
            self.servos.append(RobotServo(kit.servo[servo["id"]], servo["min"], servo["max"], servo["rot"], side, foreaft, limb))

        self.Legs = {
            "LF": FrontLeg([servo for servo in self.servos if (servo.Location & LEFT) and (servo.Location & FORE)]),
            "RF": FrontLeg([servo for servo in self.servos if (servo.Location & RIGHT) and (servo.Location & FORE)]),
            "LR": RearLeg([servo for servo in self.servos if (servo.Location & LEFT) and (servo.Location & AFT)]),
            "RR": RearLeg([servo for servo in self.servos if (servo.Location & RIGHT) and (servo.Location & AFT)]),
        }

    # Set legs straight with shoulders vertical - standing on tip-toes
    def Default(self):
        for _, leg in self.Legs.items():
            leg.Default()

    # Turn off power to all servos
    def PowerDown(self):
        for _, leg in self.Legs.items():
            leg.PowerDown()

    def Salute(self):
        self.Legs["RF"].Salute()

    def Walk(self):
        # Kick off Right Front, Left Rear legs in parallel
        t1 = threading.Thread(target=self.Legs["RF"].Step)
        t2 = threading.Thread(target=self.Legs["LR"].Step)
        t1.start()
        t2.start()
        # Wait for the leg movement to complete
        t1.join()
        t2.join()

        # Kick off Left Front, Right Rear legs in parallel
        t1 = threading.Thread(target=self.Legs["LF"].Step)
        t2 = threading.Thread(target=self.Legs["RR"].Step)
        t1.start()
        t2.start()
        # Wait for the leg movement to complete
        t1.join()
        t2.join()
