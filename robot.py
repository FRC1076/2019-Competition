import math
import wpilib 
from wpilib.interfaces import GenericHID
 
LEFT = GenericHID.Hand.kLeft
RIGHT = GenericHID.Hand.kRight

class Robot(wpilib.IterativeRobot):
    def robotInit(self):
        #assigns driver as controller 0 and operator as controller 1

        self.driver = wpilib.XboxController(0)
        self.operator = wpilib.XboxController(1)

    def robotPeriodic(self):
        pass

    def teleopInit(self):
        pass

    def teleopPeriodic(self):
        #Arcade Controls

        DEADZONE = 0.2
        MAX_ACCELERATION = 0.3

        goal_forward = -self.driver.getY(RIGHT)
        goal_rotate = self.driver.getX(LEFT)

        MAX_FORWARD = 1.0
        MAX_ROTATE = 1.0

  
    
        (x,y) = deadzone2(DEADZONE, (goal_rotate, goal_forward))
def is_in_circular_deadzone(radius, location):
    (x,y) = location
    """
    #if in the function is in deadzone it will return true.
    #if the function is outside of the deadzone the function will return false.
    """
    return(x**2+y**2) <= (radius**2)
  
def circular_deadzone(radius, location):
    """
    # if in the deazone this function will return 0,0.
    """
    (x,y) = location
    if is_in_deadzone(radius, location):
        return(0,0)
    elif location[1] == 0:
        """
        # if x is zero this function will just y without mutiplying or divideing by 0.
        """
        if x < 0:
            nx = (x + radius)/(1-radius)
        else:  
            nx = (x - radius)/(1 - radius)
            nx = round(nx, 2)
        return(nx,0)

      
    else:
        """
        # Rescales the x and the y values for the deadzone.
        will turn the x and y to polar cordinates and rescale then then turn them back into the rescaled cartesian coordinates.
        """
        i = (x**2+y**2)
        r = (math.sqrt(i))
        theta = (math.atan(x/y))
        nx = (r*math.cos(theta))
        nx = round(nx, 2)
        ny = (r*math.sin(theta))
        ny = round(ny, 2)
    return(nx,ny)

