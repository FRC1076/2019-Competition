import time
import wpilib

#Teleop duration
TELEOP_DURATION_SECONDS = 37


class MatchTimer:

    def __init__(self, duration):
        self.duration = TELEOP_DURATION_SECONDS
        self.timer = wpilib.Timer()
        self.timer.reset()
        self.timer.start()

    def time_left(self):
        if self.timer.hasPeriodPassed(1):
            self.time = (self.duration - 1)
            return (self.time)
        else:
            return (0)