import wpilib

class ContinuousRotationServo:

    def __init__(self, channel):
        """
        Create controller for servo that can be used to open and close a valve.
        """
        self.servo = wpilib.PWM(channel)
        self.close_value = 0
        #self.setBounds(1.0, 1.48, 1.5, 1.52, 2.0)
        self.setBounds(2.0, 1.65, 1.5, 1.35, 1.0)

    def setBounds(self, maximum, deadbandMax, center, deadbandMin, minimum):
        self.servo.setBounds(maximum, deadbandMax, center, deadbandMin, minimum)  

    def closingValue(self):
        return self.close_value
        
    def hasBeenClosing(self):
        return self.close_value > 1

    def turn(self, turn):
        if turn < 0:
            self.close_value -= 0.02
        else:
            self.close_value += 0.02
        self.servo.setSpeed(turn)

    def close(self):
        self.turn(1)

    def open(self):
        self.turn(-1)
    

    def setSpeed(self, speed_value):
        self.servo.setSpeed(speed_value)

    def stopMotor(self):
        self.servo.stopMotor()



class ContinuousRotationServoWithFeedback:

    def __init__(self, channel, feedback):
        self.servo = wpilib.PWM(channel)
        #self.setBounds(1.0, 1.48, 1.5, 1.52, 2.0)
        self.setBounds(1.72, 1.52, 1.5, 1.48, 1.28)
        self.position = wpilib.AnalogInput(feedback)

    def setBounds(self, maximum, deadbandMax, center, deadbandMin, minimum):
        self.servo.setBounds(maximum, deadbandMax, center, deadbandMin, minimum)  

    # speed value must be between -1 and 1
    def turn(self, turn):
        turn = turn*70
        center = 0
        self.servo.setSpeed(center + turn)

    def setSpeed(self, speed_value):
        self.servo.setSpeed(speed_value)

    def stopMotor(self):
        self.servo.setSpeed(0)
    
    def getPosition(self):

        value = self.position.getValue()
        voltage = self.position.getVoltage()
        #stars = "*"*(int(voltage*20))
        return "servo fb value: {} servo fb voltage: {}".format(value, voltage)