import wpilib

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
        """
        Get specific controller button and return True if it
        is being pressed, False otherwise.
        """
        if self.controller.getYButton():
            runDriverAssistant = True
            if self.logger is not None:
                self.logger.info("button Y has been pressed")
        
        else:
            runDriverAssistant = False
        
        return runDriverAssistant
    
