import wpilib

class ballManipulator:
    def __init__(self, motor):
        self.motor = motor

    def gather(self, speed = 1.0):
        self.motor.set(speed)

    def spit(self, speed = 1.0):
        self.motor.set(-speed)

    def stop(self):
        self.motor.set(0)
        