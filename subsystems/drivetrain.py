import wpilib 
import wpilib.drive
from wpilib import DoubleSolenoid

class Drivetrain:
    def __init__(self, left, right, gyro):
        
        self.robot_drive = wpilib.drive.DifferentialDrive(left, right)
        self.gyro = gyro

        self.right = right
        self.left = left

        self.setpoint = 0
        self.P = 1.8
        self.I = 0.0
        self.D = 0
        self.integral = 0
        self.prev_error = 0
        self.rcw = 0

    def setSetPoint(self, setpoint):
        self.setpoint = setpoint

    def PID(self):
        error = self.setpoint - self.gyro.getRate()
        self.integral = self.integral + (error * 0.05)
        derivative = (error -self.prev_error) / 0.05
        self.rcw = self.P * error + self.I * self.integral + self.D * derivative
        self.prev_error = error

    def arcade_drive(self, forward, rotate):
        self.robot_drive.arcadeDrive(forward, rotate)

    def stop(self):
        self.robot_drive.stopMotor()

    def get_encoder_position(self):
        return self.encoder_motor.getQuadraturePosition()

    def updatePID(self):
        self.PID()
        #print("Correction: ", self.rcw, " | Setpoint:", self.setpoint, " | Gyro", self.gyro.getRate())
