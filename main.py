import time
import traceback
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
R_THIGH = 43.0      # thigh length in mm
R_FORELEG = 54.8    # foreleg length in mm

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

    def IK(self, x, y, z, t=0):
        # x, y, z are expressed in mm - 0, 0, 0 is defiend as where the shoulder joint attaches to the body,
        # t is the amount of time in milliseconds to take
        # so neutral y position is distance of should servo to upper arm.
        # Sets servo angles in degrees from neutral position
        r_xz = sqrt(x**2 + z**2)                     # radius (x, z)
        r_total = sqrt(x**2 + y**2 + z**2)           # radius from (0,0,0) - where the shoulder attaches to the body
        r_leg = sqrt(r_total**2 - R_SHOULDER**2)     # radius from (0,R_SHOULDER,0) - thigh and foreleg
        if isnan(r_leg): raise RuntimeError(F'Invalid leg position when calculating radii ({x}, {y}, {z})')

        # Shoulder angle
        phi_1 = arccos(R_SHOULDER / r_total)
        phi_2 = arccos(r_xz / r_total)
        theta_0 = rad2deg(phi_1 + phi_2)

        phi_3 = arccos((R_THIGH**2 + r_leg**2 - R_FORELEG**2) / (2 * R_THIGH * r_leg))
        phi_4 = arctan2(z, x)
        theta_1 = rad2deg(phi_3 + phi_4)  # eqn 4 converted to degrees

        phi_4 = arccos((R_FORELEG**2 + R_THIGH**2 - r_leg**2) / (2 * R_THIGH * R_FORELEG))
        theta_2 = rad2deg(phi_4)

        # Convert degrees into servo location (0 .. 1)
        servo_angle_shoulder = (90 - theta_0) / 180                                # Shoulder starts at 90 degrees rotation
        servo_angle_thigh = (90 - theta_1 + self.UpperLegOffsetAngle()) / 180.0   # Thigh is +180 because horizontal plane
        servo_angle_foreleg = (180 - theta_2) / 180.0                               # Foreleg is +90 because already vertical plane
        if isnan(servo_angle_shoulder) or servo_angle_shoulder < 0 or servo_angle_shoulder > 1: raise RuntimeError(F'Invalid leg position - shoulder ({x}, {y}, {z})')
        if isnan(servo_angle_thigh) or servo_angle_thigh < 0 or servo_angle_thigh > 1: raise RuntimeError(F'Invalid leg position - thigh ({x}, {y}, {z})')
        if isnan(servo_angle_foreleg) or servo_angle_foreleg < 0 or servo_angle_foreleg > 1: raise RuntimeError(F'Invalid leg position - foreleg ({x}, {y}, {z})')

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

    def SetServoPosition(self, shoulder, upper, lower, t=0):
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
        self.IK(0, R_SHOULDER, -25)

    def Lift(self):
        self.IK(0, R_SHOULDER, -14, 200)

    def Extend(self):
        self.IK(50, R_SHOULDER, -14, 200)

    def Lower(self):
        self.IK(50, R_SHOULDER, -25, 200)

    def Zero(self):
        self.IK(0, R_SHOULDER, -25, 200)

    def Step(self):
        self.Lift()
        self.Extend()
        self.Lower() 
        self.Zero()       


class FrontLeg(Leg):

    # Set the upper leg offset angle to 45 degrees (to compensate for diagonally positioned front leg upper servo)
    def UpperLegOffsetAngle(self):
        return 45

    def Salute(self):
        self.IK(50, R_SHOULDER - 50, 40, 400)
        # self.Default()


class RearLeg(Leg):

    def UpperLegOffsetAngle(self):
        return 0


class RobotServo:
    def __init__(self, servo, min, max, direction, location):
        self.servo = servo
        self.min = min
        self.max = max
        self.direction = direction
        self.Location = location
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
    def __init__(self, servos):
        self.Legs = {
            "LF": FrontLeg([servo for servo in servos if (servo.Location & LEFT) and (servo.Location & FORE)]),
            "RF": FrontLeg([servo for servo in servos if (servo.Location & RIGHT) and (servo.Location & FORE)]),
            "LR": RearLeg([servo for servo in servos if (servo.Location & LEFT) and (servo.Location & AFT)]),
            "RR": RearLeg([servo for servo in servos if (servo.Location & RIGHT) and (servo.Location & AFT)]),
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
        self.Legs["RF"].Step()
        self.Legs["LR"].Step()
        self.Legs["LF"].Step()
        self.Legs["RR"].Step()

# Servo definitions provide the following information for each servo:
# - the actual servo (from kit.servo list)
# - the range of motion of the servo mounted in the robot (min and max)
# - the direction that the servo moves, left and right are opposites
# - a bitwise anded list describing the servo and its location
servos = [
    # FORELEG
    RobotServo(kit.servo[4], 0, 180, 1, LEFT | AFT | LOWER),  # LR   (fwd/back)
    RobotServo(kit.servo[5], 0, 180, -1, RIGHT | FORE | LOWER),  # RF   (back/fwd)
    RobotServo(kit.servo[6], 0, 170, -1, RIGHT | AFT | LOWER),  # RR   (back/fwd)
    RobotServo(kit.servo[7], 0, 180, 1, LEFT | FORE | LOWER),  # LF   (fwd/back)
    # THIGH
    RobotServo(kit.servo[8], 0, 160, -1, RIGHT | AFT | UPPER),   # RR   (back/fwd)
    RobotServo(kit.servo[9], 20, 180, -1, RIGHT | FORE | UPPER),  # RF   (back/fwd)
    RobotServo(kit.servo[10], 20, 180, 1, LEFT | AFT | UPPER),  # LR   (fwd/back)
    RobotServo(kit.servo[11], 0, 160, 1, LEFT | FORE | UPPER),  # LF   (fwd/back)
    # SHOULDER
    RobotServo(kit.servo[12], 50, 160, 1, RIGHT | AFT | SHOULDER),   # RR     (down/up)
    RobotServo(kit.servo[13], 50, 140, -1, RIGHT | FORE | SHOULDER),  # RF     (up/down)
    RobotServo(kit.servo[14], 15, 105, -1, LEFT | AFT | SHOULDER),  # LR     (up/down)
    RobotServo(kit.servo[15], 45, 125, 1, LEFT | FORE | SHOULDER),   # LF     (down/up)
]

robot = Robot(servos)

try:
    robot.Default()
    time.sleep(1)

    # # TESTING SHOULDER MOVEMENT (DEBUG)
    # for i in range(0, 11, 2):
    #     robot.Legs["LF"].SetServoPosition(i / 10, 0.5, 0)
    #     robot.Legs["RF"].SetServoPosition(i / 10, 0.5, 0)
    #     time.sleep(0.5)
    # for i in range(10, -1, -2):
    #     robot.Legs["LF"].SetServoPosition(i / 10, 0.5, 0)
    #     robot.Legs["RF"].SetServoPosition(i / 10, 0.5, 0)
    #     time.sleep(0.5)

    # for i in range(0, 11, 2):
    #     robot.Legs["LR"].SetServoPosition(i / 10, 0.5, 0)
    #     robot.Legs["RR"].SetServoPosition(i / 10, 0.5, 0)
    #     time.sleep(0.5)
    # for i in range(10, -1, -2):
    #     robot.Legs["LR"].SetServoPosition(i / 10, 0.5, 0)
    #     robot.Legs["RR"].SetServoPosition(i / 10, 0.5, 0)
    #     time.sleep(0.5)

    # # TESTNG LEG MOVEMENT LIMITS (DEBUG)
    # robot.Legs["LF"].SetServoPosition(0, 0, 0)
    # robot.Legs["RF"].SetServoPosition(1, 0, 0)
    # time.sleep(0.5)

    # for i in range(0, 11, 2):
    #     robot.Legs["LR"].SetServoPosition(0, i/10, 0.5)
    #     time.sleep(0.2)
    #     robot.Legs["RR"].SetServoPosition(0, i/10, 0.5)
    #     time.sleep(0.2)

    # for i in range(0, 11, 2):
    #     robot.Legs["LF"].SetServoPosition(0, i/10, 0.5)
    #     time.sleep(0.2)
    #     robot.Legs["RF"].SetServoPosition(0, i/10, 0.5)
    #     time.sleep(0.2)

    # Walking
    # robot.Default()
    # for i in range(2):
    #     robot.Walk()

    # And salute
    robot.Salute()

    time.sleep(.5)
    robot.PowerDown()

except Exception:
    # On failure, turn off all power to all servos
    robot.PowerDown()
    traceback.print_exc()
