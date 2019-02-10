import wpilib
import enum

import hal
#from .interfaces.generichid import GenericHID

class GuitarHeroController():
    def __init__(self):
        self.controller = wpilib.XboxController(0)
    
    def WammyBar(self):
        return self.controller.getRawAxis(2)
    



#class GuitarHeroController(GenericHID):
#    class Coler_Button(enum.IntEnum):
#        green = 0
#        red = 1
#        yellow = 3
#        blue = 2
#        orage = 4
#        #high octive
#        green8 = (0,8)
#        red8 = (1,8)
#        yellow8 = (3,8)
#        blue8 = (2,8)
#        orange8 = (4,8)
#        Start = 7
#        back = 6
#    def __init__(self, port: int) -> None:
        
#        super().__init__(port)

#        hal.report(hal.UsageReporting.kResourceType_XboxController, port)
#        Wammy_bar = self.getRawAxis(4)
#        slider = self.getRawAxis(2)
#        curser_Pad = self.getPOV
#        Strum = self.getPOV
#        tilt = self.getRawAxis(5)
    
     
     
        
        
        
        
        

        