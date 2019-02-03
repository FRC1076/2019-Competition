import wpilib 
from wpilib import DoubleSolenoid



class Lift:

    stateExtend = DoubleSolenoid.Value.kForward
    stateRetract = DoubleSolenoid.Value.kReverse

    def __init__(self, front_left, front_right, back_left, back_right):
 
        self.front_left = front_left
        self.front_right = front_right
        self.back_left = back_left
        self.back_right = back_right

    def raise_left(self):
        self.front_left.set(Lift.stateExtend)
        self.back_left.set(Lift.stateExtend)

    def raise_right(self):
        self.front_right.set(Lift.stateExtend)
        self.back_right.set(Lift.stateExtend)

    def lower_left(self):
        self.front_left.set(Lift.stateRetract)
        self.back_left.set(Lift.stateRetract)
    
    def lower_right(self):
        self.front_right.set(Lift.stateRetract)
        self.back_right.set(Lift.stateRetract)

    def lower_all(self):
        self.front_left.set(Lift.stateRetract)
        self.front_right.set(Lift.stateRetract)
        self.back_left.set(Lift.stateRetract)
        self.back_right.set(Lift.stateRetract)

    def raise_all(self):
        self.front_left.set(Lift.stateExtend)
        self.front_right.set(Lift.stateExtend)
        self.back_left.set(Lift.stateExtend)
        self.back_right.set(Lift.stateExtend)
