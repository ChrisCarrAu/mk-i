# ROBOT - Mk I

My first robot - designed, printed and assembled from scratch.

Technology & Hardware used

| Name | Description |
| :--- | :---        |
| Printer | Flashforge Adventurer 3 |
| Servos | SG90 9g TowerPro servos x 12 |
| Controller | Raspberry Pi 3B |
| PWM splitter | Adafruit 16-Channel 12-bit PWM/Servo Driver - I2C interface |
| Language | Python |

Robot, Servo, Leg definitions are in main.py

# 2-D Inverse Kinematics

Inverse kinematics is used to calculate the number of degrees to rotate the leg servos in order to place the foot in a location defined by cartesian co-ordinates (x,y,z)

For this robot, the x-axis is parallel to the body (from back to front on a flat plane), the y-axis is perpendicular to the body and the z-axis is effectively the height of the body from the ground.

Given the pelvis joint position, target foot position in 2-D space, and length of the upper leg and lower leg, we can solve the angle α using the law of cosines. Then, we can calculate the vector PK' by rotating the vector PT with angle α. Hence angle δ can be calculated with the dot product between the vector PK and vector PK'.

The dimensions used in this robot are as follows:

| Joint | Constant | Length (mm) |
| :---  | :---     |        ---: |
| Shoulder | ARM_A | 43.0 |
| Thigh | ARM_B | 43.0 |
| Foreleg | ARM_C | 54.8 |


```
           (Z)   (Y)           (Z)   (Y)
            |    /              |    /
            |   /               |   /
            |  /                |  /
  left      | /                 | /  right
<-shoulder  |/      (body)      |/ shoulder->
-----------(*)-----------------(*)---------- (X)
           /|                  /|
          / |                 / |
         /  |                /  |
        /   |               /   |
       /    |              /    |
 ```

 For 2-D motion, the shoulder is assumed to be resting in a horizontal position (0), so we are only interested in the Y and Z axes (+/-43.0, y, z)
 
 Each leg has an independant position - y and z are equivant, however left legs have negative z-axis positioning whereas the right legs have positive z-axis positioning.
