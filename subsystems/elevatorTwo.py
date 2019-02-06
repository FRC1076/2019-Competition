import wpilib

class ElevatorTwo:
    def __init__(self, left, right, encoder_motor=None):
        self.encoder_motor = encoder_motor
        self.left_motor = left
        self.right_motor = right

    def go_up(self, speed = 1.0):
        self.left_motor.set(speed)
        self.right_motor.set(speed)

    def go_down(self, speed = 1.0):
        self.left_motor.set(-speed)
        self.right_motor.set(-speed)

    def stop(self):
        self.left_motor.set(0)
        self.right_motor.set(0)