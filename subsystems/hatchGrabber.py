from wpilib import DoubleSolenoid

class Grabber:
    def __init__(self, retract, extend):
        self.out = SolenoidPair(retract, extend)

    def lower_down(self):
        self.out.retract()
    
    def raise_up(self):
        self.out.extend()

class SolenoidPair:
    def __init__(self, retract, extend):
        self._retract = retract
        self._extend = extend 
    
    def retract(self):
        self._retract.set(True)
        self._extend.set(False)

    def extend(self):
        self._extend.set(True)
        self._retract.set(False)


