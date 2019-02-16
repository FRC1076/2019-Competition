import wpilib 
from wpilib import DoubleSolenoid

class Lift:
    """
    Left and right pistons are ganged together, so
    only center/back have independent operation.
    """
    stateExtend = DoubleSolenoid.Value.kForward
    stateRetract = DoubleSolenoid.Value.kReverse

    def __init__(self, center, back):
        self.center = center
        self.back = back

    def raise_center(self):
        self.center.set(Lift.stateExtend)
    
    def raise_back(self):
        self.back.set(Lift.stateExtend)

    def lower_center(self):
        self.center.set(Lift.stateRetract)

    def lower_back(self):
        self.back.set(Lift.stateRetract)

    def lower_all(self): 
        self.lower_center()
        self.lower_back()

    def raise_all(self):
        self.raise_center()
        self.raise_center()
