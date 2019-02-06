#GENERAL PYTHON
import math

#GENERAL ROBOT
import ctre 
import wpilib
from wpilib import DoubleSolenoid
from wpilib.interfaces import GenericHID
from navx import AHRS
from hal_impl.data import hal_data

#OUR ROBOT SYSTEMS AND LIBRARIES
from subsystems.drivetrain import Drivetrain
from subsystems.elevator import Elevator
from subsystems.hatchGrabber import Grabber
from subsystems.lift import Lift
from subsystems.extendPiston import extendPiston
from subsystems.ballManipulator import BallManipulator, BallManipulatorController

LEFT_CONTROLLER_HAND = wpilib.interfaces.GenericHID.Hand.kLeft
RIGHT_CONTROLLER_HAND = wpilib.interfaces.GenericHID.Hand.kRight

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

#HATCH GRABBER PISTON IDs (solenoid)
PISTON_EXTEND_ID = 4
PISTON_RETRACT_ID = 5

RETRACT_ID = 6
EXTEND_ID = 7

#ELEVATOR PID IDs
MIN_ELEVATOR_RANGE = 0
MAX_ELEVATOR_RANGE = 200

#ELEVATOR STOPS
LOW_HATCH_VALUE = 0
LOW_CARGO_VALUE = 500
MEDIUM_HATCH_VALUE = 1000
MEDIUM_CARGO_VALUE = 1500
HIGH_HATCH_VALUE = 2000
HIGH_CARGO_VALUE = 2500

class MyRobot(wpilib.TimedRobot):
    def robotInit(self):
        #assigns driver as controller 0 and operator as controller 1
        self.driver = wpilib.XboxController(0)
        self.operator = wpilib.XboxController(1)
        self.elevatorController = ElevatorController(self.operator, self.logger)

        #GYRO
        self.gyro = wpilib.AnalogGyro(1)

        #DRIVETRAIN
        left = createMasterAndSlaves(LEFT_MASTER_ID, LEFT_SLAVE_1_ID, LEFT_SLAVE_2_ID)
        right = createMasterAndSlaves(RIGHT_MASTER_ID, RIGHT_SLAVE_1_ID, RIGHT_SLAVE_2_ID)
        self.drivetrain = Drivetrain(left, right, self.gyro)

        #HATCH GRABBER
        self.grabber = Grabber(
            hatch = wpilib.DoubleSolenoid(5, EXTEND_ID, RETRACT_ID))

        #ball manipulator and controller
        self.ballManipulator = BallManipulator(ctre.WPI_TalonSRX(BALL_MANIP_ID))
        self.ballManipulatorController = BallManipulatorController(self.operator, self.logger)

        #EXTEND HATCH GRABBER 
        self.piston = extendPiston(piston=wpilib.DoubleSolenoid(4, PISTON_EXTEND_ID, PISTON_RETRACT_ID))

        #LIFT
        '''
        The lift is being controlled by four pistons, but two doublesolenoids due to electrical chaining 4 together to make
        space on the solenoid module.
        '''
        self.lift = Lift(
                wpilib.DoubleSolenoid(CENTER_EXTEND_ID, CENTER_RETRACT_ID), 
                wpilib.DoubleSolenoid(BACK_EXTEND_ID, BACK_RETRACT_ID)
        )
        
        #ELEVATOR
        elevator_motor = ctre.WPI_TalonSRX(ELEVATOR_ID_MASTER)
        self.elevator = Elevator(elevator_motor, encoder_motor=elevator_motor)
       
        #self.ahrs = AHRS.create_spi()
        self.encoder = FakeEncoder()
        self.elevatorAttendant = ElevatorAttendant(self.encoder, 0, 100, -1, 1)


    def robotPeriodic(self):
        pass

    def teleopInit(self):
        """Executed at the start of teleop mode"""
        self.pistons_activated = False
        self.forward = 0

    def teleopPeriodic(self):
        #ARCADE DRIVE CONTROL
        deadzone_value = 0.2
        max_accel = 0.3
        max_forward = 1.0
        max_rotate = 1.0

        goal_forward = self.driver.getRawAxis(3)
        rotation_value = -self.driver.getX(LEFT_CONTROLLER_HAND)

        goal_forward = deadzone(goal_forward * max_forward, deadzone_value)
        rotation_value = deadzone(rotation_value * max_rotate, deadzone_value)

        delta = goal_forward - self.forward

        if abs(delta) < max_accel:
            self.forward += delta
        else:
            self.forward += max_accel * sign(delta)

        self.drivetrain.arcade_drive(self.forward, rotation_value)

        #4BAR CONTROL
        '''
        Left bumper = retract intake (piston in)
        Right bumper = extend intake beyond frame perimeter (piston out)
        '''
        if self.driver.getBumper(LEFT_CONTROLLER_HAND):
            self.piston.extend()
        elif self.driver.getBumper(RIGHT_CONTROLLER_HAND):
            self.piston.retract()

        #DRIVER TEMPORARY ELEVATOR CONTROL 
        '''
        Left trigger is go up, Right trigger is go down 
        '''
        left_trigger = self.driver.getTriggerAxis(LEFT_CONTROLLER_HAND)
        right_trigger = self.driver.getTriggerAxis(RIGHT_CONTROLLER_HAND)

        TRIGGER_LEVEL = 0.4

        if abs(left_trigger) > TRIGGER_LEVEL:
            self.elevator.go_up(left_trigger)
        elif abs(right_trigger) > TRIGGER_LEVEL:
            self.elevator.go_down(right_trigger)
        else:
            self.elevator.stop()

        #ELEVATOR CONTROL
        (elevateToHeight, setPoint) = self.elevatorController.getOperation()
        if elevateToHeight:
            self.elevatorAttendant.setSetpoint(setPoint)

        # Ball manipulator control
        ballMotorSetPoint = self.ballManipulatorController.getSetPoint()
        self.ballManipulator.set(ballMotorSetPoint)
        
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

        #END GAME 

        activate_pistons = self.operator.getStartButton() and self.driver.getStartButton()
        release_pistons = self.operator.getBackButton() and self.driver.getStartButton()

        if activate_pistons:
            self.lift.raise_all()
        if release_pistons:
            self.lift.lower_all()

def createMasterAndSlaves(MASTER, slave1, slave2):
    '''
    First ID must be MASTER, Second ID must be slave TALON, Third ID must be slave VICTOR
    This assumes that the left and right sides are the same, two talons and one victor. A talon must be the master.
    '''
    master_talon = ctre.WPI_TalonSRX(MASTER)

    slave_talon = ctre.WPI_TalonSRX(slave1)
    slave_victor = ctre.victorspx.VictorSPX(slave2)

    slave_talon.follow(master_talon)
    slave_victor.follow(master_talon)

    return master_talon

class ElevatorAttendant:
    def __init__(self, encoder, lowInput, highInput, lowOutput, highOutput):
        self.encoder = encoder

        kP = 0.01
        kI = 0.00
        kD = 0.00
        self.pid = wpilib.PIDController(kP, kI, kD, source=encoder, output=self)
        self.pid.setInputRange(lowInput, highInput)
        self.pid.setOutputRange(lowOutput, highOutput)

    def pidWrite(self, output):
        self.elevateToHeightRate = output
    
    def getHeightRate(self):
        return self.elevateToHeightRate

    def move(self):
        self.pid.enable()
    
    def stop(self):
        self.pid.disable()

    def setSetpoint(self, height):
        self.pid.setSetpoint(height)

class FakeEncoder:
    def pidGet(self):
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

class ElevatorController:

    def __init__(self, controller, logger = None):
        self.controller = controller
        self.logger = logger

    def getOperation(self):
        whammyBarPressed = (self.controller.getTriggerAxis(LEFT_CONTROLLER_HAND) > -0.9 and not (self.controller.getTriggerAxis(LEFT_CONTROLLER_HAND) == 0))
        if self.logger is not None:
            if whammyBarPressed:
                self.logger.info("whammy bar has been pressed")
        if self.controller.getAButton():
            if whammyBarPressed:
                setPoint = LOW_CARGO_VALUE
            else:
                setPoint = LOW_HATCH_VALUE
            if self.logger is not None:
                self.logger.info("button A has been pressed")
            runElevator = True

        elif self.controller.getBButton():
            if whammyBarPressed:
                setPoint = MEDIUM_CARGO_VALUE
            else:
                setPoint = MEDIUM_HATCH_VALUE
            runElevator = True

        elif self.controller.getXButton():
            if whammyBarPressed:
                setPoint = HIGH_CARGO_VALUE
            else:
                setPoint = HIGH_HATCH_VALUE
            runElevator = True
        
        else:
            setPoint = 0
            runElevator = False
        
        return (runElevator, setPoint)

if __name__ == "__main__":
    wpilib.run(MyRobot)