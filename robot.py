import math
import time
import wpilib
import ctre 
from subsystems.drivetrain import Drivetrain
from subsystems.elevator import Elevator
from subsystems.hatchGrabber import Grabber
from subsystems.lift import Lift
from subsystems.extendPiston import extendPiston
from wpilib import DoubleSolenoid
from wpilib.interfaces import GenericHID
from navx import AHRS
from hal_impl.data import hal_data

LEFT = wpilib.interfaces.GenericHID.Hand.kLeft
RIGHT = wpilib.interfaces.GenericHID.Hand.kRight

#DRIVETRAIN IDs (talon and victor)
LEFT_MASTER_ID = 1
LEFT_SLAVE_1_ID = 2
LEFT_SLAVE_2_ID = 3

RIGHT_MASTER_ID = 4
RIGHT_SLAVE_1_ID = 5
RIGHT_SLAVE_2_ID = 6

#HATCH GRABBER PISTON IDs (solenoid)
RETRACT_ID = 0
EXTEND_ID = 1

PISTON_EXTEND_ID = 2
PISTON_RETRACT_ID = 3
'''
Pneumatics: (contract, extend)
            1,2:     Hatchgrabber
            3,4:     Deploy Intake forward 
            5,6:     LeftFront piston
            7,8:     RightFront piston
            9,10:    RightRear piston
            11,12:   LeftRear piston
            '''
#LIFT PISTON IDs (solenoid)
FRONT_LEFT_RETRACT = 0
FRONT_LEFT_EXTEND = 1

FRONT_RIGHT_RETRACT = 2
FRONT_RIGHT_EXTEND = 3

BACK_LEFT_RETRACT = 4
BACK_LEFT_EXTEND = 5

BACK_RIGHT_RETRACT = 6
BACK_RIGHT_EXTEND = 7


#ELEVATOR ID (talon)
ELEVATOR_ID_MASTER = 7
ELEVATOR_ID_SLAVE = 8

#ELEVATOR PID IDs
MIN_ELEVATOR_RANGE = 0
MAX_ELEVATOR_RANGE = 200
#Match time for timer

#Teleop duration
TELEOP_DURATION_SECONDS = 10

class MyRobot(wpilib.IterativeRobot):
    def robotInit(self):
        #assigns driver as controller 0 and operator as controller 1
        self.driver = wpilib.XboxController(0)
        self.operator = wpilib.XboxController(1)

        #GYRO
        self.gyro = wpilib.AnalogGyro(1)

        #DRIVETRAIN
        left = createMasterAndSlaves(LEFT_MASTER_ID, LEFT_SLAVE_1_ID, LEFT_SLAVE_2_ID)
        right = createMasterAndSlaves(RIGHT_MASTER_ID, RIGHT_SLAVE_1_ID, RIGHT_SLAVE_2_ID)
        self.drivetrain = Drivetrain(left, right, self.gyro)

        #HATCH GRABBER
        self.grabber = Grabber(
            hatch = wpilib.DoubleSolenoid(1, EXTEND_ID, RETRACT_ID))

        #EXTEND HATCH GRABBER 
        self.piston = extendPiston(piston=wpilib.DoubleSolenoid(1, PISTON_EXTEND_ID, PISTON_RETRACT_ID))

        #LIFT
        self.lift = Lift(
            front_left = wpilib.DoubleSolenoid(0, FRONT_LEFT_EXTEND, FRONT_LEFT_RETRACT),
            front_right = wpilib.DoubleSolenoid(0, FRONT_RIGHT_EXTEND, FRONT_RIGHT_RETRACT),
            back_left = wpilib.DoubleSolenoid(0, BACK_LEFT_EXTEND, BACK_LEFT_RETRACT), 
            back_right = wpilib.DoubleSolenoid(0, BACK_RIGHT_EXTEND, BACK_RIGHT_RETRACT) 
        )
            
        
        #ELEVATOR
        elevator_motor = ctre.WPI_TalonSRX(ELEVATOR_ID_MASTER)
        self.elevator = Elevator(elevator_motor, encoder_motor=elevator_motor)
       
        #ELEVATOR PID
        '''
        

        '''
        self.command = None
        self.ahrs = AHRS.create_spi()
        self.encoder = fakeEncoder()
        
        self.command = elevatorAttendant(self.encoder, 0, 100, -1, 1)


    def robotPeriodic(self):
        pass

    def teleopInit(self):
        """Executed at the start of teleop mode"""
        self.pistons_activated = False
        self.forward = 0
        self.matchtimer = MatchTimer(TELEOP_DURATION_SECONDS)
        
        
            
        
    def teleopPeriodic(self):
        #ARCADE DRIVE CONTROL
        deadzone_value = 0.2
        max_accel = 0.3
        max_forward = 1.0
        max_rotate = 1.0


        goal_forward = self.driver.getRawAxis(3)
        rotation_value = -self.driver.getX(LEFT)

        goal_forward = deadzone(goal_forward * max_forward, deadzone_value)
        rotation_value = deadzone(rotation_value * max_rotate, deadzone_value)

        delta = goal_forward - self.forward

        if abs(delta) < max_accel:
            self.forward += delta
        else:
            self.forward += max_accel * sign(delta)


        self.drivetrain.arcade_drive(self.forward, rotation_value)

        #ELEVATOR CONTROL
        elevateToHeight = False

        #If proximity sensor = 0
            #self.encoder.reset()

        
        if (self.operator.getAButton() and (self.operator.getTriggerAxis(self.LEFT) > -0.9 and not (self.operator.getTriggerAxis(self.LEFT) == 0))):
            self.command.setSetpoint(LOW_CARGO_VALUE)
            elevateToHeight = True

            print("low cargo value")

        elif self.operator.getAButton():
            self.command.setSetpoint(LOW_HATCH_VALUE)
            elevateToHeight = True

        elif (self.operator.getBButton() and (self.operator.getTriggerAxis(self.LEFT) > -0.9 and not (self.operator.getTriggerAxis(self.LEFT) == 0))):
            self.command.setSetpoint(MEDIUM_CARGO_VALUE)
            elevateToHeight = True

        elif self.operator.getBButton():
            self.command.setSetpoint(MEDIUM_HATCH_VALUE)
            elevateToHeight = True
        
        elif self.operator.getXButton():
            self.command.setSetpoint(HIGH_CARGO_VALUE)
            elevateToHeight = True

        elif (self.operator.getXButton() and (self.operator.getTriggerAxis(self.LEFT) > -0.9 and not (self.operator.getTriggerAxis(self.LEFT) == 0))):
            self.command.setSetpoint(HIGH_HATCH_VALUE)
            elevateToHeight = True
        

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
            self.lift.raise_up()
        if release_pistons:
            self.lift.lower_down()

        if self.matchtimer.AreWeThereYet():
            self.lift.raise_all()
             #do something special

class MatchTimer:

    def __init__(self, duration):
        self.starttime = time.time()
        self.duration = TELEOP_DURATION_SECONDS

    def endTime(self): 
        self.end_time = (self.starttime + self.duration)
        return(self.end_time)
    def AreWeThereYet(self):
        now = time.time()
        return self.endTime() >= now
        
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

class elevatorAttendant:
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

    def turn(self):
        self.pid.enable()
    
    def stop(self):
        self.pid.disable()

    def setSetpoint(self, height):
        self.pid.setSetpoint(height)

class fakeEncoder:
    def pidGet(self):
        return hal_data['encoder'][0]['value']

    def getPIDSourceType(self):
        return PIDSourceType.kDisplacement

def deadzone(val, deadzone):
    if abs(val) < deadzone:
        return 0
    return val

def sign(number):
    if number > 0:
        return 1
    else:
        return -1

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
    