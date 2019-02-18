# simple utility to connect to sonar sensor at .11
# and log the range-cm it returns.
#

from subsystems.sonarSensor import SonarSensor
import time
import logging
logger = logging.getLogger('monitor_sonar')

sensor = SonarSensor('10.10.76.11', 5811, logger)

while(1):
    sensor.receiveRangeUpdates()
    print("Received: ", sensor.pidGet())
    time.sleep(0.1)

