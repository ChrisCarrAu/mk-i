import time
from adafruit_servokit import ServoKit

kit = ServoKit(channels = 16)

kit.servo[0].angle=None
kit.servo[1].angle=None
kit.servo[2].angle=None
kit.servo[3].angle=None

#forelegs
kit.servo[4].angle=None    # LR
kit.servo[5].angle=None   # RF
kit.servo[6].angle=None   # RR    
kit.servo[7].angle=None   # RF

#thighs
kit.servo[8].angle=None   # RR
kit.servo[9].angle=None   # RF
kit.servo[10].angle=None  # LR
kit.servo[11].angle=None  # LF

#shoulder
kit.servo[12].angle=None # RR
kit.servo[13].angle=None  # RF
kit.servo[14].angle=None  # LR
kit.servo[15].angle=None # LF
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
