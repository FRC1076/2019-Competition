import wpilib

class ContinuousRotationServo:

    def __init__(self, channel):
        channel_number = channel
        self.servo = wpilib.PWM(channel)
        #self.setBounds(1.0, 1.48, 1.5, 1.52, 2.0)
        self.setBounds(2.0, 1.65, 1.5, 1.35, 1.0)

    def setBounds(self, maximum, deadbandMax, center, deadbandMin, minimum):
        self.servo.setBounds(maximum, deadbandMax, center, deadbandMin, minimum)  

    # speed value must be between -1 and 1
    def turn(self, turn):
        turn = turn*7
        center = 0
        self.servo.setSpeed(center + turn)

    def setSpeed(self, speed_value):
        self.servo.setSpeed(speed_value)

    def stopMotor(self):
        self.servo.stopMotor()