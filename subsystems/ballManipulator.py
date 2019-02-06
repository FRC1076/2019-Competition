import wpilib
LEFT_CONTROLLER_HAND = wpilib.interfaces.GenericHID.Hand.kLeft

GATHER_SPEED = 1.0
SPIT_SPEED = 1.0
STOP_SPEED = 0.0

class BallManipulator:
    """
    Manipulator wraps a motor controller that gathers and spits
    out the cargo balls.
    """
    def __init__(self, motor):
        self.motor = motor

    def gather(self, speed = GATHER_SPEED):
        self.motor.set(speed)

    def spit(self, speed = SPIT_SPEED):
        self.motor.set(-speed)

    def stop(self):
        self.motor.set(STOP_SPEED)

    def set(self, setValue):
        """
        Direct control to be used with a controller
        that puts out f, 0, and -f for gather, stop,
        and spit, respectively.
        """
        self.motor.set(setValue)

class BallManipulatorController:

    def __init__(self, controller, logger = None):
        """
        bc = BallManipulatorController(HIDController, logger = None)
        Specify the generic controller to be examined to extract
        values that are interesting to ball manipulation.
           Whammy bar and Button Y
        optional logger receives debugging messages.
        """
        self.controller = controller
        self.logger = logger

    def getSetPoint(self):
        """
        Detect the Y with or without whammy and return a setpoint for
        the manipulator motor to use.
        """
        whammyBarPressed = (self.controller.getTriggerAxis(LEFT_CONTROLLER_HAND) > -0.9
                   and not (self.controller.getTriggerAxis(LEFT_CONTROLLER_HAND) == 0))
        
        setPoint = STOP_SPEED

        if self.controller.getYButton():
            if whammyBarPressed:
                setPoint = GATHER_SPEED
            else:
                setPoint = SPIT_SPEED

            if self.logger is not None:
                self.logger.info("BallManipulatorController: button Y has been pressed")
                self.logger.info("%s whammy bar", "WITH" if whammyBarPressed else "WITHOUT")
        
        return setPoint
