from wpilib import DoubleSolenoid

class Grabber:
    stateExtend = DoubleSolenoid.Value.kForward
    stateRetract = DoubleSolenoid.Value.kReverse
    def __init__(self, hatch):
        self.hatch = hatch

    def extend(self):
        self.hatch.set(Grabber.stateExtend)
    
    def retract(self):
        self.hatch.set(Grabber.stateRetract)



