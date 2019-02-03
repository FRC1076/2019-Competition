from wpilib import DoubleSolenoid

class extendPiston():
    stateExtend = DoubleSolenoid.Value.kForward
    stateRetract = DoubleSolenoid.Value.kReverse
    def __init__(self, piston):
        self.piston = piston

    def lower_down(self):
        self.piston.set(extendPiston.stateRetract)
    
    def raise_up(self):
        self.piston.set(extendPiston.stateExtend)
