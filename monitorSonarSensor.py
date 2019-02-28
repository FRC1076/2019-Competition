# simple utility to connect to sonar sensor at .11
# and log the range-cm it returns.
#
from subsystems.sonarSensor import SonarSensor
import time
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
rootLogger = logging.getLogger()

sensor = SonarSensor('10.10.76.11', 5811,
                     simulation=False, logger=rootLogger)

while(1):
    sensor.receiveRangeUpdates()
    print("Received: ", sensor.pidGet())
    # read 50 times a second to be sure to keep up
    time.sleep(0.02)

