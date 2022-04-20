import time
from adafruit_servokit import ServoKit
from numpy import sqrt, arccos, arcsin, arctan2, rad2deg

LEFT = 1
RIGHT = 2
FORE = 4
AFT = 8
LOWER = 16
UPPER = 32
SHOULDER = 64

ARM_A = 43.0  # shoulder width in mm
ARM_B = 43.0  # arm length in mm
ARM_C = 54.8  # hand length in mm

# Orig X, Y plane
# Me   X, Z plane

# a1: displacement in the z-direction of joint one from the ground (i.e height)
# (for me, y direction = ARM_A)

# a2: displacement from the axes of rotation from Motor 1 to Motor 2
# ( ARM_B )

# a3: displacement in the z-direction from joint 1 to joint 2 (in this case 0 because both are at the same height)
# ( 0 )

# a4:  the displacement from the axis of rotation from Motor 2 to the tool tip
# ( ARM_C )

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
        xy_radius = sqrt(x**2 + y**2)                         # radius in the x,y plane only
        total_radius = sqrt(xy_radius**2 + z**2)              # radius from (0,0,0) - where the shoulder attaches to the body
        lower_leg_radius = sqrt(total_radius **2 - ARM_A**2)  # radius from (0,ARM_A,0) - thigh and foreleg

        # Shoulder angle  
        phi_1 = arcsin(xy_radius / total_radius)      
        phi_2 = arcsin(lower_leg_radius / total_radius)
        theta_0 = rad2deg(phi_1 + phi_2)

        # radius = sqrt(x**2 + z**2)
        phi_1 = arccos((ARM_C**2 - ARM_B**2 - lower_leg_radius**2) / (-2 * ARM_B * lower_leg_radius))
        phi_2 = arctan2(z, x)
        theta_1 = rad2deg(phi_2 - phi_1)  # eqn 4 converted to degrees

        phi_3 = arccos((lower_leg_radius**2 - ARM_B**2 - ARM_C**2) / (-2 * ARM_B * ARM_C))
        theta_2 = rad2deg(phi_3)

        # Convert degrees into servo location (0 .. 1)
        servo_angle_shoulder = (theta_0 - 90) / 180                                # Shoulder starts at 90 degrees rotation
        servo_angle_thigh = (theta_1 + 180 + self.UpperLegOffsetAngle()) / 180.0   # Thigh is +180 because horizontal plane
        servo_angle_foreleg = (theta_2 + 90) / 180.0                               # Foreleg is +90 because already vertical plane

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

        for i in range(10):
            self.ShoulderServo.SetPosition(s0pos + s0iter * i)
            self.ThighServo.SetPosition(s1pos + s1iter * i)
            self.ForelegServo.SetPosition(s2pos + s2iter * i)
            # Pause for one tenth of the required time.
            time.sleep(t / 10.0 / 1000)

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
        self.IK(0, ARM_A, -50)

    def Lift(self):
        self.IK(0, ARM_A, -45, 200)

    def Extend(self):
        self.IK(30, ARM_A, -45, 200)

    def Lower(self):
        self.IK(30, ARM_A, -50, 200)


class FrontLeg(Leg):

    # Set the upper leg offset angle to 45 degrees (to compensate for diagonally positioned front leg upper servo)
    def UpperLegOffsetAngle(self):
        return 45

    # def Salute(self):
    #     self.IK(20, -40, 30, 400)
    #     self.Default()

    def Step(self):
        self.Lift()
        self.Extend()
        self.Lower()


class RearLeg(Leg):

    def Step(self):
        self.Lift()
        self.Extend()
        self.Lower()


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

    # def Salute(self):
    #     self.Legs["RF"].Salute()

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

    # # TESTNG LEG MOVEMENT LIMITS (DEBUG)
    # robot.Legs["LF"].SetServoPosition(0, 0, 0.5)
    # robot.Legs["RF"].SetServoPosition(0, 0, 0.5)

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
    # for i in range(15):
    #     robot.Walk()

    # And salute
    robot.Legs["RF"].SetServoPosition(1, 0, 0, 400)
    robot.Legs["RF"].SetServoPosition(0, 1, 0.5, 100)

    time.sleep(.5)
    robot.PowerDown()

except:
    # On failure, turn off all power to all servos
    robot.PowerDown()
