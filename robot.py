import math
import wpilib
# import ctre 
from subsystems.drivetrain import Drivetrain
# from subsystems.elevator import Elevator
#from subsystems.hatchGrabber import Grabber
#from wpilib import DoubleSolenoid, SmartDashboard
#from wpilib.interfaces import GenericHID
#import wpilib.interfaces from GenericHID
LEFT = wpilib.interfaces.GenericHID.Hand.kLeft
RIGHT = wpilib.interfaces.GenericHID.Hand.kRight

class MyRobot(wpilib.TimedRobot):
    def robotInit(self):
        #assigns driver as controller 0 and operator as controller 1
        self.driver = wpilib.XboxController(0)
        self.operator = wpilib.XboxController(1)
        self.gyro = wpilib.AnalogGyro(1)
        LeftFront = wpilib.Talon(1)
        LeftFront.setInverted(1)
        self.leftGroup = wpilib.SpeedControllerGroup(LeftFront, wpilib.Talon(2), wpilib.Talon(3))
        self.rightGroup = wpilib.SpeedControllerGroup(wpilib.Talon(4), wpilib.Talon(5), wpilib.Talon(6))
        self.robot_drive = Drivetrain(self.leftGroup, self.rightGroup, wpilib.interfaces.Gyro())

    def robotPeriodic(self):
        pass

    def teleopInit(self):
        """Executed at the start of teleop mode"""
        pass

    def teleopPeriodic(self):
        self.robot_drive.arcade_drive(-self.driver.getX(LEFT), -self.driver.getRawAxis(3))
        return;

if __name__ == "__main__":
    wpilib.run(MyRobot)