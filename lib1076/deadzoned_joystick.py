import math
def is_in_deadzone(radius, location):
    (x,y) = location
    return(x**2+y**2) < (radius**2)

def deadzone(radius, location):
 
    (x,y) = location
    i = (x**2+y**2)
    r = (math.sqrt(i))
    theta = (math.atan(x/y))
    k =((r-radius)/(1-radius))
    