from wpilib import DoubleSolenoid

class extendPiston():
    stateExtend = DoubleSolenoid.Value.kForward
    stateRetract = DoubleSolenoid.Value.kReverse
    def __init__(self, piston):
        self.piston = piston

    def retract(self):
        self.piston.set(extendPiston.stateRetract)
    
    def extend(self):
        self.piston.set(extendPiston.stateExtend)
