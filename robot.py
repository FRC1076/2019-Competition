import wpilib
import ctre 
import robotpy_ext.common_drivers.navx as navx
from subsystems.drivetrain import Drivetrain
from subsystems.elevator import elevator
from subsystems.hatchGrabber import Grabber
from wpilib import DoubleSolenoid, SmartDashboard
from wpilib.interfaces import GenericHID

LEFT = GenericHID.Hand.kLeft
RIGHT = GenericHID.Hand.kRight

class Robot(wpilib.IterativeRobot):
    def robotInit(self):
        #assigns driver as controller 0 and operator as controller 1

        self.driver = wpilib.XboxController(0)
        self.operator = wpilib.XboxController(1)

    def robotPeriodic(self):

    def teleopInit(self):

    def teleopPeriodic(self):
        #Arcade Controls

        DEADZONE = 0.2
        MAX_ACCELERATION = 0.3

        goal_forward = -self.driver.getY(RIGHT)
        goal_rotate = self.driver.getX(LEFT)

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