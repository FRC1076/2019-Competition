import math
import wpilib
import ctre 
from subsystems.drivetrain import Drivetrain
from subsystems.elevator import Elevator
from subsystems.hatchGrabber import Grabber
from wpilib import DoubleSolenoid
from wpilib.interfaces import GenericHID

LEFT = wpilib.interfaces.GenericHID.Hand.kLeft
RIGHT = wpilib.interfaces.GenericHID.Hand.kRight

#DRIVETRAIN IDs
LEFT_MASTER_ID = 1
LEFT_SLAVE_1_ID = 2
LEFT_SLAVE_2_ID = 3

RIGHT_MASTER_ID = 4
RIGHT_SLAVE_1_ID = 5
RIGHT_SLAVE_2_ID = 6

#HATCH GRABBER PISTON IDs
RETRACT_ID = 0
EXTEND_ID = 0

#ELEVATOR ID
ELEVATOR_ID = 0

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
            retract = wpilib.Solenoid(RETRACT_ID),
            extend = wpilib.Solenoid(EXTEND_ID)
            )
        
        #ELEVATOR
        elevator_motor = ctre.WPI_TalonSRX(ELEVATOR_ID)
        self.elevator = Elevator(elevator_motor, encoder_motor=elevator_motor)
       
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

        goal_forward = -self.driver.getY(RIGHT)
        rotation_value = self.driver.getX(LEFT)

        goal_forward = deadzone(goal_forward * max_forward, deadzone_value)
        rotation_value = deadzone(rotation_value * max_rotate, deadzone_value)

        delta = goal_forward - self.forward

        if abs(delta) < max_accel:
            self.forward += delta
        else:
            self.forward += max_accel * sign(delta)

        self.robot_drive.arcade_drive(self.forward, rotation_value)

        #ELEVATOR CONTROL
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
        release_pistons = self.operator.getBackButtonReleased() or self.driver.getStartButtonReleased()

        if activate_pistons:
            self.lift.raise_up()
        if release_pistons:
            self.lift.lower_down()

    def deadzone(val, deadzone):
        if abs(val) < deadzone:
            return 0
        return val

    def sign(number):
        if number > 0:
            return 1
        else:
            return -1



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


if __name__ == "__main__":
    wpilib.run(MyRobot)