import wpilib 
from wpilib import DoubleSolenoid

class Lift:
    """
    Left and right pistons are ganged together, so
    only center/back have independent operation.
    """
    stateExtend = DoubleSolenoid.Value.kForward
    stateRetract = DoubleSolenoid.Value.kReverse

    def __init__(self, back):
        #self.center = center
        self.back = back

    def raise_back(self):
        self.back.set(Lift.stateExtend)

    def lower_back(self):
        self.back.set(Lift.stateRetract)
