import time
import wpilib

class MatchTimer:

    def __init__(self, duration):
        self.duration = duration
        
        self.MatchTime = wpilib.Timer()          
        self.NotifyTimer = wpilib.Timer()
        
        self.MatchTime.reset()
        self.NotifyTimer.reset()
        
        self.NotifyTimer.start()
        self.MatchTime.start()
    def time_left(self):     
        if self.NotifyTimer.hasPeriodPassed(1):
            self.NotifyTimer.reset()
            return (int(self.duration - self.MatchTime.get()))
        else: 
            return(None)

x = MatchTimer(215)
print(x.time_left())
print(x.time_left())
print(x.time_left())
print(x.time_left())
