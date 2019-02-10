import wpilib


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

LEFT_CONTROLLER_HAND = wpilib.interfaces.GenericHID.Hand.kLeft
RIGHT_CONTROLLER_HAND = wpilib.interfaces.GenericHID.Hand.kRight
class Elevator:
    def __init__(self, elevator_motor, encoder_motor):
        self.encoder_motor = encoder_motor
        self.elevator_motor = elevator_motor

    def go_up(self, speed = 1.0):
        self.elevator_motor.set(speed)

    def go_down(self, speed = 1.0):
        self.elevator_motor.set(-speed)

    def stop(self):
        self.elevator_motor.set(0)

class ElevatorAttendant:
    def __init__(self, encoder, lowInput, highInput, lowOutput, highOutput):
        self.encoder = encoder

        kP = 0.01
        kI = 0.00
        kD = 0.00
        self.pid = wpilib.PIDController(kP, kI, kD, source=self, output=self)
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

    def pidGet(self):
        return self.encoder.getQuadraturePosition()
    
    def getPIDSourceType(self):
        return wpilib.interfaces.pidsource.PIDSource.PIDSourceType.kDisplacement
        

class ElevatorController:

    def __init__(self, controller, logger = None):
        self.controller = controller
        self.logger = logger
        self.damper = 0

    def getOperation(self):
        self.damper += 1
        triggerAxisValue = self.controller.getTriggerAxis(LEFT_CONTROLLER_HAND)
        
        if self.logger is not None:
            if (self.damper % 50) == 0:
                self.logger.info("triggerAxis(LEFT) value = %f", triggerAxisValue)
                
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

        elif self.controller.getXButton():
            if whammyBarPressed:
                setPoint = HIGH_CARGO_VALUE
            else:
                setPoint = HIGH_HATCH_VALUE
        
        else:
            setPoint = 0
            runElevator = False
        
        return (runElevator, setPoint)
    
