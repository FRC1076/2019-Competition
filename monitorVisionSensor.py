# simple utility to connect to sonar sensor at .13
# and log the bearing it returns.
#
from subsystems.visionSensor import VisionSensor
import time
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
rootLogger = logging.getLogger()

sensor = VisionSensor('10.10.76.13', 5880,
                      simulation=False, logger=rootLogger)

while(1):
    sensor.receiveAngleUpdates()
    rootLogger.debug("Received: %d", sensor.pidGet())
    # read 50 times a second to be sure to keep up
    time.sleep(0.02)
