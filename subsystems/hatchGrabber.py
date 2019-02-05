from wpilib import DoubleSolenoid

class Grabber:
    stateExtend = DoubleSolenoid.Value.kForward
    stateRetract = DoubleSolenoid.Value.kReverse
    def __init__(self, hatch):
        self.hatch = hatch

    def lower_down(self):
        self.hatch.set(Grabber.stateRetract)
    
    def raise_up(self):
        self.hatch.set(Grabber.stateExtend)



