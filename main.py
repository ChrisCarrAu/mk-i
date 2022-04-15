import time
from adafruit_servokit import ServoKit

LEFT  = 1
RIGHT = 2
FORE  = 4
AFT   = 8
LOWER = 16
UPPER = 32
SHOULDER = 64

kit = ServoKit(channels = 16)

class Leg:
  def __init__(self, servos):

    self.ForelegServo = next(filter(lambda servo: servo.Position & LOWER, servos), None)
    self.ThighServo = next(filter(lambda servo: servo.Position & UPPER, servos), None)
    self.ShoulderServo = next(filter(lambda servo: servo.Position & SHOULDER, servos), None)

  def Default(self):
    self.ForelegServo.SetValue(.5)
    self.ThighServo.SetValue(.5)
    self.ShoulderServo.SetValue(0)

  def Lift(self):
    self.ForelegServo.SetValue(0.5)
    self.ThighServo.SetValue(0)
    self.ShoulderServo.SetValue(0)

  def Extend(self):
    self.ForelegServo.SetValue(.75)
    self.ThighServo.SetValue(0.5)
    self.ShoulderServo.SetValue(0)

  def Lower(self):
    self.ForelegServo.SetValue(1)
    self.ThighServo.SetValue(1)
    self.ShoulderServo.SetValue(0)    

class FrontLeg(Leg):
  def Salute(self):
    self.ForelegServo.SetValue(1)
    self.ThighServo.SetValue(1)
    self.ShoulderServo.SetValue(1)

class RearLeg(Leg):
  def Lower(self):
    self.ForelegServo.SetValue(0)
    self.ThighServo.SetValue(1)
    self.ShoulderServo.SetValue(0)

class RobotServo:
  def __init__(self, servo, min, max, direction, position):
    self.servo = servo
    self.min = min
    self.max = max
    self.direction = direction
    self.Position = position

  def SetValue(self, value):
    assert(0 <= value <= 1)

    if self.direction > 0:
      self.servo.angle = (self.max - self.min) * value + self.min
    else:
      self.servo.angle = (self.max - self.min) * (1 - value) + self.min

  def Flop(self):
    self.Servo.angle = None

class Robot:
  def __init__(self, servos):
    self.Legs = {
      "LF": FrontLeg([servo for servo in servos if (servo.Position & LEFT) and (servo.Position & FORE)]),
      "RF": FrontLeg([servo for servo in servos if (servo.Position & RIGHT) and (servo.Position & FORE)]),
      "LR": RearLeg([servo for servo in servos if (servo.Position & LEFT) and (servo.Position & AFT)]),
      "RR": RearLeg([servo for servo in servos if (servo.Position & RIGHT) and (servo.Position & AFT)]),
    }

servos = [
  # FORELEG
  RobotServo(kit.servo[4], 0, 180, 1, LEFT | AFT | LOWER),  # LR   (fwd/back)
  RobotServo(kit.servo[5], 0, 180, -1, RIGHT | FORE | LOWER), # RF   (back/fwd)  
  RobotServo(kit.servo[6], 0, 170, -1, RIGHT | AFT | LOWER), # RR   (back/fwd)  
  RobotServo(kit.servo[7], 0, 180, 1, LEFT | FORE | LOWER),  # LF   (fwd/back)
  # THIGH
  RobotServo(kit.servo[8], 0, 140, -1, RIGHT | AFT | UPPER),   # RR   (back/fwd)
  RobotServo(kit.servo[9], 50, 180, -1, RIGHT | FORE | UPPER),  # RF   (back/fwd)
  RobotServo(kit.servo[10], 20, 180, 1, LEFT | AFT | UPPER), # LR   (fwd/back)
  RobotServo(kit.servo[11], 0, 110, 1, LEFT | FORE | UPPER),  # LF   (fwd/back)
  # SHOULDER
  RobotServo(kit.servo[12], 50, 160, 1, RIGHT | AFT | SHOULDER),   # RR     (down/up)
  RobotServo(kit.servo[13], 50, 140, -1, RIGHT | FORE | SHOULDER),  # RF     (up/down)
  RobotServo(kit.servo[14], 15, 105, -1, LEFT | AFT | SHOULDER),  # LR     (up/down)
  RobotServo(kit.servo[15], 45, 125, 1, LEFT | FORE | SHOULDER),   # LF     (down/up)
]

robot = Robot(servos)

# legs["LF"].Default()
# legs["RF"].Default()
# legs["LR"].Default()
# legs["RR"].Default()
# time.sleep(.5)
# legs["LF"].Salute()
# legs["RF"].Salute()
# time.sleep(.5)
# legs["LF"].Default()
# legs["RF"].Default()
# time.sleep(.5)
# legs["LF"].Salute()
# time.sleep(.5)
# legs["RF"].Salute()
# time.sleep(.5)
# legs["LF"].Default()
# legs["RF"].Default()

# time.sleep(.5)
# legs["LR"].Lower()
# legs["RR"].Lower()

robot.Legs["LF"].Default()
time.sleep(.5)
robot.Legs["LF"].Lift()
time.sleep(.5)
robot.Legs["LF"].Extend()
time.sleep(.5)
robot.Legs["LF"].Lower()


