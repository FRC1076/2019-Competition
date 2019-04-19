#GENERAL PYTHON
import math
import time

#GENERAL ROBOT
import ctre 
import wpilib
from wpilib import Ultrasonic
from wpilib import DoubleSolenoid
from navx import AHRS
from wpilib.interfaces import GenericHID
# try:
#     from navx import AHRS
#     MISSING_NAVX = False
# except ModuleNotFoundError as e:
#     print("Missing navx.  Carry on!")
#     MISSING_NAVX = True
    
try:
    from hal_impl.data import hal_data
    MISSING_HAL = False
except ModuleNotFoundError as e:
    print("Missing hal_data. Ignore.")
    MISSING_HAL = True

import robotpy_ext.common_drivers

#OUR ROBOT SYSTEMS AND LIBRARIES
from subsystems.drivetrain import Drivetrain
from subsystems.elevator import Elevator, ElevatorAttendant, ElevatorController
from subsystems.hatchGrabber import Grabber
from subsystems.lift import Lift
from subsystems.extendPiston import extendPiston
from subsystems.ballManipulator import BallManipulator, BallManipulatorController
from subsystems.continuousServo import ContinuousRotationServo
from subsystems.continuousServo import ContinuousRotationServoWithFeedback
from subsystems.climber import Climber
from subsystems.sonarSensor import SonarSensor
from subsystems.visionSensor import VisionSensor

LEFT_CONTROLLER_HAND = wpilib.interfaces.GenericHID.Hand.kLeft
RIGHT_CONTROLLER_HAND = wpilib.interfaces.GenericHID.Hand.kRight

#PCM CAN IDs
PCM_CAN_ID = 0

#DRIVETRAIN IDs (talon and victor)
LEFT_MASTER_ID = 1
LEFT_SLAVE_1_ID = 2
LEFT_SLAVE_2_ID = 3

RIGHT_MASTER_ID = 4
RIGHT_SLAVE_1_ID = 5
RIGHT_SLAVE_2_ID = 6

#ELEVATOR ID (talon)
ELEVATOR_ID_MASTER = 7
ELEVATOR_ID_SLAVE = 8

#BALL MANIPULATOR IDs (talon)
BALL_MANIP_ID = 9

#LIFT PISTON IDs (solenoid)
CENTER_EXTEND_ID = 0
CENTER_RETRACT_ID = 1

BACK_EXTEND_ID = 2
BACK_RETRACT_ID = 3

#4bar (solenoid)
PISTON_EXTEND_ID = 4
PISTON_RETRACT_ID = 5

#hatch 
RETRACT_ID = 6
EXTEND_ID = 7

#servo
SERVO0_CHANNEL = 0 
SERVO1_CHANNEL = 1 
SERVO2_CHANNEL = 2 
SERVO3_CHANNEL = 3 


# down sonar PIN numbers
DOWN_SONAR_TRIGGER_PIN = 4
DOWN_SONAR_ECHO_PIN = 5

'''
Raw Axes
0 L X Axis
1 L Y Axis
2 L Trigger
3 R Trigger
4 R X Axis
5 R Y Axis
'''

class MyRobot(wpilib.TimedRobot):
    def robotInit(self):
        #assigns driver as controller 0 and operator as controller 1
        self.driver = wpilib.XboxController(0)
        self.operator = wpilib.XboxController(1)
        self.elevatorController = ElevatorController(self.operator, self.logger)

        #GYRO
        self.gyro = AHRS.create_spi()

        #DRIVETRAIN
        left = createTalonAndSlaves(LEFT_MASTER_ID, LEFT_SLAVE_1_ID, LEFT_SLAVE_2_ID)
        right = createTalonAndSlaves(RIGHT_MASTER_ID, RIGHT_SLAVE_1_ID, RIGHT_SLAVE_2_ID)
        self.drivetrain = Drivetrain(left, right, self.gyro)

        #HATCH GRABBER
        self.grabber = Grabber(
            hatch = wpilib.DoubleSolenoid(PCM_CAN_ID, EXTEND_ID, RETRACT_ID))

        #ball manipulator and controller
        self.ballManipulator = BallManipulator(ctre.WPI_TalonSRX(BALL_MANIP_ID))
        self.ballManipulatorController = BallManipulatorController(self.operator, self.logger)

        #EXTEND HATCH GRABBER 
        self.piston = extendPiston(piston=wpilib.DoubleSolenoid(PCM_CAN_ID, PISTON_EXTEND_ID, PISTON_RETRACT_ID))

        #LIFT
        '''
        The lift is being controlled by four pistons, but two doublesolenoids due to electrical chaining 4 together to make
        space on the solenoid module.
        '''
        self.lift = Lift(
                wpilib.DoubleSolenoid(PCM_CAN_ID, CENTER_EXTEND_ID, CENTER_RETRACT_ID), 
                wpilib.DoubleSolenoid(PCM_CAN_ID, BACK_EXTEND_ID, BACK_RETRACT_ID)
        )
        
        #ELEVATOR
        elevator_motor = createTalonAndSlaves(ELEVATOR_ID_MASTER, ELEVATOR_ID_SLAVE)
        #elevator_motor = ctre.WPI_TalonSRX(ELEVATOR_ID_MASTER)
        self.elevator = Elevator(elevator_motor, encoder_motor=elevator_motor)
        #.WPI_TalonSRX
        #self.ahrs = AHRS.create_spi()
        # down-facing sonar unit
        self.downSonar = wpilib.Ultrasonic(DOWN_SONAR_TRIGGER_PIN, DOWN_SONAR_ECHO_PIN, Ultrasonic.Unit.kMillimeters)
        self.downSonar.setPIDSourceType(wpilib.interfaces.pidsource.PIDSource.PIDSourceType.kDisplacement)
        self.downSonar.setEnabled(True)
        self.elevatorAttendant = ElevatorAttendant(self.downSonar, 0, 2000, -1, 1)

        # remote sensors
        #Vision sensor
        self.visionSensor = VisionSensor('10.10.76.13', 5880, logger=self.logger)
        #SERVO
        self.servo0 = ContinuousRotationServo(SERVO0_CHANNEL)
        self.servo1 = ContinuousRotationServo(SERVO1_CHANNEL)
        self.servo2 = ContinuousRotationServo(SERVO2_CHANNEL)
        self.servo3 = ContinuousRotationServo(SERVO3_CHANNEL)
        #self.servo2 = ContinuousRotationServoWithFeedback(7, 3)
        
        self.climber = Climber(self.gyro, self.servo0, self.servo1, self.servo2, self.servo3)

        self.timer = 0

        #Sonar sensor
        #self.sonarSensor = SonarSensor('10.10.76.11', 5811, logger=self.logger)

        # Elevator height sonar sensor
        self.elevatorHeightSensor = SonarSensor('10.10.76.11', 5811, logger=self.logger)
        self.elevatorAttendant = ElevatorAttendant(self.elevatorHeightSensor, 0, 200, -0.5, 1.0)

        #self.visionAttendant = VisionAttendant(self.visionSensor)

        self.autoBalancing = False

        #self.pdp_small = wpilib.pdb
    def robotPeriodic(self):
        # if self.timer % 50 == 0:
        #     print("NavX Gyro Roll", self.gyro.getRoll())
        self.timer += 1

    def teleopInit(self):
        """Executed at the start of teleop mode"""
        self.forward = 0
        self.downSonar.ping()
        
        self.climber.reset()
        
    def teleopPeriodic(self):

        print("NavX Gyro Roll, ", self.gyro.getRoll(), "NavXX Gyro Pitch", self.gyro.getPitch())
        

        #ARCADE DRIVE CONTROL
        deadzone_value = 0.2
        max_accel = 0.15
        max_forward = 1.0
        max_rotate = 1.0

        goal_forward = -self.driver.getRawAxis(5)
        #RAW AXIS 5 ON PRACTICE BOARD
        rotation_value = self.driver.getX(LEFT_CONTROLLER_HAND)
        
        goal_forward = deadzone(goal_forward, deadzone_value) * max_forward

        # # manual and autonomous driving will go here
        # if self.driver.getBButton():
        #     self.logger.info("Button B pressed, turn to target!")
        #     self.visionAttendant.setSetpoint(0)
        #     self.visionAttendant.move()
        #     # if we are auton turning, we can override value with pid
        #     rotation_value = self.visionAttendant.getTurnRate()
        # else:
        #     self.visionAttendant.stop()
        #     rotation_value = deadzone(rotation_value, deadzone_value) * max_rotate
            
        # if self.driver.getTriggerAxis(RIGHT_CONTROLLER_HAND):
        #     self.drivetrain.arcade_drive((self.forward/2), (rotation_value*0.75))
        # else:
        #     self.drivetrain.arcade_drive(self.forward, rotation_value)

        delta = goal_forward - self.forward

        if abs(delta) < max_accel:
            self.forward += delta
        else:
            self.forward += max_accel * sign(delta)

        #If the driver holds the right trigger down, we will go half speed forward 
        # and backward and 75% speed when turning.
        if self.driver.getTriggerAxis(RIGHT_CONTROLLER_HAND):
            self.drivetrain.arcade_drive((self.forward/2), (rotation_value*0.75))
        else:
           self.drivetrain.arcade_drive(self.forward, rotation_value) 
        # self.drivetrain.arcade_drive(goal_forward, rotation_value)

        #4BAR CONTROL
        '''
        Left bumper = retract intake (piston in)
        Right bumper = extend intake beyond frame perimeter (piston out)

        '''
        if self.driver.getBumper(LEFT_CONTROLLER_HAND):
            self.piston.retract()
        elif self.driver.getBumper(RIGHT_CONTROLLER_HAND):
            self.piston.extend()

        #Hatch grabber default state is open. When the 5th button on the guitar is pressed, the hatch grabber closes.
        if self.operator.getBumper(LEFT_CONTROLLER_HAND):
            self.grabber.extend()
        else:
            self.grabber.retract()

        #DRIVER TEMPORARY ELEVATOR CONTROL 
        '''
        Left trigger is go up, Right trigger is go down 
        '''
        # left_trigger = self.driver.getTriggerAxis(LEFT_CONTROLLER_HAND)
        # right_trigger = self.driver.getTriggerAxis(RIGHT_CONTROLLER_HAND)

        # TRIGGER_LEVEL = 0.5

        # if abs(left_trigger) > TRIGGER_LEVEL:
        #     self.elevator.go_up(self.driver.getTriggerAxis(LEFT_CONTROLLER_HAND))
        # elif abs(right_trigger) > TRIGGER_LEVEL:
        #     self.elevator.go_down(self.driver.getTriggerAxis(RIGHT_CONTROLLER_HAND))
        # else:
        #     self.elevator.stop()
        
        


        #ELEVATOR CONTROL
        (elevateToHeight, setPoint) = self.elevatorController.getOperation()
        if elevateToHeight:
            self.elevatorAttendant.setSetpoint(setPoint)
            self.elevatorAttendant.move()
            self.elevator.set(self.elevatorAttendant.getHeightRate())
            # logging to help figure out what is up...
            heightRate = self.elevatorAttendant.getHeightRate()
            if heightRate != 0:
                self.logger.error("Elevator Height rate %f ", heightRate)
        else:
            self.elevatorAttendant.stop()
            self.elevator.set(setPoint)

        
        # Ball manipulator control
        ballMotorSetPoint = self.ballManipulatorController.getSetPoint()
        self.ballManipulator.set(ballMotorSetPoint)

        # Recieve range from sonarSensor
        self.elevatorHeightSensor.receiveRangeUpdates()

        # Recieve angle and range from visionSensor
        self.visionSensor.receiveAngleUpdates()
        #self.logger.info("Vision bearing %f degrees", self.visionSensor.bearing)
        
        #If proximity sensor = 0
            #self.encoder.reset()

        '''
        Guitar Hero controls
        1: Hatch Panel Low. 1+Wammy: Cargo Low (1, z!=0)
        2: Hatch Panel Middle. 2+wammy: Cargo Middle (2, z!=0)
        3: Hatch Panel High. 3+wammy: Cargo High (4, z!=0)
        (1-3 elevator positions = 2 CIM motors in a toughbox gearbox)
        4: Cargo intake IN. 4+wammy: Cargo intake out (single motor tbd) (3, z!=0)
        5: Hatch Panel grab (piston out). 5+wammy: Hatch Panel release (piston in). (5, z!=0)
        Start: Activate end game with Driver approval (8)
        '''

        # SONAR
        # if self.downSonar.isRangeValid():
        #     self.logger.info("Sonar returns %f", self.downSonar.pidGet())
        #     self.logger.info("Sonar inches %d", self.downSonar.getRangeInches())
        #     self.downSonar.ping()

        #END GAME 
        whammyAxis = self.operator.getRawAxis(4)
        whammy_down = (whammyAxis > -0.7 and not (whammyAxis == 0))

        driver_activate = self.driver.getYButton() and self.driver.getBButton()
        #driver_activate_center = self.driver.getBButton() and self.driver.getStartButton()

        activate_pistons = driver_activate and whammy_down
        release_back_pistons = self.driver.getBackButton() 
        release_center_pistons = self.driver.getStartButton()

        #The front (center) pistons will fire 0.25 seconds after the back pistons have been fired.
        if activate_pistons:
            #self.autoBalancing = True
            self.lift.raise_all()
            self.logger.info("Raising all!")
        else:
            if release_center_pistons:
                #self.autoBalancing = False
                self.lift.lower_center()
            elif release_back_pistons:
                #self.autoBalancing = False
                self.lift.lower_back()
            # elif self.operator.getAButton():
            #     self.autoBalancing = False

        # if self.operator.getAButton():
        #     self.autoBalancing = True
        # if self.operator.getAButtonReleased():
        #     self.autoBalancing = False
            
        # if self.autoBalancing == True:
        #     self.climber.balanceMe()
        # if self.autoBalancing == False:
        #     self.climber.stopAll()

        # if self.driver.getXButton():
        #     self.climber.closeAllValves()
        # if self.driver.getAButton():
        #     self.climber.openAllValves()
        # if self.driver.getXButtonReleased():
        #     self.climber.stopAll()
        # if self.driver.getAButtonReleased():
        #     self.climber.stopAll()

    def autonomousInit(self):
        #Because we want to drive during auton, just call the teleopInit() function to 
        #get everything from teleop.
        self.teleopInit()
        print("auton init")

    def autonomousPeriodic(self):
        # self.teleopPeriodic()
        # print("auton periodic")
        if self.driver.getTriggerAxis(LEFT_CONTROLLER_HAND):
            turn_value = -1
        else:
            turn_value = 1

        #If left trigger held, open valves
        if self.driver.getAButton(): 
            self.servo0.turn(turn_value)
        if self.driver.getAButtonReleased():
            self.servo0.stopMotor()

        if self.driver.getXButton():
            self.servo1.turn(turn_value)
        if self.driver.getXButtonReleased():
            self.servo1.stopMotor()

        if self.driver.getYButton():
            self.servo2.turn(turn_value)
        if self.driver.getYButtonReleased():
            self.servo2.stopMotor()

        if self.driver.getBButton():
            self.servo3.turn(turn_value)
        if self.driver.getBButtonReleased():
            self.servo3.stopMotor()
       
        if self.driver.getStartButton():
            self.climber.openAllValves()
        if self.driver.getBackButton():
            self.climber.closeAllValves()

        if self.driver.getStartButtonReleased():
            self.climber.stopAll()
        if self.driver.getBackButtonReleased():
            self.climber.stopAll()



def createTalonAndSlaves(MASTER, slave1, slave2=None):
    '''
    First ID must be MASTER, Second ID must be slave TALON, Third ID must be slave VICTOR
    This assumes that the left and right sides are the same, two talons and one victor. A talon must be the master.
    '''
    master_talon = ctre.WPI_TalonSRX(MASTER)
    slave_talon = ctre.WPI_TalonSRX(slave1)
    slave_talon.follow(master_talon)
    
    if slave2 is not None:
        slave_talon2 = ctre.WPI_TalonSRX(slave2)
        slave_talon2.follow(master_talon)
    return master_talon
    
class VisionAttendant:
    def __init__(self, vision_sensor):
        self.vision_sensor = vision_sensor
        self.turnRate = 0

        kP = 0.1
        kI = 0.00
        kD = 0.00
        self.pid = wpilib.PIDController(kP, kI, kD, source=vision_sensor, output=self)
        self.pid.setInputRange(-10, 10)
        self.pid.setOutputRange(-.5, .5)

    def pidWrite(self, output):
        self.turnRate = output
    
    def getTurnRate(self):
        """
        I believe the left/right motors are switched
        """
        return -self.turnRate

    def move(self):
        self.pid.enable()
    
    def stop(self):
        self.pid.disable()
        self.turnRate = 0

    def setSetpoint(self, angle):
        self.pid.setSetpoint(angle)


class FakeEncoder:
    def pidGet(self):
        if MISSING_HAL:
            return 0
        else:
            return hal_data['encoder'][0]['value']

    def getPIDSourceType(self):
        return wpilib.interfaces.pidsource.PIDSource.PIDSourceType.kDisplacement

def deadzone(val, deadzone):
    if abs(val) < deadzone:
        return 0
    elif val < (0):
        x = ((abs(val) - deadzone)/(1-deadzone))
        return (-x)
    else:
        x = ((val - deadzone)/(1-deadzone))
        return (x)

def sign(number):
    if number > 0:
        return 1
    else:
        return -1
        
if __name__ == "__main__":
    wpilib.run(MyRobot)

