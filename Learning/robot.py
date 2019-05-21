
#Main Robot Imports
import wpilib
import ctre
from wpilib import DoubleSolenoid
from wpilib.interfaces import GenericHID

#Subsystems
from drivetrain import DriveTrain
from extendPiston import extendPiston

#Motor IDs
LEFT_MOTOR1 = 3
LEFT_MOTOR2 = 4

RIGHT_MOTOR1 = 1
RIGHT_MOTOR2 = 2

EXTRA = 5

RIGHT_HAND = GenericHID.Hand.kRight
LEFT_HAND = GenericHID.Hand.kLeft

#Shifter IDs
SHIFTER_EXTEND = 0
SHIFTER_RETRACT = 1

BRAKE_EXTEND = 2
BRAKE_RETRACT = 3


class Robot(wpilib.TimedRobot):

    def robotInit(self):
        self.left_motor1 = ctre.WPI_TalonSRX(LEFT_MOTOR1)
        self.left_motor2 = ctre.WPI_TalonSRX(LEFT_MOTOR2)

        self.left = wpilib.SpeedControllerGroup(self.left_motor1, self.left_motor2)
        
        self.right_motor1 = ctre.WPI_TalonSRX(RIGHT_MOTOR1)
        self.right_motor2 = ctre.WPI_TalonSRX(RIGHT_MOTOR2)
        self.right = wpilib.SpeedControllerGroup(self.right_motor1, self.right_motor2)
        self.drive = wpilib.XboxController(0)

        self.drivetrain = DriveTrain(self.left,self.right, None)
        self.timer = wpilib.Timer()

        self.brake = extendPiston(wpilib.DoubleSolenoid(BRAKE_EXTEND,BRAKE_RETRACT))
        

    def autonomousInit(self):
        self.timer.reset()
        self.timer.start()

    def autonomousPeriodic(self):
        if self.timer.get() < 2.0:
            self.drivetrain.arcade_drive(0.5,0)
        else:
            self.drivetrain.arcade_drive(0,0)

    def teleopInit(self):
        self.forward = 0

    def teleopPeriodic(self):
        self.forward = -self.drive.getY(RIGHT_HAND)
        rotation_value = self.drive.getX(LEFT_HAND)
        if self.drive.getXButton():
            self.drivetrain.stop()
        else:
            self.drivetrain.arcade_drive(self.forward, rotation_value)

        if self.drive.getAButton():
            self.brake.extend()
        else:
            self.brake.retract()




        

if __name__ == '__main__':
    wpilib.run(Robot)