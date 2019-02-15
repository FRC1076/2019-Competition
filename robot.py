#GENERAL PYTHON
import math

#GENERAL ROBOT
import ctre 
import wpilib
from wpilib import DoubleSolenoid
from wpilib.interfaces import GenericHID
try:
    from navx import AHRS
    MISSING_NAVX = False
except ModuleNotFoundError as e:
    print("Missing navx.  Carry on!")
    MISSING_NAVX = True
    
try:
    from hal_impl.data import hal_data
    MISSING_HAL = False
except ModuleNotFoundError as e:
    print("Missing hal_data. Ignore.")
    MISSING_HAL = True

#OUR ROBOT SYSTEMS AND LIBRARIES
from subsystems.drivetrain import Drivetrain
from subsystems.elevator import Elevator, ElevatorAttendant, ElevatorController
from subsystems.hatchGrabber import Grabber
from subsystems.lift import Lift
from subsystems.extendPiston import extendPiston
from subsystems.ballManipulator import BallManipulator, BallManipulatorController

LEFT_CONTROLLER_HAND = wpilib.interfaces.GenericHID.Hand.kLeft
RIGHT_CONTROLLER_HAND = wpilib.interfaces.GenericHID.Hand.kRight

#PCM CAN IDs
PCM_CAN_ID = 0

#DRIVETRAIN IDs (talon and victor)
LEFT_MASTER_ID = 1
LEFT_SLAVE_1_ID = 2
LEFT_SLAVE_2_ID = 10

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
        self.gyro = wpilib.AnalogGyro(1)

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
                wpilib.DoubleSolenoid(CENTER_EXTEND_ID, CENTER_RETRACT_ID), 
                wpilib.DoubleSolenoid(BACK_EXTEND_ID, BACK_RETRACT_ID)
        )
        
        #ELEVATOR
        elevator_motor = createTalonAndSlaves(ELEVATOR_ID_MASTER, ELEVATOR_ID_SLAVE)
        self.elevator = Elevator(elevator_motor, encoder_motor=elevator_motor)
        #.WPI_TalonSRX
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

        goal_forward = self.driver.getRawAxis(5)
        #RAW AXIS 5 ON PRACTICE BOARD
        rotation_value = -self.driver.getX(LEFT_CONTROLLER_HAND)

        goal_forward = deadzone(goal_forward, deadzone_value) * max_forward
        rotation_value = deadzone(rotation_value, deadzone_value) * max_rotate

        # delta = goal_forward - self.forward

        # if abs(delta) < max_accel:
        #     self.forward += delta
        # else:
        #     self.forward += max_accel * sign(delta)

        self.drivetrain.arcade_drive(goal_forward, rotation_value)

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
        else:
            self.elevatorAttendant.stop()
            self.elevator.set(setPoint)
            



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
    slave_talon.follow(master_talon)
    
    # if slave2 is not None:
    slave_victor = ctre.victorspx.VictorSPX(slave2)
    slave_victor.set(ControlMode.Follower, MASTER)
    slave_victor.follow(master_talon)
    return master_talon

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

