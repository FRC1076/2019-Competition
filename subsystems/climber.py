import wpilib 
from subsystems.continuousServo import ContinuousRotationServo

ROLL_TOL = 2
PITCH_TOL = ROLL_TOL

class Climber:
    def __init__(self, gyro, servo0, servo1, servo2, servo3, logger=None):
        self.servo0 = servo0
        self.servo1 = servo1
        self.servo2 = servo2
        self.servo3 = servo3
        self.gyro = gyro

        self.logger = logger

    def balanceMe(self):

        roll_value = self.gyro.getRoll()
        pitch_value = self.gyro.getPitch()

        if abs(roll_value) > ROLL_TOL or abs(pitch_value) > PITCH_TOL:
            if roll_value < 0: #left side high
                if pitch_value < 0: #back high
                    if self.servo1.hasBeenClosing():
                        self.servo1.turn(-1)
                    else:
                        self.servo1.stopMotor()
                        self.servo2.turn(1)
                else: #front high
                    if self.servo3.hasBeenClosing():
                        self.servo3.turn(-1)
                    else:
                        self.servo3.stopMotor()
                        self.servo0.turn(1)
            else: #right side high
                if pitch_value < 0: #back high
                    if self.servo0.hasBeenClosing():
                        self.servo0.turn(-1)
                    else:
                        self.servo0.stopMotor()
                        self.servo3.turn(1)
                else: # front high
                    if self.servo2.hasBeenClosing():
                        self.servo2.turn(-1)
                    else:
                        self.servo2.stopMotor()
                        self.servo1.turn(1)
        else:
            self.servo0.stopMotor()
            self.servo1.stopMotor()
            self.servo2.stopMotor()
            self.servo3.stopMotor()

    def resetServos(self):
        pass
    def reInit(self):
        pass

    def openAllValves(self):
        self.servo0.turn(-1)
        self.servo1.turn(-1)
        self.servo2.turn(-1)
        self.servo3.turn(-1)

    def closeAllValves(self):
        self.servo0.turn(1)
        self.servo1.turn(1)
        self.servo2.turn(1)
        self.servo3.turn(1)

    def turnAllValves(self, turnRate):
        self.servo0.turn(turnRate)
        self.servo1.turn(turnRate)
        self.servo2.turn(turnRate)
        self.servo3.turn(turnRate)

    