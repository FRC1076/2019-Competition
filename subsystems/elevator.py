import wpilib

class Elevator:
    def __init__(self, motor):
        self.motor = motor

    def go_up(self, speed = 1.0):
        self.motor.set(speed)

    def go_down(self, speed = 1.0):
        self.motor.set(-speed)

    def stop(self):
        self.motor.set(0)