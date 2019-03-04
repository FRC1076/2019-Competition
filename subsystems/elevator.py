import wpilib


#ELEVATOR PID IDs
MIN_ELEVATOR_RANGE = 0
MAX_ELEVATOR_RANGE = 200

#ELEVATOR STOPS
LOW_HATCH_VALUE = 0
LOW_CARGO_VALUE = 50
MEDIUM_HATCH_VALUE = 80
MEDIUM_CARGO_VALUE = 120
HIGH_HATCH_VALUE = MEDIUM_HATCH_VALUE
HIGH_CARGO_VALUE = MEDIUM_CARGO_VALUE


LEFT_CONTROLLER_HAND = wpilib.interfaces.GenericHID.Hand.kLeft
RIGHT_CONTROLLER_HAND = wpilib.interfaces.GenericHID.Hand.kRight
class Elevator:
    def __init__(self, motor, encoder_motor=None):
        self.encoder_motor = encoder_motor
        self.motor = motor

    def go_up(self, speed = 1.0):
        self.motor.set(speed)

    def go_down(self, speed = 0.5):
        self.motor.set(-speed)

    def stop(self):
        self.motor.set(0)

    def set(self, setpoint):
        self.motor.set(setpoint)

    

class ElevatorAttendant:
    def __init__(self, encoder, lowInput, highInput, lowOutput, highOutput):
        self.encoder = encoder
        self.elevateToHeightRate = 0

        kP = 0.5
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
        self.elevateToHeightRate = 0

    def setSetpoint(self, height):
        self.pid.setSetpoint(height)

class ElevatorController:

    def __init__(self, controller, logger = None):
        self.controller = controller
        self.logger = logger
        self.damper = 0
        

    def getOperation(self):
        self.damper += 1
        WHAMMY_BAR_RAW_AXIS_INDEX = 4
        triggerAxisValue = self.controller.getRawAxis(WHAMMY_BAR_RAW_AXIS_INDEX)
        
        if self.logger is not None:
            if (self.damper % 50) == 0:
                self.logger.info("getRawAxis(WHAMMY) value = %f", triggerAxisValue)
                
        whammyBarPressed = (triggerAxisValue > -0.7 and not (triggerAxisValue == 0))
        runElevator = True     # assume running unless no buttons pressed
                    
        if self.controller.getAButton():
            if whammyBarPressed:
                setPoint = LOW_CARGO_VALUE
            else:
                setPoint = LOW_HATCH_VALUE
            if self.logger is not None:
                self.logger.info("button A has been pressed")

        elif self.controller.getBButton():
            if whammyBarPressed:
                setPoint = MEDIUM_CARGO_VALUE
            else:
                setPoint = MEDIUM_HATCH_VALUE

        elif self.controller.getYButton():
            if whammyBarPressed:
                setPoint = HIGH_CARGO_VALUE
            else:
                setPoint = HIGH_HATCH_VALUE
        
        else:
            elevator_speed = self.controller.getRawAxis(2)

            if self.controller.getStartButton(): 
                setPoint = -(elevator_speed/2)
            elif self.controller.getBackButton():
                setPoint = elevator_speed
            else:
                setPoint = 0
            runElevator = False
        return (runElevator, setPoint)
    
