import math
import wpilib 
import wpilib.drive
from wpilib import DoubleSolenoid
from navx import AHRS

LEFT_CONTROLLER_HAND = wpilib.interfaces.GenericHID.Hand.kLeft
RIGHT_CONTROLLER_HAND = wpilib.interfaces.GenericHID.Hand.kRight

class Drivetrain:
    def __init__(self, left, right, gyro):
        
        self.robot_drive = wpilib.drive.DifferentialDrive(left, right)
        self.gyro = gyro

        self.right = right
        self.left = left
        self.encoder_motor = left    # pick one

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
        
class DriverAttendant:
    def __init__(self, gyro, lowInput, highInput, lowOutput, highOutput):
        self.gyro = gyro
        self.turnCorrectionRate = 0

        kP = 0.01
        kI = 0.00
        kD = 0.00
        self.pid = wpilib.PIDController(kP, kI, kD, self.gyro, output=self)
        self.pid.setInputRange(lowInput, highInput)
        self.pid.setOutputRange(lowOutput, highOutput)
        

    def pidWrite(self, output):
        self.turnCorrectionRate = output
    
    def getTurnRate(self):
        return self.turnCorrectionRate

    def move(self):
        self.pid.enable()
    
    def stop(self):
        self.pid.disable()
        self.turnCorrectionRate = 0

    def setSetpoint(self, height):
        self.pid.setSetpoint(height)

class DriverController:
    def __init__(self, controller, logger = None):
        deadzone_value = 0.15
        self.driver = wpilib.XboxController(0)
        self.gyro = AHRS.create_usb()
        
        self.controller = controller
        self.logger = logger
        self.damper = 0
        self.last_rotation_value = deadzone(self.driver.getX(LEFT_CONTROLLER_HAND), deadzone_value)

    def getOperation(self):
        self.damper += 1
        deadzone_value = 0.15
        

        rotation_value = self.driver.getX(LEFT_CONTROLLER_HAND)
        rotation_value = deadzone(rotation_value, deadzone_value)
        
        if self.logger is not None:
            if (self.damper % 50) == 0:
                self.logger.info("getRawAxis (Driver) Rotation value = %f", rotation_value)

        runDrivetrain = False

        if rotation_value == 0:
            runDrivetrain = True
            if self.driver.getAButtonPressed():
                self.gyro.reset()
            if self.driver.getAButton():
                setPoint = 90
            if self.last_rotation_value != 0:
                self.gyro.reset()
                setPoint = 0
        else:
            setPoint = rotation_value

        self.last_rotation_value = rotation_value

        return(runDrivetrain, setPoint)
        
def deadzone(val, deadzone):
    if abs(val) < deadzone:
        return 0
    elif val < (0):
        x = ((abs(val) - deadzone)/(1-deadzone))
        return (-x)
    else:
        x = ((val - deadzone)/(1-deadzone))
        return (x)

