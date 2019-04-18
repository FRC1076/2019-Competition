import wpilib
import json
from networktables import NetworkTables


class VisionSensor:
    """
    Vision sensor has two main roles.   It listens on the specified
    port for udp angle packets and parses them to obtain the most
    recent value for the angle to target.  It also acts as a data
    source for a PIDController.

    If the target is to the left of the robot, the angle is reported
    as negative.

    Example:
        visionSensor = VisionSensor('10.10.76.7', 8812)

        This creates channel to listen on port 8812 for angle information.
    """
    def __init__(self, network_table, logger=None):
        self.network_table = network_table
        self.logger = logger
        
        
        self.bearing = 0
        self.range_cm = 0
        

    def pidGetBearing(self):
        # return cached bearing that was last received from
        # the vision system
        return self.bearing

    def pidGetRange(self):
        # return cached range that was last received from
        # the vision system
        return self.range_cm

    def pidGet(self):
        return self.pidGetBearing()

    def getPIDSourceType(self):
        return wpilib.interfaces.pidsource.PIDSource.PIDSourceType.kDisplacement

    def receiveAngleUpdates(self):
        self.bearing = self.network_table.getNumber('vision-bearing', 0.0)