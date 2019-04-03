import wpilib 
from subsystems.continuousServo import ContinuousRotationServo
from threading import Thread
from time import sleep

ROLL_TOL = 2
PITCH_TOL = ROLL_TOL

LEAN_DELAY = 3
LEAN_TARGET = 15

class Climber:
    def __init__(self, gyro, servo0, servo1, servo2, servo3, logger=None):
        self.servo0 = servo0
        self.servo1 = servo1
        self.servo2 = servo2
        self.servo3 = servo3
        self.gyro = gyro

        self.logger = logger
        self.tilt_thread = None

        self.rollTarget = 0
        self.pitchTarget = 0

        #self.leanSequence = [ (0,0) , (3,10) , (3,20) ]
        self.leanSequence = [ (0,0) ]
        self.thisLeanSequence = [(0,0)]
  
    def balanceMeToo(self): #-1 is open, 1 is close

        if self.tilt_thread is None:
            self.tilt_thread = Thread(target=Climber.leanTimed, args=(self,))
            self.tilt_thread.start()

        if self.roll_offset is None:
            self.roll_offset = self.gyro.getRoll()
        if self.pitch_offset is None:
            self.pitch_offset = self.gyro.getPitch()

        roll_value = self.gyro.getRoll() - self.roll_offset
        pitch_value = self.gyro.getPitch() - self.pitch_offset

        if abs(roll_value - self.rollTarget) > ROLL_TOL or abs(pitch_value - self.pitchTarget) > PITCH_TOL:
            if roll_value < self.rollTarget: #left side high
                if pitch_value < self.pitchTarget: #back high
                    self.servo2.stopMotor()      
                else: #front high
                    self.servo0.stopMotor()
            else: #right side high
                if pitch_value < self.pitchTarget: #back high
                    self.servo3.stopMotor()
                else: # front high
                    self.servo1.stopMotor()
        else:
            self.servo0.turn(-1)
            self.servo1.turn(-1)
            self.servo2.turn(-1)
            self.servo3.turn(-1)

    def reset(self):
        self.roll_offset = None
        self.pitch_offset = None

        self.stopAll()

    def balanceMe(self):

        roll_value = self.gyro.getRoll()
        pitch_value = self.gyro.getPitch()

        thr = Thread(target=Climber.leanTimed, args=(self,))
        thr.start()
        
        if abs(roll_value - self.rollTarget) > ROLL_TOL or abs(pitch_value - self.pitchTarget) > PITCH_TOL:
            if roll_value < self.rollTarget: #left side high
                if pitch_value < self.pitchTarget: #back high
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
                if pitch_value < self.pitchTarget: #back high
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

    def leanTimed(self):
        for (delay, angle) in self.leanSequence:
            sleep(delay)
            self.pitchTarget = angle
        
    def stopAll(self):
        self.servo0.stopMotor()
        self.servo1.stopMotor()
        self.servo2.stopMotor()
        self.servo3.stopMotor()

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

    