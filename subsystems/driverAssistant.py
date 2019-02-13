import wpilib

#from subsystems.remoteSensors import AngleSensor, RangeSensor
#This doesn't seem like it is needed here

#ELEVATOR PID IDs
#MIN_ELEVATOR_RANGE = 0
#MAX_ELEVATOR_RANGE = 200

#ELEVATOR STOPS
#LOW_HATCH_VALUE = 0
#LOW_CARGO_VALUE = 500
#MEDIUM_HATCH_VALUE = 1000
#MEDIUM_CARGO_VALUE = 1500
#HIGH_HATCH_VALUE = 2000
#HIGH_CARGO_VALUE = 2500

#LEFT_CONTROLLER_HAND = wpilib.interfaces.GenericHID.Hand.kLeft
#RIGHT_CONTROLLER_HAND = wpilib.interfaces.GenericHID.Hand.kRight
#class Elevator:
#    def __init__(self, motor, encoder_motor=None):
#        self.encoder_motor = encoder_motor
#        self.motor = motor
#
#    def go_up(self, speed = 1.0):
#        self.motor.set(speed)
#
#    def go_down(self, speed = 1.0):
#        self.motor.set(-speed)
#
#    def stop(self):
#        self.motor.set(0)

class driverAssistant:
    """
    DriverAssistant provide semi-autonomous driving directed by the remote sensors 
    identifying the angle needed to be changed and the distance needed to be traveled. 
    It uses PID algorithms from constant input of the angle and the distance that needs 
    to be changed and returns the outputs of the PID for the gyro and the PID for the 
    encoder.
    
    Create the driverAssistant as follows:
    da = DriverAssistant(gyro, movementEncoder)

    Use the obj.setSetpointTurner(angleSensor.pidGet) and obj.setSetpointMovement(rangeSensor.pidGet) 
    in order to set the points. 

    Use the activate methods to enable the PIDs and the stop methods to disable them

    Access the output from the get methods
    
    """
    
    def __init__(self, gyro, movementEncoder):

        # L = low, H = high, I = input, O = output
        self.turnerLI = -15.0
        self.turnerHI = 15.0
        self.turnerLO = -0.2
        self.turnerHO = 0.2
        self.tkP = 0.01
        self.tkI = 0.00
        self.tkD = 0.00

        self.movementLI = 0
        self.movementHI = 100
        self.movementLO = -1.0
        self.movementHO = 1.0
        self.mkP = 0.01
        self.mkI = 0.00
        self.mkD = 0.00

        self.turnerPID = aPID(gyro, self.turnerLI, self.turnerHI, self.turnerLO, self.turnerHO, self.tkP, self.tkI, self.tkD)
        self.movementPID = aPID(movementEncoder, self.movementLI, self.movementHI, self.movementLO, self.movementHO, self.mkP, self.mkI, self.mkD)

        def setSetpointTurner(self, value):
            self.turnerPID.setSetpoint(value)
        
        def setSetpointMovement(self, value):
            self.movementPID.setSetpoint(value)
        
        def activateTurner(self):
            self.turnerPID.move()

        def activateMovement(self):
            self.movementPID.move()

        def stopTurner(self):
            self.turnerPID.stop()
        
        def stopMovement(self):
            self.movementPID.stop()

        def getTurnRate(self):
            return self.turnerPID.getPIDValueRate()

        def getMovementRate(self):
            return self.movementPID.getPIDValueRate()

class aPID:
    def __init__(self, encoder, lowInput = 0, highInput = 100, lowOutput = -1.0, highOutput = 1.0, kP = 0.01, kI = 0.00, kD = 0.00):
        self.encoder = encoder
        self.PIDValueRate = 0

        self.pid = wpilib.PIDController(kP, kI, kD, source=encoder, output=self)
        self.pid.setInputRange(lowInput, highInput)
        self.pid.setOutputRange(lowOutput, highOutput)

    def pidWrite(self, output):
        self.PIDValueRate = output
    
    def getPIDValueRate(self):
        return self.PIDValueRate

    def move(self):
        self.pid.enable()
    
    def stop(self):
        self.pid.disable()

    def setSetpoint(self, height):
        self.pid.setSetpoint(height)

class driverAssistantController:

    def __init__(self, controller, logger = None):
        self.controller = controller
        self.logger = logger
        #self.damper = 0

    def getOperation(self):
        #self.damper += 1
        #triggerAxisValue = self.controller.getTriggerAxis(LEFT_CONTROLLER_HAND)
        
        #if self.logger is not None:
        #    if (self.damper % 50) == 0:
        #        self.logger.info("triggerAxis(LEFT) value = %f", triggerAxisValue)
                
        #whammyBarPressed = (triggerAxisValue > -0.7 and not (triggerAxisValue == 0))
        #runDriverAssistant = True     # assume running unless no buttons pressed
                    
        if self.controller.getYButton():
            runDriverAssistant = True
            if self.logger is not None:
                self.logger.info("button Y has been pressed")
        
        else:
            #setPoint = 0
            runDriverAssistant = False
        
        return runDriverAssistant
    
