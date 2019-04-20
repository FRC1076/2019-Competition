import wpilib
import json
from networktables import NetworkTables

class VisionSensor:
    """
    Example:
        visionSensor = VisionSensor('10.10.76.7', 8812)

        This creates channel to listen on port 8812 for angle information.
    """
    def __init__(self, network_table, logger=None):
        self.network_table = network_table
        self.logger = logger

    def pidGet(self):
        bearing = self.network_table.getNumber('vision-bearing', 0.0)
        if self.logger is not None:
            self.logger.error('Got vision-bearing of ',bearing)
        return bearing

    def getPIDSourceType(self):
        return wpilib.interfaces.pidsource.PIDSource.PIDSourceType.kDisplacement
