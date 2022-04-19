import time
from adafruit_servokit import ServoKit
from numpy import sqrt, arccos, arctan2, rad2deg

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
        # Ignore y for now - assume that the shoulder is always neutral (= ARM_A)
        # Returns : servo angles in degrees from neutral position
        y = ARM_A
        radius = sqrt(x**2 + z**2)
        phi_1 = arccos((ARM_C**2 - ARM_B**2 - radius**2) /
                       (-2 * ARM_B * radius))
        phi_2 = arctan2(z, x)
        theta_1 = rad2deg(phi_2-phi_1) + self.UpperLegOffsetAngle()  # eqn 4 converted to degrees

        phi_3 = arccos((radius**2 - ARM_B**2 - ARM_C**2) /
                       (-2 * ARM_B * ARM_C))
        theta_2 = rad2deg(phi_3)

        # Convert degrees into servo location (0 .. 1)
        # will always be -ve, but transforms to +ve
        servo_angle_thigh = (theta_1 + 180) / 180.0     # Thigh is 180 because horizontal plane
        servo_angle_foreleg = (theta_2 + 90) / 180.0    # Foreleg is 90 because already vertical plane

        # Get the current position of the servos to move and the iteration value 
        # per interval to move within the time specified
        s1pos = self.ThighServo.GetPosition()
        if s1pos == -1: s1pos = servo_angle_thigh
        s2pos = self.ForelegServo.GetPosition()
        if s2pos == -1: s2pos = servo_angle_foreleg
        s1iter = (servo_angle_thigh - s1pos) / 10.0
        s2iter = (servo_angle_foreleg - s2pos) / 10.0

        for i in range(10):
            self.ShoulderServo.SetPosition(0)
            self.ThighServo.SetPosition(s1pos + s1iter * i)
            self.ForelegServo.SetPosition(s2pos + s2iter * i)
            # Pause for one tenth of the required time.
            time.sleep(t / 10.0 / 1000)

    def Relax(self):
        for servo in self.Servos:
            servo.Relax()

    def Default(self):
        self.IK(0, ARM_A, -60)

    def Lift(self):
        self.IK(0, ARM_A, -50, 200)

    def Extend(self):
        self.IK(30, ARM_A, -50, 200)

    def Lower(self):
        self.IK(30, ARM_A, -60, 200)


class FrontLeg(Leg):
    def Salute(self):
        self.IK(20, 0, 20, 10)

    # Set the upper leg offset angle to 0.6 * 180 degrees (to compensate for diagonally positioned leg position)
    def UpperLegOffsetAngle(self):
        return 45

    def Step(self):
        self.Lift()
        self.Extend()
        self.Lower()


class RearLeg(Leg):
    # def Lower(self):
    #     self.IK(0, ARM_A, -20, 10)

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

    def Relax(self):
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
    def Relax(self):
        for _, leg in self.Legs.items():
            leg.Relax()


# Servo definitions provide the following information for each servo:
# - the actual servo (from kit.servo list)
# - the range of motion of the servo mounted in the robot (min and max)
# - the direction that the servo moves, left and right are opposites
# - a bitwise anded list describing the servo and its location
servos = [
    # FORELEG
    RobotServo(kit.servo[4], 0, 180, 1, LEFT | AFT | LOWER),  # LR   (fwd/back)
    RobotServo(kit.servo[5], 0, 180, -1, RIGHT |
               FORE | LOWER),  # RF   (back/fwd)
    RobotServo(kit.servo[6], 0, 170, -1, RIGHT |
               AFT | LOWER),  # RR   (back/fwd)
    RobotServo(kit.servo[7], 0, 180, 1, LEFT |
               FORE | LOWER),  # LF   (fwd/back)
    # THIGH
    RobotServo(kit.servo[8], 0, 140, -1, RIGHT |
               AFT | UPPER),   # RR   (back/fwd)
    RobotServo(kit.servo[9], 50, 180, -1, RIGHT |
               FORE | UPPER),  # RF   (back/fwd)
    RobotServo(kit.servo[10], 20, 180, 1, LEFT |
               AFT | UPPER),  # LR   (fwd/back)
    RobotServo(kit.servo[11], 0, 110, 1, LEFT |
               FORE | UPPER),  # LF   (fwd/back)
    # SHOULDER
    RobotServo(kit.servo[12], 50, 160, 1, RIGHT |
               AFT | SHOULDER),   # RR     (down/up)
    RobotServo(kit.servo[13], 50, 140, -1, RIGHT |
               FORE | SHOULDER),  # RF     (up/down)
    RobotServo(kit.servo[14], 15, 105, -1, LEFT |
               AFT | SHOULDER),  # LR     (up/down)
    RobotServo(kit.servo[15], 45, 125, 1, LEFT |
               FORE | SHOULDER),   # LF     (down/up)
]

robot = Robot(servos)

# robot.Default()
# time.sleep(.5)
# robot.Legs["LF"].Salute()
# robot.Legs["RF"].Salute()
# time.sleep(.5)
# robot.Default()
# time.sleep(.5)
# robot.Legs["LF"].Salute()
# time.sleep(.5)
# robot.Legs["RF"].Salute()
# time.sleep(.5)
# robot.Default()

# time.sleep(.5)
# robot.Legs["LR"].Lower()
# robot.Legs["RR"].Lower()

robot.Default()
time.sleep(1)
for i in range(5):
    robot.Legs["RF"].Step()
    robot.Legs["LR"].Step()
    robot.Legs["LF"].Step()
    robot.Legs["RR"].Step()

time.sleep(.5)
robot.Relax()
