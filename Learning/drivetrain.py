import wpilib
import wpilib.drive
from wpilib import DoubleSolenoid

class DriveTrain():

    LOW_GEAR = DoubleSolenoid.Value.kForward
    HIGH_GEAR = DoubleSolenoid.Value.kReverse

    def __init__(self, left, right, gear_shifter):
        
        self.robot_drive = wpilib.drive.DifferentialDrive(left, right)
        self.gear_shifter = gear_shifter
    def stop(self):
        self.robot_drive.stopMotor()

    def arcade_drive(self, forward, rotate):
        self.robot_drive.arcadeDrive(forward, rotate)

    def shift_low(self):
        self.gear_shifter.set(DriveTrain.LOW_GEAR)

    def shift_high(self):
        self.gear_shifter.set(DriveTrain.HIGH_GEAR)
