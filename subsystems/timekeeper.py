import time
import wpilib

#Teleop duration
TELEOP_DURATION_SECONDS = 150


class MatchTimer:

    def __init__(self, duration):
        self.starttime = time.time()
        self.duration = TELEOP_DURATION_SECONDS
        self.timer = wpilib.Timer()
        self.timer.reset()
        self.timer.start()
    def endTime(self): 
        self.end_time = (self.starttime + self.duration)
        return (self.end_time)
    def AreWeThereYet(self):
        now = time.time()
        if self.endTime() >= now:
            time_left = (self.endTime() - now)
            return (time_left)
        else:
            return(0)
    