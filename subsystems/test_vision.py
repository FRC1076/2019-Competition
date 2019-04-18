import sys
import time
from networktables import NetworkTables
from networktables.util import ntproperty
# To see messages from networktables, you must setup logging
import logging

logging.basicConfig(level=logging.DEBUG)

if len(sys.argv) != 2:
    print("Error: specify an IP to connect to!")
    exit(0)

ip = sys.argv[1]

NetworkTables.initialize(server=ip)

def connectionListener(connected, info):
    print(info, "; Connected=%s" % connected)

class someClient(object):
    vision_bearing = ntproperty("/SmartDashboard/vision-bearing", 0.0)

NetworkTables.addConnectionListener(connectionListener, immediateNotify=True)

sd = NetworkTables.getTable("SmartDashboard")

c = someClient()
while True:
    time.sleep(1)
    c.vision_bearing = -25.0