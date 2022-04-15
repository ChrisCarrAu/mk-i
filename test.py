import time
from adafruit_servokit import ServoKit

class Leg:
  def __init__(self, ForelegServoId, ThighServoId, ShoulderServoId):
    self.ForelegServoId = ForelegServoId
    self.ThighServoId = ThighServoId
    self.ShoulderServoId = ShoulderServoId

# class Robot:
#   def __init__(self)
#     self.Legs = 




kit = ServoKit(channels = 16)

# Unused
kit.servo[0].angle=None
kit.servo[1].angle=None
kit.servo[2].angle=None
kit.servo[3].angle=None

# Forelegs
kit.servo[4].angle=90    # LR    0 .. 180   (fwd/back)
kit.servo[5].angle=90    # RF    0 .. 180   (back/fwd)  
kit.servo[6].angle=90    # RR    0 .. 170   (back/fwd)  
kit.servo[7].angle=90    # LF    0 .. 180   (fwd/back)

# Thighs
kit.servo[8].angle=70    # RR    0 .. 140  (back/fwd)
kit.servo[9].angle=75    # RF    50 .. 180 (back/fwd)
kit.servo[10].angle=100  # LR    20 .. 180 (fwd/back)
kit.servo[11].angle=80   # LF    0 .. 110  (fwd/back)

# Shoulder
kit.servo[12].angle=50   # RR    50 .. 160 (down/up)
kit.servo[13].angle=140  # RF   50 .. 140  (up/down)
kit.servo[14].angle=105  # LR    15 .. 105   (up/down)
kit.servo[15].angle=45   # LF     45 .. 125 (down/up)
leg_angle = 150
shoulder_angle = 90
# # FLU
# kit.servo[0].angle = leg_angle
# # FLL
# kit.servo[1].angle = leg_angle
# # FLS
# kit.servo[2].angle = leg_angle

# # RLL
# kit.servo[3].angle = leg_angle
# RLU
#kit.servo[4].actuation_range = 0
#kit.servo[4].set_pulse_width_range(1000, 2000)
# kit.servo[4].angle = 0
# RLS
#kit.servo[5].actuation_range = 180
#kit.servo[5].set_pulse_width_range(1000, 2000)
# kit.servo[5].angle = 180


# for servo in range (4, 8) :
#   kit.servo[servo].angle =  90
# for servo in range (8, 12) :
#   kit.servo[servo].angle =  45
# for servo in range (12, 14) :
#   kit.servo[servo].angle =  90
# for servo in range (14, 16) :
#   kit.servo[servo].angle =  90

# for count in range(0, 2):
#   for servo in range (10, 12) :
#     kit.servo[servo].angle =  0
#     time.sleep(0.5)
#   for servo in range(11, 9, -1) :
#     kit.servo[servo].angle = 180
#     time.sleep(0.5)

# for servo in range (0, 12) :
#   kit.servo[servo].angle =  90
