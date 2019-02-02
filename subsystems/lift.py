import wpilib 
from wpilib import DoubleSolenoid

class Lift:
    def __init__(self, 
    front_left_retract, front_left_extend,
    front_right_retract, front_right_extend,
    back_left_retract, back_left_extend,
    back_right_retract, back_right_extend):

        self.front_left = SolenoidPair(front_left_retract, front_left_extend)
        self.front_right = SolenoidPair(front_right_retract, front_right_extend)
        self.back_left = SolenoidPair(back_left_retract, back_left_extend)
        self.back_right = SolenoidPair(back_right_retract, back_right_extend)

    def lower_all(self):
        self.front_left.retract()
        self.front_right.retract()
        self.back_left.retract()
        self.back_right.retract()

    def raise_all(self):
        self.front_left.extend()
        self.front_right.extend()
        self.back_left.extend()
        self.back_right.extend()

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
