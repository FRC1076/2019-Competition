import math
import wpilib
import ctre 
import robotpy_ext.common_drivers.navx as navx
from subsystems.drivetrain import Drivetrain
from subsystems.elevator import elevator
from subsystems.hatchGrabber import Grabber
from wpilib import DoubleSolenoid, SmartDashboard
from wpilib.interfaces import GenericHID
#import wpilib.interfaces from GenericHID
#LEFT = wpilib.interfaces.GenericHID.Hand.kLeft
RIGHT = wpilib.interfaces.GenericHID.Hand.kRight
#LEFT = GenericHID.Hand.kLeft
#RIGHT = GenericHID.Hand.kRight
print("main")

class MyRobot(wpilib.IterativeRobot):
    def robotInit(self):
        print("RobotInit")
        #assigns driver as controller 0 and operator as controller 1
        self.driver = wpilib.XboxController(0)
        self.operator = wpilib.XboxController(1)

    def robotPeriodic(self):
        pass

    def teleopInit(self):
        pass

    def teleopPeriodic(self):
        #Arcade Controls

        DEADZONE = 0.2
        MAX_ACCELERATION = 0.3

        #goal_forward = -self.driver.getY(RIGHT)
        #goal_rotate = self.driver.getX(LEFT)

        MAX_FORWARD = 1.0
        MAX_ROTATE = 1.0

        goal_forward = deadzone(goal_forward * MAX_ROTATE, DEADZONE)

        delta = goal_forward - self.forward

        if abs(delta) < MAX_ACCELERATION:
            self.forward += delta
        else:
            self.forward += MAX_ACCELERATION

#prevents slight movements of triggers from moving robot
def deadzone(val, deadzone):
    if abs(val) < deadzone:
        return 0
    return val

if __name__ == "__main__":
    wpilib.run(MyRobot)
